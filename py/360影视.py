import re
import json
import requests
import urllib3
from urllib.parse import quote
from base.spider import Spider as BaseSpider

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Spider(BaseSpider):
    def __init__(self):
        super(Spider, self).__init__()
        self.host = "https://www.360kan.com"
        self.api_host = "https://api.web.360kan.com"
        self.common_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            "User-Agent": self.common_ua,
            "Referer": self.host
        })
        self.sort_rank = {
            "qq": 1, "qiyi": 2, "imgo": 3, "mgtv": 3, 
            "youku": 4, "bilibili": 5, "sohu": 6, "leshi": 7, "douyin": 8
        }

    def getName(self):
        return "360影视[OK全能版]"

    def init(self, extend=""):
        pass

    def isVideoCast(self):
        return True

    def homeContent(self, filter):
        classes = [
            {"type_name": "电影", "type_id": "1"},
            {"type_name": "电视剧", "type_id": "2"},
            {"type_name": "综艺", "type_id": "3"},
            {"type_name": "动漫", "type_id": "4"}
        ]
        
        years = [{"n": "全部", "v": ""}] + [{"n": str(y), "v": str(y)} for y in range(2026, 2014, -1)]
        areas = [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"}, {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"}, {"n": "日本", "v": "日本"}]
        sorts = [{"n": "最近热映", "v": "rankhot"}, {"n": "最近上架", "v": "ranklatest"}, {"n": "最受好评", "v": "rankpoint"}]

        filters = {}
        for c in classes:
            c_id = c["type_id"]
            if c_id == "1":
                cats = [{"n": "全部", "v": ""}, {"n": "动作", "v": "动作"}, {"n": "喜剧", "v": "喜剧"}, {"n": "爱情", "v": "爱情"}, {"n": "科幻", "v": "科幻"}, {"n": "剧情", "v": "剧情"}, {"n": "战争", "v": "战争"}]
            elif c_id == "2":
                cats = [{"n": "全部", "v": ""}, {"n": "古装", "v": "古装"}, {"n": "偶像", "v": "偶像"}, {"n": "悬疑", "v": "悬疑"}, {"n": "军旅", "v": "军旅"}, {"n": "言情", "v": "言情"}, {"n": "都市", "v": "都市"}]
            else:
                cats = [{"n": "全部", "v": ""}]

            filters[c_id] = [
                {"key": "class", "name": "类型", "value": cats},
                {"key": "area", "name": "地区", "value": areas},
                {"key": "year", "name": "年份", "value": years},
                {"key": "by", "name": "排序", "value": sorts}
            ]
        return {"class": classes, "filters": filters}

    def categoryContent(self, tid, pg, filter, extend):
        f_dict = {}
        if extend:
            try: f_dict = json.loads(extend) if isinstance(extend, str) else extend
            except: pass
        if not f_dict and filter and not isinstance(filter, bool):
            try: f_dict = json.loads(filter) if isinstance(filter, str) else filter
            except: pass
        
        url = f"{self.api_host}/v1/filter/list?catid={tid}&rank={f_dict.get('by','rankhot')}&cat={f_dict.get('class','')}&year={f_dict.get('year','')}&area={f_dict.get('area','')}&size=35&pageno={pg}"
        
        try:
            resp = self.session.get(url, timeout=10).json()
            videos = []
            for item in resp.get("data", {}).get("movies", []):
                if str(tid) == "1":
                    remark = item.get("quality", "").upper() or item.get("pubdate", "")[:4]
                else:
                    up = item.get("upinfo", "")
                    remark = f"更新至{up}集" if up else "全集"

                videos.append({
                    "vod_id": f"{tid}|{item.get('id')}",
                    "vod_name": item.get("title"),
                    "vod_pic": "https:" + item.get("cdncover") if item.get("cdncover") and not item.get("cdncover").startswith("http") else item.get("cdncover"),
                    "vod_remarks": remark
                })
            return {"list": videos, "page": int(pg)}
        except:
            return {"list": [], "page": int(pg)}

    def _clean_url(self, site, url):
        """清洗URL - 所有站点都清洗，优酷保留vid参数"""
        if not url:
            return url
        site = site.lower()
        if site == "youku":
            base = url.split('?')[0]
            match = re.search(r'[?&]vid=([^&]+)', url)
            if match:
                return f"{base}?vid={match.group(1)}"
            return base
        else:
            return url.split('?')[0]

    def detailContent(self, ids):
        id_str = ids[0]
        cat_id, vod_real_id = id_str.split('|') if "|" in id_str else ("2", id_str)
        base_url = f"{self.api_host}/v1/detail?cat={cat_id}&id={vod_real_id}"
        
        try:
            resp = self.session.get(base_url, timeout=10).json()
            if not resp.get("data"): 
                return {"list": []}
            detail = resp["data"]
            pic = detail.get("cdncover") or detail.get("cover", "")
            if pic and not pic.startswith("http"): 
                pic = "https:" + pic

            source_list = []
            
            # 1. 电影 (cat_id=1)
            if str(cat_id) == "1":
                p_links = detail.get("playlinksdetail", {})
                for skey in p_links:
                    d_url = p_links[skey].get("default_url", "")
                    if d_url:
                        clean_url = self._clean_url(skey, d_url)
                        source_list.append({"site": skey, "name": self._get_site_name(skey), "urls": f"正片${clean_url}"})
            
            # 2. 综艺 (cat_id=3) —— 添加 pubdate 到集名后
            elif str(cat_id) == "3":
                playlinks = detail.get("playlinks", {})
                episodes = detail.get("defaultepisode", [])
                for site, play_url in playlinks.items():
                    if play_url:
                        ep_list = []
                        for ep in episodes:
                            ep_name = ep.get("name", "")
                            if not ep_name and ep.get("playlink_num"):
                                ep_name = f"第{ep.get('playlink_num')}期"
                            # 添加 pubdate（如果存在）
                            pubdate = ep.get("pubdate", "")
                            if pubdate:
                                ep_name = f"{ep_name} ({pubdate})"
                            ep_url = ep.get("url", "")
                            if ep_url:
                                clean_url = self._clean_url(site, ep_url)
                                ep_list.append(f"{ep_name}${clean_url}")
                        if ep_list:
                            source_list.append({"site": site, "name": self._get_site_name(site), "urls": "#".join(ep_list)})
                        # 综艺通常只有一个播放源，获取后退出
                        break
            
            # 3. 电视剧 / 动漫 (cat_id=2 或 4)
            else:
                sites = detail.get("playlink_sites", [])
                for site in sites:
                    try:
                        s_resp = self.session.get(f"{base_url}&site={site}", timeout=5).json()
                        s_data = s_resp.get("data", {})
                        eps = s_data.get("allepidetail", {}).get(site, [])
                        ep_list = []
                        if eps:
                            for e in eps:
                                u = e.get("url", "")
                                if u:
                                    clean_url = self._clean_url(site, u)
                                    ep_list.append(f"第{e.get('playlink_num','')}集${clean_url}")
                        else:
                            u = s_data.get("playlinks", {}).get(site, "")
                            if u:
                                clean_url = self._clean_url(site, u)
                                ep_list.append(f"播放${clean_url}")
                        if ep_list:
                            source_list.append({"site": site, "name": self._get_site_name(site), "urls": "#".join(ep_list)})
                    except: 
                        continue

            source_list.sort(key=lambda x: self.sort_rank.get(x['site'], 99))
            
            vod = {
                "vod_id": id_str,
                "vod_name": detail.get("title", ""),
                "vod_pic": pic,
                "vod_type_name": ",".join(detail.get("moviecategory", [])),
                "vod_year": detail.get("pubdate", "")[:4],
                "vod_actor": ",".join(detail.get("actor", [])),
                "vod_director": ",".join(detail.get("director", [])),
                "vod_content": detail.get("description", "").replace("\r\n", ""),
                "vod_play_from": "$$$".join([i['name'] for i in source_list]),
                "vod_play_url": "$$$".join([i['urls'] for i in source_list])
            }
            return {"list": [vod]}
        except Exception as e:
            print(f"detailContent error: {e}")
            return {"list": []}

    def _get_site_name(self, site_key):
        mapping = {"qq": "腾讯视频", "qiyi": "爱奇艺", "mgtv": "芒果TV", "imgo": "芒果TV", "youku": "优酷", "bilibili": "B站", "sohu": "搜狐", "leshi": "乐视", "douyin": "抖音"}
        return mapping.get(site_key, site_key.upper())

    def searchContent(self, key, quick, pg="1"):
        encoded_key = quote(key)
        url = f"https://api.so.360kan.com/index?force_v=1&kw={encoded_key}&from=&pageno={pg}&v_ap=1&tab=all"
        headers = {
            "User-Agent": self.common_ua,
            "Referer": f"https://so.360kan.com/?kw={encoded_key}"
        }
        try:
            resp = self.session.get(url, headers=headers, timeout=10)
            content = resp.text.strip()
            if content.startswith("__jp"):
                left = content.find("(")
                right = content.rfind(")")
                if left != -1 and right != -1:
                    content = content[left + 1 : right]

            res_json = json.loads(content)
            videos = []
            rows = res_json.get("data", {}).get("longData", {}).get("rows", [])
            for item in rows:
                tid = str(item.get("cat_id", "2"))
                v_name = item.get("titleTxt")
                if not v_name:
                    v_name = item.get("title", "未知").replace("<b>", "").replace("</b>", "")
                v_pic = item.get("cover") or item.get("cdn_cover") or ""
                if v_pic and v_pic.startswith("//"): v_pic = "https:" + v_pic
                v_id = item.get("en_id")
                if not v_id:
                    continue
                if tid == "1":
                    remark = item.get("quality", "").upper() or item.get("year", "")
                else:
                    remark = item.get("coverInfo", {}).get("txt", "")
                    if not remark:
                        up = item.get("upinfo", "")
                        remark = f"更新至{up}集" if up else "全集"
                videos.append({
                    "vod_id": f"{tid}|{v_id}",
                    "vod_name": v_name,
                    "vod_pic": v_pic,
                    "vod_remarks": remark
                })
            return {"list": videos}
        except: 
            return {"list": []}

    def playerContent(self, flag, id, vip):
        result = self._resolve_with_xinghetv(id)
        result["danmaku"] = "https://yilishawk.de5.net/danmu?url=" + quote(id)
        return result

    def _resolve_with_xinghetv(self, raw_url):
        """直接使用星河影视 API 解析视频，不依赖第三方解析接口"""
        headers = {
            "User-Agent": self.common_ua,
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.xinghetv.cc/parse",
            "Origin": "https://www.xinghetv.cc"
        }
        try:
            # 第一步：获取剧集信息（主要用于得到剧名）
            parse_info_url = f"https://www.xinghetv.cc/api/parse-info?url={quote(raw_url)}"
            info_resp = self.session.get(parse_info_url, headers=headers, timeout=10)
            if info_resp.status_code != 200:
                raise Exception("parse-info 请求失败")
            info_data = info_resp.json()
            vod_title = info_data.get("vod_title", "未知剧集")
            
            # 第二步：调用解析接口获取真实播放地址
            resolve_url = "https://www.xinghetv.cc/api/player/resolve"
            payload = {
                "playUrl": raw_url,
                "statVodId": f"parse:{vod_title}",
                "statSource": "parse",
                "statVodName": vod_title
            }
            resolve_resp = self.session.post(resolve_url, json=payload, headers=headers, timeout=15)
            if resolve_resp.status_code != 200:
                raise Exception("resolve 请求失败")
            resolve_data = resolve_resp.json()
            
            if resolve_data.get("success") and resolve_data.get("url"):
                m3u8_url = resolve_data["url"]
                # 强制播放请求头为星河影视的 Origin 和 Referer
                play_header = {
                    "Origin": "https://www.xinghetv.cc",
                    "Referer": "https://www.xinghetv.cc",
                    "User-Agent": self.common_ua
                }
                return {"parse": 0, "url": m3u8_url, "header": play_header}
            else:
                raise Exception("解析响应中没有 url 或 success 为 false")
        except Exception as e:
            print(f"星河影视解析失败: {e}")
            # 回退：直接返回原链接（不保证可播放）
            return {"parse": 1, "url": raw_url}