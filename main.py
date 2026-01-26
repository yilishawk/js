import requests
import re
import json
import urllib3
import subprocess

# 屏蔽安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 配置区 ---
BC_CONFIG_URL = 'https://bc.188766.xyz/?ip=&haiwai=true'
MIGU_M3U_URL = 'https://raw.githubusercontent.com/develop202/migu_video/main/interface.txt'
CATVOD_URL = 'https://live.catvod.com/tv.m3u'
BC_UA = 'bingcha/1.1 (mianfeifenxiang)'
# 使用更现代的浏览器 UA
BROWSER_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_content_advanced(url, ua=BROWSER_UA):
    """
    尝试多种方式下载内容，解决 GitHub Actions 被屏蔽的问题
    """
    headers = {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,en;q=0.5,en-US;q=0.3',
        'Referer': 'https://live.catvod.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    # 方法 A: 使用 requests (带 session)
    try:
        session = requests.Session()
        r = session.get(url, headers=headers, timeout=20, verify=False)
        r.encoding = 'utf-8'
        if r.status_code == 200 and "#EXTM3U" in r.text:
            return r.text
    except:
        pass

    # 方法 B: 备选方案 - 使用系统 curl 命令 (GitHub Actions 环境通常自带)
    try:
        print(f"尝试使用系统 curl 下载 {url}...")
        result = subprocess.run(
            ['curl', '-k', '-L', '-H', f'User-Agent: {ua}', '-H', 'Referer: https://live.catvod.com/', url],
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
    lines = content.splitlines()
    current_inf = ""

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#EXTM3U'): continue

        if line.startswith('#EXTINF'):
            if any(x in line for x in ['公告', '免费分享', '奸商', '提示', '微信']):
                current_inf = "SKIP"
                continue

            group_match = re.search(r'group-title="([^"]*)"', line)
            original_group = group_match.group(1) if group_match else "其他"

            if include_filter and not any(f in original_group for f in include_filter):
                current_inf = "SKIP"
                continue

            target_group = original_group
            if rename_map and original_group in rename_map:
                target_group = rename_map[original_group]
            
            final_group_name = f"{prefix} {target_group}"
            current_inf = re.sub(r'group-title="[^"]*"', f'group-title="{final_group_name}"', line)

        elif current_inf and current_inf != "SKIP" and line.startswith('http'):
            g_key_match = re.search(r'group-title="([^"]*)"', current_inf)
            if g_key_match:
                g_key = g_key_match.group(1)
                groups.setdefault(g_key, []).append(f"{current_inf}\n{line}")
            current_inf = ""
    return groups

# --- 逻辑处理 ---
# 1. 冰茶
bc_raw = get_content_advanced(BC_CONFIG_URL, BC_UA)
bc_groups = {}
if bc_raw:
    try:
        data = json.loads(bc_raw)
        bc_url = data.get('lives', [{}])[0].get('url')
        bc_groups = parse_m3u(get_content_advanced(bc_url, BC_UA), "冰茶", rename_map={"粤语频道": "香港台"})
    except: pass

# 2. 咪咕
migu_groups = parse_m3u(get_content_advanced(MIGU_M3U_URL), "咪咕")

# 3. CatVod (强化版)
print("正在尝试下载 CatVod 源...")
cat_raw = get_content_advanced(CATVOD_URL)
catvod_groups = {}
if cat_raw:
    print(f"CatVod 获取成功，长度: {len(cat_raw)}")
    catvod_groups = parse_m3u(cat_raw, "Cat", include_filter=["中国", "香港", "台湾"], rename_map={"中国": "央视频道"})
else:
    print("CatVod 仍然获取失败，可能是 GitHub IP 被封锁。")

# 4. 合并排序
all_groups = {**bc_groups, **migu_groups, **catvod_groups}
priority = ['冰茶 央视频道', '咪咕 央视频道', 'Cat 央视频道', '冰茶 卫视频道', '咪咕 卫视频道', 'Cat 香港', '冰茶 香港台', 'Cat 台湾']

final_output = ["#EXTM3U x-tvg-url=\"https://static.188766.xyz/e.xml\"\n"]
for p in priority:
    if p in all_groups:
        final_output.extend([c + "\n" for c in all_groups[p]])
        del all_groups[p]

for g in sorted(all_groups.keys()):
    final_output.extend([c + "\n" for c in all_groups[g]])

with open('live.m3u', 'w', encoding='utf-8') as f:
    f.write("".join(final_output))

print(f"处理完成！生成频道总数: {len(final_output)-1}")
