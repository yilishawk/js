import requests
import re
import json
import urllib3

# 禁用安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 配置区 ---
BC_CONFIG_URL = 'https://bc.188766.xyz/?ip=&haiwai=true'
MIGU_M3U_URL = 'https://raw.githubusercontent.com/develop202/migu_video/main/interface.txt'
CATVOD_URL = 'https://live.catvod.com/tv.m3u'
BC_UA = 'bingcha/1.1 (mianfeifenxiang)'

def get_content(url, ua='Mozilla/5.0', headers=None):
    try:
        h = {'User-Agent': ua}
        if headers: h.update(headers)
        r = requests.get(url, headers=h, timeout=30, verify=False)
        return r.text if r.status_code == 200 else None
    except:
        return None

def parse_m3u(content, prefix, include_filter=None, rename_map=None):
    """
    prefix: 来源前缀，如 "Cat"
    include_filter: 只有包含这些关键词的分组才会被留下
    rename_map: 字典，用于将旧分组名替换为新名
    """
    groups = {}
    lines = content.splitlines()
    current_inf = ""

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#EXTM3U'): continue

        if line.startswith('#EXTINF'):
            # 过滤广告
            if any(x in line for x in ['公告', '免费分享', '奸商', '提示', '微信']):
                current_inf = "SKIP"
                continue

            # 提取原组名
            group_match = re.search(r'group-title="([^"]*)"', line)
            original_group = group_match.group(1) if group_match else "其他"

            # 过滤逻辑：如果设置了过滤器，则只保留匹配的分组
            if include_filter and not any(f in original_group for f in include_filter):
                current_inf = "SKIP"
                continue

            # 更名逻辑
            target_group = original_group
            if rename_map and original_group in rename_map:
                target_group = rename_map[original_group]
            
            # 加上前缀 (方便后续优先级排序)
            final_group_name = f"{prefix} {target_group}"
            current_inf = re.sub(r'group-title="[^"]*"', f'group-title="{final_group_name}"', line)

        elif current_inf and current_inf != "SKIP" and line.startswith('http'):
            # 提取修正后的组名作为 key
            g_key_match = re.search(r'group-title="([^"]*)"', current_inf)
            if g_key_match:
                g_key = g_key_match.group(1)
                groups.setdefault(g_key, []).append(f"{current_inf}\n{line}")
            current_inf = ""

    return groups

# 1. 处理冰茶源 (原有逻辑)
bc_json_raw = get_content(BC_CONFIG_URL, BC_UA, {'Accept': 'application/json'})
bc_groups = {}
if bc_json_raw:
    data = json.loads(bc_json_raw)
    bc_live_url = data.get('lives', [{}])[0].get('url')
    if bc_live_url:
        bc_groups = parse_m3u(get_content(bc_live_url, BC_UA), "冰茶", rename_map={"粤语频道": "香港台"})

# 2. 处理咪咕源 (原有逻辑)
migu_content = get_content(MIGU_M3U_URL)
migu_groups = parse_m3u(migu_content, "咪咕") if migu_content else {}

# 3. 处理 CatVod 源 (新增逻辑)
catvod_content = get_content(CATVOD_URL)
cat_rename = {"中国": "央视频道"} # 将中国改为央视
cat_filter = ["中国", "香港", "台湾"] # 只提取这三个
catvod_groups = parse_m3u(catvod_content, "Cat", include_filter=cat_filter, rename_map=cat_rename) if catvod_content else {}

# 4. 合并与排序
all_groups = {**bc_groups, **migu_groups, **catvod_groups}
# 更新优先级列表
priority = [
    '冰茶 央视频道', '咪咕 央视频道', 'Cat 央视频道',
    '冰茶 卫视频道', '咪咕 卫视频道', 
    'Cat 香港', '冰茶 香港台', 'Cat 台湾'
]

final_output = ["#EXTM3U x-tvg-url=\"https://static.188766.xyz/e.xml\"\n"]

for p in priority:
    if p in all_groups:
        final_output.extend([c + "\n" for c in all_groups[p]])
        del all_groups[p]

for g in sorted(all_groups.keys()):
    final_output.extend([c + "\n" for c in all_groups[g]])

# 保存
with open('live.m3u', 'w', encoding='utf-8') as f:
    f.write("".join(final_output))

print("抓取完成，文件已生成：live.m3u")
