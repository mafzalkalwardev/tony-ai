from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SCREENSHOTS = ROOT / "docs" / "screenshots"


def run() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception as exc:
        print(f"Pillow unavailable, cannot generate PNG/ICO assets: {exc}")
        return 0

    icon = _icon(Image, ImageDraw, ImageFont, 1024)
    icon.save(ASSETS / "icon.png")
    icon.resize((256, 256)).save(ASSETS / "icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])

    logo = _icon(Image, ImageDraw, ImageFont, 512)
    logo.save(ASSETS / "logo.png")

    banner = Image.new("RGB", (1600, 520), "#071018")
    draw = ImageDraw.Draw(banner)
    for radius, color in [(360, "#0b2435"), (270, "#0d3f5a"), (180, "#16c8ff")]:
        x = 250 - radius // 2
        y = 260 - radius // 2
        draw.ellipse((x, y, x + radius, y + radius), outline=color, width=8)
    draw.text((520, 155), "Tony AI", fill="#e8fbff", font=_font(ImageFont, 96))
    draw.text((525, 270), "Local Voice-First Laptop Assistant for Windows", fill="#6bdcff", font=_font(ImageFont, 36))
    banner.save(ASSETS / "banner.png")

    for name, title, subtitle in [
        ("dashboard.png", "Tony AI", "Clean assistant dashboard"),
        ("voice_mode.png", "Push to Talk", "Local speech-to-text, graceful fallback"),
        ("command_test.png", "Command Simulation", "Intent, safety, status, reply"),
        ("settings_voice_setup.png", "Voice Setup", "Dependency and microphone diagnostics"),
    ]:
        image = Image.new("RGB", (1280, 720), "#08121b")
        d = ImageDraw.Draw(image)
        d.rounded_rectangle((60, 60, 1220, 660), radius=28, fill="#0e1f2d", outline="#1dc7ff", width=3)
        d.text((110, 120), title, fill="#e8fbff", font=_font(ImageFont, 72))
        d.text((115, 235), subtitle, fill="#75dfff", font=_font(ImageFont, 34))
        d.rounded_rectangle((110, 520, 1170, 590), radius=18, fill="#071018", outline="#2a5368", width=2)
        d.text((145, 538), "You said: repo status dikhao    Tony: Done, Muhammad Afzal.", fill="#d7f9ff", font=_font(ImageFont, 26))
        image.save(SCREENSHOTS / name)
    print("Generated Tony AI assets and screenshot placeholders.")
    return 0


def _icon(Image, ImageDraw, ImageFont, size: int):
    image = Image.new("RGBA", (size, size), (5, 12, 20, 255))
    draw = ImageDraw.Draw(image)
    center = size // 2
    for scale, color, width in [(0.82, "#0a2a3e", 14), (0.68, "#116b8d", 12), (0.52, "#1fd2ff", 10)]:
        radius = int(size * scale / 2)
        draw.ellipse((center - radius, center - radius, center + radius, center + radius), outline=color, width=max(2, width * size // 1024))
    font = _font(ImageFont, int(size * 0.48))
    text = "T"
    box = draw.textbbox((0, 0), text, font=font)
    draw.text((center - (box[2] - box[0]) / 2, center - (box[3] - box[1]) / 2 - size * 0.04), text, fill="#eaffff", font=font)
    return image


def _font(ImageFont, size: int):
    for name in ["arial.ttf", "segoeui.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


if __name__ == "__main__":
    raise SystemExit(run())
