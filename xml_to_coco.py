"""
Converts PubTables xml annotations in "PubTables-1M-Image_Table_Structure_PASCAL_VOC" zip for Functional Analysis to coco format
"""

import os
import json
import xml.etree.ElementTree as ET
import argparse


# parser
parser = argparse.ArgumentParser()
parser.add_argument("--root", help="root directory path", required=True, dest="root")
parser.add_argument("--out", help="output json file", required=True, dest="output")
args = parser.parse_args()
root = args.root
json_file = args.output

count = 0
image_list = []
annotation = []
count_cells = 0

for file in os.listdir(os.path.abspath(root)):
    fichier = open(os.path.join(root, file))
    tree = ET.parse(fichier)
    root = tree.getroot()

    bboxes = []
    labels = []

    filename = root.find('path').text

    for element in root.iter('size'):
        width = int(element.find('width').text)
        height = int(element.find('height').text)

    image = {
        "id": count,
        "width":width,
        "height": height,
        "file_name": filename,
    }
    image_list.append(image)

    for element in root.iter('object'):
        ymin, xmin, ymax, xmax = None, None, None, None

        for subelement in element.findall("bndbox"):
            ymin = float(subelement.find("ymin").text)
            xmin = float(subelement.find("xmin").text)
            ymax = float(subelement.find("ymax").text)
            xmax = float(subelement.find("xmax").text)
            width = xmax - xmin
            height = ymax - ymin
            poly = [xmin, ymin, xmax, ymin, xmax, ymax, xmin, ymax]

        annotate = {
            "id": count_cells,
            "image_id": count,
            "category_id": 1,
            "segmentation": list([poly]),
            "area": (width*height),
            "bbox": [xmin, ymin, width, height],
            "iscrowd": 0,
        }
        annotation.append(annotate)
        count_cells+=1
    count+=1


categories = [
    {
        "id": 1,
        "name": "cell",
        "supercategory": "none",
    }
]

res_file = {
    "images": image_list,
    "annotations": annotation,
    "categories": categories
}


with open(json_file, "w") as f:
        json_str = json.dumps(res_file)
        f.write(json_str)