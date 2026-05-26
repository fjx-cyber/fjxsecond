from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image, ImageDraw
import requests
from io import BytesIO

app = FastAPI()

class Box(BaseModel):
    x: int
    y: int
    w: int
    h: int
    comment: str

class RequestData(BaseModel):
    image_url: str
    boxes: list[Box]

@app.post("/annotate")
def annotate(data: RequestData):
    response = requests.get(data.image_url)
    img = Image.open(BytesIO(response.content))

    draw = ImageDraw.Draw(img)

    for box in data.boxes:
        x, y, w, h = box.x, box.y, box.w, box.h

        draw.ellipse(
            (x, y, x+w, y+h),
            outline="red",
            width=4
        )

        draw.text(
            (x, y-25),
            box.comment,
            fill="red"
        )

    output = "graded.png"
    img.save(output)

    return {"result": output}