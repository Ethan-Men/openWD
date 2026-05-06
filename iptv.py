import requests
import time
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_WORKERS = 20
MAX_TASKS = 1000
TIMEOUT = (2, 3)

session = requests.Session()

def is_valid_url(url):
    return url.startswith("http")

def check_speed(url):
    try:
        start = time.time()
        r = session.get(url, timeout=TIMEOUT)
        if r.status_code == 200:
            return time.time() - start
    except:
        return None

def process_channel(name, url):
    if not is_valid_url(url):
        return None

    speed = check_speed(url)
    if speed:
        return name, url, speed
    return None

def fetch_sources():
    with open("sources.txt") as f:
        return [line.strip() for line in f if line.strip()]

def parse_m3u(text):
    lines = text.splitlines()
    tasks = []

    for i in range(len(lines)):
        if len(tasks) >= MAX_TASKS:
            break

        if lines[i].startswith("#EXTINF") and i+1 < len(lines):
            match = re.search(r",(.*)", lines[i])
            if not match:
                continue

            name = match.group(1).strip()
            url = lines[i+1].strip()

            tasks.append((name, url))

    return tasks

def main():
    sources = fetch_sources()
    tasks = []
    results = {}

    for src in sources:
        try:
            text = session.get(src, timeout=10).text
            tasks.extend(parse_m3u(text))
        except:
            continue

    print(f"任务数: {len(tasks)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_channel, n, u) for n, u in tasks]

        for future in as_completed(futures):
            try:
                result = future.result(timeout=5)
            except:
                continue

            if result:
                name, url, speed = result
                if name not in results or speed < results[name][1]:
                    results[name] = (url, speed)

    os.makedirs("output", exist_ok=True)

    with open("output/output.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, (url, _) in results.items():
            f.write(f"#EXTINF:-1,{name}\n{url}\n")

    print(f"完成 ✅ 有效频道: {len(results)}")

if __name__ == "__main__":
    main()