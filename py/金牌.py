# -*- coding: utf-8 -*-
import requests
import json
import time
import hashlib
from base.spider import Spider as BaseSpider

requests.packages.urllib3.disable_warnings()

class Spider(BaseSpider):
    def getName(self):
        return "九州空间[全修复版]"

    def init(self, extend=""):
        self.host = 'https://m.9zhoukj.com'
        self.key = "cb808529bae6b6be45ecfab29a4889bc"
        self.deviceId = "7dbc13a7-7976-4d7b-89d2-c110d09d7410"
        self.ua = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        self.session = requests.Session()
        self.session.verify = False

    def get_headers(self, params_dict):
        t = str(int(time.time() * 1000))
        valid_params = {k: str(v) for k, v in params_dict.items() if v and v != ""}
        keys = sorted(valid_params.keys())
        query_string = "&".join([f"{k}={valid_params[k]}" for k in keys])
        sign_str = f"{query_string}&key={self.key}&t={t}"
        md5_val = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        sign = hashlib.sha1(md5_val.encode('utf-8')).hexdigest()
        return {
            'Host': 'm.9zhoukj.com',
            'client-type': '3',
            'deviceId': self.deviceId,
            'sign': sign,
            't': t,
            'User-Agent': self.ua,
            'Referer': f'{self.host}/',
        }

    def homeContent(self, filter):
        classes = [
            {'type_name': '国产剧', 'type_id': '2_14'},
            {'type_name': '欧美剧', 'type_id': '2_15'},
            {'type_name': '日韩剧', 'type_id': '2_62'},
            {'type_name': '港台剧', 'type_id': '2_16'},
            {'type_name': '电影', 'type_id': '1_'},
            {'type_name': '综艺', 'type_id': '3_'}
        ]
        years = [{'n': '全部', 'v': ''}] + [{'n': str(y), 'v': str(y)} for y in range(2026, 2009, -1)]
        sorts = [{'n': '最新', 'v': '1'}, {'n': '最热', 'v': '2'}]
        filters = {}
        tv_f = [
            {'key': 'v_class', 'name': '剧情', 'value': [{'n': '全部', 'v': ''}, {'n': '古装', 'v': '古装'}, {'n': '战争', 'v': '战争'}, {'n': '喜剧', 'v': '喜剧'}, {'n': '家庭', 'v': '家庭'}, {'n': '犯罪', 'v': '犯罪'}, {'n': '动作', 'v': '动作'}, {'n': '奇幻', 'v': '奇幻'}, {'n': '剧情', 'v': '剧情'}, {'n': '历史', 'v': '历史'}, {'n': '短片', 'v': '短片'}]},
            {'key': 'area', 'name': '地区', 'value': [{'n': '全部', 'v': ''}, {'n': '中国大陆', 'v': '中国大陆'}, {'n': '中国香港', 'v': '中国香港'}, {'n': '美国', 'v': '美国'}]},
            {'key': 'year', 'name': '年代', 'value': years},
            {'key': 'sort', 'name': '排序', 'value': sorts}
        ]
        mov_f = [
            {'key': 'type', 'name': '类型', 'value': [{'n': '全部', 'v': ''}, {'n': '喜剧', 'v': '22'}, {'n': '动作', 'v': '23'}, {'n': '科幻', 'v': '30'}, {'n': '爱情', 'v': '26'}, {'n': '悬疑', 'v': '27'}, {'n': '奇幻', 'v': '87'}, {'n': '剧情', 'v': '37'}, {'n': '恐怖', 'v': '36'}, {'n': '犯罪', 'v': '35'}, {'n': '动画', 'v': '33'}, {'n': '惊悚', 'v': '34'}, {'n': '战争', 'v': '25'}, {'n': '冒险', 'v': '31'}, {'n': '灾难', 'v': '81'}]},
            {'key': 'v_class', 'name': '剧情', 'value': [{'n': '全部', 'v': ''}, {'n': '爱情', 'v': '爱情'}, {'n': '动作', 'v': '动作'}, {'n': '科幻', 'v': '科幻'}, {'n': '恐怖', 'v': '恐怖'}]},
            {'key': 'area', 'name': '地区', 'value': [{'n': '全部', 'v': ''}, {'n': '中国大陆', 'v': '中国大陆'}, {'n': '中国香港', 'v': '中国香港'}, {'n': '中国台湾', 'v': '中国台湾'}, {'n': '美国', 'v': '美国'}, {'n': '日本', 'v': '日本'}, {'n': '韩国', 'v': '韩国'}, {'n': '印度', 'v': '印度'}, {'n': '泰国', 'v': '泰国'}, {'n': '英国', 'v': '英国'}, {'n': '法国', 'v': '法国'}]},
            {'key': 'year', 'name': '年代', 'value': years},
            {'key': 'sort', 'name': '排序', 'value': sorts}
        ]
        zy_f = [
            {'key': 'type', 'name': '类型', 'value': [{'n': '全部', 'v': ''}, {'n': '国产综艺', 'v': '69'}, {'n': '港台综艺', 'v': '70'}, {'n': '日韩综艺', 'v': '72'}]},
            {'key': 'v_class', 'name': '剧情', 'value': [{'n': '全部', 'v': ''}, {'n': '真人秀', 'v': '真人秀'}, {'n': '音乐', 'v': '音乐'}, {'n': '脱口秀', 'v': '脱口秀'}]},
            {'key': 'year', 'name': '年代', 'value': years}
        ]
        for c in classes:
            tid = c['type_id']
            if tid.startswith('2_'):
                filters[tid] = tv_f
            elif tid.startswith('1_'):
                filters[tid] = mov_f
            elif tid.startswith('3_'):
                filters[tid] = zy_f
        return {'class': classes, 'filters': filters}

    def categoryContent(self, tid, pg, filter, extend):
        url = f"{self.host}/api/mw-movie/anonymous/video/list"
        t_parts = tid.split('_')
        type1, sub_type = t_parts[0], t_parts[1]
        params = {
            'type1': type1,
            'pageNum': str(pg),
            'pageSize': '30',
            'sort': extend.get('sort', '1') if extend else '1',
            'sortBy': '1'
        }
        final_type = extend.get('type', sub_type) if extend else sub_type
        if final_type:
            params['type'] = final_type
        for key in ['area', 'v_class', 'year']:
            if extend and key in extend:
                params[key] = extend[key]
        try:
            hd = self.get_headers(params)
            res = self.session.get(url, params=params, headers=hd, timeout=10)
            data = res.json()
            vods = []
            for i in data.get('data', {}).get('list', []):
                vods.append({
                    'vod_id': str(i['vodId']),
                    'vod_name': i['vodName'],
                    'vod_pic': i['vodPic'],
                    'vod_remarks': i.get('vodRemarks', '')
                })
            return {'list': vods, 'page': int(pg), 'pagecount': 99, 'limit': 30, 'total': 9999}
        except:
            return {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 0, 'total': 0}

    def detailContent(self, array):
        vod_id = array[0]
        params = {'id': vod_id}
        try:
            res = self.session.get(f"{self.host}/api/mw-movie/anonymous/video/detail", params=params, headers=self.get_headers(params), timeout=10)
            data = res.json().get('data', {})
            vod = {
                "vod_id": str(data.get('vodId', vod_id)),
                "vod_name": data.get('vodName', ''),
                "vod_pic": data.get('vodPic', ''),
                "vod_play_from": '九州空间',
                "vod_content": data.get('vodContent', '')
            }
            ep_list = data.get('episodeList', [])
            play_urls = [f"{ep['name']}${vod_id}@@{ep['nid']}" for ep in ep_list]
            vod['vod_play_url'] = "#".join(play_urls) if play_urls else f"正片${vod_id}@@0"
            return {'list': [vod]}
        except:
            return {"list": []}

    def searchContent(self, key, quick, pg="1"):
        url = f"{self.host}/api/mw-movie/anonymous/video/searchByWord"
        params = {"keyword": key, "pageNum": str(pg), "pageSize": "30", "sourceCode": "1"}
        try:
            res = self.session.get(url, params=params, headers=self.get_headers(params), timeout=10)
            raw = res.json().get('data', {}).get('result', {}).get('list', [])
            filtered = [{'vod_id': str(i['vodId']), 'vod_name': i['vodName'], 'vod_pic': i['vodPic'], 'vod_remarks': i.get('vodRemarks', '')} for i in raw if key in i['vodName']]
            return {'list': filtered, 'page': int(pg)}
        except:
            return {'list': [], 'page': int(pg)}

    def playerContent(self, flag, id, vipFlags):
        ids = id.split('@@')
        url = f"{self.host}/api/mw-movie/anonymous/v2/video/episode/url"
        params = {"clientType": "3", "id": str(ids[0]), "nid": str(ids[1])}
        try:
            res = self.session.get(url, params=params, headers=self.get_headers(params), timeout=10)
            v_list = res.json().get('data', {}).get('list', [])
            if v_list:
                final_url = next((v['url'] for v in v_list if v.get('resolution') == 1080), v_list[0]['url'])
                return {"parse": 0, "url": final_url, "header": {"User-Agent": self.ua, "Referer": self.host, "Origin": self.host}}
        except:
            pass
        return {"parse": 1, "url": id}