img_url = "https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=800&q=60"
api_key = "AIzaSyAplyfgUTOS7ODQfT-8AQq0rL8BIuJnTMo"

from google.cloud import vision
import json
import sys
import cv2

client = vision.ImageAnnotatorClient()
response = client.annotate_image({
    'image': {'source': {'image_uri': img_url}},
    'features': [{'type': vision.enums.Feature.Type.FACE_DETECTION}],
})

for face in response.face_annotations:
    print(face.joy_likelihood)
    print(face.anger_likelihood)
    print(face.fd_bounding_poly)

face = response.face_annotations[0]


from PIL import Image, ImageDraw
import requests
from io import BytesIO
import numpy

resp = requests.get(img_url)
im = Image.open(BytesIO(resp.content))

emoji = Image.open("happy.png")
ex, ey = emoji.size


def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = numpy.matrix(matrix, dtype=numpy.float)
    B = numpy.array(pb).reshape(8)

    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    return numpy.array(res).reshape(8)


d1 = (face.fd_bounding_poly.vertices[0].x, face.fd_bounding_poly.vertices[0].y)
d2 = (face.fd_bounding_poly.vertices[1].x, face.fd_bounding_poly.vertices[1].y)
d3 = (face.fd_bounding_poly.vertices[2].x, face.fd_bounding_poly.vertices[2].y)
d4 = (face.fd_bounding_poly.vertices[3].x, face.fd_bounding_poly.vertices[3].y)


coeffs = find_coeffs(
    [(0, 0), (ex, 0), (ex, ey), (0, ey)],
    [d1, d2, d4, d3])


def _affine_with_matrix(img, matrix, resample=0, fillcolor=None):
    return img.transform(img.size, Image.AFFINE, matrix, resample)


r = _affine_with_matrix(emoji, coeffs)
r.show()

# x, y = im.size

# position = (
#     face.fd_bounding_poly.vertices[0].x, face.fd_bounding_poly.vertices[0].y)

# image_with_watermark = Image.new('RGBA', (x, y), (0, 0, 0, 0))
# image_with_watermark.paste(im, (0, 0))
# image_with_watermark.paste(emjoi, position, mask=emjoi)
# image_with_watermark.show()

# draw = ImageDraw.Draw(im)
# draw.rectangle([(face.fd_bounding_poly.vertices[0].x, face.fd_bounding_poly.vertices[0].y),
#                 (face.fd_bounding_poly.vertices[2].x, face.fd_bounding_poly.vertices[2].y)])
# del draw
