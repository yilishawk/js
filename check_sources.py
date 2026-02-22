import requests
import json
import hashlib
import os
from datetime import datetime

CACHE_FILE = "cache.json"           # 直接放根目录
OUTPUT_M3U = "live_sources.m3u"     # 也放根目录
JSON_URL = "https://yhzb.serv00.net/sss.json"

def fetch(url):
    headers = {"User-Agent": "LiveChecker/1.0"}
    try:
        r = requests.get(url, headers=headers, timeout=15, verify=False)  # 增加超时到15秒
        r.raise_for_status()
        return r.text.strip()
    except requests.exceptions.RequestException as e:
        print(f"Fetch failed: {url} → {str(e)}")
        return None

def compute_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest() if content else ""

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"A_url": "", "B_url": "", "A_hash": "", "B_hash": "", "last_change": ""}

def save_cache(data):
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_m3u_content(content, group_prefix=""):
    if not content:
        return []  # 如果内容为空，返回空列表避免错误
    lines = content.splitlines()
    current_group = ""
    channels = []
    for line in lines:
        line = line.strip()
        if not line: continue
        if ",#genre#" in line:
            current_group = line.split(",#genre#")[0].strip()
        elif "," in line and current_group:
            name, url = [x.strip() for x in line.split(",", 1)]
            if name and url.startswith("http"):
                channels.append(f"#EXTINF:-1 tvg-name=\"{group_prefix}{current_group} - {name}\",{name}\n{url}")
    return channels

def main():
    print(f"检查开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    json_text = fetch(JSON_URL)
    if not json_text:
        print("无法获取 JSON，退出")
        return

    try:
        data = json.loads(json_text)
    except:
        print("JSON 解析失败")
        return

    A_url = B_url = ""
    for item in data:
        name = (item.get("name") or "").strip()
        full_url = (item.get("url") or "").strip()
        real_url = full_url.split("&&&")[0].strip() if "&&&" in full_url else ""

        if "观看直播A" in name:
            A_url = real_url
        if "观看直播B" in name:
            B_url = real_url

    if not A_url or not B_url:
        print("未找到 A 或 B 链接")
        return

    cache = load_cache()
    changed = False
    messages = []

    if A_url != cache.get("A_url", "") or B_url != cache.get("B_url", ""):
        changed = True
        messages.append("URL 变化")
    else:
        A_content = fetch(A_url)
        B_content = fetch(B_url)
        if A_content is None or B_content is None:
            print("源内容获取失败，但继续检查 hash")
        
        new_A_hash = compute_hash(A_content)
        new_B_hash = compute_hash(B_content)

        if new_A_hash != cache.get("A_hash", "") or new_B_hash != cache.get("B_hash", ""):
            changed = True
            messages.append("内容变化")

    if changed:
        print("检测到变化！ " + " + ".join(messages))

        A_content = fetch(A_url) if "A_content" not in locals() else A_content
        B_content = fetch(B_url) if "B_content" not in locals() else B_content

        channels = []

        if A_content:
            a_channels = parse_m3u_content(A_content, "[A] ")
            channels.extend(a_channels)
            print(f"[A] 成功解析 {len(a_channels)} 个频道")
        else:
            print(f"[A] 获取失败：{A_url} （跳过）")

        if B_content:
            b_channels = parse_m3u_content(B_content, "[B] ")
            channels.extend(b_channels)
            print(f"[B] 成功解析 {len(b_channels)} 个频道")
        else:
            print(f"[B] 获取失败：{B_url} （跳过）")

        if channels:
            m3u_content = "#EXTM3U\n" + "\n".join(channels)
            with open(OUTPUT_M3U, "w", encoding="utf-8") as f:
                f.write(m3u_content)
            print(f"已更新 {OUTPUT_M3U}，共 {len(channels)} 个频道")
        else:
            print("无任何有效频道可写入 m3u")

        cache.update({
            "A_url": A_url,
            "B_url": B_url,
            "A_hash": compute_hash(A_content or ""),
            "B_hash": compute_hash(B_content or ""),
            "last_change": datetime.now().isoformat()
        })
        save_cache(cache)
    else:
        print("无变化")

if __name__ == "__main__":
    main()
