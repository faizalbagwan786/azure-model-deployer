import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

assets_dir = r"D:\Faizal\Learning\Reddit\azure-model-deployer\assets"
os.makedirs(assets_dir, exist_ok=True)

# -------------------------------------------------------------------------
# 1. AUTHENTIC PROJECT COVER (2560x1440 downscaled to 1280x720)
# -------------------------------------------------------------------------
W, H = 2560, 1440
canvas = Image.new("RGB", (W, H), color=(10, 14, 23)) # Slate-navy dark mode
draw = ImageDraw.Draw(canvas)

# Subtle background grid & top gradient
for y in range(H):
    ratio = y / H
    r = int(10 * (1 - ratio) + 15 * ratio)
    g = int(14 * (1 - ratio) + 20 * ratio)
    b = int(23 * (1 - ratio) + 35 * ratio)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Ambient Top-Left Azure Light
spot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
s_draw = ImageDraw.Draw(spot)
s_draw.ellipse([(-200, -200), (900, 700)], fill=(0, 120, 212, 35))
s_draw.ellipse([(W - 700, -200), (W + 200, 600)], fill=(99, 102, 241, 30))
spot = spot.filter(ImageFilter.GaussianBlur(160))
canvas.paste(spot, (0, 0), spot)
draw = ImageDraw.Draw(canvas)

# Fonts
f_brand = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
f_h1 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 80)
f_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 34)
f_card_header = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 28)
f_code_bold = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 26)
f_code = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 24)
f_tree = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 23)
f_ui_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
f_ui_body = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 23)

# Top Bar
draw.text((120, 85), "AZURE CONTAINER APPS  •  FASTAPI  •  OPEN-SOURCE LLM GATEWAY", font=f_brand, fill=(0, 150, 255))

# Title & Subtitle
draw.text((120, 130), "Private Azure AI Gateway", font=f_h1, fill=(248, 250, 252))
draw.text((120, 235), "Self-host DeepSeek-R1, Qwen 2.5 & Vision as a drop-in OpenAI API replacement with Scale-to-Zero.", font=f_sub, fill=(148, 163, 184))

# ----------------- LEFT PANE: Actual Project Code & File Tree -----------------
lx = 120
ly = 320
lw = 1100
lh = 980

# Drop Shadow
sh_left = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh_left).rounded_rectangle([(lx+10, ly+16), (lx+lw+10, ly+lh+16)], radius=24, fill=(0,0,0,160))
canvas.paste(sh_left.filter(ImageFilter.GaussianBlur(30)), (0, 0), sh_left.filter(ImageFilter.GaussianBlur(30)))
draw = ImageDraw.Draw(canvas)

# Left Card Body
draw.rounded_rectangle([(lx, ly), (lx + lw, ly + lh)], radius=20, fill=(13, 17, 26), outline=(36, 46, 66), width=2)
# Window Title Bar
draw.rounded_rectangle([(lx, ly), (lx + lw, ly + 68)], radius=20, fill=(20, 26, 40))
draw.rectangle([(lx, ly + 35), (lx + lw, ly + 68)], fill=(20, 26, 40))
# Traffic Dots
draw.ellipse([(lx + 30, ly + 25), (lx + 48, ly + 43)], fill=(239, 68, 68))
draw.ellipse([(lx + 60, ly + 25), (lx + 78, ly + 43)], fill=(245, 158, 11))
draw.ellipse([(lx + 90, ly + 25), (lx + 108, ly + 43)], fill=(16, 185, 129))
draw.text((lx + 150, ly + 20), "WORKSPACE: azure-model-deployer/ (Project Repository)", font=f_card_header, fill=(148, 163, 184))

# Section 1: File Tree (The Real Files)
draw.text((lx + 35, ly + 95), "PROJECT STRUCTURE", font=f_ui_badge, fill=(56, 189, 248))
file_tree = [
    ("📁 config/models/", (125, 211, 252)),
    ("   ├── 📄 deepseek-r1-1.5b.json     (Reasoning Model)", (203, 213, 225)),
    ("   ├── 📄 qwen2.5-coder-1.5b.json   (Code Generation)", (203, 213, 225)),
    ("   ├── 📄 llama-3.2-1b.json         (Lightweight Edge LLM)", (203, 213, 225)),
    ("   └── 📄 smolvlm-2.2b.json         (Multimodal Vision & OCR)", (203, 213, 225)),
    ("📁 docker/", (125, 211, 252)),
    ("   ├── 🐳 base_hf_server.Dockerfile (Lightweight CPU + Healthcheck)", (203, 213, 225)),
    ("   └── 🐳 gpu_hf_server.Dockerfile  (NVIDIA CUDA 12.1 Acceleration)", (167, 139, 250)),
    ("📁 src/", (125, 211, 252)),
    ("   ├── 🐍 app.py                    (FastAPI Drop-in OpenAI /v1 Engine)", (52, 211, 153)),
    ("   └── 🐍 deploy_model.py           (Azure Container Apps Orchestrator)", (52, 211, 153)),
    ("📁 examples/ (openai_sdk_demo.py, streaming_chat.py, vision_chat.py)", (148, 163, 184))
]

