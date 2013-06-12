import sys
import json
import math

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(221, projection='3d')

x = []
y = []
z = []

for line in open(sys.argv[1]):
    q = json.loads(line)
    for k in q['CTRs'].keys():
        x.append(q['lengthInPages'])
        y.append(int(k))
        z.append(float(q['CTRs'][k]))

ax.set_xlabel('query length')
ax.set_ylabel('position')
ax.set_zlabel('CTR')
ax.scatter(x,y,z)

y = []
z = []
ax = fig.add_subplot(222)
for line in open(sys.argv[1]):
    q = json.loads(line)
    for k in q['CTRs'].keys():
        y.append(int(k))
        z.append(float(q['CTRs'][k]))

ax.set_xlabel('position')
ax.set_ylabel('CTR')
ax.scatter(y,z)

x = []
z = []
ax = fig.add_subplot(223)
for line in open(sys.argv[1]):
    q = json.loads(line)
    for k in q['CTRs'].keys():
        x.append(q['lengthInPages'])
        z.append(float(q['CTRs'][k]))

ax.set_xlabel('query length')
ax.set_ylabel('CTR')
ax.scatter(x,z)

plt.show()
