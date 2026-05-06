from PIL import Image, ImageDraw, ImageFont
import math
import os

FONTS = "/Users/alex/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/a906de0f-9e79-4845-89a1-22f0fa09c134/b45cd427-3184-429d-914b-07d7fe34f2f7/skills/canvas-design/canvas-fonts"

def font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONTS, name), size)
    except:
        return ImageFont.load_default()

# Canvas at 2x for retina sharpness → 750 × 1624 then we'll save at right size
SCALE = 2
W, H = 375 * SCALE, 812 * SCALE
img = Image.new("RGB", (W, H), "#F2F6FB")
draw = ImageDraw.Draw(img)

# ── helpers ─────────────────────────────────────────────────────────────────

def rr(draw, xy, radius, fill=None, outline=None, width=1):
    """Draw a rounded rectangle."""
    x0, y0, x1, y1 = xy
    r = radius
    draw.rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill, outline=outline, width=width)

def centered_text(draw, cx, cy, text, font, fill):
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((cx - tw // 2, cy - th // 2), text, font=font, fill=fill)

def arc_ring(draw, cx, cy, r, start, end, color, width):
    """Draw an arc segment."""
    box = [cx - r, cy - r, cx + r, cy + r]
    draw.arc(box, start=start, end=end, fill=color, width=width)

# ── status bar ───────────────────────────────────────────────────────────────
draw.rectangle([0, 0, W, 88], fill="#FFFFFF")
f_status = font("InstrumentSans-Regular.ttf", 24)
draw.text((40, 30), "9:41", font=font("InstrumentSans-Bold.ttf", 26), fill="#1A1A2E")
# battery / signal glyphs (simple)
for i in range(3):
    x = W - 60 - i * 20
    h_bar = 20 + i * 8
    draw.rounded_rectangle([x, 52 - h_bar, x + 12, 52], radius=3, fill="#1A1A2E")
rr(draw, [W - 30, 34, W - 12, 52], 3, outline="#1A1A2E", width=2)
draw.rectangle([W - 26, 38, W - 18, 48], fill="#1A1A2E")

# ── header gradient card ──────────────────────────────────────────────────────
GRAD_TOP, GRAD_BOT = 88, 420
for y in range(GRAD_TOP, GRAD_BOT):
    t = (y - GRAD_TOP) / (GRAD_BOT - GRAD_TOP)
    r = int(0x0D + t * (0x0A - 0x0D))
    g = int(0x9B + t * (0x7C - 0x9B))
    b = int(0xD9 + t * (0xC0 - 0xD9))
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# greeting
draw.text((48, 110), "Guten Morgen,", font=font("BricolageGrotesque-Regular.ttf", 36), fill="#E0F7F4")
draw.text((48, 148), "Alex", font=font("BricolageGrotesque-Bold.ttf", 52), fill="#FFFFFF")

# ── health score circle ───────────────────────────────────────────────────────
CX, CY, R = W - 120, 200, 80
RING_W = 14

# background ring
arc_ring(draw, CX, CY, R, 0, 360, "#1A7A6A", RING_W)
# progress ring (82 %) — start from -90 (top), sweep 82 % of 360
end_angle = -90 + int(360 * 0.82)
arc_ring(draw, CX, CY, R, -90, end_angle, "#FFFFFF", RING_W)

centered_text(draw, CX, CY - 14, "82", font("Outfit-Bold.ttf", 52), "#FFFFFF")
centered_text(draw, CX, CY + 30, "/ 100", font("InstrumentSans-Regular.ttf", 22), "#C0EDE8")
centered_text(draw, CX, CY + 58, "VitalScore", font("InstrumentSans-Regular.ttf", 20), "#A0DDD8")

# ── metric cards row ──────────────────────────────────────────────────────────
CARD_Y = 310
CARD_H = 160
CARD_W = 156
GAP = 18
cards = [
    ("♥", "72", "bpm", "Herzfrequenz"),
    ("👣", "8.432", "Schritte", "Heute"),
    ("🌙", "7h 20", "min", "Schlaf"),
    ("💉", "120/80", "mmHg", "Blutdruck"),
]

# 2 × 2 grid
for i, (icon, val, unit, label) in enumerate(cards):
    col = i % 2
    row = i // 2
    x0 = 24 + col * (CARD_W + GAP)
    y0 = CARD_Y + row * (CARD_H + GAP)
    x1, y1 = x0 + CARD_W * 2, y0 + CARD_H

    # shadow layer
    rr(draw, [x0 + 4, y0 + 6, x1 + 4, y1 + 6], 24, fill="#C8D8E8")
    # card
    rr(draw, [x0, y0, x1, y1], 24, fill="#FFFFFF")

    # accent dot
    draw.ellipse([x0 + 22, y0 + 22, x0 + 46, y0 + 46], fill="#E8F7F5")
    centered_text(draw, x0 + 34, y0 + 34, icon, font("NothingYouCouldDo-Regular.ttf", 24), "#0D9BD9")

    draw.text((x0 + 22, y0 + 60), val, font=font("Outfit-Bold.ttf", 44), fill="#1A1A2E")
    draw.text((x0 + 22, y0 + 108), unit, font=font("InstrumentSans-Regular.ttf", 22), fill="#7A9AAA")
    draw.text((x0 + 22, y0 + 132), label, font=font("InstrumentSans-Regular.ttf", 20), fill="#AABBC8")

# ── appointment reminder card ─────────────────────────────────────────────────
REM_Y = CARD_Y + 2 * (CARD_H + GAP) + 20
REM_H = 120

for y in range(REM_Y, REM_Y + REM_H):
    t = (y - REM_Y) / REM_H
    r = int(0xFF * (1 - t) + 0xFF * t)
    g = int(0x6B * (1 - t) + 0x55 * t)
    b = int(0x35 * (1 - t) + 0x25 * t)
    draw.line([(24, y), (W - 24, y)], fill=(r, g, b))

# clip with rounded rect mask
mask = Image.new("L", (W, H), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.rounded_rectangle([24, REM_Y, W - 24, REM_Y + REM_H], radius=24, fill=255)

# Draw gradient on separate layer and paste
grad_layer = Image.new("RGB", (W, H), "#FFFFFF")
grad_draw = ImageDraw.Draw(grad_layer)
for y in range(REM_Y, REM_Y + REM_H):
    t = (y - REM_Y) / REM_H
    r = int(0xFF * (1 - t) + 0xE8 * t)
    g_c = int(0x7A * (1 - t) + 0x50 * t)
    b_c = int(0x45 * (1 - t) + 0x30 * t)
    grad_draw.line([(24, y), (W - 24, y)], fill=(r, g_c, b_c))

img.paste(grad_layer, (0, 0), mask)

# Bell icon circle
draw.ellipse([44, REM_Y + 28, 44 + 64, REM_Y + 92], fill="rgba(255,255,255,0.25)" if False else "#FFFFFF30")
centered_text(draw, 76, REM_Y + 60, "🔔", font("NothingYouCouldDo-Regular.ttf", 30), "#FFFFFF")
draw.text((76 + 46, REM_Y + 22), "Nächster Vorsorge-Termin", font=font("InstrumentSans-Regular.ttf", 20), fill="#FFE0D0")
draw.text((76 + 46, REM_Y + 46), "Zahnarzt", font=font("BricolageGrotesque-Bold.ttf", 34), fill="#FFFFFF")
draw.text((76 + 46, REM_Y + 82), "12. Mai 2026", font=font("InstrumentSans-Regular.ttf", 22), fill="#FFD0C0")

# ── appointments section ──────────────────────────────────────────────────────
SEC_Y = REM_Y + REM_H + 36
draw.text((48, SEC_Y), "Meine Vorsorge-Termine", font=font("BricolageGrotesque-Bold.ttf", 30), fill="#1A1A2E")

appts = [
    ("🏥", "Hausarzt Check-up", "28. Mai 2026", "#E8F5FF", "#0D7AC8"),
    ("👁️", "Augenarzt", "3. Jun 2026", "#F0F0FF", "#5050C8"),
    ("🩸", "Blutuntersuchung", "10. Jun 2026", "#FFF0F5", "#C82860"),
]

for j, (icon, name, date, bg, accent) in enumerate(appts):
    ay = SEC_Y + 48 + j * 100
    rr(draw, [24, ay, W - 24, ay + 82], 20, fill=bg)
    # icon circle
    draw.ellipse([44, ay + 12, 44 + 58, ay + 70], fill=accent + "22" if len(accent) == 7 else accent)
    centered_text(draw, 73, ay + 41, icon, font("NothingYouCouldDo-Regular.ttf", 28), accent)
    draw.text((120, ay + 14), name, font=font("BricolageGrotesque-Bold.ttf", 28), fill="#1A1A2E")
    draw.text((120, ay + 46), date, font=font("InstrumentSans-Regular.ttf", 22), fill="#7A9AAA")
    # chevron
    cx, cy = W - 52, ay + 41
    draw.line([(cx - 8, cy - 14), (cx + 8, cy), (cx - 8, cy + 14)], fill="#AABBC8", width=3)

# ── bottom nav ────────────────────────────────────────────────────────────────
NAV_Y = H - 110
draw.rectangle([0, NAV_Y, W, H], fill="#FFFFFF")
draw.line([(0, NAV_Y), (W, NAV_Y)], fill="#E8EEF4", width=2)

nav_items = [("🏠", "Home"), ("📅", "Termine"), ("📊", "Daten"), ("👤", "Profil")]
NW = W // len(nav_items)
for k, (icon, label) in enumerate(nav_items):
    nx = k * NW + NW // 2
    active = k == 0
    col = "#0D9BD9" if active else "#AABBC8"
    centered_text(draw, nx, NAV_Y + 34, icon, font("NothingYouCouldDo-Regular.ttf", 34), col)
    centered_text(draw, nx, NAV_Y + 72, label, font("InstrumentSans-Regular.ttf" if not active else "InstrumentSans-Bold.ttf", 20), col)
    if active:
        draw.ellipse([nx - 4, NAV_Y + 8, nx + 4, NAV_Y + 16], fill="#0D9BD9")

# ── home indicator ────────────────────────────────────────────────────────────
draw.rounded_rectangle([W // 2 - 60, H - 18, W // 2 + 60, H - 8], radius=5, fill="#C0CBD6")

# ── phone frame ───────────────────────────────────────────────────────────────

# Downscale to 375 × 812 for final output
out = img.resize((375, 812), Image.LANCZOS)
out.save("/Users/alex/Desktop/VitalCheck-Mockup.png", dpi=(144, 144))
print("Saved to /Users/alex/Desktop/VitalCheck-Mockup.png")