ty = ly + 135
for line, col in file_tree:
    draw.text((lx + 35, ty), line, font=f_tree, fill=col)
    ty += 34

# Divider
draw.line([(lx + 30, ty + 10), (lx + lw - 30, ty + 10)], fill=(36, 46, 66), width=1)

# Section 2: Real Python OpenAI Client Code
draw.text((lx + 35, ty + 25), "DROP-IN OPENAI CLIENT REPLACEMENT", font=f_ui_badge, fill=(52, 211, 153))

code_lines = [
    ("# 1. Connect official OpenAI SDK to your private Azure URL", (100, 116, 139)),
    ("from openai import OpenAI", (248, 250, 252)),
    ("client = OpenAI(", (248, 250, 252)),
    ("    base_url='https://ai-gateway.eastus2.azurecontainerapps.io/v1',", (56, 189, 248)),
    ("    api_key='sk-private-azure-key'", (251, 191, 36)),
    (")", (248, 250, 252)),
    ("stream = client.chat.completions.create(", (248, 250, 252)),
    ("    model='deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B',", (167, 139, 250)),
    ("    messages=[{'role': 'user', 'content': 'Audit this contract'}],", (203, 213, 225)),
    ("    stream=True  # Full ChatGPT-style typewriter output", (52, 211, 153)),
    (")", (248, 250, 252))
]

cy = ty + 65
for line, col in code_lines:
    draw.text((lx + 35, cy), line, font=f_code, fill=col)
    cy += 33


# ----------------- RIGHT PANE: Real API Routes & Cloud Dashboard -----------------
rx = 1340
ry = 320
rw = 1100
rh = 980

# Drop Shadow
sh_right = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(sh_right).rounded_rectangle([(rx+10, ry+16), (rx+rw+10, ry+rh+16)], radius=24, fill=(0,0,0,160))
canvas.paste(sh_right.filter(ImageFilter.GaussianBlur(30)), (0, 0), sh_right.filter(ImageFilter.GaussianBlur(30)))
draw = ImageDraw.Draw(canvas)

# Right Card Body
draw.rounded_rectangle([(rx, ry), (rx + rw, ry + rh)], radius=20, fill=(13, 17, 26), outline=(36, 46, 66), width=2)
# Window Title Bar
draw.rounded_rectangle([(rx, ry), (rx + rw, ry + 68)], radius=20, fill=(20, 26, 40))
draw.rectangle([(rx, ry + 35), (rx + rw, ry + 68)], fill=(20, 26, 40))
draw.ellipse([(rx + 30, ry + 25), (rx + 48, ry + 43)], fill=(75, 85, 99))
draw.ellipse([(rx + 60, ry + 25), (rx + 78, ry + 43)], fill=(55, 65, 81))
draw.ellipse([(rx + 90, ry + 25), (rx + 108, ry + 43)], fill=(55, 65, 81))
draw.text((rx + 150, ry + 20), "LIVE ARCHITECTURE & OPENAI ROUTE TABLE", font=f_card_header, fill=(148, 163, 184))

# Route Table Cards
routes = [
    ("POST", "/v1/chat/completions", "Full OpenAI Chat Completion with real-time SSE streaming", (16, 185, 129)),
    ("GET", "/v1/models", "OpenAI Model Registry returning active model metadata", (59, 130, 246)),
    ("POST", "/v1/embeddings", "Vector Embeddings endpoint (BGE Small 384-dim for RAG)", (139, 92, 246)),
    ("GET", "/chat", "Built-in Web Playground UI (Test models in browser directly)", (245, 158, 11)),
    ("GET", "/health", "Docker & Azure Container Apps health probe (200 OK)", (52, 211, 153))
]

r_start_y = ry + 95
for method, path, desc, m_color in routes:
    draw.rounded_rectangle([(rx + 35, r_start_y), (rx + rw - 35, r_start_y + 88)], radius=12, fill=(18, 24, 38), outline=(41, 53, 76), width=1)
    
    # Method badge
    draw.rounded_rectangle([(rx + 50, r_start_y + 16), (rx + 150, r_start_y + 50)], radius=6, fill=m_color)
    draw.text((rx + 65, r_start_y + 20), method, font=f_ui_badge, fill=(255, 255, 255))
    
    # Path & Desc
    draw.text((rx + 170, r_start_y + 16), path, font=f_code_bold, fill=(248, 250, 252))
    draw.text((rx + 170, r_start_y + 50), desc, font=f_ui_body, fill=(148, 163, 184))
    
    r_start_y += 105

# Scale-to-Zero Banner
draw.rounded_rectangle([(rx + 35, r_start_y + 10), (rx + rw - 35, r_start_y + 145)], radius=14, fill=(15, 30, 25), outline=(16, 185, 129), width=2)
draw.text((rx + 60, r_start_y + 28), "💸 AZURE CONTAINER APPS: SCALE-TO-ZERO ACTIVE", font=f_ui_badge, fill=(52, 211, 153))
draw.text((rx + 60, r_start_y + 65), "min_replicas: 0  |  idle_timeout: 300s (5 mins)", font=f_tree, fill=(241, 245, 249))
draw.text((rx + 60, r_start_y + 100), "When requests stop, cloud cost drops to exactly $0.00. No 24/7 GPU bills.", font=f_ui_body, fill=(148, 163, 184))

