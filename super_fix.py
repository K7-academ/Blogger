import os
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = "1755058049502207131"
POST_ID = "9130895322221594772"

PERFECT_IDS = [
    "J3-QR12eVqo", "EcZn4tIKlps", "LK_mKm3yPQs", "CTlHQDw6biU", "UjA0PBlCQsw", "kqUyrz6BFPE",
    "jxY0_L86pF8", "42IszXaO83Y", "NQ7FFUbjqjU", "nczj7pqBXTA", "oUwi4z1M9e0", "jsYowPRa1MA", 
    "Zefl9l1tXrI", "L4ArPJBvd8Q", "rftOZ6oBb2A", "3VZCnPIdi_U", "dq50VHr5GeI", "JVu7Yq5cw1Y", 
    "U9agO8sljqE", "4kqQP4z9vqA", "YJRfNES0260", "14bhhBwDuP8", "wlt__3V2faY", "7e_SjKU8nMw"
]

def main():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/blogger'])
    service = build('blogger', 'v3', credentials=creds)
    post = service.posts().get(blogId=BLOG_ID, postId=POST_ID).execute()
    content = post.get('content', '')
    
    match = re.search(r'const\s+videoIds\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if match:
        new_array = ", ".join(f'"{vid}"' for vid in PERFECT_IDS)
        new_content = content[:match.start(1)] + "\n      \t\t" + new_array + "\n    " + content[match.end(1):]
        
        body = {
            'title': post.get('title'),
            'content': new_content,
            'labels': post.get('labels', [])
        }
        service.posts().update(blogId=BLOG_ID, postId=POST_ID, body=body).execute()
        
    with open('azov_wave/processed.json', 'w', encoding='utf-8') as f:
        json.dump(PERFECT_IDS, f, indent=2)

if __name__ == '__main__':
    main()
