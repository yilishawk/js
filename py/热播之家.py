# -*- coding: utf-8 -*-
import time
import hashlib
import json
import requests
import urllib3
from base.spider import Spider as BaseSpider

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Spider(BaseSpider):
    def getName(self):
        return "AppRJ"

    def init(self, extend=""):
        self.base_url = "http://v.rbotv.cn"
        self.secret = "7gp0bnd2sr85ydii2j32pcypscoc4w6c7g5spl"
        self.common_ua = "okhttp-okgo/jeasonlzy"
        if extend:
            try:
                cfg = json.loads(extend)
                if cfg.get("url"):
                    self.base_url = cfg.get("url").rstrip('/')
            except Exception as e:
                print(f"init error: {e}")
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({"User-Agent": self.common_ua})

    def _make_sign(self, timestamp):
        raw = f"{self.secret}{timestamp}"
        return hashlib.md5(raw.encode('utf-8')).hexdigest()

    def _post(self, path, params):
        url = f"{self.base_url}{path}"
        data = {"timestamp": params.get("timestamp"), "sign": params.get("sign")}
        for k, v in params.items():
            if k not in ["timestamp", "sign"]:
                data[k] = v
        try:
            resp = self.session.post(url, data=data, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"POST error: {e}")
        return None

    def homeContent(self, filter):
        timestamp = str(int(time.time()))
        sign = self._make_sign(timestamp)
        params = {"timestamp": timestamp, "sign": sign}
        result = self._post("/v3/type/top_type", params)
        if not result or result.get("code") != 1:
            return {"class": [], "filters": {}}

        data = result.get("data", {})
        class_list = []
        filters = {}
        for item in data.get("list", []):
            type_id = str(item.get("type_id"))
            type_name = item.get("type_name")
            class_list.append({"type_id": type_id, "type_name": type_name})

            filter_items = []
            extend_list = item.get("extend", [])
            if extend_list and len(extend_list) > 1:
                filter_items.append({
                    "key": "class",
                    "name": "类型",
                    "value": [{"n": v, "v": v} for v in extend_list if v.strip()]
                })
            area_list = item.get("area", [])
            if area_list and len(area_list) > 1:
                filter_items.append({
                    "key": "area",
                    "name": "地区",
                    "value": [{"n": v, "v": v} for v in area_list if v.strip()]
                })
            year_list = item.get("year", [])
            if year_list and len(year_list) > 1:
                filter_items.append({
                    "key": "year",
                    "name": "年份",
                    "value": [{"n": v, "v": v} for v in year_list if v.strip()]
                })
            lang_list = item.get("lang", [])
            if lang_list and len(lang_list) > 1:
                filter_items.append({
                    "key": "lang",
                    "name": "语言",
                    "value": [{"n": v, "v": v} for v in lang_list if v.strip()]
                })
            filters[type_id] = filter_items

        return {"class": class_list, "filters": filters}

    def categoryContent(self, tid, pg, filter, extend):
        timestamp = str(int(time.time()))
        sign = self._make_sign(timestamp)
        params = {
            "timestamp": timestamp,
            "sign": sign,
            "type_id": tid,
            "page": pg,
            "limit": "12"
        }
        if extend:
            for k in ["area", "class", "lang", "year"]:
                if k in extend:
                    params[k] = extend[k]

        result = self._post("/v3/home/type_search", params)
        if not result or result.get("code") != 1:
            return {"list": [], "page": int(pg), "pagecount": 1, "limit": 12, "total": 0}

        data = result.get("data", {})
        video_list = []
        for item in data.get("list", []):
            pic = item.get("vod_pic") or item.get("vod_pic_thumb") or ""
            video_list.append({
                "vod_id": str(item.get("vod_id")),
                "vod_name": item.get("vod_name"),
                "vod_pic": pic,
                "vod_remarks": item.get("vod_remarks", "")
            })
        return {"list": video_list, "page": int(pg), "pagecount": 99, "limit": 12, "total": 9999}

    def detailContent(self, array):
        if not array:
            return {"list": []}
        vod_id = array[0]
        timestamp = str(int(time.time()))
        sign = self._make_sign(timestamp)
        params = {"timestamp": timestamp, "sign": sign, "vod_id": vod_id}
        result = self._post("/v3/home/vod_details", params)
        if not result or result.get("code") != 1:
            return {"list": []}

        data = result.get("data", {})
        pic = data.get("vod_pic") or data.get("vod_pic_thumb") or ""

        play_from_list = []
        play_url_list = []
        for source in data.get("vod_play_list", []):
            source_name = source.get("name") or source.get("title", "未知源")
            parse_urls = source.get("parse_urls", [])
            parse_param = "@".join(parse_urls) if parse_urls else ""
            episodes = []
            for url_item in source.get("urls", []):
                name = url_item.get("name", "")
                raw_url = url_item.get("url", "")
                cleaned = raw_url.strip('|')
                if '|' in cleaned:
                    encrypted = cleaned.split('|')[0]
                else:
                    encrypted = cleaned
                ep_str = f"{name}${parse_param}|{encrypted}"
                episodes.append(ep_str)
            if episodes:
                play_from_list.append(source_name)
                play_url_list.append("#".join(episodes))

        vod = {
            "vod_id": vod_id,
            "vod_name": data.get("vod_name", ""),
            "vod_pic": pic,
            "vod_content": data.get("vod_content", ""),
            "vod_year": data.get("vod_year", ""),
            "vod_actor": data.get("vod_actor", ""),
            "vod_director": data.get("vod_director", ""),
            "type_name": data.get("vod_class", ""),
            "vod_remarks": data.get("vod_remarks", ""),
            "vod_play_from": "$$$".join(play_from_list),
            "vod_play_url": "$$$".join(play_url_list)
        }
        return {"list": [vod]}

    def searchContent(self, key, quick, pg="1"):
        timestamp = str(int(time.time()))
        sign = self._make_sign(timestamp)
        params = {
            "timestamp": timestamp,
            "sign": sign,
            "keyword": key,
            "limit": "12",
            "page": pg
        }
        result = self._post("/v3/home/search", params)
        if not result or result.get("code") != 1:
            return {"list": [], "page": int(pg)}
        data = result.get("data", {})
        video_list = []
        for item in data.get("list", []):
            pic = item.get("vod_pic") or item.get("vod_pic_thumb") or ""
            video_list.append({
                "vod_id": str(item.get("vod_id")),
                "vod_name": item.get("vod_name"),
                "vod_pic": pic,
                "vod_remarks": item.get("vod_remarks", "")
            })
        return {"list": video_list, "page": int(pg)}

    def playerContent(self, flag, id, vipFlags):
        try:
            if '$' in id:
                parts = id.split('$')[1]
            else:
                parts = id
            segments = parts.split('|')
            if len(segments) >= 2:
                parse_param = segments[0]
                encrypted = segments[1]
            else:
                return {"parse": 0, "url": id}

            if parse_param and parse_param.startswith('http'):
                timestamp = str(int(time.time()))
                sign = self._make_sign(timestamp)
                if '?url=' in parse_param or '&url=' in parse_param:
                    req_url = f"{parse_param}{encrypted}"
                else:
                    req_url = f"{parse_param}?url={encrypted}"
                if '&sign=' not in req_url and '?sign=' not in req_url:
                    req_url += f"&sign={sign}&timestamp={timestamp}"
                headers = {"User-Agent": self.common_ua}
                resp = self.session.get(req_url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    real_url = data.get("url")
                    if real_url and real_url.startswith("http"):
                        return {"parse": 0, "url": real_url}
            return {"parse": 0, "url": ""}
        except Exception as e:
            print(f"playerContent error: {e}")
            return {"parse": 0, "url": ""}