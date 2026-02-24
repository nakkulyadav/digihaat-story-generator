import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0"}

def scrape_product(link):

    try:
        r = requests.get(link, headers=headers, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")

        # PRODUCT NAME
        name_tag = soup.find("h1")
        name = name_tag.get_text(strip=True) if name_tag else "Product"

        # ---------- PRICE EXTRACTION ----------
        old_price = None

        # 1. try strikethrough
        strike = soup.select_one("span.line-through")
        if strike:
            try:
                old_price = int(
                    strike.get_text(strip=True)
                    .replace("₹","")
                    .replace(",","")
                )
            except:
                old_price = None

        # 2. if no strike → try normal price on page
        if old_price is None:
            price_tag = soup.select_one("span.text-lg") or soup.select_one("span.font-semibold")

            if price_tag:
                try:
                    old_price = int(
                        price_tag.get_text(strip=True)
                        .replace("₹","")
                        .replace(",","")
                    )
                except:
                    old_price = None

        # 3. final fallback
        if old_price is None:
            old_price = 0

        # PRODUCT IMAGE
        image_url = None

        img = soup.select_one('img[alt="Product"]')
        if img:
            image_url = img.get("src") or img.get("data-src")

        # fallback image search
        if not image_url:
            imgs = soup.find_all("img")
            for i in imgs:
                src = i.get("src")
                if src and "http" in src and (".jpg" in src or ".png" in src):
                    image_url = src
                    break

        # final fallback image
        if not image_url:
            image_url = "https://via.placeholder.com/500x500.png?text=No+Image"

        return {
            "name": name,
            "old_price": old_price,
            "image": image_url
        }

    except Exception as e:
        print("SCRAPER ERROR:", e)

        # never crash app
        return {
            "name": "Product",
            "old_price": 0,
            "image": "https://via.placeholder.com/500x500.png?text=Error"
        }