from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap

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

    # wrap by width
    for word in words:
        test = current + (" " if current else "") + word
        bbox = draw.textbbox((0,0), test, font=font)
        if bbox[2] - bbox[0] <= w:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    # max 3 lines
    lines = lines[:5]

    # if still too long → add ...
    if len(lines) == 5:
        while True:
            bbox = draw.textbbox((0,0), lines[-1] + "...", font=font)
            if bbox[2] - bbox[0] <= w:
                lines[-1] += "..."
                break
            lines[-1] = lines[-1][:-1]

    # total height calc
    line_heights = []
    for l in lines:
        bbox = draw.textbbox((0,0), l, font=font)
        line_heights.append(bbox[3]-bbox[1])

    total_text_height = sum(line_heights) + (len(lines)-1)*5

    # vertical center inside box
    current_y = y + (h - total_text_height)//2

    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        text_w = bbox[2]-bbox[0]
        text_h = bbox[3]-bbox[1]

        draw.text(
            (x + (w - text_w)//2, current_y),
            line,
            font=font,
            fill=fill
        )

        current_y += text_h + 5

def draw_centered_text(draw, text, font, box, color):
    x, y, w, h = box

    bbox = draw.textbbox((0,0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    draw.text(
        (
            x + (w - text_w)//2,
            y + (h - text_h)//2
        ),
        text,
        font=font,
        fill=color
    )

def render_story(name, old_price, new_price, image_url):

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
    box_x = 240 * SCALE
    box_y = 240 * SCALE
    box_w = 600 * SCALE
    box_h = 100 * SCALE

    draw_text_box_centered(
        draw,
        name,
        font_small,
        (box_x, box_y, box_w, box_h),
        (0, 0, 0)
    )

    if not image_url or not image_url.startswith("http"):
        raise Exception("Invalid image URL")

    # Product Image
    try:
        response = requests.get(image_url, timeout=15)
        response.raise_for_status()
        product_img = Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        print("IMAGE LOAD ERROR:", e)
        # fallback placeholder
        product_img = Image.new("RGBA", (500, 500), (240, 240, 240, 255))

    box_w = 635*SCALE
    box_h = 460*SCALE

    ratio = min(box_w / product_img.width, box_h / product_img.height)
    new_size = (int(product_img.width*ratio), int(product_img.height*ratio))

    product_img = product_img.resize(new_size)

    img_x = 218*SCALE + (box_w - new_size[0])//2
    img_y = 354*SCALE + (box_h - new_size[1])//2

    canvas.paste(product_img, (img_x, img_y), product_img)

    # Other platform price
    old_text = format_price(old_price)
    draw_centered_text(
        draw,
        old_text,
        font_old,
        (
            214*SCALE,
            1535*SCALE,
            160*SCALE,
            55*SCALE
        ),
        (145,94,17)
    )

    # Digihaat price
    new_text = format_price(new_price)
    draw_centered_text(
        draw,
        new_text,
        font_new,
        (
            700*SCALE,
            1535*SCALE,
            180*SCALE,
            60*SCALE
        ),
        (255,255,255)
    )

    return canvas