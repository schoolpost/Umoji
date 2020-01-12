img_url = "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60"
# img_url = "https://avatars3.githubusercontent.com/u/10094074?s=460&v=4"
# img_url = "https://expandyourpossibilities.files.wordpress.com/2015/07/emotions-faces.jpg"
# img_url = "https://imgflip.com/s/meme/Distracted-Boyfriend.jpg"
# img_url = "https://i.cbc.ca/1.3731271.1471893597!/fileImage/httpImage/image.jpg_gen/derivatives/16x9_780/437333815.jpg"
# img_url = "https://static.independent.co.uk/s3fs-public/thumbnails/image/2019/02/26/15/friends-30-5.jpg"

from google.cloud import vision
import json
import sys
import os
import io
from PIL import Image, ImageDraw, ExifTags
import requests
from io import BytesIO
import numpy
import base64


def getDictionary():

    dic = dict()
    path = "emoji"

    for r, d, f in os.walk(path):
        for file in f:
            key = file.split(".")[0]
            dic[key] = os.path.join(r, file)

    return dic


def create_umoji(image_file, debug=True):

    client = vision.ImageAnnotatorClient()
    # response = client.annotate_image({
    #     'image': {'source': {'image_uri': img_url}},
    #     'features': [{'type': vision.enums.Feature.Type.FACE_DETECTION}],
    # })

    try:
        im = Image.open(BytesIO(image_file))
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(im._getexif().items())

        if exif[orientation] == 3:
            im = im.rotate(180, expand=True)
        elif exif[orientation] == 6:
            im = im.rotate(270, expand=True)
        elif exif[orientation] == 8:
            im = im.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        pass

    # imgByteArr = io.BytesIO()
    # im.save(imgByteArr, format="JPEG")

    response = client.annotate_image({
        'image': {'content': image_file},
        'features': [{'type': vision.enums.Feature.Type.FACE_DETECTION}],
    })

    emotions = getDictionary()

    x, y = im.size

    image_with_watermark = Image.new('RGBA', (x, y), (0, 0, 0, 0))
    image_with_watermark.paste(im, (0, 0))

    for face in response.face_annotations:

        di = dict()

        print("joy: " + str(face.joy_likelihood), "anger: " + str(face.anger_likelihood),
              "sorrow: " + str(face.sorrow_likelihood), "surprise: " + str(face.surprise_likelihood))

        di["JO"] = face.joy_likelihood
        di["AN"] = face.anger_likelihood
        di["SO"] = face.sorrow_likelihood
        di["SU"] = face.surprise_likelihood

        current = 99
        for k, v in di.items():
            if current > v:
                current = v

        validItems = []
        for k, v in di.items():
            if v != current:
                validItems.append(k)

        emoji_file = emotions["NULL"]

        if len(validItems) != 0:

            for k, v in emotions.items():
                tup = k.split("-")
                if len(tup) == len(validItems):
                    if len(set(validItems + tup)) == len(tup):
                        emoji_file = v

        emoji = Image.open(emoji_file)
        ex, ey = emoji.size

        d1 = (face.fd_bounding_poly.vertices[0].x,
              face.fd_bounding_poly.vertices[0].y)
        d2 = (face.fd_bounding_poly.vertices[1].x,
              face.fd_bounding_poly.vertices[1].y)
        d3 = (face.fd_bounding_poly.vertices[2].x,
              face.fd_bounding_poly.vertices[2].y)
        d4 = (face.fd_bounding_poly.vertices[3].x,
              face.fd_bounding_poly.vertices[3].y)

        size = ((d2[0]-d1[0]), (d3[1]-d2[1]))

        if size[0] > 160 or size[1] > 160:
            factor = 1.5
            si = ((d2[0]-d1[0]) * factor, (d3[1]-d2[1]) * factor)
            emoji = emoji.resize((int(si[0]), int(si[1])))
        else:
            factor = 2
            si = ((d2[0]-d1[0]) * factor, (d3[1]-d2[1]) * factor)
            emoji.thumbnail(si, Image.ANTIALIAS)
        xRatio = im.size[0] / emoji.size[0]
        yRatio = im.size[1] / emoji.size[1]
        xCenter = int(d1[0] + ((d2[0] - d1[0]) / 2))
        yCenter = int(d2[1] + ((d3[1] - d2[1]) / 2))
        position = (int(d1[0] - ((emoji.size[0] / xRatio)/2)),
                    int(d1[1] - ((emoji.size[1] / yRatio)/2)))
        xDiff = int(xCenter - (position[0] + ((emoji.size[0]) / 2)))
        yDiff = int(yCenter - (position[1] + ((emoji.size[1]) / 2)))

        # if x > y:
        position = (position[0] + xDiff, position[1] + yDiff)
        # elif y > x:
        #     position = (position[0] + yDiff, position[1] + xDiff)

        image_with_watermark.paste(emoji, position, mask=emoji)

        # draw = ImageDraw.Draw(image_with_watermark)
        # draw.rectangle([(face.fd_bounding_poly.vertices[0].x, face.fd_bounding_poly.vertices[0].y),
        #                 (face.fd_bounding_poly.vertices[2].x, face.fd_bounding_poly.vertices[2].y)])
        # del draw

    if debug:
        image_with_watermark.show()
    return image_with_watermark


# resp = requests.get(img_url)
# um = create_umoji(resp.content)
