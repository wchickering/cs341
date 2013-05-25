import json
import sys

import numpy as np

if (len(sys.argv) != 3):
    print >> sys.stderr, "Example: cat shared_multiReRank_json/k3.start.json | python "+sys.argv[0]+" exp_clicks 0.01 > shared_multiReRank_json/exp_clicks.json"
    exit(0)

line = sys.stdin.readline()
params = json.loads(line)

for i in np.arange(0,1+float(sys.argv[2]),float(sys.argv[2])):
    params[sys.argv[1]] = i
    print json.dumps(params)

