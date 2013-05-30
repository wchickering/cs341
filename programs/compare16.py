import json

reorderedQueriesFn = "data/000050_0.48chunk.k15.reordered_queries"
reorderedQueriesFo = open(reorderedQueriesFn)

origPosCount = 0
n = 0

for line in reorderedQueriesFo:
    lineDict = json.loads(line)
    if (len(lineDict['reordered_shown_items']) >= 16):
        item16 = lineDict['reordered_shown_items'][15]

        print str(item16),
        print " was " + str(lineDict['shown_items'].index(item16)+1) + ". Now 16"
        n += 1
        origPosCount += lineDict['shown_items'].index(item16)+1

print "Average original position of 16th reranked item: " + str(float(origPosCount)/n)