# Security & Compliance Tile
draw.rounded_rectangle([(rx + 35, r_start_y + 170), (rx + rw - 35, r_start_y + 260)], radius=14, fill=(20, 26, 42), outline=(59, 130, 246), width=1)
draw.text((rx + 60, r_start_y + 188), "🔒 ZERO-TRUST PRIVACY & 100% GDPR COMPLIANT", font=f_ui_badge, fill=(56, 189, 248))
draw.text((rx + 60, r_start_y + 220), "Zero customer data ever leaves your own Azure cloud subscription.", font=f_ui_body, fill=(148, 163, 184))

# Downsample cover to 1280x720 using LANCZOS
final_cover = canvas.resize((1280, 720), Image.Resampling.LANCZOS)
dest_cover = os.path.join(assets_dir, "cover.png")
final_cover.save(dest_cover, "PNG", quality=95)
print("✅ Project Cover saved to:", dest_cover)


# -------------------------------------------------------------------------
# 2. AUTHENTIC PROJECT THUMBNAIL (1200x1200 downscaled to 600x600)
# -------------------------------------------------------------------------
TW, TH = 1200, 1200
t_canvas = Image.new("RGB", (TW, TH), color=(10, 14, 23))
t_draw = ImageDraw.Draw(t_canvas)

# Gradient
for y in range(TH):
    ratio = y / TH
    r = int(10 * (1 - ratio) + 16 * ratio)
    g = int(14 * (1 - ratio) + 24 * ratio)
    b = int(23 * (1 - ratio) + 42 * ratio)
    t_draw.line([(0, y), (TW, y)], fill=(r, g, b))

# Outer Card Frame
t_draw.rounded_rectangle([(40, 40), (TW - 40, TH - 40)], radius=32, fill=(13, 17, 26), outline=(36, 46, 66), width=3)

# Fonts
tf_kicker = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
tf_title1 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 66)
tf_title2 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 66)
tf_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 32)
tf_bullet = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 25)
tf_badge = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 24)

# Top Kicker
t_draw.text((TW // 2, 105), "AZURE CONTAINER APPS BOILERPLATE", font=tf_kicker, fill=(0, 150, 255), anchor="mm")

# Title
t_draw.text((TW // 2, 185), "PRIVATE AZURE", font=tf_title1, fill=(248, 250, 252), anchor="mm")
t_draw.text((TW // 2, 260), "AI GATEWAY", font=tf_title2, fill=(0, 150, 255), anchor="mm")
t_draw.text((TW // 2, 335), "Drop-in OpenAI API (/v1) for Self-Hosted LLMs", font=tf_sub, fill=(148, 163, 184), anchor="mm")

# Central Feature Checklist Box
t_draw.rounded_rectangle([(80, 395), (TW - 80, 890)], radius=20, fill=(18, 24, 38), outline=(41, 53, 76), width=2)

bullets = [
    ("✓ Drop-in OpenAI API (/v1/chat/completions)", (52, 211, 153)),
    ("✓ Real-Time Token Streaming (SSE Typewriter)", (52, 211, 153)),
    ("✓ Scale-to-Zero ($0.00 Idle Cloud Bill)", (251, 191, 36)),
    ("✓ DeepSeek-R1, Qwen 2.5 Coder & Llama 3.2", (56, 189, 248)),
    ("✓ SmolVLM Multimodal Vision & OCR Support", (203, 213, 225)),
    ("✓ BGE Small Vector Embeddings for RAG", (167, 139, 250)),
    ("✓ Dual Dockerfiles (CPU & CUDA 12.1 GPU)", (203, 213, 225)),
    ("✓ Built-in Web Chat Playground (/chat)", (52, 211, 153)),
    ("✓ 1-Command CLI Deployment to Azure ACA", (0, 150, 255))
]

by = 430
for text, col in bullets:
    t_draw.text((120, by), text, font=tf_bullet, fill=col)
    by += 48

# Bottom Guarantee Ribbon
t_draw.rounded_rectangle([(180, 940), (TW - 180, 1030)], radius=16, fill=(16, 185, 129), outline=None)
t_draw.text((TW // 2, 985), "FULL PRODUCTION SOURCE CODE INCLUDED", font=tf_badge, fill=(255, 255, 255), anchor="mm")

t_draw.text((TW // 2, 1080), "Python 3.10+ • FastAPI • PyTorch • Docker • Azure", font=ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 22), fill=(100, 116, 139), anchor="mm")

# Downsample thumbnail to 600x600 using LANCZOS
final_thumb = t_canvas.resize((600, 600), Image.Resampling.LANCZOS)
dest_thumb = os.path.join(assets_dir, "thumbnail.png")
final_thumb.save(dest_thumb, "PNG", quality=95)
print("✅ Project Thumbnail saved to:", dest_thumb)

