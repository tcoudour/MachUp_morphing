
'''Script for testing json editing commands, not used in main script'''
import json
from collections import OrderedDict

# with open('airplane1.json', 'r+') as f :
	# data = json.load(f, object_pairs_hook=OrderedDict)
	# data['wings']['Wing_1']['sweep'] = 10
	# f.seek(0)
	# json.dump(data, f, indent=4)
	# f.truncate()
	
with open('airplane1.json', 'r+') as f :
	data = json.load(f, object_pairs_hook=OrderedDict)
	data['wings']['Wing_1']['airfoils']['af1']['properties']['CL_alpha'] = 10
	f.seek(0)
	json.dump(data, f, indent=4)
	f.truncate()