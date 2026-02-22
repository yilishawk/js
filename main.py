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
        print(f"狀態碼: {r.status_code}，無 #EXTM3U")
        return None
    except Exception as e:
        print(f"請求失敗: {e}")
        return None

def parse_and_filter(content):
    if not content:
        return {}
    
    groups = {}
    seen = set()  # (target_group, name) 去重
    
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
        
        lower_text = (inf + name).lower()
        if any(kw in lower_text for kw in ['測試', '失效', '公告', '分享', '提示', '微信']):
            continue
        
        group_match = re.search(r'group-title="([^"]*)"', inf, re.IGNORECASE)
        if not group_match:
            continue
        original_group = group_match.group(1).strip()
        
        # 只保留指定的分組（加 "卫视频道" 以匹配源）
        if original_group not in ["央视", "卫视", "卫视频道", "地方"]:
            continue
        
        # 地方 只留陝西開頭的
        if original_group == "地方" and not name.startswith("陝西"):
            continue
        
        # 決定新分組名稱（合併衛視變體）
        if original_group == "央视":
            target_group = "咪咕 • 央視頻道"
        elif original_group in ["卫视", "卫视频道"]:
            target_group = "咪咕 • 衛視頻道"
        elif original_group == "地方":
            target_group = "咪咕 • 陝西頻道"
        else:
            continue
        
        # 去重
        key = (target_group, name)
        if key in seen:
            continue
        seen.add(key)
        
        # 替換 group-title
        new_inf = re.sub(
            r'group-title="[^"]*"',
            f'group-title="{target_group}"',
            inf,
            flags=re.IGNORECASE
        )
        
        # 如果沒 group-title，補上
        if 'group-title="' not in new_inf:
            new_inf = re.sub(
                r'(#EXTINF:[^,]+)',
                r'\1 group-title="{target_group}"',
                new_inf,
                count=1
            )
        
        entry = f"{new_inf},{name}\n{url}"
        groups.setdefault(target_group, []).append(entry)
    
    return groups

def main():
    print("抓取 jn950 holive 源...")
    content = get_m3u_content(SOURCE_M3U_URL)
    if not content:
        print("獲取失敗")
        return
    
    groups = parse_and_filter(content)
    if not groups:
        print("無符合條件的頻道（請確認源是否有 '央视' '卫视' '地方' 分組）")
        return
    
    priority = [
        "咪咕 • 央視頻道",
        "咪咕 • 衛視頻道",
        "咪咕 • 陝西頻道",
    ]
    
    final_lines = ['#EXTM3U x-tvg-url="https://static.188766.xyz/e.xml"\n']
    
    added_count = 0
    for p in priority:
        if p in groups:
            final_lines.extend(groups[p])
            final_lines.append("\n")
            added_count += len(groups[p])
            del groups[p]
    
    for g in sorted(groups.keys()):
        final_lines.extend(groups[g])
        final_lines.append("\n")
        added_count += len(groups[g])
    
    output_file = "jn950_only_cctv_ws_shanxi.m3u"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("".join(final_lines))
    
    print(f"生成 {output_file} 完成，共 {added_count} 個頻道（已去重）")

if __name__ == "__main__":
    main()
