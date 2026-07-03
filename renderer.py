from PIL import Image, ImageDraw, ImageFont, ImageColor

BASE_WIDTH = 1080
BASE_HEIGHT = 1920
SCALE = 2

MRP_COLOR = "#A1A1A7"
DEAL_PRICE_COLOR = "#2A7F33"
SAVE_COLOR = "#2A7F33"
NAME_COLOR = "#151515"

def format_price(price):
    if isinstance(price, (int, float)):
        return f"₹{price:,}"
    return str(price)

def truncate_to_char_limit(text, limit):
    """Truncates at the last full word that fits within limit chars, never cutting a word."""
    if len(text) <= limit:
        return text

    words = text.split()
    result = ""
    for word in words:
        candidate = f"{result} {word}".strip()
        if len(candidate) > limit:
            break
        result = candidate

    return result or text[:limit]

def format_savings(old_price, new_price):
    if not isinstance(old_price, (int, float)) or not isinstance(new_price, (int, float)):
        return None
    if old_price <= 0 or new_price > old_price:
        return None

    savings = round(old_price - new_price)
    pct_off = round((old_price - new_price) / old_price * 100)

    return f"₹{savings:,} ({pct_off}%)"

def draw_centered_text(draw, text, font, box, color):
    x, y, w, h = box

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    draw.text(
        (
            x + (w - text_w) // 2,
            y + (h - text_h) // 2
        ),
        text,
        font=font,
        fill=color
    )


def draw_text_line(draw, text, font, x, y, line_height, color):
    """Draws left-aligned text vertically centered within a (x, y, line_height) box,
    matching how design tools export single-line text as (top-left, line-height)."""
    draw.text((x, y + line_height / 2), text, font=font, anchor="lm", fill=color)


def get_fitted_font(draw, text, font_path, target_size, max_width, min_size=10):
    """Loads font_path at target_size, shrinking (never growing) until text fits max_width."""
    size = target_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font)
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 1
    return ImageFont.truetype(font_path, min_size)


def paste_product_image_cover(canvas, product_img, box, scale=1.0, offset_x=0, offset_y=0):
    """Resizes product_img to cover the box (scaling up until an edge hits, cropping the
    overflow on the other axis), then pastes it. scale zooms in further beyond the cover
    fit; offset_x/offset_y (in box-space pixels) pan the crop, clamped to the image bounds."""
    box_x, box_y, box_w, box_h = box

    cover_ratio = max(box_w / product_img.width, box_h / product_img.height)
    ratio = cover_ratio * max(scale, 1.0)

    new_size = (
        max(1, round(product_img.width * ratio)),
        max(1, round(product_img.height * ratio))
    )
    resized = product_img.resize(new_size)

    max_crop_x = new_size[0] - box_w
    max_crop_y = new_size[1] - box_h

    crop_x = max(0, min(max_crop_x // 2 - round(offset_x), max_crop_x))
    crop_y = max(0, min(max_crop_y // 2 - round(offset_y), max_crop_y))

    cropped = resized.crop((crop_x, crop_y, crop_x + box_w, crop_y + box_h))
    canvas.paste(cropped, (box_x, box_y), cropped)


def render_story(
    name,
    old_price,
    new_price,
    product_img,
    image_scale=1.0,
    image_offset_x=0,
    image_offset_y=0
):

    canvas = Image.open("assets/background_new.png").resize(
        (BASE_WIDTH * SCALE, BASE_HEIGHT * SCALE)
    )

    draw = ImageDraw.Draw(canvas)

    font_mrp = ImageFont.truetype(
        "assets/Inter Black 900.otf",
        74 * SCALE
    )

    font_deal_price = ImageFont.truetype(
        "assets/Inter Black 900.otf",
        74 * SCALE
    )

    # Product Name
    name_box = (34 * SCALE, 1585 * SCALE, 1012 * SCALE, 80 * SCALE)
    name_text = truncate_to_char_limit(name, 46)
    font_name = get_fitted_font(
        draw,
        name_text,
        "assets/Inter Black 900.otf",
        60 * SCALE,
        name_box[2]
    )
    draw_centered_text(
        draw,
        name_text,
        font_name,
        name_box,
        ImageColor.getrgb(NAME_COLOR)
    )

    # Product Image — cover-fit 600x600 box, scaled up until an edge hits
    paste_product_image_cover(
        canvas,
        product_img,
        (250 * SCALE, 500 * SCALE, 600 * SCALE, 600 * SCALE),
        scale=image_scale,
        offset_x=image_offset_x * SCALE,
        offset_y=image_offset_y * SCALE
    )

    # MRP
    draw_text_line(
        draw,
        format_price(old_price),
        font_mrp,
        135 * SCALE,
        1380 * SCALE,
        95.4 * SCALE,
        ImageColor.getrgb(MRP_COLOR)
    )

    # MRP strikethrough line
    strike_x, strike_y = 166.62 * SCALE, 1420.28 * SCALE
    strike_w, strike_h = 210 * SCALE, 10 * SCALE
    draw.rectangle(
        [strike_x, strike_y, strike_x + strike_w, strike_y + strike_h],
        fill=ImageColor.getrgb(MRP_COLOR)
    )

    # Deal Price
    draw_text_line(
        draw,
        format_price(new_price),
        font_deal_price,
        675 * SCALE,
        1380 * SCALE,
        95.4 * SCALE,
        ImageColor.getrgb(DEAL_PRICE_COLOR)
    )

    # You Save — covers the background's baked-in "You save ... on DigiHaat" text
    # with the full dynamic sentence, since the new box sits on top of it.
    savings_amount = format_savings(old_price, new_price)
    if savings_amount:
        draw.rectangle(
            [0, 1670 * SCALE, BASE_WIDTH * SCALE, 1760 * SCALE],
            fill=(255, 255, 255)
        )

        save_box = (130 * SCALE, 1680 * SCALE, 827 * SCALE, 50 * SCALE)
        savings_text = f"You save {savings_amount} on DigiHaat"
        font_save = get_fitted_font(
            draw,
            savings_text,
            "assets/Inter Black 900.otf",
            47 * SCALE,
            save_box[2]
        )
        draw_centered_text(
            draw,
            savings_text,
            font_save,
            save_box,
            ImageColor.getrgb(SAVE_COLOR)
        )

    return canvas
