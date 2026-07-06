from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw
from concurrent.futures import ThreadPoolExecutor
import asyncio, io, base64, traceback, re

def _first_cut_index(text):
    """Returns the earliest index at which text should be cut, or None if no
    delimiter is present. A comma cuts at its own position; '-', '|', '(' and
    digits only cut when they start a word (so 'Wi-Fi' and '3M' survive intact
    unless they're the entire name, in which case the empty-result fallback
    in shorten_product_name kicks in)."""
    candidates = []

    comma_index = text.find(",")
    if comma_index != -1:
        candidates.append(comma_index)

    for match in re.finditer(r"\S+", text):
        word = match.group()
        if word[0] in "-|(" or word[0].isdigit():
            candidates.append(match.start())
            break

    return min(candidates) if candidates else None


def shorten_product_name(name):
    """Keeps only the core product name, dropping marketing copy tacked onto scraped titles.

    Bundle listings (containing a standalone '+') are left untouched since every part
    identifies what's included. Otherwise, a leading bracketed prefix is skipped
    (e.g. "(Combo Pack) Widget" -> "Widget"), then the name is truncated at whichever
    comes first: a comma, or a word starting with '-', '|', '(', or a digit
    (weight/pack-size/day-count/bundle callouts). If that truncation would leave
    nothing, the original name is returned untouched rather than shipping a blank title.
    """
    if not name:
        return name

    original = name.strip()

    if re.search(r"(?:^|\s)\+(?:\s|$)", original):
        return original

    text = original

    if text.startswith("("):
        close_index = text.find(")")
        if close_index != -1:
            text = text[close_index + 1:].strip()

    cut_index = _first_cut_index(text)
    if cut_index is not None:
        text = text[:cut_index].rstrip()

    return text if text else original

def _placeholder_data_url(text="No Image"):
    img = Image.new("RGB", (500, 500), color=(200, 200, 200))
    draw = ImageDraw.Draw(img)
    draw.text((170, 240), text, fill=(100, 100, 100))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

def _parse_price(text):
    try:
        return int(str(text).replace("₹", "").replace(",", "").strip())
    except (ValueError, TypeError):
        return None

async def _fetch_html_async(link):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(link, wait_until="networkidle", timeout=30000)
        try:
            await page.wait_for_selector('img.object-cover[alt="Product"]', timeout=8000)
        except Exception:
            pass
        html = await page.content()
        await browser.close()
    return html

def _run_in_thread(link):
    import sys
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_fetch_html_async(link))
    finally:
        loop.close()
        asyncio.set_event_loop(None)

def _fetch_rendered_html(link):
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(_run_in_thread, link).result(timeout=60)

def scrape_product(link):
    try:
        html = _fetch_rendered_html(link)
        soup = BeautifulSoup(html, "html.parser")

        # ---------- PRODUCT NAME ----------
        name = None

        # digihaat product h1 has class text-textBase
        name_tag = soup.select_one("h1.text-textBase")
        if not name_tag:
            name_tag = soup.find("h1")
        if name_tag:
            name = name_tag.get_text(strip=True) or None

        if not name:
            og_title = soup.find("meta", property="og:title")
            if og_title:
                name = str(og_title.get("content", "")).strip() or None

        name = shorten_product_name(name or "Product")

        # ---------- PRICE ----------
        old_price = None

        # 1. strikethrough MRP — digihaat shows old price crossed out
        strike = soup.select_one("span.line-through")
        if strike:
            old_price = _parse_price(strike.get_text(strip=True))

        # 2. common MRP selectors
        if old_price is None:
            for selector in [
                "span.text-lg",
                "span.font-semibold",
                ".original-price",
                ".mrp",
                ".mrp-price",
                "[data-testid='original-price']",
                "[class*='originalPrice']",
                "[class*='original_price']",
            ]:
                tag = soup.select_one(selector)
                if tag:
                    old_price = _parse_price(tag.get_text(strip=True))
                    if old_price:
                        break

        # 3. OpenGraph price meta tag
        if old_price is None:
            for tag in [
                soup.find("meta", property="product:price:amount"),
                soup.find("meta", attrs={"name": "product:price:amount"}),
            ]:
                if tag:
                    old_price = _parse_price(tag.get("content"))
                    if old_price:
                        break

        if old_price is None:
            old_price = 0

        # ---------- IMAGE ----------
        image_url = None

        # primary: digihaat main product image (JS-rendered)
        img_tag = soup.select_one('img.object-cover[alt="Product"]')

        if not img_tag:
            img_tag = soup.select_one('img[alt="Product"]')

        if img_tag:
            image_url = str(
                img_tag.get("src")
                or img_tag.get("data-src")
                or img_tag.get("data-lazy-src")
                or ""
            ).strip() or None

            if not image_url and img_tag.get("srcset"):
                srcset = str(img_tag.get("srcset"))
                image_url = srcset.split(",")[0].split(" ")[0]

        # fallback: og:image
        if not image_url:
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image_url = str(og_image.get("content", "")).strip() or None

        if not image_url:
            image_url = _placeholder_data_url("No Image")

        return {
            "name": name,
            "old_price": old_price,
            "image": image_url
        }

    except Exception as e:
        traceback.print_exc()
        raise
