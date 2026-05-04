import requests
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_WORKERS = 30   # 并发数（关键）

def check_speed(url):
    try:
        start = time.time()
        r = requests.get(url, timeout=2, stream=True)
        if r.status_code == 200:
            return time.time() - start
    except:
        return None

def process_channel(name, url):
    speed = check_speed(url)
    if speed:
        return name, url, speed
    return None

def main():
    with open("sources.txt") as f:
        sources = [line.strip() for line in f if line.strip()]

    tasks = []
    results = {}

    for src in sources:
        try:
            lines = requests.get(src, timeout=10).text.splitlines()
        except:
            continue

        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF") and i+1 < len(lines):
                name = re.search(r",(.*)", lines[i])
                if not name:
                    continue
                name = name.group(1).strip()
                url = lines[i+1].strip()
                tasks.append((name, url))

    print(f"总任务数: {len(tasks)}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_channel, n, u) for n, u in tasks]

        for future in as_completed(futures):
            result = future.result()
            if result:
                name, url, speed = result
                if name not in results or speed < results[name][1]:
                    results[name] = (url, speed)

    with open("output/output.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, (url, _) in results.items():
            f.write(f"#EXTINF:-1,{name}\n{url}\n")

    print("完成 ✅")

if __name__ == "__main__":
    main()
