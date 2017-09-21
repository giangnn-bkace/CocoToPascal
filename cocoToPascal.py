from itertools import starmap
from lxml import objectify, etree

from pycocotools.coco import COCO
import numpy as np
import argparse

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

def instance_to_xml(ann):
	E = objectify.ElementMaker(annotate=False)
	xmin, ymin, width, height = ann['bbox']
	return E.object(
		E.name(ann['category_id']),
		E.bndbox(
			E.xmin(round(xmin)),
			E.ymin(round(ymin)),
			E.xmax(round(xmin+width)),
			E.ymax(round(ymin+height)),
		),
	)

def create_annotations(dataDir, dataType, dst):
	annFile = '{}/annotations/instances_{}.json'.format(dataDir, dataType)
	coco = COCO(annFile)
	imgIds = coco.getImgIds()
	
	for imgId in imgIds:
		img = coco.loadImgs(imgId)[0]
		file_name = img['file_name']
		annotation = root(dataDir+'/images', file_name, img['width'], img['height'])

		annIds = coco.getAnnIds(img['id'])
		anns = coco.loadAnns(annIds)

		for ann in anns:
			annotation.append(instance_to_xml(ann))
			#etree.ElementTree(annotation).write(dst / '{}.xml'.format(file_name))
		etree.ElementTree(annotation).write(dst+'/{}.xml'.format(file_name), pretty_print=True)		
		print (file_name)

if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-d", "--dataDir", required=True, help="path to annotation file")
	ap.add_argument("-t", "--dataType", required=True, help="data type")
	ap.add_argument("-s", "--destination", required=True, help="path to save xml files")
	args = vars(ap.parse_args())

	create_annotations(args["dataDir"], args["dataType"], args["destination"])
