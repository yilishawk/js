import requests
import re
import json
import urllib3
import subprocess
import os

# 屏蔽安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 配置区 ---
BC_CONFIG_URL = 'https://bc.188766.xyz/?ip=&haiwai=true'
MIGU_M3U_URL = 'https://raw.githubusercontent.com/develop202/migu_video/main/interface.txt'
# 填入你测试成功的 PHP 跳板地址
CATVOD_URL = 'https://kwyili.dpdns.org/catvod.php' 

BC_UA = 'bingcha/1.1 (mianfeifenxiang)'
BROWSER_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_content_advanced(url, ua=BROWSER_UA):
    headers = {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'https://live.catvod.com/',
        'Connection': 'keep-alive'
    }
    try:
        r = requests.get(url, headers=headers, timeout=20, verify=False)
        r.encoding = 'utf-8'
        if r.status_code == 200 and "#EXTM3U" in r.text:
            return r.text
    except Exception:
        pass

    try:
        result = subprocess.run(
            ['curl', '-k', '-L', '-H', f'User-Agent: {ua}', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and "#EXTM3U" in result.stdout:
            return result.stdout
    except:
        pass
    return None

def parse_m3u(content, prefix, include_filter=None, rename_map=None):
    if not content: return {}
    groups = {}
    
    # 正则匹配 #EXTINF 行（含名称）和 URL 行
    pattern = re.compile(r'(#EXTINF:[^\n]+),\s*([^\n]+)\n+(http[^\s\n]+)', re.MULTILINE)
    matches = pattern.findall(content)

    for inf, name, url in matches:
        if any(x in inf for x in ['公告', '分享', '提示', '微信', '扫码']):
            continue

        # 提取 group-title
        group_match = re.search(r'group-title="([^"]*)"', inf)
        original_group = group_match.group(1) if group_match else "其他"

        # --- 基于关键词的精准分类逻辑 ---
        if "卫视" in name:
            target_group = "卫视频道"
        elif any(x in name for x in ["凤凰", "鳳凰", "香港", "翡翠"]):
            target_group = "香港"
        elif "CCTV" in name.upper():
            target_group = "央视频道"
        else:
            target_group = rename_map.get(original_group, original_group) if rename_map else original_group

        # 过滤器
        if include_filter:
            if not any(f in target_group for f in ["央视", "卫视", "香港", "台湾"]):
                if not any(f in original_group for f in include_filter):
                    continue

        final_group_name = f"{prefix} {target_group}"
        new_inf = re.sub(r'group-title="[^"]*"', f'group-title="{final_group_name}"', inf)
        groups.setdefault(final_group_name, []).append(f"{new_inf},{name}\n{url}")
    
    return groups

def main():
    # 1. 冰茶
    bc_raw = get_content_advanced(BC_CONFIG_URL, BC_UA)
    bc_groups = {}
    if bc_raw:
        try:
            bc_url = json.loads(bc_raw).get('lives', [{}])[0].get('url')
            if bc_url:
                bc_groups = parse_m3u(get_content_advanced(bc_url, BC_UA), "冰茶", rename_map={"粤语频道": "香港台"})
        except: pass

    # 2. 咪咕
    migu_groups = parse_m3u(get_content_advanced(MIGU_M3U_URL), "咪咕")

    # 3. CatVod (通过 PHP)
    cat_raw = get_content_advanced(CATVOD_URL)
    catvod_groups = {}
    if cat_raw:
        catvod_groups = parse_m3u(cat_raw, "Cat", include_filter=["中国", "香港", "台湾"], rename_map={"中国": "央视频道"})

    # 4. 合并
    all_groups = {**bc_groups, **migu_groups, **catvod_groups}
    if not all_groups: return

    # 排序优先级
    priority = [
        '冰茶 央视频道', '咪咕 央视频道', 'Cat 央视频道', 
        '冰茶 卫视频道', '咪咕 卫视频道', 'Cat 卫视频道',
        'Cat 香港', '冰茶 香港台', 'Cat 台湾'
    ]

    final_output = ["#EXTM3U x-tvg-url=\"https://static.188766.xyz/e.xml\"\n"]
    
    for p in priority:
        if p in all_groups:
            for item in all_groups[p]:
                final_output.append(item + "\n")
            del all_groups[p]

    for g in sorted(all_groups.keys()):
        for item in all_groups[g]:
            final_output.append(item + "\n")

    with open('live.m3u', 'w', encoding='utf-8') as f:
        f.write("".join(final_output))

if __name__ == "__main__":
    main()
