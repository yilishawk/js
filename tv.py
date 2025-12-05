#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终版：央视/卫视/香港/台灣 100% 保留你最初代码逻辑
仅将「中国大陆」组中非央视、非卫视的频道按省份重新归类
"""

import re
import requests
from collections import defaultdict, OrderedDict

URL = "https://freetv.fun/test_channels_new.txt"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BLACKLIST = {"https://stream1.freetv.fun/tang-he-yi-tao-1.m3u8"}

# 简繁快速转换（足够用，不依赖 opencc）
def ts(t):
    rep = {
        "臺":"台","衛":"卫","視":"视","頻":"频","廣":"广","東":"东",
        "鳳":"凤","凰":"凰","資":"资","訊":"讯","綜":"综","藝":"艺",
        "劇":"剧","無線":"无线","翡翠":"翡翠","緯來":"纬来"
    }
    for a,b in rep.items(): t = t.replace(a,b)
    return t.strip()

class LiveStreamCrawler:
    def __init__(self):
        self.rawContent = ""
        self.parsedData = defaultdict(list)
        self.finalGroups = OrderedDict()

        self.fetchData()
        self.parseData()

        # 下面这四行是你最初的代码，完全不动！
        self.processCCTVChannels()
        self.processMainlandChina()   # 只提取卫视
        self.processHongKong()
        self.processTaiwan()

        # 新增：把中国大陆剩下的频道按省份归类
        self.processProvinceFromMainland()

        self.outputResult()

    # ==================== 你最初的代码，原样保留 ====================
    def fetchData(self):
        r = requests.get(URL, headers=HEADERS, timeout=30)
        r.raise_for_status()
        self.rawContent = r.text

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
                title, url = line.split(",", 1)
                title = title.strip()
                url = url.strip()
                if url in BLACKLIST: continue
                self.parsedData[currentGroup].append({
                    "title": title,
                    "url": url,
                    "original_title": title
                })

    def cleanTitle(self, title):
        patterns = [
            r'\s*\(backup\)', r'\s*\(h265\)', r'\s*\(h264\)',
            r'\s*\(备用\)', r'\s*\(备\)', r'\s*\[.*?\]', r'\s*#\d+'
        ]
        for p in patterns:
            title = re.sub(p, '', title, flags=re.I)
        return ts(title).strip()

    def getCCTVWeight(self, title):
        cleanTitle = self.cleanTitle(title)
        m = re.match(r'^CCTV[-\s]?(\d+)', cleanTitle, re.I)
        if m: return int(m.group(1))
        special = {
            "CCTV 8K":100, "CCTV-Documentary":101, "CCTV-戲曲":102,
            "CCTV第一劇場":103, "CCTV風雲足球":104, "CCTV第一剧场":103, "CCTV风云足球":104,
        }
        for k,v in special.items():
            if cleanTitle.startswith(k): return v
        if cleanTitle.startswith("CCTV"): return 999
        return 1000

    def processCCTVChannels(self):
        allCCTV = {}
        for channels in self.parsedData.values():
            for ch in channels:
                clean = self.cleanTitle(ch["title"])
                if clean.startswith("CCTV"):
                    key = f"{clean}|{ch['url']}"
                    if key not in allCCTV:
                        weight = self.getCCTVWeight(ch["title"])
                        allCCTV[key] = {"title": clean, "url": ch["url"], "weight": weight}
        cctv_list = sorted(allCCTV.values(), key=lambda x: (x["weight"], x["title"]))
        if cctv_list:
            self.finalGroups["央视,#genre#"] = [{"title": c["title"], "url": c["url"]} for c in cctv_list]

    def processMainlandChina(self):
        key = "中國大陸,#genre#"
        if key not in self.parsedData: return
        channels = self.parsedData[key]
        satelliteGroup = []
        cctv_titles = {c["title"] for c in self.finalGroups.get("央视,#genre#", [])}
        for ch in channels:
            clean = self.cleanTitle(ch["title"])
            if clean in cctv_titles: continue
            if "衛視" in clean or "卫视" in clean:
                satelliteGroup.append({"title": clean, "url": ch["url"]})
        if satelliteGroup:
            self.finalGroups["卫视,#genre#"] = satelliteGroup

    def processHongKong(self):
        key = "香港,#genre#"
        if key not in self.parsedData: return
        channels = self.parsedData[key]
        phoenix = []
        others = []
        for ch in channels:
            clean = self.cleanTitle(ch["title"])
            item = {"title": clean, "url": ch["url"]}
            if any(x in clean for x in ["鳳凰衛視中文", "鳳凰資訊", "凤凰卫视中文", "凤凰资讯"]):
                phoenix.append(item)
            else:
                others.append(item)
        final_hk = phoenix + others
        if final_hk:
            self.finalGroups["香港,#genre#"] = final_hk

    def processTaiwan(self):
        key = "台灣,#genre#"
        if key not in self.parsedData: return
        channels = self.parsedData[key]
        priority = []
        others = []
        for ch in channels:
            clean = self.cleanTitle(ch["title"])
            item = {"title": clean, "url": ch["url"]}
            if any(k in clean for k in ["新聞", "綜合", "娛樂", "新闻", "综合", "娱乐"]):
                priority.append(item)
            else:
                others.append(item)
        final_tw = priority + others
        if final_tw:
            self.finalGroups["台灣,#genre#"] = final_tw

    # ==================== 新增：只处理剩下的地方台，按省份归类 ====================
    def processProvinceFromMainland(self):
        key = "中國大陸,#genre#"
        if key not in self.parsedData: return

        # 已使用的标题（央视 + 卫视）
        used = set()
        for g in ["央视,#genre#", "卫视,#genre#"]:
            for c in self.finalGroups.get(g, []):
                used.add(self.cleanTitle(c["title"]))

        province_map = {
            "北京":["北京"],"上海":["上海"],"重庆":["重庆"],"天津":["天津"],
            "广东":["广东","廣東","广州","廣州","深圳","东莞","東莞","佛山","珠海","惠州","中山","江门","汕头","湛江"],
            "浙江":["浙江","杭州","宁波","寧波","温州","溫州","嘉兴","绍兴","金华","台州"],
            "江苏":["江苏","江蘇","南京","苏州","蘇州","无锡","無錫","常州","南通","扬州","镇江"],
            "山东":["山东","山東","济南","濟南","青岛","青島","烟台","潍坊"],
            "四川":["四川","成都","绵阳","德阳","南充"],
            "陕西":["陕西","陝西","西安","咸阳","宝鸡"],
            "湖北":["湖北","武汉","武漢","宜昌","襄阳"],
            "湖南":["湖南","长沙","長沙","株洲","湘潭","岳阳"],
            "河南":["河南","郑州","鄭州","洛阳"],
            "福建":["福建","福州","厦门","廈門","泉州"],
            "安徽":["安徽","合肥","芜湖"],
            "江西":["江西","南昌","赣州"],
            "河北":["河北","石家庄","唐山"],
            "黑龙江":["黑龙江","黑龍江","哈尔滨","哈爾濱"],
            "辽宁":["辽宁","遼寧","沈阳","瀋陽","大连"],
            "广西":["广西","廣西","南宁","南寧"],
            "云南":["云南","雲南","昆明"],
        }

        province_groups = defaultdict(list)
        for ch in self.parsedData[key]:
            clean = self.cleanTitle(ch["title"])
            if clean in used: continue
            if clean.startswith("CCTV"): continue
            if "卫视" in clean or "衛視" in clean: continue

            found = False
            for province, keys in province_map.items():
                if any(k in clean for k in keys):
                    province_groups[province].append({"title": clean, "url": ch["url"]})
                    found = True
                    break
            if not found:
                province_groups["其他省份"].append({"title": clean, "url": ch["url"]})

        # 按你喜欢的顺序输出
        order = ["北京","上海","广东","浙江","江苏","湖南","山东","四川","陕西","湖北","河南","福建","安徽","江西","河北","黑龙江","辽宁","广西","云南","重庆","天津"]
        for p in order:
            if province_groups[p]:
                self.finalGroups[f"{p},#genre#"] = province_groups[p]
        for p in sorted(province_groups):
            if p not in order:
                self.finalGroups[f"{p},#genre#"] = province_groups[p]

    # ==================== 输出顺序完全按你要求 ====================
    def outputResult(self):
        ordered = ["央视,#genre#", "卫视,#genre#", "香港,#genre#", "台灣,#genre#"]
        lines = []

        for g in ordered:
            if g in self.finalGroups and self.finalGroups[g]:
                lines.append(g)
                for ch in self.finalGroups[g]:
                    lines.append(f"{ch['title']},{ch['url']}")
                lines.append("")

        # 省份组
        for g in self.finalGroups:
            if g not in ordered and g.endswith(",#genre#"):
                lines.append(g)
                for ch in self.finalGroups[g]:
                    lines.append(f"{ch['title']},{ch['url']}")
                lines.append("")

        result = "\n".join(lines).rstrip() + "\n"
        print(result)
        with open("tv.txt", "w", encoding="utf-8") as f:
            f.write(result)

if __name__ == "__main__":
    LiveStreamCrawler()
