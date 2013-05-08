import sys
import json

total = 0

for line in sys.stdin:
    record = json.loads(line)
    for item in record['clicked_shown_items']:
        total += record['shown_items'].index(item) + 1

print total

