import os
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = "1755058049502207131"
POST_ID = "576072813965804678"

def main():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/blogger'])
    service = build('blogger', 'v3', credentials=creds)
    post = service.posts().get(blogId=BLOG_ID, postId=POST_ID).execute()
    content = post.get('content', '')
    
    # 6kNvUnBRv-M is the ACTUAL latest video at the top of the array
    LATEST_VIDEO = "6kNvUnBRv-M"
    
    new_content = re.sub(
        r'<img src="https://img\.youtube\.com/vi/[^/]+/hqdefault\.jpg"',
        f'<img src="https://img.youtube.com/vi/{LATEST_VIDEO}/hqdefault.jpg"',
        content,
        count=1
    )
    
    new_content = re.sub(
        r'<div class="youtube-cover" style="display:none;">[^<]+</div>',
        f'<div class="youtube-cover" style="display:none;">{LATEST_VIDEO}</div>',
        new_content,
        count=1
    )
    
    if new_content != content:
        body = {
            'title': post.get('title'),
            'content': new_content,
            'labels': post.get('labels', [])
        }
        service.posts().update(blogId=BLOG_ID, postId=POST_ID, body=body).execute()
        print("Thumbnail updated successfully to " + LATEST_VIDEO)
    else:
        print("No changes needed or regex failed.")

if __name__ == '__main__':
    main()
