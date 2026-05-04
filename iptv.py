import requests

def check_url(url):
    try:
        r = requests.get(url, timeout=3)
        return r.status_code == 200
    except:
        return False

def process_m3u(file):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    output = []
    for i in range(0, len(lines), 2):
        info = lines[i].strip()
        url = lines[i+1].strip()

        if check_url(url):
            output.append(info)
            output.append(url)

    with open("output.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(output))

process_m3u("source.m3u")
