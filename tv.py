import re, requests, time
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor

# --- 配置区 ---
URL = "https://freetv.fun/test_channels_new.txt"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BLACKLIST = {"https://stream1.freetv.fun/tang-he-yi-tao-1.m3u8"}
MAX_WORKERS = 50  
TIMEOUT = 3       
# 仅对以下最常看的分组进行深度测速排序
SPEED_TEST_GROUPS = ["央视,#genre#", "卫视,#genre#", "香港,#genre#"]
OUTPUT_FILE = "tv.txt"

def ts(t):
    rep = {"臺":"台","衛":"卫","視":"视","頻":"频","廣":"广","東":"东","鳳":"凤","凰":"凰","資":"资","訊":"讯","綜":"综","藝":"艺","劇":"剧","無線":"无线","翡翠":"翡翠","緯來":"纬来"}
    for a,b in rep.items(): t = t.replace(a,b)
    return t.strip()

class LiveStreamCrawler:
    def __init__(self):
        self.finalGroups = OrderedDict()
        self.fetch_and_process()

    def cleanTitle(self, title):
        title = re.sub(r'CCTV-?1\(RTHK33\)', 'CCTV1', title, flags=re.I)
        patterns = [r'\(backup\)', r'\(h26\d\)', r'\(备用\)', r'\(备\)', r'\[.*?\]', r'#\d+']
        for p in patterns: title = re.sub(p, '', title, flags=re.I)
        title = ts(title)
        if title.upper().startswith("CCTV"): title = title.replace("-", "").replace(" ", "")
        return title.strip()

    def is_all_abc(self, title):
        """识别纯英文名称频道，如 CNN, HBO, BBC"""
        clean_text = re.sub(r'[\s\d\-\_\.\(\)\[\]]', '', title)
        if clean_text.isalpha() and not re.search(r'[\u4e00-\u9fa5]', title):
            return True
        return False

    def get_weight(self, title, group_name):
        t = title.upper()
        # 1. 央视按数字排序
        if "央视" in group_name:
            m = re.search(r'CCTV(\d+)', t)
            return int(m.group(1)) if m else 99
        # 2. 香港组：凤凰优先
        if "香港" in group_name:
            if "凤凰" in t or "鳳凰" in t: return 1
            return 10
        # 3. 台湾组：虽然不测速，但这里保留权重用于基础排序
        if "台湾" in group_name:
            if "新闻" in t or "新聞" in t: return 1
            if "综合" in t or "綜合" in t: return 2
            if "娱乐" in t or "娛樂" in t or "综艺" in t: return 3
            return 10
        return 100

    def check_speed(self, item, group_name):
        """重点组 1MB 深度测速"""
        try:
            start_time = time.time()
            with requests.get(item['url'], headers=HEADERS, timeout=TIMEOUT, stream=True) as r:
                if r.status_code == 200:
                    ttfb = time.time() - start_time
                    downloaded = 0
                    test_start = time.time()
                    for chunk in r.iter_content(chunk_size=1024 * 64):
                        downloaded += len(chunk)
                        if downloaded >= 1024 * 1024 or (time.time() - test_start) > 1.5:
                            break
                    duration = time.time() - test_start
                    speed = (downloaded / 1024 / 1024) / (duration + 0.001)
                    score = ttfb * 0.3 + (1 / (speed + 0.1)) * 0.7
                    return {**item, "score": score, "weight": self.get_weight(item['title'], group_name)}
        except: pass
        return None

    def fetch_and_process(self):
        try:
            r = requests.get(URL, headers=HEADERS, timeout=15)
            lines = r.text.splitlines()
        except Exception as e:
            print(f"Fetch failed: {e}"); return

        parsed_data = defaultdict(list)
        current_group = ""
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#EXT"): continue
            if "#genre#" in line:
                current_group = line; continue
            if current_group and "," in line:
                parts = line.split(",", 1)
                title, url = parts[0].strip(), parts[1].strip()
                if url in BLACKLIST: continue
                parsed_data[current_group].append({"title": self.cleanTitle(title), "url": url})

        # --- 1. 分组与 ABC 过滤 ---
        # 核心组
        self.finalGroups["央视,#genre#"] = [i for g in parsed_data.values() for i in g if i['title'].upper().startswith("CCTV")]
        mainland = parsed_data.get("中國大陸,#genre#", [])
        self.finalGroups["卫视,#genre#"] = [i for i in mainland if "卫视" in i['title'] and not i['title'].upper().startswith("CCTV")]
        
        # 香港 & 台湾 (均应用 ABC 过滤)
        self.finalGroups["香港,#genre#"] = [i for i in parsed_data.get("香港,#genre#", []) if not self.is_all_abc(i['title'])]
        self.finalGroups["台湾,#genre#"] = [i for i in parsed_data.get("台灣,#genre#", []) if not self.is_all_abc(i['title'])]

        # --- 2. 测速排序 (仅针对重点组) ---
        for g_name in list(self.finalGroups.keys()):
            channels = self.finalGroups[g_name]
            if g_name in SPEED_TEST_GROUPS:
                # 重点组执行深度测速
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    results = list(executor.map(lambda x: self.check_speed(x, g_name), channels))
                valid = sorted([r for r in results if r], key=lambda x: (x['weight'], x['score']))
                for v in valid: v.pop('score', None); v.pop('weight', None)
                self.finalGroups[g_name] = valid
            else:
                # 台湾组：不测速，但按关键词权重进行简单排序
                self.finalGroups[g_name] = sorted(channels, key=lambda x: self.get_weight(x['title'], g_name))

        # --- 3. 提取省份组 (不测速) ---
        exclude_titles = set(i['title'] for i in self.finalGroups["央视,#genre#"] + self.finalGroups["卫视,#genre#"])
        province_map = {"北京":["北京"],"上海":["上海"],"广东":["广东","广州","深圳"],"浙江":["浙江","杭州","宁波"],"江苏":["江苏","南京","苏州"],"湖南":["湖南","长沙"]}
        for p, keys in province_map.items():
            p_list = []
            for i in mainland:
                if i['title'] in exclude_titles or i['title'].upper().startswith("CCTV"): continue
                if any(k in i['title'] for k in keys):
                    p_list.append(i)
            if p_list:
                self.finalGroups[f"{p},#genre#"] = p_list

        self.output_result()

    def output_result(self):
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for g, chans in self.finalGroups.items():
                if not chans: continue
                f.write(f"{g}\n")
                seen = set()
                for ch in chans:
                    line = f"{ch['title']},{ch['url']}"
                    if line not in seen:
                        f.write(line + "\n")
                        seen.add(line)
                f.write("\n")

if __name__ == "__main__":
    LiveStreamCrawler()
