import os
import json

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