import sys
import json
import math

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.lines import Line2D

fig = plt.figure()
ax = fig.gca()

limit = 6

markers = []
for m in Line2D.markers:
    try:
        if len(m) == 1 and m != ' ':
            markers.append(m)
    except TypeError:
        pass

i = 0
j = 0
for line in open(sys.argv[1]):
    data = []
    q = json.loads(line)
    if q['lengthInPages'] < limit:
        for k in q['CTRs'].keys():
            data.append([int(k),float(q['CTRs'][k])])

        data.sort(cmp=lambda a,b: a[0] - b[0])
        ax.plot([x[0] for x in data],[y[1] for y in data],label=str(int(q['lengthInPages']))+' page', marker=markers[i])
        j+=1
    if j >= limit:
        break
    i += 1

leg = ax.legend()
leg.draggable()
ax.set_xlabel('position')
ax.set_ylabel('CTR')
plt.show()
