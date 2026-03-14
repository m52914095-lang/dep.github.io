import os
import sys
from conan_utils import xor_encrypt
from conan_downloader import find_magnet, download_torrent, hardsub_video, upload_to_doodstream, update_html

def get_target_episode():
    ep_input = os.environ.get('EPISODE_NUMBER', '').strip()
    if ep_input.isdigit():
        return int(ep_input)
    # Auto-calculate based on date
    from datetime import datetime
    BASE_DATE = datetime(2026, 3, 14)
    now = datetime.now()
    weeks_passed = (now - BASE_DATE).days // 7
    BASE_EPISODE = 1193
    return BASE_EPISODE + max(0, weeks_passed)

def main():
    episode = get_target_episode()
    print(f"Target episode: {episode}")

    magnet_link = os.environ.get('MAGNET_LINK', '').strip()

    if magnet_link:
        magnet = magnet_link
        print(f"Using provided magnet link: {magnet}")
    else:
        magnet = find_magnet(episode)
        if not magnet:
            print(f"Magnet not found for episode {episode}")
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

    # Cleanup
    if os.path.exists(mkv_file):
        os.remove(mkv_file)
    if os.path.exists(mp4_file):
        os.remove(mp4_file)

if __name__ == "__main__":
    main()
