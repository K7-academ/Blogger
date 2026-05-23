import requests
import re
import json

def get_channel_videos(url):
    html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    videos = []
    # ytInitialData
    match = re.search(r'ytInitialData\s*=\s*({.*?});', html)
    if match:
        data = json.loads(match.group(1))
        # Find all "videoId" keys using regex on the stringified JSON
        vids = re.findall(r'"videoId":"([^"]+)"', match.group(1))
        # Remove duplicates preserving order
        seen = set()
        for v in vids:
            if v not in seen and len(v) == 11:
                seen.add(v)
                videos.append(v)
    return videos

vids = get_channel_videos('https://www.youtube.com/@infinityvideohub/videos')
print("Total found:", len(vids))
print(vids[:40])
