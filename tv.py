import re, requests, time
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor

# --- 配置区 ---
URL = "https://freetv.fun/test_channels_new.txt"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BLACKLIST = {"https://stream1.freetv.fun/tang-he-yi-tao-1.m3u8"}
MAX_WORKERS = 50  
TIMEOUT = 3       
# 仅对以下分组进行深度测速
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

    def get_weight(self, title, group_name):
        t = title.upper()
        if "央视" in group_name:
            m = re.search(r'CCTV(\d+)', t)
            return int(m.group(1)) if m else 99
        return 0

    def check_speed(self, item, group_name):
        """深度测速：1.5秒内尝试下载1MB，计算真实流畅度"""
        try:
            start_time = time.time()
            with requests.get(item['url'], headers=HEADERS, timeout=TIMEOUT, stream=True) as r:
                if r.status_code == 200:
                    ttfb = time.time() - start_time # 首字节延迟
                    
                    # 动态下载测试
                    downloaded = 0
                    test_start = time.time()
                    for chunk in r.iter_content(chunk_size=1024 * 64):
                        downloaded += len(chunk)
                        # 下载够1MB或耗时超过1.5秒则停止
                        if downloaded >= 1024 * 1024 or (time.time() - test_start) > 1.5:
                            break
                    
                    duration = time.time() - test_start
                    # 速度 (MB/s)，加0.1防止除以0
                    speed = (downloaded / 1024 / 1024) / (duration + 0.001)
                    
                    # 评分公式：延迟占30%，速度倒数占70%
                    # 结果越小，排名越靠前
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

        # 重新分配组
        self.finalGroups["央视,#genre#"] = [i for g in parsed_data.values() for i in g if i['title'].upper().startswith("CCTV")]
        self.finalGroups["卫视,#genre#"] = [i for i in parsed_data.get("中國大陸,#genre#", []) if "卫视" in i['title'] and not i['title'].upper().startswith("CCTV")]
        self.finalGroups["香港,#genre#"] = parsed_data.get("香港,#genre#", [])
        self.finalGroups["台湾,#genre#"] = parsed_data.get("台灣,#genre#", [])

        # 测速
        for g_name in list(self.finalGroups.keys()):
            channels = self.finalGroups[g_name]
            if not channels: continue
            
            # 只有指定的组才进行深度测速，其余只进行简单存活检查
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                results = list(executor.map(lambda x: self.check_speed(x, g_name), channels))
            
            # 过滤掉失败的源，并按照 频道权重->测速评分 排序
            valid = sorted([r for r in results if r], key=lambda x: (x['weight'], x['score']))
            for v in valid: v.pop('score', None); v.pop('weight', None)
            self.finalGroups[g_name] = valid

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
                        f.write(f"{line}\n")
                        seen.add(line)
                f.write("\n")

if __name__ == "__main__":
    LiveStreamCrawler()
