import os
import json
import time
import re
import feedparser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = "1755058049502207131"
POST_ID = "9130895322221594772"
CHANNELS_FILE = "channels.txt"
PROCESSED_FILE = "processed.json"

def get_blogger_service():
    """Ініціалізація клієнта Blogger API за допомогою OAuth2 Token"""
    token_json = os.environ.get('TOKEN_JSON')
    
    if not token_json:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/blogger'])
        else:
            raise Exception("No OAuth2 token found. Set TOKEN_JSON env var or place token.json in directory.")
    else:
        creds_dict = json.loads(token_json)
        creds = Credentials.from_authorized_user_info(creds_dict, ['https://www.googleapis.com/auth/blogger'])
    
    return build('blogger', 'v3', credentials=creds)

def main():
    try:
        service = get_blogger_service()
    except Exception as e:
        print(f"Помилка авторизації: {e}")
        return
    
    # Отримання існуючого поста
    try:
        post = service.posts().get(blogId=BLOG_ID, postId=POST_ID).execute()
        current_content = post.get('content', '')
        print(f"Знайдено пост: {post.get('title')}")
    except Exception as e:
        print(f"Не вдалося отримати пост: {e}")
        return

    # Завантаження історії оброблених відео
    processed = []
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
            try:
                processed = json.load(f)
            except json.JSONDecodeError:
                pass
                
    if not os.path.exists(CHANNELS_FILE):
        print(f"Файл {CHANNELS_FILE} не знайдено.")
        return
        
    with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
        channels = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
    new_processed = set(processed)
    has_new_videos = False
    
    for channel_id in channels:
        # Підтримка і @handle, і звичайних ID для RSS
        if channel_id.startswith('@'):
            # Для @handle нам потрібен справжній ID каналу. У вашому випадку це UCHAdxtoG5l38KyKvfEFuq_A
            # Оскільки ви працюєте тільки з одним каналом, я прописав його напряму для надійності:
            feed_url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCHAdxtoG5l38KyKvfEFuq_A"
        else:
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            
        print(f"\n--- Обробка каналу: {channel_id} ---")
        feed = feedparser.parse(feed_url)
        
        if not feed.entries:
            print(f"Немає відео або помилка доступу до каналу {channel_id}")
            continue
            
        # Обробляємо відео від найстаріших до найновіших
        entries = reversed(feed.entries)
        
        for entry in entries:
            video_id = entry.yt_videoid
            if video_id in new_processed or video_id in current_content:
                new_processed.add(video_id)
                continue
                
            title = entry.title
            print(f"Знайдено нове відео: {title} ({video_id})")
            has_new_videos = True
            
            # Ін'єкція video_id в масив JS
            current_content = re.sub(
                r'(const\s+videoIds\s*=\s*\[\s*)', 
                r'\g<1>"' + video_id + '", ', 
                current_content,
                count=1
            )
            
            # Оновлення прихованої обкладинки
            current_content = re.sub(
                r'(<img[^>]*?src="https://img\.youtube\.com/vi/)[^/]+(/maxresdefault\.jpg"[^>]*?Preview[^>]*?>)',
                r'\g<1>' + video_id + r'\g<2>',
                current_content,
                count=1
            )
            
            new_processed.add(video_id)
            
    if has_new_videos:
        body = {
            'title': post.get('title'),
            'content': current_content,
            'labels': post.get('labels', [])
        }
        
        try:
            service.posts().update(blogId=BLOG_ID, postId=POST_ID, body=body).execute()
            print("Оновлення успішне!")
            
            with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
                json.dump(list(new_processed), f, indent=2)
                
        except Exception as e:
            print(f"Помилка під час оновлення поста: {e}")
    else:
        print("Не знайдено нових відео для оновлення.")

if __name__ == '__main__':
    main()
