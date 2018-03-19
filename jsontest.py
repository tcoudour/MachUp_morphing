import json
from collections import OrderedDict

with open('airplane1.json', 'r+') as f :
	data = json.load(f, object_pairs_hook=OrderedDict)
	data['wings']['Wing_1']['sweep'] = 10
	f.seek(0)
	json.dump(data, f, indent=4)
	f.truncate()