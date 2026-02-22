import requests
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SOURCE_M3U_URL = 'https://raw.githubusercontent.com/jn950/live/main/tv/holive.m3u'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_m3u_content(url):
    headers = {'User-Agent': UA, 'Accept': '*/*'}
    try:
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        r.encoding = 'utf-8'
        if r.status_code == 200 and "#EXTM3U" in r.text.upper():
            return r.text
        print(f"狀態碼: {r.status_code}")
        return None
    except Exception as e:
        print(f"請求失敗: {e}")
        return None

def parse_and_filter(content):
    if not content:
        return {}

    groups = {}
    seen = set()

    pattern = re.compile(
        r'(#EXTINF:[^\n]+?)(?:,|\s+)([^\n]*?)\n+(https?://[^\s\n]+)',
        re.IGNORECASE | re.MULTILINE | re.DOTALL
    )

    matches = pattern.findall(content)
    print(f"找到 {len(matches)} 個候選條目")

    for inf, name, url in matches:
        name = name.strip()
        if not name or len(name) < 2:
            continue

        # 过滤测试、广告等垃圾频道
        lower_text = (inf + name).lower()
        if any(kw in lower_text for kw in ['測試', '失效', '公告', '分享', '提示', '微信']):
            continue

        # 只匹配分组名
        group_match = re.search(r'group-title="([^"]*)"', inf, re.IGNORECASE)
        if not group_match:
            continue
        g = group_match.group(1).strip()

        # ==============================================
        # 【重点】只保留：央视、卫视
        # 央视频道、卫视频道、其他 全部丢掉
        # ==============================================
        if g not in ["央视", "卫视"]:
            continue

        # 去重
        key = (g, name)
        if key in seen:
            continue
        seen.add(key)

        entry = f"{inf},{name}\n{url}"
        groups.setdefault(g, []).append(entry)

    return groups

def main():
    print("抓取 jn950 holive 源...")
    content = get_m3u_content(SOURCE_M3U_URL)
    if not content:
        print("獲取失敗")
        return

    groups = parse_and_filter(content)
    if not groups:
        print("無符合條件的頻道")
        return

    final_lines = ['#EXTM3U\n']
    added = 0

    # 输出顺序：央视 → 卫视
    for p in ["央视", "卫视"]:
        if p in groups:
            final_lines.extend(groups[p])
            final_lines.append("\n")
            added += len(groups[p])

    output_file = "only_cctv_and_ws.m3u"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("".join(final_lines))

    print(f"生成完成：{output_file}")
    print(f"共提取 {added} 個頻道（僅 央视 + 卫视）")

if __name__ == "__main__":
    main()
