# -*- coding: utf-8 -*-
import requests
import re
import json
from bs4 import BeautifulSoup
from base.spider import Spider as BaseSpider

requests.packages.urllib3.disable_warnings()

class Spider(BaseSpider):
    def getName(self):
        return "WWGZ影视"

    def init(self, extend=""):
        self.host = "https://vip.wwgz.cn:5200"
        self.header = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate"
        }
        self.api_host = "https://api.wwgz.cn:520"
        self.session = requests.Session()
        self.session.headers.update(self.header)
        self.session.verify = False

    def homeContent(self, filter):
        classes = [
            {"type_name": "国产剧", "type_id": "12"},
            {"type_name": "电影", "type_id": "1"},
            {"type_name": "电视剧", "type_id": "2"},
            {"type_name": "综艺", "type_id": "3"},
            {"type_name": "短剧", "type_id": "26"}
        ]
        area_options = [{"n": "全部", "v": ""}]
        for area in ["大陆", "香港", "台湾", "美国", "日本", "韩国", "英国", "法国", "泰国", "新加坡", "马来西亚", "印度", "加拿大", "西班牙", "俄罗斯", "其它"]:
            area_options.append({"n": area, "v": area})
        year_options = [{"n": "全部", "v": "0"}]
        for y in range(2025, 2004, -1):
            year_options.append({"n": str(y), "v": str(y)})
        order_options = [
            {"n": "最新", "v": "time"},
            {"n": "最热", "v": "hits"},
            {"n": "评分", "v": "score"}
        ]
        movie_type = [{"n": "全部", "v": "0"}]
        for t, v in [("动作片", "5"), ("喜剧片", "6"), ("爱情片", "7"), ("科幻片", "8"),
                     ("恐怖片", "9"), ("剧情片", "10"), ("战争片", "11"), ("惊悚片", "16"), ("奇幻片", "17")]:
            movie_type.append({"n": t, "v": v})
        tv_type = [{"n": "全部", "v": "0"}]
        for t, v in [("国产剧", "12"), ("港台泰", "13"), ("日韩剧", "14"), ("欧美剧", "15")]:
            tv_type.append({"n": t, "v": v})
        variety_type = [{"n": "全部", "v": "0"}]
        short_type = [{"n": "全部", "v": "0"}]
        filters = {
            "1": [
                {"key": "class", "name": "类型", "value": movie_type},
                {"key": "area", "name": "地区", "value": area_options},
                {"key": "year", "name": "年份", "value": year_options},
                {"key": "order", "name": "排序", "value": order_options}
            ],
            "12": [
                {"key": "area", "name": "地区", "value": area_options},
                {"key": "year", "name": "年份", "value": year_options},
                {"key": "order", "name": "排序", "value": order_options}
            ],
            "2": [
                {"key": "class", "name": "类型", "value": tv_type},
                {"key": "area", "name": "地区", "value": area_options},
                {"key": "year", "name": "年份", "value": year_options},
                {"key": "order", "name": "排序", "value": order_options}
            ],
            "3": [
                {"key": "class", "name": "类型", "value": variety_type},
                {"key": "area", "name": "地区", "value": area_options},
                {"key": "year", "name": "年份", "value": year_options},
                {"key": "order", "name": "排序", "value": order_options}
            ],
            "26": [
                {"key": "class", "name": "类型", "value": short_type},
                {"key": "area", "name": "地区", "value": area_options},
                {"key": "year", "name": "年份", "value": year_options},
                {"key": "order", "name": "排序", "value": order_options}
            ]
        }
        return {"class": classes, "filters": filters}

    def _get_total_pages(self, soup):
        page_links = soup.select(".page a")
        pages = [int(a.get_text(strip=True)) for a in page_links if a.get_text(strip=True).isdigit()]
        return max(pages) if pages else 1

    def categoryContent(self, tid, pg, filter, extend):
        if extend is None:
            extend = {}
        order = extend.get("order", "time")
        class_id = extend.get("class", "0")
        year = extend.get("year", "0")
        area = extend.get("area", "")
        year_part = f"-{year}" if year != "0" else "--"
        area_part = f"-{area}" if area else "--"
        if class_id != "0":
            list_id = class_id
            class_param = "--"
        else:
            list_id = tid
            class_param = "0"
        url = f"{self.host}/vod-list-id-{list_id}-pg-{pg}-order--by-{order}-class-{class_param}-year{year_part}-letter--area{area_part}-lang-.html"
        try:
            res = self.session.get(url, timeout=10)
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select("ul.resize_list li")
            video_list = []
            for li in items:
                a = li.find("a")
                if not a:
                    continue
                href = a.get("href")
                title = a.get("title", "")
                pic_elem = li.find("div", class_="pic").find("img")
                pic_url = pic_elem.get("data-echo") or pic_elem.get("src") if pic_elem else ""
                remarks_elem = li.select_one("span.sBottom span")
                remarks = remarks_elem.get_text(strip=True) if remarks_elem else ""
                if href.startswith("/vod-detail-id-"):
                    detail_id = href.split('-')[-1].replace('.html', '')
                    vod_id = f"detail_{detail_id}"
                else:
                    vod_id = href
                video_list.append({
                    "vod_id": vod_id,
                    "vod_name": title,
                    "vod_pic": pic_url,
                    "vod_remarks": remarks
                })
            total_pages = self._get_total_pages(soup)
            return {
                "list": video_list,
                "page": int(pg),
                "pagecount": total_pages,
                "limit": 20,
                "total": total_pages * 20
            }
        except Exception as e:
            print(f"[categoryContent] 错误: {e}")
            return {"list": [], "page": int(pg), "pagecount": 1, "limit": 0, "total": 0}

    def detailContent(self, array):
        vod_id = array[0]
        if vod_id.startswith("detail_"):
            detail_id = vod_id.split("_")[1]
            detail_url = f"{self.host}/vod-detail-id-{detail_id}.html"
        else:
            detail_url = vod_id if vod_id.startswith("http") else self.host + vod_id
            match = re.search(r'vod-detail-id-(\d+)', detail_url)
            detail_id = match.group(1) if match else ""
        try:
            res = self.session.get(detail_url, timeout=10)
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            title_elem = soup.select_one("h1.title a")
            title = title_elem.get_text(strip=True) if title_elem else ""
            pic_elem = soup.select_one(".page-hd img")
            pic = pic_elem.get("src") or pic_elem.get("data-echo") if pic_elem else ""
            actor_elems = soup.select(".desc_item:contains('主演:') a")
            actor = ", ".join([a.get_text(strip=True) for a in actor_elems]) if actor_elems else ""
            director_elems = soup.select(".desc_item:contains('导演:') a")
            director = ", ".join([a.get_text(strip=True) for a in director_elems]) if director_elems else ""
            year_elem = soup.select_one(".desc_item:contains('年代:') a")
            year = year_elem.get_text(strip=True) if year_elem else ""
            intro_elem = soup.select_one("article.detail-con p") or soup.select_one(".detail-con")
            intro = re.sub(r"\s+", " ", intro_elem.get_text(strip=True)).strip() if intro_elem else ""
            play_from_list = []
            play_url_list = []
            if detail_id:
                play_url = f"{self.host}/vod-play-id-{detail_id}-src-1-num-1.html"
                try:
                    play_res = self.session.get(play_url, timeout=8)
                    play_res.encoding = "utf-8"
                    play_html = play_res.text
                    line_name = "lzm3u8"
                    mac_from_match = re.search(r"mac_from\s*=\s*'([^']+)'", play_html)
                    if mac_from_match:
                        line_name = mac_from_match.group(1)
                    mac_url_match = re.search(r"mac_url\s*=\s*'([^']+)'", play_html)
                    if mac_url_match:
                        mac_url = mac_url_match.group(1)
                        episodes = [ep.strip() for ep in mac_url.split("#") if ep.strip()]
                        episodes.sort(key=lambda x: int(re.search(r'第(\d+)集', x).group(1)) if re.search(r'第(\d+)集', x) else 0)
                        if episodes:
                            play_from_list.append(line_name)
                            play_url_list.append("#".join(episodes))
                except:
                    pass
            vod = {
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": pic,
                "vod_type": "",
                "vod_area": "",
                "vod_year": year,
                "vod_director": director,
                "vod_actor": actor,
                "vod_content": intro,
                "vod_play_from": "$$$".join(play_from_list),
                "vod_play_url": "$$$".join(play_url_list)
            }
            return {"list": [vod]}
        except Exception as e:
            print(f"[detailContent] 错误: {e}")
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        search_url = f"{self.host}/vod-search-pg-{pg}-wd-{key}.html"
        try:
            res = self.session.get(search_url, timeout=10)
            res.encoding = "utf-8"
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select("ul#data_list li") or soup.select("ul.ulPicTxt li")
            video_list = []
            for li in items:
                title_elem = li.select_one(".txt .sTit") or li.select_one("a[title]")
                title = title_elem.get_text(strip=True) if title_elem else ""
                detail_a = li.select_one(".pic a") or li.select_one(".aPlayBtn")
                href = detail_a.get("href", "") if detail_a else ""
                if not href or not title:
                    continue
                img_elem = li.select_one(".pic img")
                pic_url = img_elem.get("data-src") or img_elem.get("src") if img_elem else ""
                remarks_elem = li.select_one(".sStyle") or li.select_one(".sDes em:not(.emTit)")
                remarks = remarks_elem.get_text(strip=True) if remarks_elem else ""
                if href.startswith("/vod-detail-id-"):
                    detail_id = href.split('-')[-1].replace('.html', '')
                    vod_id = f"detail_{detail_id}"
                else:
                    vod_id = href
                video_list.append({
                    "vod_id": vod_id,
                    "vod_name": title,
                    "vod_pic": pic_url,
                    "vod_remarks": remarks
                })
            page_count = 1
            page_elem = soup.select_one(".page a:last-child")
            if page_elem:
                page_href = page_elem.get("href", "")
                page_match = re.search(r"pg-(\d+)", page_href)
                if page_match:
                    page_count = int(page_match.group(1))
            return {
                "list": video_list,
                "page": int(pg),
                "pagecount": page_count,
                "limit": len(video_list),
                "total": len(video_list) * page_count
            }
        except:
            return {"list": [], "page": int(pg), "pagecount": 1, "limit": 0, "total": 0}

    def playerContent(self, flag, id, vipFlags):
        if id and not id.startswith(("http", "/")) and "$" not in id and "?" not in id:
            api_url = f"{self.api_host}/player/?url={id}"
            try:
                res = self.session.get(api_url, timeout=10)
                url_match = re.search(r'"url":\s*"([^"]+)"', res.text)
                if url_match:
                    real_url = url_match.group(1).replace("\\u0026", "&")
                    return {"parse": 0, "url": real_url, "header": {"User-Agent": self.header["User-Agent"], "Referer": self.host}}
                iframe_match = re.search(r'<iframe[^>]+src="([^"]+)"', res.text)
                if iframe_match:
                    return {"parse": 0, "url": iframe_match.group(1)}
                return {"parse": 0, "url": ""}
            except:
                return {"parse": 0, "url": ""}
        else:
            play_url = self.host + id if not id.startswith("http") else id
            try:
                resp = self.session.get(play_url, timeout=10)
                resp.encoding = "utf-8"
                mac_url_match = re.search(r"mac_url\s*=\s*'([^']+)'", resp.text, re.DOTALL)
                if not mac_url_match:
                    return {"parse": 0, "url": ""}
                mac_url = mac_url_match.group(1)
                current_num = int(re.search(r"-num-(\d+)\.html", play_url).group(1)) if re.search(r"-num-(\d+)\.html", play_url) else 1
                target_encrypted = None
                for part in mac_url.split("#"):
                    m = re.match(r"第(\d+)集\$(.*)", part)
                    if m and int(m.group(1)) == current_num:
                        target_encrypted = m.group(2)
                        break
                if not target_encrypted:
                    target_encrypted = re.search(rf"第{current_num}集\$(.*?)(?=#|$)", mac_url).group(1) if re.search(rf"第{current_num}集\$(.*?)(?=#|$)", mac_url) else ""
                if target_encrypted:
                    api_url = f"{self.api_host}/player/?url={target_encrypted}"
                    res = self.session.get(api_url, timeout=10)
                    url_match = re.search(r'"url":\s*"([^"]+)"', res.text)
                    if url_match:
                        real_url = url_match.group(1).replace("\\u0026", "&")
                        return {"parse": 0, "url": real_url, "header": {"User-Agent": self.header["User-Agent"], "Referer": self.host}}
                return {"parse": 0, "url": ""}
            except:
                return {"parse": 0, "url": ""}