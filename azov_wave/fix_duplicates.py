import os
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = "1755058049502207131"
POST_ID = "9130895322221594772"
PROCESSED_FILE = "processed.json"

def get_blogger_service():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/blogger'])
    return build('blogger', 'v3', credentials=creds)

def main():
    service = get_blogger_service()
    post = service.posts().get(blogId=BLOG_ID, postId=POST_ID).execute()
    content = post.get('content', '')
    
    # 1. Знайти всі video_id в JS масиві
    match = re.search(r'const\s+videoIds\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not match:
        print("Не знайдено масив videoIds")
        return
        
    array_content = match.group(1)
    
    # Витягнути всі ID
    ids = re.findall(r'"([^"]+)"', array_content)
    
    # Очистити від дублікатів (залишити перший знайдений)
    unique_ids = []
    seen = set()
    for vid in ids:
        if vid not in seen:
            unique_ids.append(vid)
            seen.add(vid)
            
    # Перезібрати масив
    new_array_content = ", ".join(f'"{vid}"' for vid in unique_ids)
    
    # Замінити в контенті
    new_content = content[:match.start(1)] + "\n      \t\t" + new_array_content + "\n    " + content[match.end(1):]
    
    # Оновити пост
    body = {
        'title': post.get('title'),
        'content': new_content,
        'labels': post.get('labels', [])
    }
    
    service.posts().update(blogId=BLOG_ID, postId=POST_ID, body=body).execute()
    print("✅ Пост успішно очищено від дублікатів!")
    
    # Створити processed.json з унікальними ID
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique_ids, f, indent=2)
    print("✅ Файл processed.json оновлено.")

if __name__ == '__main__':
    main()
