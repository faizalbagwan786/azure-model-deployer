import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

assets_dir = r"D:\Faizal\Learning\Reddit\azure-model-deployer\assets"
os.makedirs(assets_dir, exist_ok=True)

# -------------------------------------------------------------
# 1. PREMIUM COVER (2560x1440 downscaled to 1280x720)
# -------------------------------------------------------------
W, H = 2560, 1440
canvas = Image.new("RGB", (W, H), color=(8, 10, 15))
draw = ImageDraw.Draw(canvas)

# Subtle ambient light
spotlight = Image.new("RGBA", (W, H), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(spotlight)
s_draw.ellipse([(W//2 - 950, -400), (W//2 + 950, 750)], fill=(0, 120, 212, 40))
s_draw.ellipse([(W//2 - 450, -200), (W//2 + 450, 480)], fill=(139, 92, 246, 30))
spotlight = spotlight.filter(ImageFilter.GaussianBlur(150))
canvas.paste(spotlight, (0, 0), spotlight)
draw = ImageDraw.Draw(canvas)

# Micro Dot Grid
dot_color = (25, 30, 42)
for gx in range(60, W - 60, 48):
    for gy in range(60, H - 60, 48):
        draw.ellipse([(gx, gy), (gx + 3, gy + 3)], fill=dot_color)

# Fonts
f_kicker = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
f_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 90)
f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 36)
f_card_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 32)
f_card_body = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 24)
f_code_bold = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 27)
f_code = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 25)
f_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)

# Top Kicker
draw.text((140, 105), "AZURE CLOUD INFRASTRUCTURE  /  SCALE-TO-ZERO BOILERPLATE", font=f_kicker, fill=(0, 150, 255))

# Title & Subtitle
draw.text((140, 155), "Private Azure AI Gateway", font=f_title, fill=(248, 250, 252))
sub_text = "Drop-in OpenAI-compatible API (/v1) for DeepSeek, Qwen & Llama with Scale-to-Zero ($0 idle cost)."
draw.text((140, 275), sub_text, font=f_sub, fill=(148, 163, 184))

# Left Column: 3 Real Value Cards
left_w = 1080
card_h = 175
card_y_start = 390
card_gap = 32

cards_data = [
    (
        "Drop-In OpenAI API Compatibility",
        "Switch existing apps & LangChain by changing 1 line: base_url='https://your-azure-app/v1'. Supports streaming SSE.",
        (0, 120, 212)
    ),
    (
        "Hot Modern Models (2025/2026)",
        "Pre-configured for DeepSeek-R1 Reasoning, Qwen 2.5 Coder, Meta Llama 3.2, and SmolVLM multimodal vision.",
        (139, 92, 246)
    ),
    (
        "Scale-to-Zero Cloud Cost Optimizer",
        "Spins down to 0 replicas during idle periods so you pay $0.00 when not in use. Saves 90% on Azure cloud invoices.",
        (16, 185, 129)
    )
]

for idx, (title, desc, accent) in enumerate(cards_data):
    cy = card_y_start + idx * (card_h + card_gap)
    draw.rounded_rectangle([(140, cy), (140 + left_w, cy + card_h)], radius=16, fill=(15, 18, 26), outline=(33, 41, 57), width=2)
    draw.rounded_rectangle([(140, cy + 24), (148, cy + card_h - 24)], radius=4, fill=accent)
    draw.text((175, cy + 28), title, font=f_card_title, fill=(241, 245, 249))
    
    words = desc.split(" ")
    line1 = " ".join(words[:11])
    line2 = " ".join(words[11:])
    draw.text((175, cy + 80), line1, font=f_card_body, fill=(148, 163, 184))
    if line2:
        draw.text((175, cy + 118), line2, font=f_card_body, fill=(148, 163, 184))

# Right Column: VS Code / Terminal Code Window
term_x = 1300
term_y = 390
term_w = 1120
term_h = 750

