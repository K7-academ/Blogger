import re
import json

content = open('post_snippet_2.txt', encoding='utf-8').read()
match = re.search(r'const\s+videoIds\s*=\s*\[(.*?)\]', content, re.DOTALL)
ids = re.findall(r'"([^"]+)"', match.group(1))
json.dump(ids, open('processed_hellfxrmance.json', 'w', encoding='utf-8'), indent=2)
