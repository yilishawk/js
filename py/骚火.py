# -*- coding: utf-8 -*-
import requests
import re
import json
import base64
import time
from pyquery import PyQuery as pq
from base.spider import Spider as BaseSpider

requests.packages.urllib3.disable_warnings()

class Spider(BaseSpider):
    def getName(self):
        return "骚火电影[首页秒开版]"

    def init(self, extend=""):
        self.host = 'https://shdy3.com'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; V2196A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.129 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept-Encoding': 'gzip, deflate'
        }
        self.session = requests.Session()
        self.session.headers.update(self.header)
        self.session.verify = False
        self._fetch_domain()

    def _fetch_domain(self):
        try:
            res = self.session.get('http://shapp.us', timeout=5)
            res.encoding = 'utf-8'
            match = re.search(r'(https://.*?\.com).*?最新网址', res.text)
            if match:
                self.host = match.group(1).strip()
                print(f"[日志] 域名更新为: {self.host}")
        except Exception as e:
            print(f"[日志] 域名解析失败: {e}")

    def natural_sort_key(self, s):
        return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

    def decode_key(self, encoded_str, ee_dict):
        try:
            decoded_base64 = base64.b64decode(encoded_str).decode('utf-8')
            sorted_keys = sorted(ee_dict.keys(), key=len, reverse=True)
            result = ""
            i = 0
            while i < len(decoded_base64):
                match_found = False
                for k in sorted_keys:
                    if decoded_base64.startswith(k, i):
                        result += ee_dict[k]
                        i += len(k)
                        match_found = True
                        break
                if not match_found:
                    result += decoded_base64[i]
                    i += 1
            return result
        except:
            return ""

    def _retry_request(self, method, url, max_retries=3, timeout=15, **kwargs):
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    resp = self.session.get(url, timeout=timeout, **kwargs)
                else:
                    resp = self.session.post(url, timeout=timeout, **kwargs)
                resp.raise_for_status()
                return resp
            except:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        return None

    def homeContent(self, filter):
        result = {'class': [], 'filters': {}}
        result['class'] = [
            {'type_name': '国产剧', 'type_id': '20'},
            {'type_name': '电影', 'type_id': '1'},
            {'type_name': '电视剧', 'type_id': '2'},
            {'type_name': '动漫', 'type_id': '4'}
        ]
        tv_filters = [{"key": "cateId", "name": "类型", "value": [
            {"n": "全部", "v": "2"}, {"n": "大陆", "v": "20"}, {"n": "TVB", "v": "21"},
            {"n": "韩剧", "v": "22"}, {"n": "美剧", "v": "23"}
        ]}]
        movie_filters = [{"key": "cateId", "name": "类型", "value": [
            {"n": "全部", "v": "1"}, {"n": "喜剧", "v": "6"}, {"n": "爱情", "v": "7"},
            {"n": "动作", "v": "9"}, {"n": "科幻", "v": "10"}, {"n": "剧情", "v": "15"}
        ]}]
        result['filters'] = {
            "20": tv_filters,
            "1": movie_filters,
            "2": tv_filters,
            "4": [{"key": "cateId", "name": "类型", "value": [{"n": "全部", "v": "4"}]}]
        }
        return result

    def categoryContent(self, tid, pg, filter, extend):
        curr_tid = extend.get('cateId', tid) if extend else tid
        url = f"{self.host}/list/{curr_tid}-{pg}.html"
        try:
            res = self.session.get(url, timeout=10)
            res.encoding = 'utf-8'
            video_list = self.parse_list(pq(res.text))
            return {
                'list': video_list,
                'page': int(pg),
                'pagecount': 999,
                'limit': 20,
                'total': 9999
            }
        except:
            return {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 0, 'total': 0}

    def detailContent(self, array):
        url = array[0]
        try:
            res = self.session.get(url, timeout=10)
            res.encoding = 'utf-8'
            doc = pq(res.text)
            v_info = doc('.v_info_box')
            info_text = v_info('p').text().strip()
            area = year = vod_type = director = actor = ""

            area_match = re.search(r'^(.*?)\s*/', info_text)
            if area_match:
                area = area_match.group(1).strip()
            year_match = re.search(r'(\d{4})', info_text)
            if year_match:
                year = year_match.group(1)
            type_match = re.search(r'\d{4}\s*/\s*(.*?)\s*/', info_text)
            if type_match:
                vod_type = type_match.group(1).strip()
            director_match = re.search(r'导演:(.*?)(?= / 主演:|$)', info_text)
            if director_match:
                director = director_match.group(1).strip()
            actor_match = re.search(r'主演:(.*?)$', info_text)
            if actor_match:
                actor = actor_match.group(1).strip()

            vod = {
                "vod_id": url,
                "vod_name": v_info('h1.v_title a').text(),
                "vod_pic": doc('.v_img img').attr('data-original') or doc('.v_img img').attr('src'),
                "type_name": vod_type,
                "vod_area": area,
                "vod_year": year,
                "vod_director": director,
                "vod_actor": actor,
                "vod_content": doc('.p_txt.show_part').text().replace('剧情介绍', '').strip(),
                "vod_play_from": "$$$".join([li.text() for li in doc('.play_from ul li').items()]),
            }

            play_urls = []
            for group in doc('#play_link li').items():
                current_line_links = []
                for a in group('a').items():
                    name = a.text()
                    link = a.attr('href')
                    full_link = link if link.startswith('http') else self.host + link
                    current_line_links.append({"name": name, "url": full_link})
                current_line_links.sort(key=lambda x: self.natural_sort_key(x['name']))
                formatted = [f"{item['name']}${item['url']}" for item in current_line_links]
                play_urls.append("#".join(formatted))
            vod["vod_play_url"] = "$$$".join(play_urls)
            return {"list": [vod]}
        except:
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        search_url = f"{self.host}/s----------.html?wd={key}"
        try:
            res = self.session.get(search_url, timeout=10)
            res.encoding = 'utf-8'
            video_list = self.parse_list(pq(res.text))
            return {
                'list': video_list,
                'page': int(pg),
                'pagecount': 1,
                'limit': len(video_list),
                'total': len(video_list)
            }
        except:
            return {'list': [], 'page': int(pg)}

    def parse_list(self, doc):
        videos = []
        for item in doc('ul.v_list li').items():
            link = item('.v_img a').attr('href')
            if not link:
                continue
            full_id = link if link.startswith('http') else self.host + link
            img = item('.v_img img').attr('data-original') or item('.v_img img').attr('src')
            videos.append({
                'vod_id': full_id,
                'vod_name': item('.v_title a').text(),
                'vod_pic': img,
                'vod_remarks': item('.v_note').text()
            })
        return videos

    def playerContent(self, flag, id, vipFlags):
        try:
            res = self._retry_request('GET', id, timeout=15)
            if not res:
                return {"parse": 1, "url": id}
            iframe_match = re.search(r'iframe src="(.*?)"', res.text)
            if not iframe_match:
                return {"parse": 1, "url": id}
            jx_url = iframe_match.group(1)
            if not jx_url.startswith('http'):
                jx_url = self.host + jx_url

            jx_headers = self.header.copy()
            jx_headers['Referer'] = self.host + "/"
            jx_res = self._retry_request('GET', jx_url, headers=jx_headers, timeout=15)
            if not jx_res:
                return {"parse": 1, "url": id}
            jx_html = jx_res.text

            url_val = re.search(r'var url = "(.*?)";', jx_html)
            t_val = re.search(r'var t = "(.*?)";', jx_html)
            encoded_key = re.search(r'var key = OKOK\("(.*?)"\);', jx_html)
            ee_match = re.search(r'const ee = (\{.*?\}) ;', jx_html)
            if not url_val or not t_val or not encoded_key or not ee_match:
                return {"parse": 1, "url": id}

            url_val = url_val.group(1)
            t_val = t_val.group(1)
            encoded_key = encoded_key.group(1)
            ee_dict = json.loads(ee_match.group(1))

            real_key = self.decode_key(encoded_key, ee_dict)
            if not real_key:
                return {"parse": 1, "url": id}

            api_url = "https://hhjx.hhplayer.com/api.php"
            payload = {"url": url_val, "t": t_val, "key": real_key, "act": "0", "play": "1"}
            api_headers = self.header.copy()
            api_headers.update({
                'Origin': 'https://hhjx.hhplayer.com',
                'Referer': jx_url,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest'
            })
            api_res = self._retry_request('POST', api_url, data=payload, headers=api_headers, timeout=15)
            if not api_res:
                return {"parse": 1, "url": id}
            final_data = api_res.json()
            if final_data.get('code') == 200:
                video_url = final_data['url']
                if video_url and not video_url.startswith('http'):
                    video_url = 'https://hhjx.hhplayer.com' + video_url
                return {
                    "parse": 0,
                    "url": video_url,
                    "header": {
                        "User-Agent": self.header['User-Agent'],
                        "Origin": "https://hhjx.hhplayer.com"
                    }
                }
            return {"parse": 1, "url": id}
        except:
            return {"parse": 1, "url": id}