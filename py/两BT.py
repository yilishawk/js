# -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    def getName(self):
        return "两个BT[修复版]"

    def init(self, extend=""):
        self.host = "https://www.bttwo.org"
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        self.base_headers = {
            "User-Agent": self.ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": "myannoun=1"
        }
        self.session = requests.Session()
        self.session.headers.update(self.base_headers)
        self.session.verify = False
        self._domain_inited = False
        self._ensure_domain()

    def _ensure_domain(self):
        if self._domain_inited:
            return
        print(f"[INIT] 开始初始化域名: {self.host}")
        try:
            resp = self.session.get(self.host, timeout=8)
            if resp.status_code == 200:
                self._update_headers_referer()
                self._domain_inited = True
                return
        except Exception as e:
            print(f"[INIT] 当前域名不可用: {e}")

        publish_url = "https://www.bttwo.vip/"
        try:
            p_resp = self.session.get(publish_url, timeout=8)
            p_resp.encoding = "utf-8"
            match = re.search(r'href="(https?://www\.bttwo\.[a-z]+)"', p_resp.text)
            if match:
                new_host = match.group(1).rstrip('/')
                self.host = new_host
                self._update_headers_referer()
                test_resp = self.session.get(self.host, timeout=8)
                if test_resp.status_code == 200:
                    self._domain_inited = True
        except Exception as e:
            print(f"[INIT] 获取发布页失败: {e}")

    def _update_headers_referer(self):
        self.session.headers.update({"Referer": self.host + "/"})

    def homeContent(self, filter):
        classes = [
            {"type_name": "国产剧", "type_id": "zgjun"},
            {"type_name": "电影", "type_id": "new-movie"},
            {"type_name": "美剧", "type_id": "meiju"},
            {"type_name": "日韩剧", "type_id": "jpsrtv"}
        ]
        return {"class": classes, "filters": {}}

    def categoryContent(self, tid, pg, filter, extend):
        self._ensure_domain()
        if int(pg) == 1:
            url = f"{self.host}/{tid}"
        else:
            url = f"{self.host}/{tid}/page/{pg}"

        try:
            resp = self.session.get(url, timeout=12)
            if resp.status_code != 200:
                return {"list": [], "page": int(pg), "pagecount": 0, "limit": 20, "total": 0}
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select("div.bt_img ul li")
            if not items:
                items = soup.select("ul.movie_list li")
            if not items:
                items = soup.select(".list_box li")
            if not items:
                items = soup.select("div.item")

            video_list = []
            for li in items:
                a_tag = li.find("a")
                if not a_tag:
                    continue
                href = a_tag.get("href")
                full_url = urljoin(self.host, href)
                img_tag = a_tag.find("img")
                pic_url = ""
                if img_tag:
                    pic_url = img_tag.get("data-original") or img_tag.get("src") or ""
                remark_tag = li.select_one(".jidi span") or li.select_one(".remarks")
                remark = remark_tag.get_text(strip=True) if remark_tag else ""
                name = img_tag.get("alt", "") if img_tag else a_tag.get_text(strip=True)
                if not name:
                    name = "未知影片"
                video_list.append({
                    "vod_id": full_url,
                    "vod_name": name,
                    "vod_pic": pic_url,
                    "vod_remarks": remark
                })
            return {"list": video_list, "page": int(pg), "pagecount": 99, "limit": 20, "total": 9999}
        except Exception as e:
            print(f"[CATEGORY] 异常: {e}")
            return {"list": [], "page": int(pg), "pagecount": 0, "limit": 0, "total": 0}

    def detailContent(self, array):
        url = array[0] if array else ""
        if not url:
            return {"list": []}
        self._ensure_domain()

        try:
            resp = self.session.get(url, timeout=12)
            if resp.status_code != 200:
                return {"list": []}
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            title_tag = soup.select_one("h1")
            vod_name = title_tag.get_text(strip=True) if title_tag else ""
            pic_tag = soup.select_one(".dyimg img")
            vod_pic = pic_tag.get("src") if pic_tag else ""
            desc_tag = soup.select_one(".yp_context")
            vod_content = desc_tag.get_text(strip=True) if desc_tag else ""

            vod = {
                "vod_id": url,
                "vod_name": vod_name,
                "vod_pic": vod_pic,
                "vod_content": vod_content
            }
            info_items = soup.select(".moviedteail_list li")
            for li in info_items:
                text = li.get_text(strip=True)
                if "类型：" in text:
                    vod["type_name"] = text.replace("类型：", "").strip()
                elif "地区：" in text:
                    vod["vod_area"] = text.replace("地区：", "").strip()
                elif "年份：" in text:
                    vod["vod_year"] = text.replace("年份：", "").strip()
                elif "导演：" in text:
                    vod["vod_director"] = text.replace("导演：", "").strip()
                elif "主演：" in text:
                    vod["vod_actor"] = text.replace("主演：", "").strip()
                elif "语言：" in text:
                    vod["vod_language"] = text.replace("语言：", "").strip()

            if "情色" in vod.get("type_name", ""):
                vod["vod_play_from"] = "温馨提示"
                vod["vod_play_url"] = "内容敏感，暂不提供播放$#"
            else:
                play_links = []
                play_btns = soup.select(".paly_list_btn a")
                if not play_btns:
                    play_btns = soup.select(".downurl a")
                for a in play_btns:
                    name = a.get_text(strip=True)
                    href = urljoin(self.host, a.get("href"))
                    play_links.append(f"{name}${href}")
                if play_links:
                    vod["vod_play_from"] = "两个BT"
                    vod["vod_play_url"] = "#".join(play_links)
                else:
                    vod["vod_play_from"] = "暂无资源"
                    vod["vod_play_url"] = ""

            return {"list": [vod]}
        except Exception as e:
            print(f"[DETAIL] 异常: {e}")
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        self._ensure_domain()
        search_url = f"{self.host}/xsssearch?q={quote(key)}"
        try:
            old_referer = self.session.headers.get("Referer")
            self.session.headers.update({"Referer": self.host + "/xsssearch"})
            resp = self.session.get(search_url, timeout=12)
            if old_referer:
                self.session.headers.update({"Referer": old_referer})
            else:
                self.session.headers.pop("Referer", None)

            if resp.status_code != 200:
                return {"list": [], "page": int(pg)}
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select("ul li")
            valid_items = []
            for li in items:
                a = li.select_one("h3.dytit a") or li.find("a")
                if a and "/movie/" in a.get("href", ""):
                    valid_items.append(li)
            if not valid_items:
                return {"list": [], "page": int(pg)}

            target = valid_items[0]
            title_a = target.select_one("h3.dytit a") or target.find("a")
            img = target.find("img")
            remark = target.select_one(".jidi span")
            remark_text = remark.get_text(strip=True) if remark else ""

            video_list = [{
                "vod_id": urljoin(self.host, title_a.get("href")),
                "vod_name": title_a.get_text(strip=True),
                "vod_pic": img.get("data-original") or img.get("src", "") if img else "",
                "vod_remarks": remark_text
            }]
            return {"list": video_list, "page": int(pg)}
        except Exception as e:
            print(f"[SEARCH] 异常: {e}")
            return {"list": [], "page": int(pg)}

    def playerContent(self, flag, id, vipFlags):
        play_headers = {
            "User-Agent": self.ua,
            "Origin": self.host.rstrip('/'),
            "Referer": ""
        }
        try:
            resp = self.session.get(id, timeout=12)
            if resp.status_code != 200:
                return {"parse": 1, "url": id, "header": play_headers}
            resp.encoding = "utf-8"
            html = resp.text

            patterns = [
                r'fetch\s*\(\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'url\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'video\s*:\s*\{\s*url\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'loadSource\s*\(\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'src\s*:\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
                r'(https?://[^\s"\']+\.m3u8[^\s"\']*)'
            ]
            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    m3u8_url = match.group(1)
                    if m3u8_url.startswith('/'):
                        m3u8_url = self.host + m3u8_url
                    m3u8_url = m3u8_url.replace('\\/', '/')
                    return {"parse": 0, "url": m3u8_url, "header": play_headers}
            return {"parse": 1, "url": id, "header": play_headers}
        except Exception as e:
            print(f"[PLAYER] 异常: {e}")
            return {"parse": 1, "url": id, "header": play_headers}

    def localProxy(self, param):
        return [200, "video/MP2T", ""]