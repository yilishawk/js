# -*- coding: utf-8 -*-
import re
import requests
from pyquery import PyQuery as pq
from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    def getName(self):
        return "4k影视"

    def init(self, extend=""):
        self.host = "https://www.4kvm.me"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': self.host
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.verify = False

    def _clean_title(self, raw_title):
        if not raw_title:
            return ''
        raw_title = raw_title.strip()
        match = re.match(r'^(.*?)[\s:：]+(\1)$', raw_title)
        if match:
            return match.group(1)
        if ' ' in raw_title:
            parts = raw_title.split(' ', 1)
            if parts[0] == parts[1]:
                return parts[0]
        return raw_title

    def _get_areas_options(self):
        return [
            {"n": "全部地区", "v": ""}, {"n": "中国", "v": "7"}, {"n": "美国", "v": "5"},
            {"n": "日本", "v": "11"}, {"n": "韩国", "v": "12"}, {"n": "英国", "v": "30"},
            {"n": "法国", "v": "6"}, {"n": "德国", "v": "18"}, {"n": "意大利", "v": "19"},
            {"n": "西班牙", "v": "24"}, {"n": "加拿大", "v": "32"}, {"n": "澳大利亚", "v": "22"},
            {"n": "俄罗斯", "v": "16"}, {"n": "印度", "v": "34"}, {"n": "泰国", "v": "33"},
            {"n": "中国香港", "v": "14"}, {"n": "中国台湾", "v": "21"}, {"n": "巴西", "v": "26"},
            {"n": "阿根廷", "v": "27"},
        ]

    def _get_tvclasses_options(self):
        return [
            {"n": "全部类型", "v": ""}, {"n": "国产剧", "v": "20"}, {"n": "美剧", "v": "21"},
            {"n": "韩剧", "v": "22"}, {"n": "日剧", "v": "23"}, {"n": "泰剧", "v": "24"},
            {"n": "日番", "v": "25"}, {"n": "国漫", "v": "26"},
        ]

    def _get_types_options(self):
        return [
            {"n": "全部类型", "v": ""}, {"n": "剧情", "v": "1"}, {"n": "悬疑", "v": "2"},
            {"n": "恐怖", "v": "3"}, {"n": "惊悚", "v": "4"}, {"n": "喜剧", "v": "5"},
            {"n": "爱情", "v": "6"}, {"n": "科幻", "v": "14"}, {"n": "动作", "v": "10"},
            {"n": "冒险", "v": "18"}, {"n": "犯罪", "v": "9"}, {"n": "动画", "v": "11"},
            {"n": "奇幻", "v": "12"}, {"n": "音乐", "v": "13"}, {"n": "历史", "v": "15"},
            {"n": "战争", "v": "16"}, {"n": "家庭", "v": "19"}, {"n": "纪录", "v": "20"},
            {"n": "西部", "v": "23"}, {"n": "情色", "v": "25"}, {"n": "真人秀", "v": "26"},
            {"n": "古装", "v": "27"}, {"n": "传记", "v": "28"}, {"n": "同性", "v": "29"},
            {"n": "运动", "v": "30"}, {"n": "武侠", "v": "31"}, {"n": "歌舞", "v": "32"},
            {"n": "灾难", "v": "34"}, {"n": "短片", "v": "35"},
        ]

    def homeContent(self, filter):
        custom_classes = [
            {"type_name": "国产剧", "type_id": "2|tvclasses=20"}
        ]
        standard_classes = [
            {"type_name": "电影", "type_id": "1"},
            {"type_name": "电视剧", "type_id": "2"},
            {"type_name": "综艺", "type_id": "4"}
        ]
        classes = custom_classes + standard_classes
        filters = {
            "1": [
                {"key": "areas", "name": "地区", "value": self._get_areas_options()},
                {"key": "types", "name": "类型", "value": self._get_types_options()},
            ],
            "2": [
                {"key": "areas", "name": "地区", "value": self._get_areas_options()},
                {"key": "tvclasses", "name": "电视剧分类", "value": self._get_tvclasses_options()},
                {"key": "types", "name": "类型", "value": self._get_types_options()},
            ],
            "4": [
                {"key": "areas", "name": "地区", "value": self._get_areas_options()},
                {"key": "types", "name": "类型", "value": self._get_types_options()},
            ],
        }
        return {"class": classes, "filters": filters}

    def categoryContent(self, tid, pg, filter, extend):
        default_params = {}
        if '|' in str(tid):
            parts = tid.split('|', 1)
            real_tid = parts[0]
            param_str = parts[1]
            for pair in param_str.split('&'):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    default_params[k] = v
        else:
            real_tid = tid

        url = f"{self.host}/filter?classify={real_tid}&page={pg}"
        params = {**default_params, **(extend or {})}
        if params.get('areas'):
            url += f"&areas={params['areas']}"
        if params.get('tvclasses'):
            url += f"&tvclasses={params['tvclasses']}"
        if params.get('types'):
            url += f"&types={params['types']}"

        try:
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            doc = pq(resp.text)
            videos = []
            cards = doc('.movie-card')
            if not cards:
                cards = doc('.group')
            for card in cards.items():
                link = card('a[href^="/play/"]')
                if not link:
                    continue
                href = link.attr('href')
                vod_id = href.split('/')[-1]
                title_elem = card('h3')
                raw_title = title_elem.text().strip() if title_elem else ''
                title = self._clean_title(raw_title)
                img = card('img')
                pic = img.attr('data-src') or img.attr('src') if img else ''
                if pic and not pic.startswith('http'):
                    pic = self.host + pic
                remark_elem = card('span.absolute.bottom-0') or card('.remark')
                remark = remark_elem.text().strip() if remark_elem else ''
                videos.append({
                    'vod_id': vod_id,
                    'vod_name': title,
                    'vod_pic': pic,
                    'vod_remarks': remark
                })

            has_next = doc('a:contains("下一页")').length > 0 or doc('.pagination .next').length > 0
            pagecount = int(pg) + 1 if has_next else int(pg)
            pagecount = min(pagecount + 5, 20)
            limit = len(videos)
            total = limit * pagecount

            return {
                'list': videos,
                'page': int(pg),
                'pagecount': pagecount,
                'limit': limit,
                'total': total
            }
        except:
            return {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 0, 'total': 0}

    def detailContent(self, array):
        vod_id = array[0]
        url = f"{self.host}/play/{vod_id}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            doc = pq(resp.text)

            title_elem = doc('h1')
            raw_title = title_elem.text().strip() if title_elem else ''
            title = self._clean_title(raw_title)

            img = doc('.movie-poster img')
            pic = img.attr('src') if img else ''
            if pic and not pic.startswith('http'):
                pic = self.host + pic

            director = actor = area = year = ''
            info_items = doc('.bg-dark-800.rounded-lg.p-3 .grid')
            for item in info_items.items():
                cells = item('.col-span-1, .col-span-2')
                cell_list = list(cells.items())
                for i in range(0, len(cell_list), 2):
                    key = cell_list[i].text().strip()
                    val = cell_list[i+1].text().strip() if i+1 < len(cell_list) else ''
                    if '导演' in key:
                        director = val
                    elif '主演' in key:
                        actor = val
                    elif '地区' in key:
                        area = val
                    elif '年份' in key:
                        year = val

            desc = doc('.bg-dark-800.rounded-lg.p-3 p')
            content = desc.text().strip() if desc else ''

            play_from = []
            play_urls = []
            episode_links = doc('.episode-link')
            if episode_links:
                line_name = "4K影视"
                episodes = []
                for a in episode_links.items():
                    ep_name = a.text().strip()
                    ep_link = a.attr('href')
                    if ep_link:
                        full_link = ep_link if ep_link.startswith('http') else self.host + ep_link
                        episodes.append(f"{ep_name}${full_link}")
                if episodes:
                    play_from.append(line_name)
                    play_urls.append('#'.join(episodes))

            vod = {
                "vod_id": vod_id,
                "vod_name": title,
                "vod_pic": pic,
                "vod_director": director,
                "vod_actor": actor,
                "vod_area": area,
                "vod_year": year,
                "vod_content": content,
                "vod_play_from": "$$$".join(play_from),
                "vod_play_url": "$$$".join(play_urls)
            }
            return {"list": [vod]}
        except:
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/search?q={key}"
        try:
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            doc = pq(resp.text)
            videos = []
            for item in doc('.group').items():
                a = item('a[href^="/play/"]')
                if not a:
                    continue
                href = a.attr('href')
                vod_id = href.split('/')[-1]
                title_elem = item('h3')
                raw_title = title_elem.text().strip() if title_elem else ''
                title = self._clean_title(raw_title)
                img = item('img')
                pic = img.attr('data-src') or img.attr('src') if img else ''
                if pic and not pic.startswith('http'):
                    pic = self.host + pic
                videos.append({
                    'vod_id': vod_id,
                    'vod_name': title,
                    'vod_pic': pic,
                    'vod_remarks': ''
                })
            return {"list": videos, "page": int(pg), "pagecount": 1, "limit": len(videos), "total": len(videos)}
        except:
            return {"list": [], "page": int(pg), "pagecount": 1, "limit": 0, "total": 0}

    def playerContent(self, flag, id, vipFlags):
        url = id if id.startswith('http') else self.host + id
        try:
            resp = self.session.get(url, timeout=10)
            resp.encoding = 'utf-8'
            html = resp.text
            patterns = [
                r'<video[^>]+src="([^"]+)"',
                r'<source[^>]+src="([^"]+)"',
                r'(?:var|let|const)\s+videoUrl\s*=\s*["\']([^"\']+)["\']',
                r'(?:var|let|const)\s+url\s*=\s*["\']([^"\']+\.m3u8)["\']',
                r'"url"\s*:\s*"([^"]+\.m3u8)"',
                r'([^"\']+\.m3u8[^"\']*)'
            ]
            for pat in patterns:
                match = re.search(pat, html, re.IGNORECASE)
                if match:
                    video_url = match.group(1)
                    if video_url.startswith('//'):
                        video_url = 'https:' + video_url
                    elif video_url.startswith('/'):
                        video_url = self.host + video_url
                    headers = {
                        "User-Agent": self.headers['User-Agent'],
                        "Referer": url,
                        "Origin": self.host
                    }
                    return {"parse": 0, "url": video_url, "header": headers}
            headers = {
                "User-Agent": self.headers['User-Agent'],
                "Origin": self.host,
                "Referer": url
            }
            return {"parse": 1, "url": url, "header": headers}
        except:
            headers = {
                "User-Agent": self.headers['User-Agent'],
                "Origin": self.host,
                "Referer": url
            }
            return {"parse": 1, "url": url, "header": headers}