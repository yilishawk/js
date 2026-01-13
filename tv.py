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
            print(f"无法获取源数据: {e}")

    def parseData(self):
        currentGroup = ""
        for line in self.rawContent.splitlines():
            line = line.strip()
            if not line: continue
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
        title = re.sub(r'CCTV-?1\(RTHK33\)', 'CCTV1', title, flags=re.I)
        patterns = [r'\s*\(backup\)', r'\s*\(h265\)', r'\s*\(h264\)', r'\s*\(备用\)', r'\s*\(备\)', r'\s*\[.*?\]', r'\s*#\d+']
        for p in patterns: title = re.sub(p, '', title, flags=re.I)
        title = ts(title)
        if title.upper().startswith("CCTV"):
            title = title.replace("-", "").replace(" ", "")
        return title.strip()

    def get_weight(self, title, group_type):
        """根据分组类型计算标题权重"""
        title_upper = title.upper()
        
        if group_type == "CCTV":
            m = re.search(r'CCTV(\d+)', title_upper)
            if m: return int(m.group(1))
            special = {"CCTV8K":100, "CCTVDOCUMENTARY":101, "CCTV戲曲":102, "CCTV第一劇場":103, "CCTV风云足球":104}
            for k,v in special.items():
                if k in title_upper: return v
            return 999

        elif group_type == "HK":
            # 香港排序逻辑：凤凰 > 中文 > 英文
            if "凤凰" in title or "鳳凰" in title: return 1
            if "中文" in title: return 2
            if "英文" in title or "ENGLISH" in title_upper: return 3
            return 10

        elif group_type == "TW":
            # 台湾排序逻辑：新闻 > 综合 > 娱乐
            if "新闻" in title or "新聞" in title: return 1
            if "综合" in title or "綜合" in title: return 2
            if "娱乐" in title or "娛樂" in title: return 3
            return 10
            
        return 0

    def check_url_speed(self, item, group_type):
        try:
            start = time.time()
            with requests.get(item['url'], headers=HEADERS, timeout=TIMEOUT, stream=True) as r:
                if r.status_code == 200:
                    for _ in r.iter_content(chunk_size=1024):
                        break
                    duration = time.time() - start
                    return {**item, "speed": duration, "weight": self.get_weight(item['title'], group_type)}
        except:
            pass
        return None

    def speedTestSelectedGroups(self):
        print("开始分类测速排序...")
        for group_name in list(self.finalGroups.keys()):
            channels = self.finalGroups[group_name]
            if not channels: continue
            
            if group_name in SPEED_TEST_GROUPS:
                # 确定当前分组属于哪种排序逻辑
                g_type = "CCTV" if "央视" in group_name else ("HK" if "香港" in group_name else "OTHER")
                
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    # 将 g_type 传入测速函数
                    results = list(executor.map(lambda x: self.check_url_speed(x, g_type), channels))
                
                # 双重排序：权重升序，同权重内速度升序
                valid_sorted = sorted([r for r in results if r], key=lambda x: (x['weight'], x['speed']))
                for item in valid_sorted: 
                    item.pop('speed', None)
                    item.pop('weight', None)
                self.finalGroups[group_name] = valid_sorted

    def processCCTVChannels(self):
        cctv_list = []
        for channels in self.parsedData.values():
            for ch in channels:
                clean = self.cleanTitle(ch["title"])
                if clean.upper().startswith("CCTV"):
                    cctv_list.append({"title": clean, "url": ch["url"]})
        if cctv_list: self.finalGroups["央视,#genre#"] = cctv_list

    def processMainlandChina(self):
        key = "中國大陸,#genre#"
        if key not in self.parsedData: return
        satelliteGroup = []
        for ch in self.parsedData[key]:
            clean = self.cleanTitle(ch["title"])
            if "卫视" in clean and not clean.upper().startswith("CCTV"):
                satelliteGroup.append({"title": clean, "url": ch["url"]})
        if satelliteGroup: self.finalGroups["卫视,#genre#"] = satelliteGroup

    def processHongKong(self):
        key = "香港,#genre#"
        if key not in self.parsedData: return
        self.finalGroups["香港,#genre#"] = [{"title": self.cleanTitle(ch["title"]), "url": ch["url"]} for ch in self.parsedData[key]]

    def processTaiwan(self):
        key = "台灣,#genre#"
        if key not in self.parsedData: return
        # 台湾分组不参与 SPEED_TEST_GROUPS 测速，但我们手动处理它的排序
        channels = [{"title": self.cleanTitle(ch["title"]), "url": ch["url"]} for ch in self.parsedData[key]]
        # 按照 新闻 > 综合 > 娱乐 排序
        channels.sort(key=lambda x: self.get_weight(x['title'], "TW"))
        self.finalGroups["台灣,#genre#"] = channels

    def processProvinceFromMainland(self):
        key = "中國大陸,#genre#"
        if key not in self.parsedData: return
        used = set()
        for g in ["央视,#genre#", "卫视,#genre#"]:
            for c in self.finalGroups.get(g, []): used.add(c["title"])
        
        province_map = {"北京":["北京"],"上海":["上海"],"广东":["广东","广州","深圳"],"浙江":["浙江","杭州","宁波"],"江苏":["江苏","南京","苏州"],"湖南":["湖南","长沙"]}
        province_groups = defaultdict(list)
        for ch in self.parsedData[key]:
            clean = self.cleanTitle(ch["title"])
            if clean in used or clean.upper().startswith("CCTV") or "卫视" in clean: continue
            found = False
            for province, keys in province_map.items():
                if any(k in clean for k in keys):
                    province_groups[province].append({"title": clean, "url": ch["url"]})
                    found = True; break
            if not found: province_groups["其他省份"].append({"title": clean, "url": ch["url"]})
        for p in province_map:
            if province_groups[p]: self.finalGroups[f"{p},#genre#"] = province_groups[p]

    def outputResult(self):
        ordered_top = ["央视,#genre#", "卫视,#genre#", "香港,#genre#", "台灣,#genre#"]
        lines = []
        for g in ordered_top:
            if g in self.finalGroups and self.finalGroups[g]:
                lines.append(g)
                for ch in self.finalGroups[g]: lines.append(f"{ch['title']},{ch['url']}")
                lines.append("")
        for g, channels in self.finalGroups.items():
            if g not in ordered_top and channels:
                lines.append(g)
                for ch in channels: lines.append(f"{ch['title']},{ch['url']}")
                lines.append("")
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines).rstrip() + "\n")

if __name__ == "__main__":
    LiveStreamCrawler()
