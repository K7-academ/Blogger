import re
import json
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

BLOG_ID = "1755058049502207131"
POST_ID = "3593205608361563180"
PROCESSED_FILE = "processed_infinityvideohub.json"

VIDEOS_TO_CHECK = ['_CkcchasDDY', 'pxCAgfhki_A', 'KUtNslwVMuU', '98abi7kMwVI', 'UcM9KfyiVhE', 'eFHVQmAiAts', 'D7gptJfUrXk', 'mqopWrkRL6g', 'palxO2BNPIw', 'VMa75IwtE9w', 'Wk3JHzgEkP0', '3Em-NsFclg4', '5Gx1N2j_jss', 'ey-zeBasqxo', 'LKreRR0e1GM', 'RSGHvRCPedc', 'p9q_L7MYgvY', 'dk27uYSx2Qc', 'X3ClCYQSWjs', 'WafV1vj8qEA', 'WosQWljrEIQ', 'xVzqubaJEpY', '0xCTtxTUa94', 'rOA7ucFjNEs', 'ud2IvBKuB2I', 'Usi1Z7FAdfk', 'cLypQHIUqX8', 'VqT-Z7ej-Kw', 'HcpWYassqXM', 'jJzuUKnOViI']

def is_short(video_id):
    try:
        url = f"https://www.youtube.com/shorts/{video_id}"
        response = requests.head(url, allow_redirects=False, timeout=5)
        return response.status_code == 200
    except Exception as e:
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
    existing_ids = re.findall(r'"([^"]+)"', original_ids_str)
    
    with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
        processed_set = set(json.load(f))
        
    videos_to_add = []
    # Reverse so we add older videos first, maintaining chronology when prepended
    for vid in reversed(VIDEOS_TO_CHECK):
        if vid in existing_ids:
            continue
        if is_short(vid):
            print(f"Skipping short: {vid}")
            processed_set.add(vid)
        else:
            print(f"Found long video to add: {vid}")
            videos_to_add.append(vid)
            processed_set.add(vid)
            
    if not videos_to_add:
        print("No new long videos found.")
        return
        
    # Prepend to existing_ids
    # videos_to_add has older first. So if we prepend them in order, the last one (newest) will be at the end of the prepended block? 
    # Wait, if we want the newest at index 0, we should put the newest first.
    # Actually, `videos_to_add` is ordered oldest to newest.
    # To prepend so that newest is at index 0:
    # final_ids = newest + older + existing
    # `reversed(videos_to_add)` brings it back to newest first.
    final_ids = list(reversed(videos_to_add)) + existing_ids
    
    new_ids_str = ", ".join(f'"{vid}"' for vid in final_ids)
    new_content = content[:match.start(1)] + new_ids_str + content[match.end(1):]
    
    # Update thumbnail to the absolute newest
    latest_vid = final_ids[0]
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
    print(f"Added {len(videos_to_add)} missing videos!")
    
    with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(processed_set), f, indent=2)

if __name__ == '__main__':
    main()
