import re
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = "1755058049502207131"
POST_ID = "3593205608361563180"

def is_short(video_id):
    try:
        url = f"https://www.youtube.com/shorts/{video_id}"
        response = requests.head(url, allow_redirects=False, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Помилка перевірки Shorts для {video_id}: {e}")
        return False

def main():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/blogger'])
    service = build('blogger', 'v3', credentials=creds)
    post = service.posts().get(blogId=BLOG_ID, postId=POST_ID).execute()
    content = post.get('content', '')

    match = re.search(r'const\s+videoIds\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if not match:
        print("No videoIds found.")
        return

    original_ids_str = match.group(1)
    ids = re.findall(r'"([^"]+)"', original_ids_str)
    
    # We only check the first 20 videos to save time and API calls
    recent_ids = ids[:20]
    older_ids = ids[20:]
    
    kept_recent_ids = []
    removed_count = 0
    
    print("Checking recent 20 videos for Shorts...")
    for vid in recent_ids:
        if is_short(vid):
            print(f"Removing Short: {vid}")
            removed_count += 1
        else:
            kept_recent_ids.append(vid)
            
    if removed_count == 0:
        print("No Shorts found to remove.")
        return
        
    final_ids = kept_recent_ids + older_ids
    new_ids_str = ", ".join(f'"{vid}"' for vid in final_ids)
    
    new_content = content[:match.start(1)] + new_ids_str + content[match.end(1):]
    
    # Also update the thumbnail to the latest NON-SHORT video
    latest_vid = final_ids[0]
    print(f"Latest real video is: {latest_vid}")
    
    new_content = re.sub(
        r'<img src="https://img\.youtube\.com/vi/[^/]+/hqdefault\.jpg"',
        f'<img src="https://img.youtube.com/vi/{latest_vid}/hqdefault.jpg"',
        new_content,
        count=1
    )
    
    new_content = re.sub(
        r'<div class="youtube-cover" style="display:none;">[^<]+</div>',
        f'<div class="youtube-cover" style="display:none;">{latest_vid}</div>',
        new_content,
        count=1
    )
    
    body = {
        'title': post.get('title'),
        'content': new_content,
        'labels': post.get('labels', [])
    }
    service.posts().update(blogId=BLOG_ID, postId=POST_ID, body=body).execute()
    print(f"Successfully cleaned up {removed_count} Shorts from the post!")

if __name__ == '__main__':
    main()
