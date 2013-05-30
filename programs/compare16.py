import json

reorderedQueriesFn = "data/000050_0.48chunk.k15.reordered_queries"
reorderedQueriesFo = open(reorderedQueriesFn)

ITEMS_IN_TOP = 16

for pos in range(10,20):
    origPosCount = 0
    n = 0
    top = [0]*ITEMS_IN_TOP

    for line in reorderedQueriesFo:
        lineDict = json.loads(line)
        if (len(lineDict['reordered_shown_items']) >= pos\
                and lineDict['reordered_shown_items'] != lineDict['shown_items']):
            item = lineDict['reordered_shown_items'][pos-1]
    
            n += 1
            origPosCount += lineDict['shown_items'].index(item)+1
            for i in range(ITEMS_IN_TOP):
                if lineDict['shown_items'].index(item) <= i:
                    top[i] += 1
    
    print "===== " + str(pos) + " ====="
    print "Number of reranked queries with >= " + str(pos) + " items: " + str(n)
    print "Average original position of "+str(pos)+"th reranked item: " + str(float(origPosCount)/n)
    for i in range(ITEMS_IN_TOP):
        print "Number of times item " + str(pos) + " was in the top " + str(i+1) +": " + str(top[i])
    print

    reorderedQueriesFo.seek(0)

