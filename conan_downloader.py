import requests
from bs4 import BeautifulSoup
import os
import subprocess
import re

DOODSTREAM_API_KEY = os.environ.get('DOODSTREAM_API_KEY', '554366xrjxeza9m7e4m02v')
BASE_EPISODE = 1193
BASE_DATE = '2026-03-14'
XOR_KEY_URL = "DetectiveConan2024"
HTML_FILE = "index.html"

def get_expected_episode():
    from datetime import datetime
    base_dt = datetime.strptime(BASE_DATE, '%Y-%m-%d')
    now = datetime.now()
    weeks = (now - base_dt).days // 7
    return BASE_EPISODE + max(0, weeks)

def find_magnet(episode):
    query = f'[Erai-raws] Detective Conan - {episode} [1080p]'
    url = f'https://nyaa.si/?f=0&c=0_0&q={requests.utils.quote(query)}'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    for row in soup.select('tr.success, tr.default'):
        for a in row.find_all('a', href=True):
            if a['href'].startswith('magnet:'):
                return a['href']
    return None

def download_torrent(magnet):
    print("Downloading torrent...")
    subprocess.run(['aria2c', '--seed-time=0', magnet], check=True)
    files = [f for f in os.listdir('.') if f.endswith('.mkv') and 'Detective Conan' in f]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def escape_ffmpeg_path(path):
    return path.replace('\\', '\\\\').replace("'", "\\'").replace(':', '\\:').replace('[', '\\[').replace(']', '\\]')

def hardsub_video(input_file):
    output_file = "processed_episode.mp4"
    print(f"Hard-subbing {input_file}...")
    escaped_input = escape_ffmpeg_path(input_file)
    cmd = ['ffmpeg', '-y', '-i', input_file, '-vf', f"subtitles='{escaped_input}'", '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-c:a', 'copy', output_file]
    try:
        subprocess.run(cmd, check=True)
        return output_file
    except:
        # fallback
        cmd_alt = ['ffmpeg', '-y', '-i', input_file, '-vf', f"subtitles={escaped_input}", '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22', '-c:a', 'copy', output_file]
        subprocess.run(cmd_alt, check=True)
        return output_file

def upload_to_doodstream(file_path, title):
    print(f"Uploading {file_path} to DoodStream...")
    server = requests.get(f'https://doodapi.co/api/upload/server?key={os.environ.get("DOODSTREAM_API_KEY", "554366xrjxeza9m7e4m02v")}').json()
    if server.get('status') != 200:
        return None
    url = server['result']
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        data = {'api_key': os.environ.get('DOODSTREAM_API_KEY', '554366xrjxeza9m7e4m02v'), 'title': title}
        resp = requests.post(f"{url}?{os.environ.get('DOODSTREAM_API_KEY', '554366xrjxeza9m7e4m02v')}", files=files, data=data)
        resp_json = resp.json()
        if resp_json.get('status') == 200:
            file_code = resp_json['result'][0]['filecode']
            return f"https://doodstream.com/e/{file_code}"
    return None

def update_html(episode, version, embed_url):
    if not os.path.exists(HTML_FILE):
        return False
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    # Simplified update logic
    content = content.replace('<!-- VIDEO_EMBED_LINK -->', embed_url)
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    return True

def main():
    episode = get_expected_episode()
    magnet = find_magnet(episode)
    if not magnet:
        print(f"Episode {episode} not found.")
        sys.exit(0)
    mkv_file = download_torrent(magnet)
    if not mkv_file:
        sys.exit(1)
    ss_url = upload_to_doodstream(mkv_file, f"{episode} SS")
    if ss_url:
        update_html(episode, "SS", ss_url)
    mp4_file = hardsub_video(mkv_file)
    if mp4_file:
        hs_url = upload_to_doodstream(mp4_file, f"{episode} HS")
        if hs_url:
            update_html(episode, "HS", hs_url)
    # cleanup
    if os.path.exists(mkv_file):
        os.remove(mkv_file)
    if os.path.exists(mp4_file):
        os.remove(mp4_file)

if __name__ == "__main__":
    main()
