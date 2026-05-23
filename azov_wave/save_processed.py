import os
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/blogger'])
service = build('blogger', 'v3', credentials=creds)
post = service.posts().get(blogId='1755058049502207131', postId='9130895322221594772').execute()
content = post.get('content', '')
match = re.search(r'const\s+videoIds\s*=\s*\[(.*?)\]', content, re.DOTALL)
ids = re.findall(r'"([^"]+)"', match.group(1))
with open('processed.json', 'w', encoding='utf-8') as f:
    json.dump(list(dict.fromkeys(ids)), f, indent=2)
