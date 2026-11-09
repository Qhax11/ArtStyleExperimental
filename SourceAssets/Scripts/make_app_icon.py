"""Draws the game's Windows icon and splash screen: a dress on a hanger, in the UI's pink and rose.

  python make_app_icon.py <project_dir>
Writes <project_dir>/Build/Windows/Application.ico (UBT puts it in the exe) and
<project_dir>/Content/Splash/Splash.bmp (shown while the game loads).
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

PINK = (242, 197, 212)
ROSE = (169, 63, 108)
DARK = (110, 30, 62)
WHITE = (255, 250, 252)
S = 1024  # drawn large, scaled down for each icon size


def draw_icon():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((24, 24, S - 24, S - 24), radius=210, fill=PINK, outline=ROSE, width=36)

    # Hanger: hook, then the triangle the dress hangs from.
    cx = S // 2
    d.arc((cx - 70, 120, cx + 70, 260), start=180, end=40, fill=DARK, width=34)
    d.line((cx, 260, cx, 300), fill=DARK, width=34)
    d.line((cx, 300, 230, 420), fill=DARK, width=34, joint="curve")
    d.line((cx, 300, S - 230, 420), fill=DARK, width=34, joint="curve")
    d.line((230, 420, S - 230, 420), fill=DARK, width=34)
    for x in (230, S - 230):
        d.ellipse((x - 17, 403, x + 17, 437), fill=DARK)

    # Dress: straps, bodice, waist ribbon, flared skirt.
    outline = 26
    body = [
        (cx - 150, 400), (cx - 105, 400), (cx - 90, 470), (cx + 90, 470), (cx + 105, 400), (cx + 150, 400),
        (cx + 130, 600), (cx + 290, 880), (cx - 290, 880), (cx - 130, 600),
    ]
    d.polygon(body, fill=WHITE, outline=DARK, width=outline)
    d.rectangle((cx - 132, 585, cx + 132, 630), fill=ROSE)
    d.ellipse((cx - 38, 578, cx + 38, 638), fill=ROSE, outline=DARK, width=10)
    # Skirt folds.
    for dx in (-150, 0, 150):
        d.line((cx + dx * 0.35, 640, cx + dx, 860), fill=(232, 205, 216), width=14)
    d.polygon(body, outline=DARK, width=outline)
    return img


def main():
    project = sys.argv[1]
    icon = draw_icon()

    ico_path = os.path.join(project, "Build", "Windows", "Application.ico")
    os.makedirs(os.path.dirname(ico_path), exist_ok=True)
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon.resize((256, 256), Image.LANCZOS).save(ico_path, sizes=sizes)

    # Splash: pink card, icon on the left, the name on the right. BMP has no alpha.
    w, h = 640, 320
    splash = Image.new("RGB", (w, h), PINK)
    sd = ImageDraw.Draw(splash)
    sd.rectangle((0, 0, w - 1, h - 1), outline=ROSE, width=8)
    small = icon.resize((220, 220), Image.LANCZOS)
    splash.paste(small, (40, (h - 220) // 2), small)
    font_path = "C:/Windows/Fonts/segoeuib.ttf"
    font = ImageFont.truetype(font_path, 76) if os.path.exists(font_path) else ImageFont.load_default()
    sd.text((290, h // 2), "DressUp", font=font, fill=DARK, anchor="lm")
    splash_path = os.path.join(project, "Content", "Splash", "Splash.bmp")
    os.makedirs(os.path.dirname(splash_path), exist_ok=True)
    splash.save(splash_path)

    preview = os.path.join(project, "Saved", "AppIconPreview.png")
    icon.resize((256, 256), Image.LANCZOS).save(preview)
    print(ico_path, splash_path, preview)


if __name__ == "__main__":
    main()
