# -*- coding: utf-8 -*-
import requests
import re
import json
import base64
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote
from base.spider import Spider as BaseSpider

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Spider(BaseSpider):
    def getName(self):
        return "独播库[全功能筛选版]"

    def init(self, extend=""):
        self.host = "https://www.dbku.tv"
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Referer": self.host + "/",
        }
        self.session = requests.Session()
        self.session.headers.update(self.header)
        self.session.verify = False

    def homeContent(self, filter):
        classes = [
            {"type_name": "陆剧", "type_id": "13"},
            {"type_name": "电视剧", "type_id": "2"},
            {"type_name": "电影", "type_id": "1"},
            {"type_name": "综艺", "type_id": "3"},
            {"type_name": "动漫", "type_id": "4"},
            {"type_name": "日韩剧", "type_id": "15"},
            {"type_name": "短剧", "type_id": "21"},
            {"type_name": "台泰剧", "type_id": "14"},
            {"type_name": "港剧", "type_id": "20"}
        ]
        
        tv_filter = [
            {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "悬疑", "v": "悬疑"}, {"n": "武侠", "v": "武侠"}, {"n": "科幻", "v": "科幻"}, {"n": "都市", "v": "都市"}, {"n": "爱情", "v": "爱情"}, {"n": "古装", "v": "古装"}, {"n": "战争", "v": "战争"}, {"n": "青春", "v": "青春"}, {"n": "偶像", "v": "偶像"}, {"n": "喜剧", "v": "喜剧"}, {"n": "家庭", "v": "家庭"}, {"n": "奇幻", "v": "奇幻"}, {"n": "剧情", "v": "剧情"}, {"n": "乡村", "v": "乡村"}, {"n": "年代", "v": "年代"}, {"n": "警匪", "v": "警匪"}, {"n": "谍战", "v": "谍战"}, {"n": "历险", "v": "历险"}, {"n": "罪案", "v": "罪案"}, {"n": "宫廷", "v": "宫廷"}, {"n": "经典", "v": "经典"}, {"n": "动作", "v": "动作"}, {"n": "惊悚", "v": "惊悚"}, {"n": "历史", "v": "历史"}, {"n": "穿越", "v": "穿越"}, {"n": "同性", "v": "同性"}]},
            {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"}, {"n": "韩国", "v": "韩国"}, {"n": "日本", "v": "日本"}, {"n": "新加坡", "v": "新加坡"}, {"n": "泰国", "v": "泰国"}]},
            {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "更早", "v": "更早"}]},
            {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "粤语", "v": "粤语"}, {"n": "韩语", "v": "韩语"}, {"n": "泰语", "v": "泰语"}, {"n": "日语", "v": "日语"}]},
            {"key": "by", "name": "排序", "value": [{"n": "时间", "v": "time"}, {"n": "人气", "v": "hits"}, {"n": "评分", "v": "score"}]}
        ]
        
        movie_filter = [
            {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "喜剧", "v": "喜剧"}, {"n": "爱情", "v": "爱情"}, {"n": "恐怖", "v": "恐怖"}, {"n": "动作", "v": "动作"}, {"n": "科幻", "v": "科幻"}, {"n": "剧情", "v": "剧情"}, {"n": "警匪", "v": "警匪"}, {"n": "战争", "v": "战争"}, {"n": "犯罪", "v": "犯罪"}, {"n": "动画", "v": "动画"}, {"n": "奇幻", "v": "奇幻"}, {"n": "武侠", "v": "武侠"}, {"n": "冒险", "v": "冒险"}, {"n": "悬疑", "v": "悬疑"}, {"n": "惊悚", "v": "惊悚"}, {"n": "古装", "v": "古装"}, {"n": "同性", "v": "同性"}]},
            {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"}, {"n": "韩国", "v": "韩国"}, {"n": "英国", "v": "英国"}, {"n": "法国", "v": "法国"}, {"n": "加拿大", "v": "加拿大"}, {"n": "澳大利亚", "v": "澳大利亚"}]},
            {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}]},
            {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "粤语", "v": "粤语"}, {"n": "韩语", "v": "韩语"}, {"n": "英语", "v": "英语"}, {"n": "法语", "v": "法语"}]},
            {"key": "by", "name": "排序", "value": [{"n": "时间", "v": "time"}, {"n": "人气", "v": "hits"}, {"n": "评分", "v": "score"}]}
        ]

        filters = {}
        for c in classes:
            if c['type_id'] in ["1", "4"]:
                filters[c['type_id']] = movie_filter
            else:
                filters[c['type_id']] = tv_filter
                
        return {"class": classes, "filters": filters}

    def categoryContent(self, tid, pg, filter, extend):
        if extend is None:
            extend = {}
        params = {
            "area": extend.get("area", ""),
            "by": extend.get("by", "time"),
            "class": extend.get("class", ""),
            "lang": extend.get("lang", ""),
            "year": extend.get("year", ""),
        }
        
        url = "{}/vodshow/{}-{}-{}-{}-{}-{}---{}---{}.html".format(
            self.host,
            tid,
            quote(params["area"]),
            params["by"],
            quote(params["class"]),
            quote(params["lang"]),
            "",
            pg,
            params["year"]
        )
        
        try:
            res = self.session.get(url, timeout=10)
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            video_list = []
            for li in soup.select("ul.myui-vodlist li"):
                a = li.select_one("a.myui-vodlist__thumb")
                if not a:
                    continue
                video_list.append({
                    "vod_id": a.get("href"),
                    "vod_name": a.get("title"),
                    "vod_pic": a.get("data-original"),
                    "vod_remarks": li.select_one(".pic-text").get_text(strip=True) if li.select_one(".pic-text") else ""
                })
            return {"list": video_list, "page": int(pg), "pagecount": 99, "limit": 48, "total": 9999}
        except:
            return {"list": [], "page": int(pg), "pagecount": 1, "limit": 48, "total": 0}

    def detailContent(self, array):
        url = self.host + array[0] if not array[0].startswith("http") else array[0]
        try:
            res = self.session.get(url, timeout=10)
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            detail = soup.select_one(".myui-content__detail")
            vod = {
                "vod_id": array[0],
                "vod_name": detail.select_one("h1.title").get_text(strip=True),
                "vod_pic": soup.select_one(".myui-content__thumb img")["data-original"],
                "vod_content": soup.select_one(".sketch.content").get_text(strip=True) if soup.select_one(".sketch.content") else "",
                "vod_play_from": "独播库",
            }
            for p in detail.select("p.data"):
                t = p.get_text(strip=True)
                if "导演：" in t:
                    vod["vod_director"] = t.replace("导演：", "")
                elif "主演：" in t:
                    vod["vod_actor"] = " / ".join([a.get_text(strip=True) for a in p.select("a")])
                elif "分类：" in t:
                    a_tags = p.select("a")
                    if len(a_tags) > 0:
                        vod["type_name"] = a_tags[0].get_text(strip=True)
                    if len(a_tags) > 1:
                        vod["vod_area"] = a_tags[1].get_text(strip=True)
                    if len(a_tags) > 2:
                        vod["vod_year"] = a_tags[2].get_text(strip=True)
                elif "更新：" in t:
                    vod["vod_remarks"] = t.replace("更新：", "")

            play_urls = [f"{a.get_text(strip=True)}${a.get('href')}" for a in soup.select(".myui-content__list li a")]
            vod["vod_play_url"] = "#".join(play_urls)
            return {"list": [vod]}
        except:
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/vodsearch/-------------.html?wd={quote(key)}"
        try:
            res = self.session.get(url, timeout=10)
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            video_list = []
            for li in soup.select("#searchList li"):
                a = li.select_one("a.myui-vodlist__thumb")
                if not a:
                    continue
                video_list.append({
                    "vod_id": a.get("href"),
                    "vod_name": a.get("title"),
                    "vod_pic": a.get("data-original"),
                    "vod_remarks": a.select_one(".tag").get_text(strip=True) if a.select_one(".tag") else ""
                })
            return {"list": video_list, "page": int(pg)}
        except:
            return {"list": [], "page": int(pg)}

    def playerContent(self, flag, id, vipFlags):
        url = self.host + id if not id.startswith("http") else id
        try:
            res = self.session.get(url, timeout=10)
            match = re.search(r'"url"\s*:\s*"([^"]+)"', res.text)
            if match:
                enc_url = match.group(1)
                missing_padding = len(enc_url) % 4
                if missing_padding:
                    enc_url += '=' * (4 - missing_padding)
                real_url = unquote(base64.b64decode(enc_url).decode("utf-8"))
                return {"parse": 0, "url": real_url, "header": {"User-Agent": self.header["User-Agent"], "Referer": self.host}}
            return {"parse": 1, "url": url}
        except:
            return {"parse": 1, "url": url}