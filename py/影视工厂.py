# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote
from base.spider import Spider as BaseSpider

class Spider(BaseSpider):
    def getName(self):
        return "电影人生"

    def init(self, extend=""):
        self.host = "https://dyrs1.vip"
        self.header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": self.host
        }
        self._backup_fetched = False
        self.session = requests.Session()
        self.session.headers.update(self.header)
        self.session.verify = False
        self._ensure_host()

    def _ensure_host(self):
        try:
            if self.session.get(f"{self.host}/", timeout=5).status_code == 200:
                return
        except:
            pass
        self._fetch_backup()

    def _fetch_backup(self):
        if self._backup_fetched:
            return
        self._backup_fetched = True
        try:
            data = self.session.get("https://ysgcw.cc/api/videox/least", timeout=10).json()
            new_host = data.get("least") or next((u for u in data.get("urls", []) if u.startswith("http")), None)
            if new_host:
                self.host = new_host.rstrip('/')
                self.header["Referer"] = self.host
                self.session.headers.update({"Referer": self.host})
        except:
            pass

    def _fix_pic(self, pic):
        return self.host + pic if pic and pic.startswith('/') else pic

    def homeContent(self, filter):
        categories = [
            {'type_name': '电视剧', 'type_id': 'dianshiju'},
            {'type_name': '电影', 'type_id': 'dianying'},
            {'type_name': '综艺', 'type_id': 'zongyi'},
            {'type_name': '短剧', 'type_id': 'duanju'}
        ]
        current_year = 2026
        year_options = [{'n': '全部', 'v': ''}] + [{'n': str(y), 'v': str(y)} for y in range(current_year, 1999, -1)]
        sort_options = [{'n': '默认', 'v': ''}, {'n': '热度', 'v': 'play_hot'}, {'n': '年份', 'v': 'year'}]

        tv_class = [{'n': '全部', 'v': ''}, {'n': '剧情', 'v': '剧情'}, {'n': '爱情', 'v': '爱情'}, {'n': '喜剧', 'v': '喜剧'}]
        tv_area = [{'n': '全部', 'v': ''}, {'n': '内地', 'v': '内地'}, {'n': '美国', 'v': '美国'}, {'n': '中国香港', 'v': '中国香港'}]
        movie_class = [{'n': '全部', 'v': ''}, {'n': '剧情', 'v': '剧情'}, {'n': '喜剧', 'v': '喜剧'}, {'n': '动作', 'v': '动作'}]
        movie_area = [{'n': '全部', 'v': ''}, {'n': '美国', 'v': '美国'}, {'n': '内地', 'v': '内地'}, {'n': '中国香港', 'v': '中国香港'}]
        variety_class = [{'n': '全部', 'v': ''}, {'n': '真人秀', 'v': '真人秀'}, {'n': '大陆综艺', 'v': '大陆综艺'}]
        variety_area = [{'n': '全部', 'v': ''}, {'n': '大陆', 'v': '大陆'}, {'n': '内地', 'v': '内地'}]
        short_class = [{'n': '全部', 'v': ''}, {'n': '短剧', 'v': '短剧'}, {'n': '剧情', 'v': '剧情'}]
        short_area = [{'n': '全部', 'v': ''}, {'n': '中国大陆', 'v': '中国大陆'}, {'n': '大陆', 'v': '大陆'}]

        filters_dict = {
            'dianshiju': [
                {'key': 'class', 'name': '分类', 'value': tv_class},
                {'key': 'area', 'name': '地区', 'value': tv_area},
                {'key': 'year', 'name': '年份', 'value': year_options},
                {'key': 'sort', 'name': '排序', 'value': sort_options}
            ],
            'dianying': [
                {'key': 'class', 'name': '分类', 'value': movie_class},
                {'key': 'area', 'name': '地区', 'value': movie_area},
                {'key': 'year', 'name': '年份', 'value': year_options},
                {'key': 'sort', 'name': '排序', 'value': sort_options}
            ],
            'zongyi': [
                {'key': 'class', 'name': '分类', 'value': variety_class},
                {'key': 'area', 'name': '地区', 'value': variety_area},
                {'key': 'year', 'name': '年份', 'value': year_options},
                {'key': 'sort', 'name': '排序', 'value': sort_options}
            ],
            'duanju': [
                {'key': 'class', 'name': '分类', 'value': short_class},
                {'key': 'area', 'name': '地区', 'value': short_area},
                {'key': 'year', 'name': '年份', 'value': year_options},
                {'key': 'sort', 'name': '排序', 'value': sort_options}
            ]
        }
        return {"class": categories, "filters": filters_dict}

    def categoryContent(self, tid, pg, filter, extend):
        if extend is None:
            extend = {}
        area = extend.get('area', '')
        cls = extend.get('class', '')
        year = extend.get('year', '')
        sort = extend.get('sort', 'play_hot')
        params = []
        if area:
            params.append(f"area={quote(area)}")
        if cls:
            params.append(f"class={quote(cls)}")
        if year:
            params.append(f"year={quote(year)}")
        if sort:
            params.append(f"sort_field={quote(sort)}")
        if pg != "1":
            params.append(f"page={pg}")

        url = f"{self.host}/{tid}.html"
        if params:
            url += "?" + "&".join(params)
        else:
            url += "?sort_field=play_hot"
            if pg != "1":
                url += f"&page={pg}"

        try:
            res = self.session.get(url, timeout=10)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            vod_list = []
            items = soup.find_all('div', class_='group relative')
            for item in items:
                a = item.find('a', title=True)
                if not a:
                    continue
                img = item.find('img')
                vod_list.append({
                    "vod_id": a['href'],
                    "vod_name": a['title'],
                    "vod_pic": self._fix_pic(img.get('data-src') or img.get('src')),
                    "vod_remarks": item.find('div', class_='top-2').text.strip() if item.find('div', class_='top-2') else ""
                })
            return {'list': vod_list, 'page': int(pg), 'pagecount': 99, 'limit': 20, 'total': 9999}
        except:
            return {'list': [], 'page': int(pg), 'pagecount': 1, 'limit': 0, 'total': 0}

    def _parse_line(self, tab):
        try:
            from_name = tab.find('button').get('data-origin')
            resp = self.session.get(self.host + tab['href'], timeout=5)
            resp.encoding = 'utf-8'
            match = re.search(r"dyrs_vod_list\s*=\s*JSON\.parse\('(.*?)'\);", resp.text)
            if not match:
                return None
            raw = match.group(1).encode('utf-8').decode('unicode_escape')
            try:
                raw = raw.encode('iso-8859-1').decode('utf-8')
            except:
                pass
            ep_data = json.loads(raw.replace('\\/', '/'))
            urls = []
            for ep in ep_data:
                title = ep.get('title', '正片')
                if any(c in title for c in 'çé'):
                    title = title.encode('iso-8859-1').decode('utf-8')
                raw_url = ep.get('url', '')
                if raw_url.startswith('http'):
                    full = raw_url
                elif raw_url.startswith('//'):
                    full = 'https:' + raw_url
                elif raw_url.startswith('/'):
                    full = self.host + raw_url
                else:
                    full = self.host + '/' + raw_url
                urls.append(f"{title}${full}")
            return {"from": from_name, "url": "#".join(urls)}
        except:
            return None

    def detailContent(self, array):
        detail_url = self.host + array[0]
        try:
            soup = BeautifulSoup(self.session.get(detail_url, timeout=10).text, 'html.parser')
            title = pic = content = director = actor = year = area = lang = type_name = ""

            script = soup.find('script', type='application/ld+json')
            if script:
                try:
                    jd = json.loads(script.string)
                    title = jd.get('name') or jd.get('alternateName', '')
                    d = jd.get('director')
                    if d:
                        if isinstance(d, dict):
                            director = d.get('name', '')
                        elif isinstance(d, str):
                            director = d
                        elif isinstance(d, list) and d and isinstance(d[0], dict):
                            director = d[0].get('name', '')
                    actors = jd.get('actor', [])
                    if actors:
                        actor = ', '.join([a.get('name', '') if isinstance(a, dict) else str(a) for a in actors])
                    genre = jd.get('genre')
                    if genre:
                        type_name = ', '.join(genre) if isinstance(genre, list) else str(genre)
                    desc = jd.get('description', '')
                    if desc:
                        content = re.sub(r'<[^>]+>', '', desc).strip()
                    release = jd.get('releaseDate', '')
                    if release:
                        y = re.search(r'\b(19|20)\d{2}\b', release)
                        if y:
                            year = y.group()
                    if not year and jd.get('year'):
                        year = str(jd['year'])
                    area = jd.get('countryOfOrigin', '')
                    lang = jd.get('inLanguage', '')
                    if jd.get('image'):
                        pic = jd['image']
                except:
                    pass

            if not title:
                h3 = soup.find('h3', title=True)
                title = h3.get('title', '未知') if h3 else '未知'
            if not pic:
                img_tag = soup.find('img', class_='lazy-image')
                pic = img_tag.get('data-src') or img_tag.get('src', '') if img_tag else ''
            if not content:
                cont_div = soup.find('div', class_='text-justify')
                content = cont_div.text.strip() if cont_div else ''
            if not any([director, actor, year, area, lang, type_name]):
                info_div = soup.find('div', class_='flex flex-col gap-y-2')
                if info_div:
                    for line in info_div.find_all('div', class_='flex'):
                        text = line.text.replace('\n', '').strip()
                        if '导演' in text and not director:
                            director = text.replace('导演：', '').strip()
                        elif '主演' in text and not actor:
                            actor = text.replace('主演：', '').strip()
                        elif '上映' in text and not year:
                            year = text.replace('上映：', '').strip()
                        elif '地区' in text and not area:
                            area = text.replace('地区：', '').strip()
                        elif '语言' in text and not lang:
                            lang = text.replace('语言：', '').strip()
                        elif '类型' in text and not type_name:
                            type_name = text.replace('类型：', '').strip()

            pic = self._fix_pic(pic)

            tabs = soup.select('#originTabs a')
            play_from = []
            play_url = []
            with ThreadPoolExecutor(max_workers=8) as ex:
                results = list(ex.map(self._parse_line, tabs))
            for r in results:
                if r and r['url']:
                    play_from.append(r['from'])
                    play_url.append(r['url'])

            return {"list": [{
                "vod_id": array[0],
                "vod_name": title or "未知",
                "vod_pic": pic,
                "type_name": type_name,
                "vod_year": year,
                "vod_area": area,
                "vod_lang": lang,
                "vod_director": director,
                "vod_actor": actor,
                "vod_content": content,
                "vod_play_from": "$$$".join(play_from),
                "vod_play_url": "$$$".join(play_url)
            }]}
        except:
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        return {"parse": 0, "url": id, "header": self.header}

    def searchContent(self, key, quick, pg="1"):
        try:
            soup = BeautifulSoup(self.session.get(f"{self.host}/s.html", params={"name": key}, timeout=10).text, 'html.parser')
            grid = soup.find('div', id='image-grid')
            if not grid:
                return {'list': [], 'page': int(pg)}
            first = grid.find('div', class_='group relative')
            if not first:
                return {'list': [], 'page': int(pg)}
            a = first.find('a', title=True)
            if not a:
                return {'list': [], 'page': int(pg)}
            img = first.find('img')
            return {'list': [{
                "vod_id": a['href'],
                "vod_name": a['title'],
                "vod_pic": self._fix_pic(img.get('data-src') or img.get('src')) if img else "",
                "vod_remarks": first.find('div', class_='top-2').text.strip() if first.find('div', class_='top-2') else ""
            }], 'page': int(pg)}
        except:
            return {'list': [], 'page': int(pg)}