import json

class CTR:
    def __init__(self):
        self.ctf = {}
        self.numClicks = 0.0

    def ingestQuery(self, query):
        for item in query.clicked_shown_items:
            click_position = query.shown_items.index(item) + 1
            try:
                self.ctf[click_position] += 1
            except KeyError:
                self.ctf[click_position] = 1
        self.numClicks += len(query.clicked_shown_items)

    def CTRByPositionDict(self):
        ctr = {}
        for k in self.ctf.keys():
            ctr[k] = self.ctf[k] / self.numClicks
        return ctr

    def CTFByPositionDict(self):
        return self.ctf

    def __str__(self):
        s = ""
        ctr = self.CTFByPositionDict()
        for k in sorted(ctr.keys()):
           s += str(k) + ": " + str(ctr[k]) + "  "
        return s

# custom JSON encoder for CTR object
# http://stackoverflow.com/questions/1458450/python-serializable-objects-json
class CTREncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, CTR):
            return super(MyEncoder, self).default(obj)
        return obj.CTRByPositionDict()

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print 'Usage: ' + sys.argv[0] + ' <queries>'
        sys.exit(1)

    import Query
    from pprint import pprint

    queriesFo = open(sys.argv[1])

    ctrs = {}
    queryLengthCount = {}

    for line in queriesFo:
        query = Query.Query(line)
        try:
            ctrs[len(query)].ingestQuery(query)
            queryLengthCount[len(query)] += 1
        except KeyError:
            ctrs[len(query)] = CTR()
            ctrs[len(query)].ingestQuery(query)
            queryLengthCount[len(query)] = 1
    
    for k in ctrs.keys():
        print '{"'+str(k)+'": '+json.dumps(ctrs[k], cls=CTREncoder)+', "queries": '+str(queryLengthCount[k])+'}'

