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

directories = []

for file in os.listdir(root):
    d = os.path.join(root, file)
    if os.path.isdir(d):
        directories.append(d)

json_dir_path = directories[0]
xml_detection_dir_path = directories[1]
xml_structure_dir_path = directories[2]

json_file = args.output


# define lists and var
structure_id_list = []
pmc_id_list = []
pdf_page_index_list = []
json_list = []
xml_detection_bboxes = []
xml_structure_bboxes = []
files_list_dict = []  # list containing for each key 1 dict with the 3 files associated to a table
width_list = []
height_list = []
page_bbox_list = []
annotation = []  # list containing annotation category in COCO format
list_images = []
list_bboxes = []  # list of all bboxes in all cells in all files
extend_xml_detection_bboxes = []
extend_xml_structure_bboxes = []
list_image_id = []

images_dict = {}

count_detection = 0  # iterate over page bboxes
count_structure = 0  # iterate over table bboxes
image_id = 0


# define functions
def get_xml_bboxes(xml_type):
    """Take xml_type detection or structure as arg, return xml bboxes for page (detection) or table (structure)."""
    if (xml_type=="detection"):
        xml_fichier = open(os.path.join(xml_detection_dir_path, files_list_dict[i]['detection']))
        tree = ET.parse(xml_fichier)
        root = tree.getroot()
        element = root.find('object')
        for subelement in element.findall("bndbox"):
            xml_xmin = float(subelement.find("xmin").text)
            xml_ymin = float(subelement.find("ymin").text)
            xml_detection_bbox = [xml_xmin, xml_ymin]
            xml_detection_bboxes.append(xml_detection_bbox)
        return xml_detection_bboxes
        xml_fichier.close()

    elif (xml_type=="structure"):
        xml_fichier = open(os.path.join(xml_structure_dir_path, files_list_dict[i]['structure']))
        tree = ET.parse(xml_fichier)
        root = tree.getroot()
        element = root.find('object')
        for subelement in element.findall("bndbox"):
            xml_xmin = float(subelement.find("xmin").text)
            xml_ymin = float(subelement.find("ymin").text)
            xml_structure_bbox = [xml_xmin, xml_ymin]
            xml_structure_bboxes.append(xml_structure_bbox)
        return xml_structure_bboxes
        xml_fichier.close()


def get_images_dict(content):
    """get table image dimension, id and path"""
    for j in content:
        page_bbox_list.append(j["pdf_full_page_bbox"])
        width_list.append(page_bbox_list[0][2]-page_bbox_list[0][0])
        height_list.append(page_bbox_list[0][3]-page_bbox_list[0][1])
    images_dict = {
        "id": i,
        "width": width_list[i],
        "height": height_list[i],
        "file_name": structure_id_list[i] + ".jpg",
    }
    return images_dict


def get_bboxes(content):
    """get cells bboxes"""
    for i in content:
        cellules = (i['cells'])
        for i in cellules:
            list_bboxes.append(i['pdf_bbox'])
    return list_bboxes


"""process files"""
# create dict for each table with its associated xml and json files
for file in os.listdir(os.path.abspath(json_dir_path)):
    json_fichier = open(os.path.join(json_dir_path, file))
    content = json.load(json_fichier)

    # get list of files ids
    for i in content:
        structure_id_list.append(i['structure_id'])
        pmc_id_list.append(i['pmc_id'])
        pdf_page_index_list.append(i['pdf_page_index'])
        json_list.append(os.path.basename(file))

    json_fichier.close()

for  i in range(0,len(structure_id_list)):
    files_list_dict.append(
        {
            "json": json_list[i],
            "structure": structure_id_list[i] + ".xml",
            "detection": pmc_id_list[i] + "_" + str(pdf_page_index_list[i]) + ".xml"
        }
    )
unique_json_files = list(dict.fromkeys(json_list))  # same json list without duplicates


"""use functions"""
for i in range(0, len(files_list_dict)):
    json_fichier = open(os.path.join(json_dir_path, json_list[i]))
    content = json.load(json_fichier)
    list_images.append(get_images_dict(content))
    list_detection = get_xml_bboxes("detection")
    list_structure = get_xml_bboxes("structure")
    json_fichier.close()


for i in range(0, len(unique_json_files)):
    json_fichier = open(os.path.join(json_dir_path, unique_json_files[i]))
    content = json.load(json_fichier)
    liste_bboxes = get_bboxes(content)
    json_fichier.close()


# get margin for all
for i in range(0, len(unique_json_files)):
    json_fichier = open(os.path.join(json_dir_path, unique_json_files[i]))
    content = json.load(json_fichier)
    for i in content:
        cellules = (i['cells'])
        for i in cellules:
            extend_xml_detection_bboxes.append(xml_detection_bboxes[count_detection])
        count_detection+=1
    json_fichier.close()


for i in range(0, len(unique_json_files)):
    json_fichier = open(os.path.join(json_dir_path, unique_json_files[i]))
    content = json.load(json_fichier)
    for i in content:
        cellules = (i['cells'])
        for i in cellules:
            extend_xml_structure_bboxes.append(xml_structure_bboxes[count_structure])
        count_structure+=1
    json_fichier.close()


# get list of ids for unique json files
for i in range(0, len(unique_json_files)):
    json_fichier = open(os.path.join(json_dir_path, unique_json_files[i]))
    content = json.load(json_fichier)
    for i in content:
        cellules = (i['cells'])
        for i in cellules:
            list_image_id.append(image_id)
        image_id+=1
    json_fichier.close()


# get annotations for each cell of each tables with its bbox, id, image id, etc
for i in range(0,len(liste_bboxes)):
    xmin = (liste_bboxes[i][0]*1.26) - (extend_xml_detection_bboxes[i][0] - extend_xml_structure_bboxes[i][0])
    ymin = (liste_bboxes[i][1]*1.26) - (extend_xml_detection_bboxes[i][1] - extend_xml_structure_bboxes[i][1])
    xmax = (liste_bboxes[i][2]*1.26) - (extend_xml_detection_bboxes[i][0] - extend_xml_structure_bboxes[i][0]) + 7
    ymax = (liste_bboxes[i][3]*1.26) - (extend_xml_detection_bboxes[i][1] - extend_xml_structure_bboxes[i][1])
    width = xmax - xmin
    height = ymax - ymin
    area = width*height
    poly = [xmin, ymin, xmax, ymin, xmax, ymax, xmin, ymax]

    annotate = {
        "id": i,
        "image_id": list_image_id[i],
        "category_id": 1,
        "segmentation": list([poly]),
        "area": area,
        "bbox": [xmin, ymin, width, height],
        "iscrowd": 0,
    }
    annotation.append(annotate)


# only one category to detect : cells
categories = [
    {
        "id": 1,
        "name": "cell",
        "supercategory": "none",
    }
]


res_file = {
    "images": list_images,
    "annotations": annotation,
    "categories": categories
}


with open(json_file, "w") as f:
        json_str = json.dumps(res_file)
        f.write(json_str)