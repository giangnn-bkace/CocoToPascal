from itertools import starmap
from lxml import objectify, etree

from pycocotools.coco import COCO
import argparse
import os
import json

def root(folder, filename, width, height):
	E = objectify.ElementMaker(annotate=False)
	return E.annotation(
		E.folder(folder),
		E.filename(filename),
		E.source(
			E.database('MS COCO 2017'),
			E.annotation('MS COCO 2017'),
			E.image('Flickr'),
		),
		E.size(
			E.width(width),
			E.height(height),
			E.depth(3),
		),
		E.segmented(0)
		)

def instance_to_xml(ann, cat_dict):
	E = objectify.ElementMaker(annotate=False)
	xmin, ymin, width, height = ann['bbox']
	return E.object(
		E.name(cat_dict[ann['category_id']]),
		E.bndbox(
			E.xmin(xmin),
			E.ymin(ymin),
			E.xmax(xmin+width),
			E.ymax(ymin+height),
		),
	)

def create_annotations(dataDir, dataType, dst):
	annFile = '{}/instances_{}.json'.format(dataDir, dataType)
	coco = COCO(annFile)
	
	cats = coco.loadCats(coco.getCatIds())
	cat_dict = {}
	#animal_ids = range(16, 26)
	for cat in cats:
		cat_dict[cat['id']] = cat['supercategory']
		#if cat['id'] in animal_ids:
		#	cat_dict[cat['id']] = 'animal'
		#else:
		#	cat_dict[cat['id']] = cat['name']
	with open("supercat.txt", 'w') as f:
		json.dump(cat_dict, f)
	f.close()
	imgIds = coco.getImgIds()
	for imgId in imgIds:
		img = coco.loadImgs(imgId)[0]
		file_name = img['file_name']
		annotation = root(dataDir+'/images', file_name, img['width'], img['height'])

		annIds = coco.getAnnIds(img['id'])
		anns = coco.loadAnns(annIds)
		ok = False
		for ann in anns:
		#	if cat_dict[ann['category_id']] == 'animal':
			annotation.append(instance_to_xml(ann, cat_dict))
		#		ok = True
		#if ok:
		etree.ElementTree(annotation).write(dst+'/{}.xml'.format(os.path.splitext(file_name)[0]), pretty_print=True)		
		print (file_name)
	
if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-d", "--dataDir", required=True, help="path to annotation file")
	ap.add_argument("-t", "--dataType", required=True, help="data type")
	ap.add_argument("-s", "--destination", required=True, help="path to save xml files")
	args = vars(ap.parse_args())

	create_annotations(args["dataDir"], args["dataType"], args["destination"])
