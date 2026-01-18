import requests
import re
import json

# --- 配置区 ---
BC_CONFIG_URL = 'https://bc.188766.xyz/?ip=&haiwai=true'
MIGU_M3U_URL = 'https://raw.githubusercontent.com/develop202/migu_video/main/interface.txt'
BC_UA = 'bingcha/1.1 (mianfeifenxiang)'

def get_content(url, ua='Mozilla/5.0', headers=None):
    try:
        h = {'User-Agent': ua}
        if headers:
            h.update(headers)
        r = requests.get(url, headers=h, timeout=30, verify=False)
        return r.text if r.status_code == 200 else None
    except:
        return None

def parse_m3u(content, prefix):
    groups = {}
    lines = content.split('\n')
    current_inf = ""
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#EXTM3U'):
            continue
        
        if line.startswith('#EXTINF'):
            # 过滤广告
            if any(x in line for x in ['公告', '免费分享', '奸商', '提示', '微信']):
                current_inf = "SKIP"
                continue
            
            # 提取分组并更名
            group_match = re.search(r'group-title="([^"]*)"', line)
            group_name = group_match.group(1) if group_match else "其他"
            if group_name == "粤语频道":
                group_name = "香港台"
            
            new_group = f"{prefix} {group_name}"
            # 替换行内的 group-title
            current_inf = re.sub(r'group-title="[^"]*"', f'group-title="{new_group}"', line)
            if new_group not in groups:
                groups[new_group] = []
        
        elif current_inf and current_inf != "SKIP" and line.startswith('http'):
            # 记录 组名 -> 完整的频道块
            group_key = re.search(r'group-title="([^"]*)"', current_inf).group(1)
            groups[group_key].append(f"{current_inf}\n{line}")
            current_inf = ""
            
    return groups

# 1. 处理冰茶源
bc_json_raw = get_content(BC_CONFIG_URL, BC_UA, {'Accept': 'application/json'})
bc_groups = {}
if bc_json_raw:
    data = json.loads(bc_json_raw)
    bc_live_url = data.get('lives', [{}])[0].get('url')
    if bc_live_url:
        bc_content = get_content(bc_live_url, BC_UA)
        if bc_content:
            bc_groups = parse_m3u(bc_content, "冰茶")

# 2. 处理咪咕源
migu_content = get_content(MIGU_M3U_URL)
migu_groups = parse_m3u(migu_content, "咪咕") if migu_content else {}

# 3. 合并与排序
all_groups = {**bc_groups, **migu_groups}
priority = ['冰茶 央视频道', '咪咕 央视频道', '冰茶 卫视频道', '咪咕 卫视频道', '冰茶 香港台', '咪咕 香港台']

final_output = ["#EXTM3U x-tvg-url=\"https://static.188766.xyz/e.xml\"\n"]

# 按优先级写入
for p in priority:
    if p in all_groups:
        for channel in all_groups[p]:
            final_output.append(channel + "\n")
        del all_groups[p]

# 剩余按字母排序写入
for g in sorted(all_groups.keys()):
    for channel in all_groups[g]:
        final_output.append(channel + "\n")

# 保存文件
with open('live.m3u', 'w', encoding='utf-8') as f:
    f.write("\n".join(final_output))
