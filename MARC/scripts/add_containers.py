from vandura.config import marc_dir, shared_dir

import csv
from lxml import etree
import os
from os.path import join
import re

def add_containers(marc_dir, shared_dir):
	ead_dir = join(marc_dir, "converted_eads_working")
	beal_locations_csv = join(shared_dir, "CSVs", "locations.csv")

	beal_container_dict = make_beal_container_dict(beal_locations_csv)

	no_containers = []
	for filename in os.listdir(ead_dir):
		print "Adding containers to {}".format(filename)
		tree = etree.parse(join(ead_dir, filename))
		archdesc = tree.xpath("//archdesc")[0]
		collectionid = filename.replace(".xml","").strip()
		unitid = tree.xpath("//unitid")[0].text.strip()
		rewrite = False
		if collectionid in beal_container_dict:
			rewrite = True
			for container_type in beal_container_dict[collectionid]:
				for container in beal_container_dict[collectionid][container_type]:
					container_element = etree.Element("container")
					container_element.attrib["label"] = container_type
					container_element.text = str(container)
					archdesc.append(container_element)
		else:
			no_containers.append(unitid)
			
		if rewrite:
			with open(join(ead_dir, filename), 'w') as f:
				f.write(etree.tostring(tree, encoding="utf-8", xml_declaration=True, pretty_print=True))

	make_no_containers_csv(marc_dir, no_containers)

def make_no_containers_csv(marc_dir, no_containers):
	no_container_file = join(marc_dir, "CSVs", "no_containers.csv")

	with open(no_container_file,'wb') as csvfile:
		writer = csv.writer(csvfile)
		for unitid in no_containers:
			writer.writerow([unitid])

def make_beal_container_dict(beal_locations_csv):
	beal_container_dict = {}

	with open(beal_locations_csv,'rb') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			collectionids = re.findall(r"[\d\.]+",row["collection_id"])
			if collectionids:
				collectionid = collectionids[0]
				if collectionid not in beal_container_dict:
					beal_container_dict[collectionid] = {}
				container_type = row["loc_type"]
				if container_type not in beal_container_dict[collectionid]:
					beal_container_dict[collectionid][container_type] = []
				begin_box = row["begin_box"]
				end_box = row["end_box"]
				if begin_box:
					try:
						begin_box = int(begin_box)
						suffix = False
					except:
						digits = re.findall(r"\d+",begin_box)
						digit = digits[0]
						suffix = begin_box.replace(digit, "")
						begin_box = int(digit)
					if end_box:
						try:
							end_box = int(end_box)
							suffix = False
						except:
							digits = re.findall(r"\d+", end_box)
							if digits:
								digit = digits[0]
								suffix = end_box.replace(digit, "")
								end_box = int(digit)
					else:
						end_box = begin_box
					if not str(end_box).isdigit():
						end_box = begin_box
					containers = range(begin_box, end_box+1)
					containers = [str(container) for container in containers]
					if suffix:
						containers = ["{0}{1}".format(container, suffix) for container in containers]

					beal_container_dict[collectionid][container_type].extend(containers)

	return beal_container_dict

if __name__ == "__main__":
	add_containers(marc_dir, shared_dir)
