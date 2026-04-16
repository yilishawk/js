# -*- coding: utf-8 -*-
import re
import json
import time
import hashlib
import requests
import urllib3
import traceback
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from base.spider import Spider as BaseSpider

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Spider(BaseSpider):
    def getName(self):
        return "量子资源(完整版)"

    def init(self, extend=""):
        self.host = "https://v.xlys.ltd.ua/"
        self.common_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({"User-Agent": self.common_ua})

    def homeContent(self, filter):
        classes = [
            {"type_name": "电视剧", "type_id": "1"},
            {"type_name": "电影",   "type_id": "0"}
        ]

        type_options = [
            {"n": "全部", "v": ""}, {"n": "动作", "v": "dongzuo"}, {"n": "爱情", "v": "aiqing"},
            {"n": "喜剧", "v": "xiju"}, {"n": "科幻", "v": "kehuan"}, {"n": "恐怖", "v": "kongbu"},
            {"n": "战争", "v": "zhanzheng"}, {"n": "武侠", "v": "wuxia"}, {"n": "魔幻", "v": "mohuan"},
            {"n": "剧情", "v": "juqing"}, {"n": "动画", "v": "donghua"}, {"n": "惊悚", "v": "jingsong"},
            {"n": "3D", "v": "3d"}, {"n": "灾难", "v": "zainan"}, {"n": "悬疑", "v": "xuanyi"},
            {"n": "警匪", "v": "jingfei"}, {"n": "文艺", "v": "wenyi"}, {"n": "青春", "v": "qingchun"},
            {"n": "冒险", "v": "maoxian"}, {"n": "犯罪", "v": "fanzui"}, {"n": "纪录", "v": "jilu"},
            {"n": "古装", "v": "guzhuang"}, {"n": "奇幻", "v": "qihuan"}, {"n": "国语", "v": "guoyu"},
            {"n": "综艺", "v": "zongyi"}, {"n": "历史", "v": "lishi"}, {"n": "运动", "v": "yundong"},
            {"n": "原创", "v": "yuanchuang"}, {"n": "压制", "v": "yazhi"}, {"n": "美剧", "v": "meiju"},
            {"n": "韩剧", "v": "hanju"}, {"n": "国产电视剧", "v": "guoju"}, {"n": "日剧", "v": "riju"},
            {"n": "英剧", "v": "yingju"}, {"n": "德剧", "v": "deju"}, {"n": "俄剧", "v": "eju"},
            {"n": "巴剧", "v": "baju"}, {"n": "加剧", "v": "jiaju"}, {"n": "西剧", "v": "spanish"},
            {"n": "意大利剧", "v": "yidaliju"}, {"n": "泰剧", "v": "taiju"}, {"n": "港台剧", "v": "gangtaiju"},
            {"n": "法剧", "v": "faju"}, {"n": "澳剧", "v": "aoju"}, {"n": "短剧", "v": "duanju"},
        ]

        area_options = [
            {"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"}, {"n": "中国台湾", "v": "中国台湾"},
            {"n": "东南亚", "v": "东南亚"}, {"n": "欧美", "v": "欧美"}, {"n": "英国", "v": "英国"},
            {"n": "日本", "v": "日本"}, {"n": "韩国", "v": "韩国"}, {"n": "香港", "v": "香港"},
            {"n": "台湾", "v": "台湾"}, {"n": "法国", "v": "法国"}, {"n": "西班牙", "v": "西班牙"},
            {"n": "新加坡", "v": "新加坡"}, {"n": "澳大利亚", "v": "澳大利亚"}, {"n": "其他", "v": "其他"},
            {"n": "非洲", "v": "非洲"}, {"n": "印度", "v": "印度"}, {"n": "马来西亚", "v": "马来西亚"},
            {"n": "俄罗斯", "v": "俄罗斯"},
        ]

        year_options = [{"n": "全部", "v": ""}] + [{"n": str(y), "v": str(y)} for y in range(2012, 2027)]

        filters = {}
        for tid in ["0", "1"]:
            filters[tid] = [
                {"key": "type_slug", "name": "影视类型", "value": type_options},
                {"key": "area", "name": "地区", "value": area_options},
                {"key": "year", "name": "年份", "value": year_options}
            ]

        return {"class": classes, "filters": filters}

    def categoryContent(self, tid, pg, filter, extend):
        page = int(pg)
        type_slug = extend.get("type_slug", "").strip() if extend else ""
        area = extend.get("area", "").strip() if extend else ""
        year = extend.get("year", "").strip() if extend else ""

        slug = type_slug if type_slug else "all"
        path = f"s/{slug}/{page}"
        params = [f"type={tid}"]
        if area:
            params.append(f"area={area}")
        if year:
            params.append(f"year={year}")

        url = f"{self.host}{path}"
        if params:
            url += "?" + "&".join(params)

        try:
            res = self.session.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'lxml')
            videos = []
            for card in soup.select('.row-cards .col-4 .card-sm'):
                a = card.select_one('a')
                if not a:
                    continue
                vod_id = a.get('href').split(';')[0].strip()
                name_elem = card.select_one('h3.text-truncate')
                name = name_elem.text.strip() if name_elem else ''
                img_elem = card.select_one('img')
                pic = img_elem.get('src') if img_elem else ''
                remark_elem = card.select_one('.bg-pink')
                remark = remark_elem.text.strip() if remark_elem else ''
                videos.append({
                    "vod_id": vod_id,
                    "vod_name": name,
                    "vod_pic": pic,
                    "vod_remarks": remark
                })
            return {"list": videos, "page": page, "pagecount": 99, "limit": 30, "total": 9999}
        except Exception as e:
            print(f"[CAT] Error: {e}")
            return {"list": [], "page": page, "pagecount": 1, "limit": 0, "total": 0}

    def detailContent(self, array):
        url = array[0] if array[0].startswith("http") else self.host + array[0].lstrip('/')
        try:
            res = self.session.get(url, timeout=10)
            soup = BeautifulSoup(res.text, 'lxml')

            second_h2 = soup.select_one('h2.d-sm-block.d-md-none')
            name = second_h2.text.strip() if second_h2 else ''

            pic_elem = soup.select_one('.cover-lg-max-25 img')
            pic = pic_elem.get('src') if pic_elem else ''

            content_elem = soup.select_one('#synopsis .card-body')
            content = content_elem.text.strip() if content_elem else ''

            director = ''
            actor = ''
            area = ''
            lang = ''
            remarks = ''

            info_container = soup.select_one('div.col.mb-2')
            if info_container:
                for p in info_container.select('p'):
                    strong = p.select_one('strong')
                    if not strong:
                        continue
                    label = strong.text.strip().rstrip('：')
                    p_clone = p.__copy__()
                    for s in p_clone.select('strong'):
                        s.decompose()
                    value = p_clone.get_text(strip=True)

                    if label == '导演':
                        directors = [a.text.strip() for a in p.select('a')]
                        director = ', '.join(directors) if directors else value
                    elif label == '主演':
                        actors = [a.text.strip() for a in p.select('a')]
                        actor = ', '.join(actors) if actors else value
                    elif label == '制片国家/地区':
                        area = value.strip('[]')
                    elif label == '语言':
                        lang = value
                    elif label == '集数':
                        remarks = value

            plays = []
            for a in soup.select('#play-list a.btn-square'):
                text = a.text.strip()
                href = a.get('href').split(';')[0].strip()
                plays.append(f"{text}${href}")

            vod = {
                "vod_id": array[0],
                "vod_name": name,
                "vod_pic": pic,
                "vod_content": content,
                "vod_play_from": "哔嘀影视",
                "vod_play_url": "#".join(plays),
                "vod_director": director,
                "vod_actor": actor,
                "vod_area": area,
                "vod_lang": lang,
                "vod_remarks": remarks,
            }
            return {"list": [vod]}
        except Exception as e:
            print(f"[DETAIL] Error: {e}")
            return {"list": []}

    def get_sg_and_t(self, pid):
        curr_t = str(int(time.time() * 1000))
        plain_text = f"{pid}-{curr_t}"
        md5_hash = hashlib.md5(plain_text.encode('utf-8')).hexdigest()
        aes_key = md5_hash[:16].encode('utf-8')
        cipher = AES.new(aes_key, AES.MODE_ECB)
        padded_data = pad(plain_text.encode('utf-8'), AES.block_size, style='pkcs7')
        encrypted = cipher.encrypt(padded_data)
        sg = encrypted.hex().upper()
        return sg, curr_t

    def playerContent(self, flag, id, vipFlags):
        try:
            play_url = id if id.startswith("http") else self.host + id.lstrip('/')
            session = requests.Session()
            session.verify = False
            session.headers.update({"User-Agent": self.common_ua})
            session.get(self.host, timeout=10)

            res_page = session.get(play_url, timeout=10)
            pid_match = re.search(r'var pid\s*=\s*(\d+)', res_page.text)
            if not pid_match:
                return {"parse": 1, "url": play_url}
            pid = pid_match.group(1)

            sg, t_val = self.get_sg_and_t(pid)
            api_url = f"{self.host}lines?t={t_val}&sg={sg}&pid={pid}"
            api_headers = {
                "Referer": play_url,
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/javascript, */*; q=0.01"
            }
            resp = session.get(api_url, headers=api_headers, timeout=10)
            content = resp.text
            json_match = re.search(r'(\{.*\})', content)
            if json_match:
                data = json.loads(json_match.group(1))
                if data.get('code') == 0 and 'data' in data:
                    res_info = data['data']
                    raw_url = res_info.get('url3') or res_info.get('m3u8_2') or res_info.get('m3u8')
                    if raw_url:
                        final_url = raw_url.split(',')[0].split('#')[0].strip()
                        return {
                            "parse": 0,
                            "url": final_url,
                            "header": {"User-Agent": self.common_ua}
                        }
            return {"parse": 1, "url": play_url}
        except Exception as e:
            print(f"[ERROR] {e}")
            return {"parse": 1, "url": id}

    def searchContent(self, key, quick, pg="1"):
        # 该源未实现搜索，返回空列表
        return {"list": [], "page": int(pg)}