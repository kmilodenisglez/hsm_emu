#!/usr/bin/env python3
import os
import sys
import json


if sys.version_info.major < 3:
	sys.stderr.write('Sorry, Python 3.x required by this example.\n')
	sys.exit(1)


"""
This functionalitys are temporaries
"""
filename = 'storage'
dir_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def getData():
	with open('{}/data/{}.json'.format(dir_path, filename)) as infile:
		return json.load(infile)


def saveChangeData(storage):
	with open('{}/data/{}.json'.format(dir_path, filename), mode='w') as infile:
		return json.dump(storage, infile, indent=0)


if __name__ == '__main__':
	storage = getData()
	print(storage['masterpubkey'])