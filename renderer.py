from PIL import Image, ImageDraw, ImageFont

BASE_WIDTH = 1080
BASE_HEIGHT = 1920
SCALE = 2

def format_price(price):
    return f"₹{price:,}"

def draw_text_box_centered(draw, text, font, box, fill):
    x, y, w, h = box

    words = text.split()
    lines = []
    current = ""

    # Wrap by width
    for word in words:
        test = current + (" " if current else "") + word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= w:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    # Max 3 lines
    lines = lines[:3]

    # Calculate total height
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])

    total_text_height = sum(line_heights) + (len(lines) - 1) * 5
    current_y = y + (h - total_text_height) // 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        draw.text(
            (x + (w - text_w) // 2, current_y),
            line,
            font=font,
            fill=fill
        )

        current_y += text_h + 5


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


def render_story(name, old_price, new_price, product_img):

    canvas = Image.open("assets/background.png").resize(
        (BASE_WIDTH * SCALE, BASE_HEIGHT * SCALE)
    )

    draw = ImageDraw.Draw(canvas)

    FONT_BOOST = 1.8

    font_small = ImageFont.truetype(
        "assets/AmazonEmberDisplay_Bd.ttf",
        int(14 * SCALE * FONT_BOOST)
    )

    font_old = ImageFont.truetype(
        "assets/AmazonEmberDisplay_Rg.ttf",
        int(36 * SCALE * FONT_BOOST)
    )

    font_new = ImageFont.truetype(
        "assets/AmazonEmberDisplay_Bd.ttf",
        int(40 * SCALE * FONT_BOOST)
    )

    # Product Name
    draw_text_box_centered(
        draw,
        name,
        font_small,
        (240 * SCALE, 240 * SCALE, 600 * SCALE, 100 * SCALE),
        (0, 0, 0)
    )

    # Product Image
    box_w = 635 * SCALE
    box_h = 460 * SCALE

    ratio = min(box_w / product_img.width, box_h / product_img.height)
    new_size = (int(product_img.width * ratio), int(product_img.height * ratio))

    product_img_resized = product_img.resize(new_size)

    img_x = 218 * SCALE + (box_w - new_size[0]) // 2
    img_y = 354 * SCALE + (box_h - new_size[1]) // 2

    canvas.paste(product_img_resized, (img_x, img_y), product_img_resized)

    # Old Price
    draw_centered_text(
        draw,
        format_price(old_price),
        font_old,
        (214 * SCALE, 1535 * SCALE, 160 * SCALE, 55 * SCALE),
        (145, 94, 17)
    )

    # New Price
    draw_centered_text(
        draw,
        format_price(new_price),
        font_new,
        (700 * SCALE, 1535 * SCALE, 180 * SCALE, 60 * SCALE),
        (255, 255, 255)
    )

    return canvas