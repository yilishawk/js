import re
import requests
import time
from collections import defaultdict, OrderedDict
from concurrent.futures import ThreadPoolExecutor

# --- 配置区 ---
URL = "https://freetv.fun/test_channels_new.txt"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BLACKLIST = {"https://stream1.freetv.fun/tang-he-yi-tao-1.m3u8"}
MAX_WORKERS = 20  
TIMEOUT = 5       
# 仅对以下分组进行测速和速度排序
SPEED_TEST_GROUPS = ["央视,#genre#", "卫视,#genre#", "香港,#genre#"]
OUTPUT_FILE = "tv.txt"

def ts(t):
    rep = {"臺":"台","衛":"卫","視":"视","頻":"频","廣":"广","東":"东","鳳":"凤","凰":"凰","資":"资","訊":"讯","綜":"综","藝":"艺","劇":"剧","無線":"无线","翡翠":"翡翠","緯來":"纬来"}
    for a,b in rep.items(): t = t.replace(a,b)
    return t.strip()

class LiveStreamCrawler:
    def __init__(self):
        self.rawContent = ""
        self.parsedData = defaultdict(list)
        self.finalGroups = OrderedDict()

        self.fetchData()
        self.parseData()
        self.processCCTVChannels()
        self.processMainlandChina()
        self.processHongKong()
        self.processTaiwan()
        self.processProvinceFromMainland()

        self.speedTestSelectedGroups()
        self.outputResult()

    def fetchData(self):
        try:
            r = requests.get(URL, headers=HEADERS, timeout=30)
            r.raise_for_status()
            self.rawContent = r.text
        except Exception as e:
            print(f"Fetch failed: {e}")

    def parseData(self):
        currentGroup = ""
        for line in self.rawContent.splitlines():
            line = line.strip()
            if not line or line.startswith("#EXT"): continue
            if "#genre#" in line:
                currentGroup = line.strip()
                self.parsedData[currentGroup] = []
                continue
            if currentGroup and "," in line:
                parts = line.split(",", 1)
                if len(parts) == 2:
                    title, url = parts
                    if url.strip() in BLACKLIST: continue
                    self.parsedData[currentGroup].append({"title": title.strip(), "url": url.strip()})

    def cleanTitle(self, title):
        # 统一更名
        title = re.sub(r'CCTV-?1\(RTHK33\)', 'CCTV1', title, flags=re.I)
        patterns = [r'\s*\(backup\)', r'\s*\(h265\)', r'\s*\(h264\)', r'\s*\(备用\)', r'\s*\(备\)', r'\s*\[.*?\]', r'\s*#\d+']
        for p in patterns: title = re.sub(p, '', title, flags=re.I)
        title = ts(title)
        if title.upper().startswith("CCTV"):
            title = title.replace("-", "").replace(" ", "")
        return title.strip()

    def get_weight(self, title, group_type):
        title_up = title.upper()
        if "央视" in group_type:
            m = re.search(r'CCTV(\d+)', title_up)
            if m: return int(m.group(1))
            spec = {"CCTV8K":100, "CCTVDOCUMENTARY":101, "CCTV戲曲":102, "CCTV第一劇場":103, "CCTV风云足球":104}
            for k,v in spec.items():
                if k in title_up: return v
            return 999
        if "香港" in group_type:
            if any(x in title for x in ["凤凰", "鳳凰"]): return 1
            if "中文" in title: return 2
            if any(x in title_up for x in ["英文", "ENGLISH"]): return 3
            return 10
        if "台灣" in group_type or "台湾" in group_type:
            if any(x in title for x in ["新闻", "新聞"]): return 1
            if any(x in title for x in ["综合", "綜合"]): return 2
            if any(x in title for x in ["娱乐", "娛樂"]): return 3
            return 10
        return 0

    def check_url_speed(self, item, group_name):
        try:
            start = time.time()
            with requests.get(item['url'], headers=HEADERS, timeout=TIMEOUT, stream=True) as r:
                if r.status_code == 200:
                    for _ in r.iter_content(chunk_size=1024): break
                    return {**item, "speed": time.time() - start, "weight": self.get_weight(item['title'], group_name)}
        except: pass
        return None

    def speedTestSelectedGroups(self):
        for g_name in list(self.finalGroups.keys()):
            channels = self.finalGroups[g_name]
            if g_name in SPEED_TEST_GROUPS:
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    results = list(executor.map(lambda x: self.check_url_speed(x, g_name), channels))
                valid = sorted([r for r in results if r], key=lambda x: (x['weight'], x['speed']))
                for i in valid: i.pop('speed', None); i.pop('weight', None)
                self.finalGroups[g_name] = valid
            elif "台灣" in g_name:
                # 台湾不测速，但按关键字权重物理排序
                channels.sort(key=lambda x: self.get_weight(x['title'], g_name))
                self.finalGroups[g_name] = channels

    def processCCTVChannels(self):
        cctv = []
        for channels in self.parsedData.values():
            for ch in channels:
                clean = self.cleanTitle(ch["title"])
                if clean.upper().startswith("CCTV"):
                    cctv.append({"title": clean, "url": ch["url"]})
        if cctv: self.finalGroups["央视,#genre#"] = cctv

    def processMainlandChina(self):
        key = "中國大陸,#genre#"
        if key not in self.parsedData: return
        satellite = []
        for ch in self.parsedData[key]:
            clean = self.cleanTitle(ch["title"])
            if "卫视" in clean and not clean.upper().startswith("CCTV"):
                satellite.append({"title": clean, "url": ch["url"]})
        if satellite: self.finalGroups["卫视,#genre#"] = satellite

    def processHongKong(self):
        key = "香港,#genre#"
        if key not in self.parsedData: return
        self.finalGroups["香港,#genre#"] = [{"title": self.cleanTitle(ch["title"]), "url": ch["url"]} for ch in self.parsedData[key]]

    def processTaiwan(self):
        key = "台灣,#genre#"
        if key not in self.parsedData: return
        self.finalGroups["台灣,#genre#"] = [{"title": self.cleanTitle(ch["title"]), "url": ch["url"]} for ch in self.parsedData[key]]

    def processProvinceFromMainland(self):
        key = "中國大陸,#genre#"
        if key not in self.parsedData: return
        used = set()
        for g in ["央视,#genre#", "卫视,#genre#"]:
            if g in self.finalGroups:
                for c in self.finalGroups[g]: used.add(c["title"])
        province_map = {"北京":["北京"],"上海":["上海"],"广东":["广东","广州","深圳"],"浙江":["浙江","杭州","宁波"],"江苏":["江苏","南京","苏州"],"湖南":["湖南","长沙"]}
        province_groups = defaultdict(list)
        for ch in self.parsedData[key]:
            clean = self.cleanTitle(ch["title"])
            if clean in used or clean.upper().startswith("CCTV") or "卫视" in clean: continue
            found = False
            for p, keys in province_map.items():
                if any(k in clean for k in keys):
                    province_groups[p].append({"title": clean, "url": ch["url"]})
                    found = True; break
            if not found: province_groups["其他省份"].append({"title": clean, "url": ch["url"]})
        for p in province_map:
            if province_groups[p]: self.finalGroups[f"{p},#genre#"] = province_groups[p]

    def outputResult(self):
        order = ["央视,#genre#", "卫视,#genre#", "香港,#genre#", "台灣,#genre#"]
        lines = []
        for g in order:
            if g in self.finalGroups:
                lines.append(g)
                for ch in self.finalGroups[g]: lines.append(f"{ch['title']},{ch['url']}")
                lines.append("")
        for g, chans in self.finalGroups.items():
            if g not in order:
                lines.append(g)
                for ch in chans: lines.append(f"{ch['title']},{ch['url']}")
                lines.append("")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines).rstrip() + "\n")

if __name__ == "__main__":
    LiveStreamCrawler()
