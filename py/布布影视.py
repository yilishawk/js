# -*- coding: utf-8 -*-
import json
import re
import requests
from urllib.parse import quote
from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    def getName(self):
        return "布布影视"

    def init(self, extend=""):
        self.host = 'https://bubuyingshi.com'
        self.api_host = 'https://bubuyingshi.com/api.php/web'
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'X-Client': '8f3d2a1c7b6e5d4c9a0b1f2e3d4c5b6a',
            'web-sign': 'f65f3a83d6d9ad6f',
            'Referer': self.host
        }
        self.type_map = {'2': '剧集', '': '电影', '3': '综艺', '4': '动漫'}
        self.session = requests.Session()
        self.session.headers.update(self.header)
        self.session.verify = False

    def homeContent(self, filter):
        result = {'class': [], 'filters': {}}
        for k, v in self.type_map.items():
            result['class'].append({'type_name': v, 'type_id': k})
        return result

    def homeVideoContent(self):
        return {'list': self.get_vod_list(type_id='2', page=1)}

    def categoryContent(self, tid, pg, filter, extend):
        sort = extend.get('sort', 'hits') if extend else 'hits'
        videos = self.get_vod_list(type_id=tid, page=pg, sort=sort)
        return {'list': videos, 'page': int(pg), 'pagecount': 99, 'limit': 15, 'total': 9999}

    def get_vod_list(self, type_id, page, sort='hits'):
        t_name = self.type_map.get(str(type_id), '剧集')
        url = f"{self.api_host}/filter/vod?type_name={quote(t_name)}&type_id={type_id}&page={page}&sort={sort}"
        try:
            res = self.session.get(url, timeout=10)
            res_json = res.json()
            videos = []
            if res_json.get('code') == 200:
                for item in res_json.get('data', []):
                    videos.append({
                        'vod_id': item.get('vod_id'),
                        'vod_name': item.get('vod_name'),
                        'vod_pic': item.get('vod_pic'),
                        'vod_remarks': item.get('vod_remarks')
                    })
            return videos
        except:
            return []

    def detailContent(self, array):
        vid = array[0]
        url = f"{self.api_host}/vod/get_detail?vod_id={vid}"
        try:
            res = self.session.get(url, timeout=10)
            res_json = res.json()
            if res_json.get('code') != 200 or not res_json.get('data'):
                return {"list": []}
            
            item = res_json['data'][0]
            from_list = item.get('vod_play_from', '').split('$$$')
            url_list = item.get('vod_play_url', '').split('$$$')
            
            new_play_url_list = []
            for i in range(len(from_list)):
                sid = from_list[i]
                episodes = url_list[i].split('#')
                formatted_episodes = []
                for ep in episodes:
                    if '$' in ep:
                        name, _ = ep.split('$', 1)
                        nid_match = re.search(r'\d+', name)
                        nid = nid_match.group() if nid_match else "1"
                        formatted_episodes.append(f"{name}${vid}|{sid}|{nid}")
                new_play_url_list.append('#'.join(formatted_episodes))
            
            vod = {
                'vod_id': item.get('vod_id'),
                'vod_name': item.get('vod_name'),
                'vod_pic': item.get('vod_pic'),
                'type_name': item.get('type_name'),
                'vod_year': item.get('vod_year'),
                'vod_remarks': item.get('vod_remarks'),
                'vod_actor': item.get('vod_actor'),
                'vod_director': item.get('vod_director'),
                'vod_content': item.get('vod_content', '').replace('<p>', '').replace('</p>', ''),
                'vod_play_from': item.get('vod_play_from', ''),
                'vod_play_url': '$$$'.join(new_play_url_list)
            }
            return {"list": [vod]}
        except:
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.api_host}/search/index?wd={quote(key)}&page={pg}&limit=15"
        try:
            res = self.session.get(url, timeout=10)
            res_json = res.json()
            videos = []
            if res_json.get('code') == 200:
                for item in res_json.get('data', []):
                    videos.append({
                        'vod_id': item.get('vod_id'),
                        'vod_name': item.get('vod_name'),
                        'vod_pic': item.get('vod_pic'),
                        'vod_remarks': item.get('vod_remarks')
                    })
            return {'list': videos[:1], 'page': int(pg)}
        except:
            return {'list': [], 'page': int(pg)}

    def playerContent(self, flag, id, vipFlags):
        try:
            parts = id.split('|')
            if len(parts) == 3:
                v_id, sid, nid = parts
                full_url = f"https://bubuyingshi.com/play/{v_id}#sid={sid}&nid={nid}"
                return {
                    'parse': 1,
                    'url': full_url,
                    'header': self.header
                }
        except:
            pass
        return {'parse': 1, 'url': id, 'header': self.header}