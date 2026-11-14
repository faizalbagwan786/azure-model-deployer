import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

assets_dir = r"D:\Faizal\Learning\Reddit\azure-model-deployer\assets"
os.makedirs(assets_dir, exist_ok=True)

def draw_rounded_card(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def draw_badge(draw, x, y, text, font, bg_color, text_color, padding=(14, 6)):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    box = (x, y, x + w + padding[0]*2, y + h + padding[1]*2)
    draw.rounded_rectangle(box, radius=h//2 + 4, fill=bg_color)
    draw.text((x + padding[0], y + padding[1]), text, font=font, fill=text_color)
    return box[2]

# ----------------- 1. COVER IMAGE (1280x720) -----------------
img = Image.new("RGB", (1280, 720), color=(11, 15, 25))
draw = ImageDraw.Draw(img)

# Vertical Gradient
for i in range(720):
    ratio = i / 720.0
    r = int(11 * (1 - ratio) + 15 * ratio)
    g = int(15 * (1 - ratio) + 23 * ratio)
    b = int(25 * (1 - ratio) + 45 * ratio)
    draw.line([(0, i), (1280, i)], fill=(r, g, b))

# Ambient glow overlay
glow = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
glow_draw = ImageDraw.Draw(glow)
glow_draw.ellipse([(-100, -100), (500, 500)], fill=(0, 150, 255, 35))
glow_draw.ellipse([(800, 300), (1400, 900)], fill=(139, 92, 246, 40))
glow = glow.filter(ImageFilter.GaussianBlur(80))
img.paste(glow, (0, 0), glow)
draw = ImageDraw.Draw(img)

# Fonts
font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 52)
font_subtitle = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22)
font_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
font_code = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
font_tag = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)

# Top Bar / Badges
bx = 70
bx = draw_badge(draw, bx, 65, "FASTAPI", font_badge, (15, 118, 110), (204, 251, 241)) + 12
bx = draw_badge(draw, bx, 65, "AZURE CONTAINER APPS", font_badge, (30, 64, 175), (219, 234, 254)) + 12
bx = draw_badge(draw, bx, 65, "DOCKER (CPU & GPU)", font_badge, (29, 78, 216), (224, 231, 255)) + 12
bx = draw_badge(draw, bx, 65, "SMOLVLM & LLMS", font_badge, (180, 83, 9), (254, 243, 199))

# Main Title & Subtitle
draw.text((70, 130), "Azure AI Model Deployer", font=font_title, fill=(255, 255, 255))
draw.text((70, 200), "Production AI Serving Engine & Cloud Deployment Boilerplate", font=font_subtitle, fill=(148, 163, 184))

# Left Feature Cards
features = [
    ("Zero-Trust Security", "Header-based X-API-Key auth with rate limiting (10/min)"),
    ("Universal Model Serving", "SmolVLM 500M / 2.2B Vision Models + GPT-2 text gen"),
    ("1-Command Cloud Deploy", "Orchestrates Docker build, ACR push, and ACA live URLs"),
    ("Enterprise Grade", "Pytest suite, CORS middleware, Docker health checks, CI/CD")
]

fy = 265
for title, desc in features:
    draw_rounded_card(draw, (70, fy, 660, fy + 72), radius=10, fill=(17, 24, 39), outline=(55, 65, 81), width=1)
    draw.ellipse([(90, fy + 26), (108, fy + 44)], fill=(16, 185, 129))
    draw.text((120, fy + 14), title, font=ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 18), fill=(241, 245, 249))
    draw.text((120, fy + 40), desc, font=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13), fill=(148, 163, 184))
    fy += 85

# Right Terminal Card (Code Preview)
card_x = 700
card_y = 265
card_w = 510
card_h = 370

draw_rounded_card(draw, (card_x, card_y, card_x + card_w, card_y + card_h), radius=12, fill=(15, 23, 42), outline=(59, 130, 246), width=2)

# Terminal Header
draw_rounded_card(draw, (card_x, card_y, card_x + card_w, card_y + 42), radius=12, fill=(30, 41, 59))
draw.rectangle([(card_x, card_y + 30), (card_x + card_w, card_y + 42)], fill=(30, 41, 59))
draw.ellipse([(card_x + 18, card_y + 16), (card_x + 28, card_y + 26)], fill=(239, 68, 68))
draw.ellipse([(card_x + 36, card_y + 16), (card_x + 46, card_y + 26)], fill=(245, 158, 11))
draw.ellipse([(card_x + 54, card_y + 16), (card_x + 64, card_y + 26)], fill=(16, 185, 129))
draw.text((card_x + 180, card_y + 12), "terminal -- inference preview", font=font_tag, fill=(148, 163, 184))

