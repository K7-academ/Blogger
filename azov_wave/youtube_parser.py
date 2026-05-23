import os
import json
import time
import re
import feedparser
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = "1755058049502207131"

CONFIGS = [
    {
        "channel_id": "UCRLXjm61c8gqrIgpiuPK4bw",
        "post_id": "9130895322221594772",
        "processed_file": "processed_ardmixes.json"
    },
    {
        "channel_id": "UCkoaodpQjvGZ4vjotUs9Gjw",
        "post_id": "4880300034766882371",
        "processed_file": "processed_hellfxrmance.json"
    },
    {
        "channel_id": "UCU9eTpOS-sQQu4BzJ88IU8g",
        "post_id": "1888318045958197622",
        "processed_file": "processed_gvngmix.json"
    },
    {
        "channel_id": "UC9JwZiaWudOWmw2TOjWyyVg",
        "post_id": "3395509229888708702",
        "processed_file": "processed_soundeomixtape.json"
    },
    {
        "channel_id": "UC-pVYBvaCW3Puj90iEQ03Uw",
        "post_id": "576072813965804678",
        "processed_file": "processed_ghettomixtape.json"
    }
]

def get_blogger_service():
    if not os.path.exists('token.json'):
        if 'TOKEN_JSON' in os.environ:
            with open('token.json', 'w') as f:
                f.write(os.environ['TOKEN_JSON'])
        else:
            raise Exception("No OAuth2 token found. Set TOKEN_JSON env var or place token.json in directory.")
            
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/blogger'])
    return build('blogger', 'v3', credentials=creds)

def process_config(service, config):
    channel_id = config['channel_id']
    post_id = config['post_id']
    processed_file = config['processed_file']
    
    print(f"\n--- Обробка каналу: {channel_id} ---")
    
    # Завантажуємо історію
    processed_videos = set()
    if os.path.exists(processed_file):
        with open(processed_file, 'r', encoding='utf-8') as f:
            processed_videos = set(json.load(f))
            
    # Отримуємо RSS стрічку
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    
    if not feed.entries:
        print(f"Немає відео або помилка доступу до каналу {channel_id}")
        return
        
    # Сортуємо від найстарішого до найновішого, щоб зберегти хронологію
    entries = sorted(feed.entries, key=lambda x: x.published_parsed)
    
    try:
        post = service.posts().get(blogId=BLOG_ID, postId=post_id).execute()
        current_content = post.get('content', '')
        
        has_new_videos = False
        new_processed = set(processed_videos)
        
        for entry in entries:
            video_id = entry.yt_videoid
            if video_id in new_processed or video_id in current_content:
                new_processed.add(video_id)
                continue
                
            title = entry.title
            
            # Оновлюємо мініатюру посту (сховане зображення для прев'ю)
            current_content = re.sub(
                r'<img src="https://img\.youtube\.com/vi/[^/]+/(maxresdefault|hqdefault|sddefault)\.jpg"',
                f'<img src="https://img.youtube.com/vi/{video_id}/\\g<1>.jpg"',
                current_content,
                count=1
            )
            
            # Якщо є блок div з youtube-cover
            current_content = re.sub(
                r'<div class="youtube-cover" style="display:none;">[^<]+</div>',
                f'<div class="youtube-cover" style="display:none;">{video_id}</div>',
                current_content,
                count=1
            )
            
            # Додаємо video_id на початок масиву
            current_content = re.sub(
                r'(const\s+videoIds\s*=\s*\[\s*)', 
                r'\g<1>"' + video_id + '", ', 
                current_content,
                count=1
            )
            
            
            try:
                print(f"Знайдено нове відео: {title} ({video_id})")
            except UnicodeEncodeError:
                print(f"Знайдено нове відео: [Title contains emojis] ({video_id})")
                
            has_new_videos = True
            new_processed.add(video_id)
            
        if has_new_videos:
            body = {
                'title': post.get('title'),
                'content': current_content,
                'labels': post.get('labels', [])
            }
            service.posts().update(blogId=BLOG_ID, postId=post_id, body=body).execute()
            print("Оновлення успішне!")
            
            with open(processed_file, 'w', encoding='utf-8') as f:
                json.dump(list(new_processed), f, indent=2)
                
        else:
            print("Не знайдено нових відео для оновлення.")
            
    except Exception as e:
        print(f"Помилка при оновленні Blogger: {e}")

def main():
    try:
        service = get_blogger_service()
        for config in CONFIGS:
            process_config(service, config)
    except Exception as e:
        print(f"Помилка авторизації: {e}")

if __name__ == '__main__':
    main()