# Shadow
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(shadow)
s_draw.rounded_rectangle([(term_x + 10, term_y + 16), (term_x + term_w + 10, term_y + term_h + 16)], radius=24, fill=(0, 0, 0, 160))
shadow = shadow.filter(ImageFilter.GaussianBlur(30))
canvas.paste(shadow, (0, 0), shadow)
draw = ImageDraw.Draw(canvas)

# Window Body
draw.rounded_rectangle([(term_x, term_y), (term_x + term_w, term_y + term_h)], radius=20, fill=(13, 16, 23), outline=(41, 51, 71), width=2)
draw.rounded_rectangle([(term_x, term_y), (term_x + term_w, term_y + 70)], radius=20, fill=(20, 24, 34))
draw.rectangle([(term_x, term_y + 40), (term_x + term_w, term_y + 70)], fill=(20, 24, 34))

draw.ellipse([(term_x + 32, term_y + 26), (term_x + 50, term_y + 44)], fill=(75, 85, 99))
draw.ellipse([(term_x + 64, term_y + 26), (term_x + 82, term_y + 44)], fill=(55, 65, 81))
draw.ellipse([(term_x + 96, term_y + 26), (term_x + 114, term_y + 44)], fill=(55, 65, 81))

draw.text((term_x + 160, term_y + 20), "openai_client.py  —  1-Line Drop-in Replacement", font=f_card_body, fill=(156, 163, 175))

# Code Snippet Lines
code_lines = [
    ("# 1. Connect standard OpenAI SDK to your private Azure URL", (100, 116, 139), False),
    ("from openai import OpenAI", (248, 250, 252), True),
    ("client = OpenAI(", (248, 250, 252), True),
    ("    base_url='https://ai-gateway.eastus2.azurecontainerapps.io/v1',", (56, 189, 248), True),
    ("    api_key='sk-private-azure-key'", (251, 191, 36), True),
    (")", (248, 250, 252), True),
    ("", (0,0,0), False),
    ("# 2. Stream completions from DeepSeek or Qwen in real-time", (100, 116, 139), False),
    ("stream = client.chat.completions.create(", (248, 250, 252), True),
    ("    model='deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B',", (167, 139, 250), False),
    ("    messages=[{'role': 'user', 'content': 'Audit this smart contract'}],", (203, 213, 225), False),
    ("    stream=True", (52, 211, 153), True),
    (")", (248, 250, 252), True),
    ("", (0,0,0), False),
    ("[*] Scale-to-Zero Status: ACTIVE (Idle cost: $0.00/mo)", (16, 185, 129), True)
]

cur_y = term_y + 105
for text, col, is_bold in code_lines:
    if text:
        fn = f_code_bold if is_bold else f_code
        draw.text((term_x + 40, cur_y), text, font=fn, fill=col)
    cur_y += 42

# Bottom Badges
bx = 140
by = 1260
badges = [
    ("OpenAI /v1 Spec", (15, 118, 110), (204, 251, 241)),
    ("Scale-to-Zero ($0 Idle)", (22, 101, 52), (220, 252, 231)),
    ("DeepSeek-R1", (180, 83, 9), (254, 243, 199)),
    ("Qwen 2.5 Coder", (67, 56, 202), (224, 231, 255)),
    ("Llama 3.2", (30, 64, 175), (219, 234, 254)),
    ("Azure Container Apps", (31, 41, 55), (209, 213, 219)),
    ("Full Pytest Suite", (30, 41, 59), (226, 232, 240))
]

for label, bg, fg in badges:
    bbox = draw.textbbox((0, 0), label, font=f_badge)
    bw = bbox[2] - bbox[0] + 36
    bh = bbox[3] - bbox[1] + 24
    draw.rounded_rectangle([(bx, by), (bx + bw, by + bh)], radius=12, fill=bg, outline=(55, 65, 81), width=1)
    draw.text((bx + 18, by + 12), label, font=f_badge, fill=fg)
    bx += bw + 20

