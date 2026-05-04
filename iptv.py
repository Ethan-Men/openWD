import requests
import time
import re

def load_sources():
    with open("sources.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def fetch_m3u(url):
    try:
        return requests.get(url, timeout=10).text.splitlines()
    except:
        return []

def check_speed(url):
    try:
        start = time.time()
        r = requests.get(url, timeout=3, stream=True)
        if r.status_code == 200:
            return time.time() - start
    except:
        return None

def classify(name):
    if "CCTV" in name:
        return "CCTV"
    elif "卫视" in name:
        return "卫视"
    elif any(x in name for x in ["TVB", "翡翠", "本港台"]):
        return "港澳"
    else:
        return "其他"

def main():
    sources = load_sources()
    channels = {}

    for src in sources:
        lines = fetch_m3u(src)

        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                name = re.search(r",(.*)", lines[i])
                if not name or i+1 >= len(lines):
                    continue

                name = name.group(1).strip()
                url = lines[i+1].strip()

                speed = check_speed(url)
                if speed:
                    if name not in channels or speed < channels[name][1]:
                        channels[name] = (url, speed)

    with open("output/output.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for name, (url, _) in channels.items():
            group = classify(name)
            f.write(f'#EXTINF:-1 group-title="{group}",{name}\n{url}\n')

if __name__ == "__main__":
    main()
