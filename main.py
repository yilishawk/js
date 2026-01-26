import requests
import re
import json
import urllib3

# 屏蔽 https 安全警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 配置区 ---
BC_CONFIG_URL = 'https://bc.188766.xyz/?ip=&haiwai=true'
MIGU_M3U_URL = 'https://raw.githubusercontent.com/develop202/migu_video/main/interface.txt'
CATVOD_URL = 'https://live.catvod.com/tv.m3u'
BC_UA = 'bingcha/1.1 (mianfeifenxiang)'
# 模拟真实浏览器的 UA
BROWSER_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get_content(url, ua=BROWSER_UA, headers=None):
    """
    强化版下载函数：模拟浏览器行为并强制 UTF-8 编码
    """
    try:
        h = {
            'User-Agent': ua,
            'Accept': '*/*',
            'Referer': 'https://live.catvod.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        if headers: h.update(headers)
        
        # 使用 verify=False 绕过证书校验
        r = requests.get(url, headers=h, timeout=30, verify=False)
        
        # 核心修复：强制指定编码，防止“中国”等中文字符在抓取时变成乱码
        r.encoding = 'utf-8' 
        
        if r.status_code == 200:
            return r.text
        return None
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return None

def parse_m3u(content, prefix, include_filter=None, rename_map=None):
    groups = {}
    lines = content.splitlines()
    current_inf = ""

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#EXTM3U'): continue

        if line.startswith('#EXTINF'):
            # 过滤干扰信息
            if any(x in line for x in ['公告', '免费分享', '奸商', '提示', '微信', 'QQ']):
                current_inf = "SKIP"
                continue

            # 提取原组名
            group_match = re.search(r'group-title="([^"]*)"', line)
            original_group = group_match.group(1) if group_match else "其他"

            # 过滤逻辑：只保留指定的地区分组
            if include_filter and not any(f in original_group for f in include_filter):
                current_inf = "SKIP"
                continue

            # 更名逻辑：例如将“中国”改为“央视频道”
            target_group = original_group
            if rename_map and original_group in rename_map:
                target_group = rename_map[original_group]
            
            # 重新拼装带前缀的组名
            final_group_name = f"{prefix} {target_group}"
            current_inf = re.sub(r'group-title="[^"]*"', f'group-title="{final_group_name}"', line)

        elif current_inf and current_inf != "SKIP" and line.startswith('http'):
            # 提取修正后的组名作为字典键
            g_key_match = re.search(r'group-title="([^"]*)"', current_inf)
            if g_key_match:
                g_key = g_key_match.group(1)
                groups.setdefault(g_key, []).append(f"{current_inf}\n{line}")
            current_inf = ""

    return groups

# --- 1. 处理冰茶源 ---
bc_json_raw = get_content(BC_CONFIG_URL, BC_UA, {'Accept': 'application/json'})
bc_groups = {}
if bc_json_raw:
    data = json.loads(bc_json_raw)
    bc_live_url = data.get('lives', [{}])[0].get('url')
    if bc_live_url:
        bc_groups = parse_m3u(get_content(bc_live_url, BC_UA), "冰茶", rename_map={"粤语频道": "香港台"})

# --- 2. 处理咪咕源 ---
migu_content = get_content(MIGU_M3U_URL)
migu_groups = parse_m3u(migu_content, "咪咕") if migu_content else {}

# --- 3. 处理 CatVod 源 (先完整下载到内容，再进行正则抓取) ---
print("正在尝试下载 CatVod 源...")
catvod_raw_data = get_content(CATVOD_URL)
catvod_groups = {}
if catvod_raw_data:
    print(f"CatVod 下载成功 (长度: {len(catvod_raw_data)})，开始提取...")
    # 按照你的需求：提取中国/香港/台湾，并将中国改为央视频道
    cat_filter = ["中国", "香港", "台湾"]
    cat_rename = {"中国": "央视频道"}
    catvod_groups = parse_m3u(catvod_raw_data, "Cat", include_filter=cat_filter, rename_map=cat_rename)
else:
    print("CatVod 源下载失败，请检查网络或 URL。")

# --- 4. 合并与排序 ---
all_groups = {**bc_groups, **migu_groups, **catvod_groups}
priority = [
    '冰茶 央视频道', '咪咕 央视频道', 'Cat 央视频道',
    '冰茶 卫视频道', '咪咕 卫视频道', 
    'Cat 香港', '冰茶 香港台', 'Cat 台湾'
]

final_output = ["#EXTM3U x-tvg-url=\"https://static.188766.xyz/e.xml\"\n"]

# 写入优先级频道
for p in priority:
    if p in all_groups:
        for channel in all_groups[p]:
            final_output.append(channel + "\n")
        del all_groups[p]

# 剩余频道按字母排序写入
for g in sorted(all_groups.keys()):
    for channel in all_groups[g]:
        final_output.append(channel + "\n")

# --- 5. 保存文件 ---
with open('live.m3u', 'w', encoding='utf-8') as f:
    f.write("\n".join(final_output))

print("处理完成！生成的频道总数:", len(final_output) - 1)
