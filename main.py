import requests
import re
import urllib3

# 屏蔽安全警告（如果有https驗證問題）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置
MIGU_M3U_URL = 'https://raw.githubusercontent.com/develop202/migu_video/main/interface.txt'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_m3u_content(url):
    headers = {
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    try:
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        r.encoding = 'utf-8'
        if r.status_code == 200 and "#EXTM3U" in r.text.upper():
            return r.text
        print(f"狀態碼: {r.status_code}，內容不包含 #EXTM3U")
        return None
    except Exception as e:
        print(f"請求失敗: {e}")
        return None


def parse_and_classify_migu(content):
    if not content:
        return {}

    groups = {}
    
    # 匹配 #EXTINF 行 和 下一行的 url
    pattern = re.compile(
        r'(#EXTINF:[^\n]+),\s*([^\n]*?)\n+(https?://[^\s\n]+)',
        re.IGNORECASE | re.MULTILINE
    )
    
    matches = pattern.findall(content)
    print(f"找到 {len(matches)} 個頻道")

    for inf, name, url in matches:
        name = name.strip()
        if not name:
            continue
            
        # 跳過廣告/公告類
        if any(x in inf.lower() for x in ['公告', '分享', '提示', '微信', '掃碼', '失效', '测试']):
            continue
            
        # 提取原始 group-title
        group_match = re.search(r'group-title="([^"]*)"', inf, re.IGNORECASE)
        original_group = group_match.group(1).strip() if group_match else "未分類"
        
        # 簡單分類（可自行增減規則）
        if "CCTV" in name.upper() or "央視" in name:
            target_group = "央視頻道"
        elif "衛視" in name or "衛星" in name:
            target_group = "衛視頻道"
        elif any(x in name for x in ["鳳凰", "凤凰", "翡翠", "TVB", "香港"]):
            target_group = "港澳頻道"
        elif any(x in name for x in ["民視", "中視", "台視", "三立", "東森", "中天", "SET"]):
            target_group = "台灣頻道"
        else:
            target_group = original_group
            
        group_name = f"咪咕 • {target_group}"
        
        # 替換 group-title
        new_inf = re.sub(
            r'group-title="[^"]*"',
            f'group-title="{group_name}"',
            inf,
            flags=re.IGNORECASE
        )
        
        # 如果 inf 裡本來沒有 group-title，就補上
        if 'group-title=' not in new_inf:
            new_inf = new_inf.replace("#EXTINF:", '#EXTINF:-1 group-title="' + group_name + '",')
        
        entry = f"{new_inf},{name}\n{url}"
        groups.setdefault(group_name, []).append(entry)
    
    return groups


def main():
    print("正在抓取咪咕源...")
    content = get_m3u_content(MIGU_M3U_URL)
    
    if not content:
        print("獲取失敗或內容無效")
        return
    
    groups = parse_and_classify_migu(content)
    
    if not groups:
        print("沒有解析到任何有效頻道")
        return
    
    # 輸出排序（可自訂優先順序）
    priority = [
        "咪咕 • 央視頻道",
        "咪咕 • 衛視頻道",
        "咪咕 • 港澳頻道",
        "咪咕 • 台灣頻道",
    ]
    
    final_lines = ["#EXTM3U x-tvg-url=\"https://static.188766.xyz/e.xml\"\n"]
    
    # 優先頻道
    for p in priority:
        if p in groups:
            final_lines.extend(groups[p])
            final_lines.append("\n")
            del groups[p]
    
    # 其他剩餘分類（按名稱排序）
    for group in sorted(groups.keys()):
        final_lines.extend(groups[group])
        final_lines.append("\n")
    
    # 寫入檔案
    output_file = "migu_live.m3u"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("".join(final_lines))
    
    print(f"已生成 {output_file}，共 {len(groups)} 個分類")


if __name__ == "__main__":
    main()
