# Imports the Google Cloud client library
from google.cloud import vision
import math
from PIL import Image, ImageDraw, ImageFont
import sys

def detect_document(path):
    """Detects document features in an image."""
    from google.cloud import vision
    res = []
    pos = (0, 0)
    mean_size = 0
    i = 0
    count = 1

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                res.append("")
                for word in paragraph.words:
                    word_text = "".join([symbol.text for symbol in word.symbols])
                    for symbole in word.symbols :
                        if (symbole.text in "0123456789=") :
                            count += 1
                            box = symbole.bounding_box.vertices
                            max_y = max(box[1].y, box[2].y, box[3].y, box[0].y)
                            min_y = min(box[1].y, box[2].y, box[3].y, box[0].y)
                            mean_size += (max_y - min_y)
                            if (symbole.text == "=") :
                                max_x = max(box[1].x, box[2].x, box[3].x, box[0].x)
                                pos = (max_x + 100, min_y + 100)
                    res[i] += word_text + " "
                    mean_size /= count
                i+=1

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    return (res, pos, mean_size)


def draw(result : float, path, pos, size) :
    print(size / 15)
    with Image.open(path) as im :
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("ARIAL.TTF", size)
        draw.text(pos, text=str(result), fill=128, font=font)
        im.show()

def compute_calcule(calcule) :
    final = 0
    for line in calcule :
        res = line.replace("=", "").replace("÷", "/").replace("²", "**2").replace(" ", "").replace("×", "*")
        res = res.replace("log", "math.log").replace("ln", "math.log")
        res = res.replace("exp", "math.exp")
        try :
            a = eval(res)
            if (res == str(a)) :
                continue
            print(line.replace("=", "").replace(" ", "") + " = " + str(a))
            final = a
        except :
            continue
    return final
        

path = "tested_images/worked/square4.jpg"
(calcule, pos, mean_size) = detect_document(path)
res = compute_calcule(calcule)
draw(res, path, pos, mean_size)