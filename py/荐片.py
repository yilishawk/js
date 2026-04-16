# -*- coding: utf-8 -*-
import requests
import re
import json
from base.spider import Spider as BaseSpider

requests.packages.urllib3.disable_warnings()

class Spider(BaseSpider):
    def getName(self):
        return "ZT-API(详情加速版)"

    def init(self, extend=""):
        self.host = 'https://api.ztcgi.com'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 9; V2196A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36',
            'Referer': 'https://api.ztcgi.com/',
            'Connection': 'Keep-Alive'
        }
        self.img_host = "https://img.jgsfnl.com"
        self.session = requests.Session()
        self.session.headers.update(self.header)
        self.session.verify = False

    def homeContent(self, filter):
        result = {'class': [], 'filters': {}}
        result['class'] = [
            {'type_name': '国产剧', 'type_id': '15'},
            {'type_name': '电视剧', 'type_id': '2'},
            {'type_name': '喜剧电影', 'type_id': '7'},
            {'type_name': '综艺', 'type_id': '4'},
            {'type_name': '动漫', 'type_id': '3'}
        ]
        c_year = [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "107"}, {"n": "2024", "v": "119"}, {"n": "2023", "v": "153"}, {"n": "2022", "v": "101"}]
        c_sort = [{"n": "热门", "v": "hot"}, {"n": "评分", "v": "rating"}, {"n": "更新", "v": "update"}]
        result['filters'] = {
            "15": [{"key": "year", "name": "年代", "value": c_year}, {"key": "sort", "name": "排序", "value": c_sort}],
            "2": [{"key": "cateId", "name": "类型", "value": [{"n": "全部", "v": "2"}, {"n": "国产", "v": "15"}, {"n": "港台", "v": "16"}]}, {"key": "year", "name": "年代", "value": c_year}, {"key": "sort", "name": "排序", "value": c_sort}],
            "7": [{"key": "year", "name": "年代", "value": c_year}, {"key": "sort", "name": "排序", "value": c_sort}],
            "4": [{"key": "year", "name": "年代", "value": c_year}, {"key": "sort", "name": "排序", "value": c_sort}],
            "3": [{"key": "year", "name": "年代", "value": c_year}, {"key": "sort", "name": "排序", "value": c_sort}]
        }
        return result

    def categoryContent(self, tid, pg, filter, extend):
        fcate_pid = extend.get('cateId', tid) if extend else tid
        year = extend.get('year', '') if extend else ''
        sort = extend.get('sort', 'hot') if extend else 'hot'
        url = f"{self.host}/api/crumb/list?fcate_pid={fcate_pid}&category_id=&area=&year={year}&type=&sort={sort}&page={pg}"
        try:
            res = self.session.get(url, timeout=8)
            data = res.json()
            if data.get('code') == 1:
                return {'list': self.parse_json_list(data.get('data', [])), 'page': int(pg), 'pagecount': 99, 'limit': 20, 'total': 9999}
        except:
            pass
        return {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 0, 'total': 0}

    def detailContent(self, array):
        vod_id = array[0]
        url = f"{self.host}/api/video/detailv2?id={vod_id}"
        try:
            res = self.session.get(url, timeout=5)
            res.encoding = 'utf-8'
            res_json = res.json()
            if res_json.get('code') != 1:
                return {'list': []}
            data = res_json.get('data', {})
            img_path = data.get('thumbnail', '') or data.get('path', '')
            vod_pic = self.get_img_url(img_path)
            vod = {
                "vod_id": vod_id,
                "vod_name": data.get('title', ''),
                "vod_pic": vod_pic,
                "vod_remarks": data.get('mask', ''),
                "vod_actor": " / ".join([a.get('name', '') for a in data.get('actors', [])]),
                "vod_director": " / ".join([d.get('name', '') for d in data.get('directors', [])]),
                "vod_content": data.get('description', '').strip(),
            }
            play_from, play_url = [], []
            sources = data.get('source_list_source', [])
            for s in sources:
                if not s:
                    continue
                source_eps = s.get('source_list', [])
                if not source_eps:
                    continue
                play_from.append(s.get('name', '线路'))
                urls = []
                for ep in source_eps:
                    name = ep.get('source_name', '正片')
                    if str(name).isdigit():
                        name = f"第{name}集"
                    urls.append(f"{name}${ep.get('url', '')}")
                play_url.append("#".join(urls))
            vod["vod_play_from"] = "$$$".join(play_from)
            vod["vod_play_url"] = "$$$".join(play_url)
            return {"list": [vod]}
        except:
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/api/v2/search/videoV2?key={key}&page={pg}"
        try:
            res = self.session.get(url, timeout=10)
            data = res.json()
            if data.get('code') == 1:
                items = data.get('data', [])
                if items:
                    items = [items[0]]
                return {'list': self.parse_json_list(items), 'page': int(pg)}
        except:
            pass
        return {'list': [], 'page': int(pg)}

    def parse_json_list(self, items):
        videos = []
        for item in items:
            if not item:
                continue
            path = item.get('path') or item.get('thumbnail')
            videos.append({
                'vod_id': str(item.get('id')),
                'vod_name': item.get('title'),
                'vod_pic': self.get_img_url(path),
                'vod_remarks': item.get('mask', '')
            })
        return videos

    def get_img_url(self, path):
        if not path:
            return ""
        path_str = str(path).strip()
        if not path_str.startswith('/'):
            path_str = '/' + path_str
        return f"{self.img_host}{path_str}"

    def playerContent(self, flag, id, vipFlags):
        vod_id = ""
        id_match = re.search(r'id=(\d+)', id)
        if id_match:
            vod_id = id_match.group(1)
        weight = "正片"
        if "$" in str(id):
            parts = str(id).split("$", 1)
            if len(parts) >= 1:
                weight = parts[0].strip()
        danmu_url = f"{self.host}/api/v2/comment/list?video_id={vod_id}&weight={requests.utils.quote(weight)}&sort=changed&page=1&pageSize=200"
        play_header = self.header.copy()
        if 'Referer' in play_header:
            del play_header['Referer']
        return {
            "parse": 0,
            "url": id,
            "header": play_header,
            "danmaku": danmu_url
        }