# Terminal Code Lines
code_lines = [
    ("$ curl -X POST https://ai-app.azurecontainerapps.io/predict \\", (248, 250, 252)),
    ("    -H 'X-API-Key: sk-prod-model-key' \\", (248, 250, 252)),
    ("    -H 'Content-Type: application/json' \\", (248, 250, 252)),
    ("    -d '{\"text\": \"Describe image\", \"image_url\": \"...\"}'", (248, 250, 252)),
    ("", (0, 0, 0)),
    ("HTTP/1.1 200 OK", (52, 211, 153)),
    ("{", (148, 163, 184)),
    ('  "status": "healthy",', (56, 189, 248)),
    ('  "model": "SmolVLM2-2.2B-Instruct",', (251, 191, 36)),
    ('  "result": "A high-resolution golden retriever...",', (241, 245, 249)),
    ('  "device": "CUDA 12.1",', (167, 139, 250)),
    ('  "latency_ms": 78', (52, 211, 153)),
    ("}", (148, 163, 184))
]

cy = card_y + 55
for line, color in code_lines:
    if line:
        draw.text((card_x + 22, cy), line, font=font_code, fill=color)
    cy += 23

# Bottom Ribbon / Guarantee
draw.text((70, 645), "Includes Full Source Code, Dockerfiles, GitHub Actions CI/CD & Tests", font=ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16), fill=(56, 189, 248))

cover_path = os.path.join(assets_dir, "cover.png")
img.save(cover_path, "PNG", quality=95)
print("Cover saved to:", cover_path)

# ----------------- 2. THUMBNAIL IMAGE (600x600) -----------------
thumb = Image.new("RGB", (600, 600), color=(11, 15, 25))
draw_t = ImageDraw.Draw(thumb)

# Gradient
for i in range(600):
    ratio = i / 600.0
    r = int(11 * (1 - ratio) + 20 * ratio)
    g = int(15 * (1 - ratio) + 28 * ratio)
    b = int(25 * (1 - ratio) + 55 * ratio)
    draw_t.line([(0, i), (600, i)], fill=(r, g, b))

# Center Glow
thumb_glow = Image.new("RGBA", (600, 600), (0, 0, 0, 0))
tg_draw = ImageDraw.Draw(thumb_glow)
tg_draw.ellipse([(150, 150), (450, 450)], fill=(59, 130, 246, 50))
thumb_glow = thumb_glow.filter(ImageFilter.GaussianBlur(60))
thumb.paste(thumb_glow, (0, 0), thumb_glow)
draw_t = ImageDraw.Draw(thumb)

# Border
draw_rounded_card(draw_t, (20, 20, 580, 580), radius=20, fill=None, outline=(59, 130, 246), width=2)

# Central badge icon
draw_rounded_card(draw_t, (220, 75, 380, 225), radius=24, fill=(30, 41, 59), outline=(96, 165, 250), width=2)
# Draw rocket icon with polygons / lines
# Rocket body
draw_t.polygon([(300, 100), (330, 170), (270, 170)], fill=(255, 255, 255))
draw_t.polygon([(270, 170), (250, 195), (270, 195)], fill=(56, 189, 248))
draw_t.polygon([(330, 170), (350, 195), (330, 195)], fill=(56, 189, 248))
draw_t.polygon([(285, 195), (300, 215), (315, 195)], fill=(245, 158, 11))
draw_t.ellipse([(292, 135), (308, 151)], fill=(30, 41, 59), outline=(56, 189, 248), width=2)

# Title
font_th_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 34)
font_th_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)
font_th_pills = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 14)

draw_t.text((105, 260), "AZURE AI MODEL", font=font_th_title, fill=(255, 255, 255))
draw_t.text((215, 305), "DEPLOYER", font=font_th_title, fill=(56, 189, 248))

draw_t.text((165, 365), "FastAPI • Docker • SmolVLM", font=font_th_sub, fill=(148, 163, 184))

# Badges at bottom
draw_badge(draw_t, 85, 430, "CPU & CUDA GPU", font_th_pills, (30, 64, 175), (219, 234, 254), padding=(16, 8))
draw_badge(draw_t, 310, 430, "1-CLICK AZURE", font_th_pills, (15, 118, 110), (204, 251, 241), padding=(16, 8))

draw_badge(draw_t, 180, 495, "PRODUCTION READY", font_th_pills, (180, 83, 9), (254, 243, 199), padding=(18, 8))

thumb_path = os.path.join(assets_dir, "thumbnail.png")
thumb.save(thumb_path, "PNG", quality=95)
print("Thumbnail saved to:", thumb_path)

