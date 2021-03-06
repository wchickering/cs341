import json
import sys

import numpy as np

if (len(sys.argv) != 5):
    print >> sys.stderr, "Example: cat shared_multiReRank_json/k3.start.json | python "+sys.argv[0]+" exp_clicks 0 1 0.01 > shared_multiReRank_json/exp_clicks.json"
    exit(0)

line = sys.stdin.readline()
params = json.loads(line)

paramType, paramName = sys.argv[1].split('_',1)

if (paramType == 'exp'):
    params["coeff_"+paramName] = 1.0

for i in np.arange(float(sys.argv[2]),float(sys.argv[3])+float(sys.argv[4]),float(sys.argv[4])):
    params[sys.argv[1]] = i
    print json.dumps(params)

