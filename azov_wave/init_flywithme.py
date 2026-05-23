import json
import re
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = "1755058049502207131"
POST_ID = "6052281470851197159"

creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/blogger'])
service = build('blogger', 'v3', credentials=creds)
post = service.posts().get(blogId=BLOG_ID, postId=POST_ID).execute()
content = post.get('content', '')

match = re.search(r'const\s+videoIds\s*=\s*\[(.*?)\]', content, re.DOTALL)
if match:
    ids = re.findall(r'"([^"]+)"', match.group(1))
    with open('processed_flywithme.json', 'w', encoding='utf-8') as f:
        json.dump(ids, f, indent=2)
    print(f"Saved {len(ids)} ids to processed_flywithme.json")
else:
    print("No videoIds found in post")
