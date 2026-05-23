import os
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = "1755058049502207131"
POST_ID = "9130895322221594772"

def main():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/blogger'])
    service = build('blogger', 'v3', credentials=creds)
    post = service.posts().get(blogId=BLOG_ID, postId=POST_ID).execute()
    content = post.get('content', '')
    
    # Замінюємо мініатюру на J3-QR12eVqo
    new_content = re.sub(
        r'<img src="https://img\.youtube\.com/vi/[^/]+/maxresdefault\.jpg"',
        r'<img src="https://img.youtube.com/vi/J3-QR12eVqo/maxresdefault.jpg"',
        content,
        count=1
    )
    
    if new_content != content:
        body = {
            'title': post.get('title'),
            'content': new_content,
            'labels': post.get('labels', [])
        }
        service.posts().update(blogId=BLOG_ID, postId=POST_ID, body=body).execute()
        print("Thumbnail updated successfully!")
    else:
        print("No changes needed or regex failed.")

if __name__ == '__main__':
    main()
