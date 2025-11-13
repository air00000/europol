# api/pdf_generator.py — генерация PDF через Figma API
import requests
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from io import BytesIO
import logging

from config import FIGMA_TOKEN, FILE_KEY, FRAME_NAME, BUTTON_NAME, PAGE_NAME, SCALE, CONV

log = logging.getLogger("EUROPOL_PDF")

app = FastAPI()

class LinkRequest(BaseModel):
    url: str

def get_figma_json():
    r = requests.get(f"https://api.figma.com/v1/files/{FILE_KEY}",
                     headers={"X-FIGMA-TOKEN": FIGMA_TOKEN}, timeout=30)
    r.raise_for_status()
    return r.json()

def export_node(node_id: str) -> bytes:
    r = requests.get(f"https://api.figma.com/v1/images/{FILE_KEY}",
                     params={"ids": node_id, "format": "png", "scale": SCALE},
                     headers={"X-FIGMA-TOKEN": FIGMA_TOKEN}, timeout=30)
    r.raise_for_status()
    img_url = r.json()["images"][node_id]
    return requests.get(img_url, timeout=30).content

def find_node(data, name):
    log.info(f"ищу → {name}")
    def search(nodes):
        for node in nodes:
            if node.get("name") == name:
                log.info(f"найден → {name}")
                return node
            if "children" in node:
                found = search(node["children"])
                if found: return found
    page = next(p for p in data["document"]["children"] if p["name"] == PAGE_NAME)
    result = search(page["children"])
    if not result:
        log.error(f"НЕ НАЙДЕН → {name}")
    return result

@app.post("/generate_pdf")
async def generate_pdf(req: LinkRequest):
    if not req.url.startswith("http"):
        raise HTTPException(400, "Ссылка должна начинаться с http/https")

    log.info(f"Генерация PDF с ссылкой: {req.url}")

    data = get_figma_json()

    frame = find_node(data, FRAME_NAME)
    if not frame:
        raise HTTPException(500, "Фрейм europol1 не найден")

    button = find_node(data, BUTTON_NAME)
    if not button:
        raise HTTPException(500, "Кнопка europol1botton не найдена")

    # Экспорт фона
    bg_bytes = export_node(frame["id"])

    # Размеры
    box = frame["absoluteBoundingBox"]
    pw = box["width"] * SCALE * CONV
    ph = box["height"] * SCALE * CONV

    # Создаём PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(pw, ph))
    c.drawImage(ImageReader(BytesIO(bg_bytes)), 0, 0, width=pw, height=ph)

    # Кликабельная кнопка
    b = button["absoluteBoundingBox"]
    x1 = (b["x"] - box["x"]) * SCALE * CONV
    y1 = ph - (b["y"] - box["y"] + b["height"]) * SCALE * CONV
    x2 = x1 + b["width"] * SCALE * CONV
    y2 = y1 + b["height"] * SCALE * CONV
    c.linkURL(req.url, (x1, y1, x2, y2), relative=1)

    c.showPage()
    c.save()
    buffer.seek(0)

    log.info("PDF готов с кликабельной кнопкой")
    return Response(content=buffer.read(), media_type="application/pdf")