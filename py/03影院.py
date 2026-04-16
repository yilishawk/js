# -*- coding: utf-8 -*-
import re
import json
import base64
import requests
from bs4 import BeautifulSoup
from base.spider import Spider as BaseSpider

requests.packages.urllib3.disable_warnings()

class Spider(BaseSpider):
    def getName(self):
        return "03YY影视"

    def init(self, extend=""):
        """初始化配置"""
        self.host = "https://www.03yy.live"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': self.host
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.verify = False

    # ========== 首页分类与筛选 ==========
    def homeContent(self, filter):
        classes = [
            {"type_name": "大陆剧", "type_id": "13"},
            {"type_name": "电影", "type_id": "1"},
            {"type_name": "综艺", "type_id": "3"},
            {"type_name": "短剧", "type_id": "48"}
        ]
        tv_types = [
            {"n": "全部", "v": ""},
            {"n": "大陆剧", "v": "13"},
            {"n": "欧美剧", "v": "27"},
            {"n": "韩国剧", "v": "26"},
            {"n": "香港剧", "v": "14"},
            {"n": "台湾剧", "v": "46"},
            {"n": "日本剧", "v": "16"},
            {"n": "泰国剧", "v": "47"},
            {"n": "海外剧", "v": "28"}
        ]
        movie_types = [
            {"n": "全部", "v": ""},
            {"n": "动作片", "v": "5"},
            {"n": "喜剧片", "v": "10"},
            {"n": "爱情片", "v": "6"},
            {"n": "科幻片", "v": "7"},
            {"n": "恐怖片", "v": "8"},
            {"n": "战争片", "v": "9"},
            {"n": "剧情片", "v": "12"},
            {"n": "动画片", "v": "25"}
        ]
        variety_types = [
            {"n": "全部", "v": ""},
            {"n": "大陆综艺", "v": "29"},
            {"n": "港台综艺", "v": "30"},
            {"n": "日韩综艺", "v": "31"},
            {"n": "欧美综艺", "v": "32"}
        ]
        short_types = tv_types
        filters = {
            "13": [{"key": "class", "name": "类型", "value": tv_types}],
            "1": [{"key": "class", "name": "类型", "value": movie_types}],
            "3": [{"key": "class", "name": "类型", "value": variety_types}],
            "48": [{"key": "class", "name": "类型", "value": short_types}]
        }
        return {"class": classes, "filters": filters}

    # ========== 分类列表 ==========
    def categoryContent(self, tid, pg, filter, extend):
        sub_tid = extend.get('class') if extend and extend.get('class') else tid
        url = f"{self.host}/type/index{sub_tid}-{pg}.html"
        try:
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            videos = []
            items = soup.select('.Pic-list .pic-content')
            for item in items:
                a = item.select_one('a:first-of-type')
                if not a:
                    continue
                href = a.get('href')
                if not href:
                    continue
                vid_match = re.search(r'/movie/index(\d+)\.html', href)
                if not vid_match:
                    continue
                vid = vid_match.group(1)
                title = a.get('title') or (item.select_one('h4 a') and item.select_one('h4 a').text) or ''
                img = item.select_one('img')
                pic = img.get('src') if img else ''
                if pic and not pic.startswith('http'):
                    pic = self.host + pic
                remark = item.select_one('span').text if item.select_one('span') else (item.select_one('i').text if item.select_one('i') else '')
                videos.append({
                    "vod_id": vid,
                    "vod_name": title.strip(),
                    "vod_pic": pic,
                    "vod_remarks": remark
                })
            return {"list": videos, "page": int(pg), "pagecount": 99, "limit": 20, "total": 9999}
        except Exception as e:
            print(f"[categoryContent] 错误: {e}")
            return {"list": [], "page": int(pg), "pagecount": 1, "limit": 20, "total": 0}

    # ========== 详情页 ==========
    def detailContent(self, array):
        vid = array[0]
        url = f"{self.host}/movie/index{vid}.html"
        try:
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.select_one('h1').text.strip() if soup.select_one('h1') else ''
            img = soup.select_one('.m-pic-l img')
            pic = img.get('src') if img else ''
            if pic and not pic.startswith('http'):
                pic = self.host + pic

            director = ''
            actor = ''
            area = ''
            type_name = ''
            year = ''
            lis = soup.select('.m-content ul li')
            for li in lis:
                text = li.text
                if '导演：' in text:
                    a = li.select_one('a')
                    director = a.text.replace(' ', '').strip() if a else ''
                elif '主演：' in text:
                    actors = [a.text for a in li.select('a')]
                    actor = ','.join(actors)
                elif '地区' in text and li.select('span'):
                    spans = li.select('span')
                    if len(spans) >= 1:
                        area = spans[0].text
                    if len(spans) >= 2:
                        type_name = spans[1].text
                    if len(spans) >= 3:
                        year = spans[2].text

            intro_p = soup.select('.m-intro p')
            content = ' '.join([p.text.strip() for p in intro_p]) if intro_p else ''

            play_from = []
            play_urls = []
            line_tabs = soup.select('.playfrom #playlist li')
            for idx, tab in enumerate(line_tabs):
                line_name = tab.text.strip()
                list_id = f"stab8{idx+1}"
                list_div = soup.select_one(f'#{list_id}')
                if not list_div:
                    continue
                episodes = []
                for a in list_div.select('ul li a'):
                    ep_name = a.text
                    ep_link = a.get('href')
                    if ep_link:
                        full_link = ep_link if ep_link.startswith('http') else self.host + ep_link
                        episodes.append(f"{ep_name}${full_link}")
                if episodes:
                    play_from.append(line_name)
                    play_urls.append('#'.join(episodes))

            vod = {
                "vod_id": vid,
                "vod_name": title,
                "vod_pic": pic,
                "vod_director": director,
                "vod_actor": actor,
                "vod_area": area,
                "type_name": type_name,
                "vod_year": year,
                "vod_content": content,
                "vod_play_from": "$$$".join(play_from),
                "vod_play_url": "$$$".join(play_urls)
            }
            return {"list": [vod]}
        except Exception as e:
            print(f"[detailContent] 错误: {e}")
            return {"list": []}

    # ========== 搜索 ==========
    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/search.php?searchword={key}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            videos = []
            items = soup.select('.Pic-list .pic-content')
            for item in items:
                a = item.select_one('a:first-of-type')
                if not a:
                    continue
                href = a.get('href')
                vid_match = re.search(r'/movie/index(\d+)\.html', href)
                if not vid_match:
                    continue
                vid = vid_match.group(1)
                title = a.get('title') or (item.select_one('h4 a') and item.select_one('h4 a').text) or ''
                img = item.select_one('img')
                pic = img.get('src') if img else ''
                if pic and not pic.startswith('http'):
                    pic = self.host + pic
                remark = item.select_one('i').text if item.select_one('i') else (item.select_one('span').text if item.select_one('span') else '')
                videos.append({
                    "vod_id": vid,
                    "vod_name": title.strip(),
                    "vod_pic": pic,
                    "vod_remarks": remark
                })
            return {"list": videos, "page": int(pg)}
        except Exception as e:
            print(f"[searchContent] 错误: {e}")
            return {"list": [], "page": int(pg)}

    # ========== 播放解析 ==========
    def playerContent(self, flag, id, vipFlags):
        def extract_video_from_html(html, ref_url):
            media_match = re.search(r'(?:var|const|let)\s+mediaInfo\s*=\s*(\[.*?\]);', html, re.DOTALL)
            if media_match:
                try:
                    media_list = json.loads(media_match.group(1))
                    if media_list and isinstance(media_list, list):
                        best_url = None
                        for item in media_list:
                            url = item.get('url')
                            if url:
                                if '1080P' in item.get('definition', ''):
                                    best_url = url
                                    break
                                if not best_url:
                                    best_url = url
                        if best_url:
                            headers = {"User-Agent": self.headers['User-Agent'], "Origin": self.host}
                            return {"parse": 0, "url": best_url, "header": headers}
                except:
                    pass
            video_match = re.search(r'(?:var|const|let)\s+videoUrl\s*=\s*"([^"]+)"', html)
            if video_match and video_match.group(1):
                video_url = video_match.group(1).replace('\\/', '/')
                headers = {"User-Agent": self.headers['User-Agent'], "Referer": ref_url, "Origin": self.host}
                return {"parse": 0, "url": video_url, "header": headers}
            return None

        try:
            resp = self.session.get(id, timeout=10)
            resp.encoding = 'utf-8'
            play_html = resp.text
        except Exception as e:
            print(f"[playerContent] 请求播放页失败: {e}")
            return {"parse": 1, "url": id}

        pn_match = re.search(r'var pn="([^"]+)"', play_html)
        pn = pn_match.group(1) if pn_match else None
        now_match = re.search(r'var now=base64decode\("([^"]+)"\)', play_html)
        now = base64.b64decode(now_match.group(1)).decode('utf-8') if now_match else ''
        next_page = re.search(r'var nextPage="([^"]+)"', play_html)
        next_page = next_page.group(1) if next_page else ''

        if not pn or not now:
            result = extract_video_from_html(play_html, id)
            if result:
                return result
            return {"parse": 1, "url": id}

        player_loader_url = f"{self.host}/js/player/{pn}.html"
        try:
            loader_resp = self.session.get(player_loader_url, timeout=10)
            loader_resp.encoding = 'utf-8'
            loader_html = loader_resp.text
        except Exception as e:
            print(f"[playerContent] 请求播放器加载页失败: {e}")
            return {"parse": 1, "url": id}

        iframe_src = None
        src_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', loader_html)
        if src_match:
            iframe_src = src_match.group(1)
        else:
            src_match2 = re.search(r'iframe\.src\s*=\s*["\']([^"\']+)["\']', loader_html)
            if src_match2:
                iframe_src = src_match2.group(1)

        if not iframe_src:
            print(f"[playerContent] 未提取到 iframe.src")
            return {"parse": 1, "url": id}

        api_path = iframe_src.split('?')[0] if '?' in iframe_src else iframe_src
        params = {'url': now}
        ref = id
        next_param = f"https://www.03yy.live{next_page}" if next_page else ''
        if 'ref' in iframe_src or 'parentUrl' in iframe_src:
            params['ref'] = ref
        if 'next' in iframe_src or 'nextParam' in iframe_src:
            if next_param:
                params['next'] = next_param
        query = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_api_url = f"{self.host}{api_path}?{query}"

        try:
            api_resp = self.session.get(full_api_url, timeout=10)
            api_resp.encoding = 'utf-8'
            api_html = api_resp.text
            result = extract_video_from_html(api_html, id)
            if result:
                return result
        except Exception as e:
            print(f"[playerContent] 请求API失败: {e}")

        return {"parse": 1, "url": id}