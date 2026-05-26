from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image, ImageDraw
from io import BytesIO
import requests
import os
import time

app = FastAPI()

# 创建 static 文件夹
os.makedirs("static", exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


# 框的数据结构
class Box(BaseModel):
    x: int
    y: int
    w: int
    h: int
    comment: str


# 请求数据结构
class RequestData(BaseModel):
    image_url: str
    boxes: list[Box]


@app.get("/")
def root():
    return {"message": "API is running"}


@app.post("/annotate")
def annotate(data: RequestData):
    try:
        # 下载图片
        response = requests.get(data.image_url)
        response.raise_for_status()

        # 打开图片
        img = Image.open(BytesIO(response.content)).convert("RGB")

        draw = ImageDraw.Draw(img)

        # 画圈 + 标注
        for box in data.boxes:
            x, y, w, h = box.x, box.y, box.w, box.h

            # 红圈
            draw.ellipse(
                [(x, y), (x + w, y + h)],
                outline="red",
                width=5
            )

            # 标注文字
            draw.text(
                (x, y - 30),
                box.comment,
                fill="red"
            )

        # 防缓存：每次生成唯一文件名
        filename = f"graded_{int(time.time())}.png"
        filepath = f"static/{filename}"

        img.save(filepath)

        return {
            "image": f"https://web-production-bcf26.up.railway.app/static/{filename}"
        }

    except Exception as e:
        return {
            "error": str(e)
        }
