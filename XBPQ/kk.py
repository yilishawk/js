# -*- coding: utf-8 -*-
# 完美适配 kkvod.cc，模仿 4k-av.com 可用脚本
import sys
from pyquery import PyQuery as pq
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        super().__init__()
        self.host = "https://www.kkvod.cc"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Referer': self.host,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

    def getName(self):
        return "KK影视"

    def homeContent(self, filter):
        html = self.fetch(self.host, headers=self.headers).text
        doc = pq(html)

        classes = []
        # 分类：从导航栏提取
        for item in doc('#nav .nav-list a').items():
            href = item.attr('href')
            text = item.text().strip()
            if href and text and 'list' in href and text not in ['首页', '搜索']:
                tid = href.split('-id-')[-1].split('-')[0] if '-id-' in href else href
                classes.append({
                    "type_name": text,
                    "type_id": tid
                })

        # 推荐视频
        videos = []
        for item in doc('.video-item').items()[:30]:
            a = item('a')
            img = item('img')
            videos.append({
                "vod_id": a.attr('href').split('-id-')[-1].split('.')[0],
                "vod_name": a.attr('title') or img.attr('alt'),
                "vod_pic": img.attr('data-original') or img.attr('src'),
                "vod_remarks": item('.video-con--t').text() or ""
            })

        return {"class": classes, "list": videos}

    def categoryContent(self, tid, pg, filter, extend):
        url = f"{self.host}/vod-list-id-{tid}-pg-{pg}-order-by-hits-class-year-letter-area-lang.html"
        html = self.fetch(url, headers=self.headers).text
        doc = pq(html)

        videos = []
        for item in doc('.video-item').items():
            a = item('a')
            img = item('img')
            videos.append({
                "vod_id": a.attr('href').split('-id-')[-1].split('.')[0],
                "vod_name": a.attr('title') or img.attr('alt'),
                "vod_pic": img.attr('data-original') or img.attr('src'),
                "vod_remarks": item('.video-con--t').text() or ""
            })

        return {
            "page": int(pg),
            "pagecount": 999,
            "limit": 30,
            "total": 9999,
            "list": videos
        }

    def detailContent(self, ids):
        vid = ids[0]
        url = f"{self.host}/vod-detail-id-{vid}.html"
        html = self.fetch(url, headers=self.headers).text
        doc = pq(html)

        vod = {
            "vod_id": vid,
            "vod_name": doc('.video-title').text(),
            "vod_pic": doc('.lazy').attr('src'),
            "type_name": doc('.video-info:contains("类型")').next().text(),
            "vod_year": doc('.video-info:contains("年份")').next().text(),
            "vod_area": doc('.video-info:contains("地区")').next().text(),
            "vod_actor": doc('.video-info:contains("主演")').next().text(),
            "vod_director": doc('.video-info:contains("导演")').next().text(),
            "vod_content": doc('.video-content p').text(),
            "vod_play_from": "KK线路",
            "vod_play_url": ""
        }

        # 剧集列表（支持翻页）
        play_urls = []
        total_pages = 1
        page_info = doc('.page').text()
        import re
        m = re.search(r'共(\d+)页', page_info)
        if m: total_pages = int(m.group(1))

        for page in range(1, total_pages + 1):
            page_url = f"{url}?page={page}" if page > 1 else url
            page_html = self.fetch(page_url, headers=self.headers).text
            page_doc = pq(page_html)
            for item in page_doc('.play-list a').items():
                title = item.text()
                href = item.attr('href')
                if href:
                    play_urls.append(f"{title}$https://www.kkvod.cc{href}")

        vod["vod_play_url"] = "#".join(play_urls) if play_urls else "暂无播放源"
        return {"list": [vod]}

    def playerContent(self, flag, id, vipFlags):
        html = self.fetch(id, headers=self.headers).text
        doc = pq(html)
        src = doc('video source').attr('src') or doc('video').attr('src')
        if not src:
            return {"parse": 1, "url": id}
        return {
            "parse": 0,
            "url": src,
            "header": self.headers
        }

    def searchContent(self, key, quick):
        url = f"{self.host}/vod-search-wd-{key}-pg-1.html"
        html = self.fetch(url, headers=self.headers).text
        doc = pq(html)

        videos = []
        for item in doc('.video-item').items():
            a = item('a')
            img = item('img')
            videos.append({
                "vod_id": a.attr('href').split('-id-')[-1].split('.')[0],
                "vod_name": a.attr('title') or img.attr('alt'),
                "vod_pic": img.attr('data-original') or img.attr('src'),
                "vod_remarks": ""
            })

        return {"list": videos}