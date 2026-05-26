from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import os

app = FastAPI()

# 创建 static 文件夹（如果不存在）
os.makedirs("static", exist_ok=True)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")


class Box(BaseModel):
    x: int
    y: int
    w: int
    h: int
    comment: str


class RequestData(BaseModel):
    image_url: str
    boxes: list[Box]


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/annotate")
def annotate(data: RequestData):
    # 下载图片
    response = requests.get(data.image_url)
    img = Image.open(BytesIO(response.content))

    draw = ImageDraw.Draw(img)

    # 画圈 + 标注
    for box in data.boxes:
        x, y, w, h = box.x, box.y, box.w, box.h

        draw.ellipse(
            (x, y, x + w, y + h),
            outline="red",
            width=5
        )

        draw.text(
            (x, y - 25),
            box.comment,
            fill="red"
        )

    # 保存到 static
    output = "static/graded.png"
    img.save(output)

    # 返回图片链接
    return {
        "image": "https://web-production-bcf26.up.railway.app/static/graded.png"
    }