final_cover = canvas.resize((1280, 720), Image.Resampling.LANCZOS)
cover_path = os.path.join(assets_dir, "cover.png")
final_cover.save(cover_path, "PNG", quality=95)
print("Updated Cover saved to:", cover_path)

# ----------------- 2. PREMIUM THUMBNAIL (1200x1200 downscaled to 600x600) -----------------
TW, TH = 1200, 1200
t_canvas = Image.new("RGB", (TW, TH), color=(8, 10, 15))
t_draw = ImageDraw.Draw(t_canvas)

t_glow = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
tg_draw = ImageDraw.Draw(t_glow)
tg_draw.ellipse([(200, 200), (1000, 1000)], fill=(0, 120, 212, 45))
tg_draw.ellipse([(350, 350), (850, 850)], fill=(99, 102, 241, 35))
t_glow = t_glow.filter(ImageFilter.GaussianBlur(100))
t_canvas.paste(t_glow, (0, 0), t_glow)
t_draw = ImageDraw.Draw(t_canvas)

t_draw.rounded_rectangle([(50, 50), (1150, 1150)], radius=40, fill=None, outline=(33, 41, 57), width=3)
t_draw.rounded_rectangle([(56, 56), (1144, 1144)], radius=36, fill=None, outline=(15, 23, 42), width=2)

# Central Emblem
emblem_box = [(450, 170), (750, 470)]
t_draw.rounded_rectangle(emblem_box, radius=48, fill=(17, 24, 39), outline=(0, 120, 212), width=4)

t_draw.ellipse([(570, 290), (630, 350)], fill=(0, 150, 255))
nodes = [(510, 250), (690, 250), (510, 390), (690, 390)]
for nx, ny in nodes:
    t_draw.line([(600, 320), (nx + 18, ny + 18)], fill=(51, 65, 85), width=4)
    t_draw.ellipse([(nx, ny), (nx + 36, ny + 36)], fill=(30, 41, 59), outline=(96, 165, 250), width=3)

tf_kicker = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 28)
tf_title1 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 66)
tf_title2 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 66)
tf_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 36)
tf_tag = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)

t_draw.text((600, 560), "DROP-IN OPENAI COMPATIBLE", font=tf_kicker, fill=(0, 150, 255), anchor="mm")
t_draw.text((600, 650), "PRIVATE AZURE", font=tf_title1, fill=(248, 250, 252), anchor="mm")
t_draw.text((600, 735), "AI GATEWAY", font=tf_title2, fill=(0, 150, 255), anchor="mm")

t_draw.text((600, 835), "DeepSeek • Qwen 2.5 • Llama 3.2 • Vision", font=tf_sub, fill=(148, 163, 184), anchor="mm")

t_draw.rounded_rectangle([(180, 930), (580, 1000)], radius=20, fill=(15, 23, 42), outline=(33, 41, 57), width=2)
t_draw.text((380, 965), "OPENAI /v1 SPEC", font=tf_tag, fill=(52, 211, 153), anchor="mm")

t_draw.rounded_rectangle([(620, 930), (1020, 1000)], radius=20, fill=(15, 23, 42), outline=(33, 41, 57), width=2)
t_draw.text((820, 965), "SCALE-TO-ZERO ($0)", font=tf_tag, fill=(251, 191, 36), anchor="mm")

t_draw.rounded_rectangle([(330, 1030), (870, 1090)], radius=16, fill=(30, 41, 59), outline=(51, 65, 85), width=1)
t_draw.text((600, 1060), "1-COMMAND AZURE DEPLOY", font=ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22), fill=(203, 213, 225), anchor="mm")

final_thumb = t_canvas.resize((600, 600), Image.Resampling.LANCZOS)
thumb_path = os.path.join(assets_dir, "thumbnail.png")
final_thumb.save(thumb_path, "PNG", quality=95)
print("Updated Thumbnail saved to:", thumb_path)
