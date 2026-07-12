import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re
import time
import random

# ================= 配置区 =================
WORKER_URL = 'https://holy-wave-671a.824383214.workers.dev'
MAX_IP_PER_PAGE = 4  # 每页仅抓取 4 个有效 IP
# ==========================================

def fetch_html(url, referer, headers=None):
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    if headers: default_headers.update(headers)
    if referer: default_headers['Referer'] = referer.replace(WORKER_URL, 'https://tonkiang.us')

    try:
        response = requests.get(url, headers=default_headers, timeout=20)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ 请求失败: {url}, 错误: {e}")
        return None

def parse_ip_list(html):
    if not html: return []
    soup = BeautifulSoup(html, 'html.parser')
    entries = []
    result_divs = soup.find_all('div', class_='result')
    for div in result_divs:
        if '暂时失效' in div.get_text(): continue
        channel_link = div.find('a', href=re.compile(r'channellist\.html\?ip='))
        if not channel_link: continue
        href = channel_link.get('href')
        params = parse_qs(urlparse(href).query)
        ip = params.get('ip', [''])[0]
        tk = params.get('tk', [''])[0]
        p_val = params.get('p', ['1'])[0]
        if not ip or not tk: continue

        info_tag = div.find('i')
        location, isp = '未知地区', '未知运营商'
        if info_tag:
            info_text = info_tag.get_text(strip=True)
            parts = re.split(r'\d{2}:\d{2}上线\s*', info_text)
            geo_isp = parts[-1].strip() if len(parts) > 1 else info_text
            match = re.match(r'(.+?)\s+((?:[\u4e00-\u9fa5]+)?(?:电信|联通|移动|广电|铁通|长宽|教育网))\s*$', geo_isp)
            if match:
                location, isp = match.group(1).strip(), match.group(2).strip()
            else:
                location = geo_isp
        entries.append({'ip': ip, 'tk': tk, 'p': p_val, 'region_isp': f"{location} {isp}"})
    return entries

def parse_channel_page(html):
    if not html: return []
    soup = BeautifulSoup(html, 'html.parser')
    channels = []
    for div in soup.find_all('div', class_='result'):
        channel_div = div.find('div', class_='channel')
        if not channel_div: continue
        tip_div = channel_div.find('div', class_='tip')
        channel_name = tip_div.get_text(strip=True) if tip_div else "未知频道"
        m3u8_div = div.find('div', class_='m3u8')
        if not m3u8_div: continue
        for td in m3u8_div.find_all('td'):
            text = td.get_text(strip=True)
            if text.startswith('http'):
                channels.append({'channel_name': channel_name, 'm3u8_url': text})
                break
    return channels

def crawl_source(base_url, list_php, total_pages, output_file):
    all_lines = []
    for page in range(1, total_pages + 1):
        list_url = f"{base_url}/{list_php}" if page == 1 else f"{base_url}/{list_php}?page={page}&iphone16=&code="
        referer = f"{base_url}/" if page == 1 else f"{base_url}/{list_php}"
        
        print(f"🚀 正在抓取第 {page} 页: {list_url}")
        list_html = fetch_html(list_url, referer)
        entries = parse_ip_list(list_html)
        
        # 只保留前 4 个有效条目
        valid_entries = entries[:MAX_IP_PER_PAGE]
        print(f"✅ 提取到 {len(entries)} 个条目，仅处理前 {len(valid_entries)} 个")

        for entry in valid_entries:
            detail_url = f"{base_url}/getall26.php?ip={entry['ip']}&c=&tk={entry['tk']}&p={entry['p']}"
            channel_ref = f"{base_url}/channellist.html?ip={entry['ip']}&tk={entry['tk']}&p={entry['p']}"
            print(f"  🔍 解析: {entry['region_isp']}")
            detail_html = fetch_html(detail_url, channel_ref)
            channels = parse_channel_page(detail_html)
            if channels:
                all_lines.append(f"{entry['region_isp']},#genre#")
                for ch in channels:
                    all_lines.append(f"{ch['channel_name']},{ch['m3u8_url']}")
            time.sleep(random.uniform(1, 2))

    if all_lines:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(all_lines))
        print(f"🎉 成功写入 {output_file}")

def run_crawler(total_pages=1):
    sources = [
        {'php': 'iptvhotelx.php', 'output': 'iptvhote.txt'},
        {'php': 'iptvproxy.php',  'output': 'iptvpmigu.txt'}
    ]
    for source in sources:
        crawl_source(WORKER_URL, source['php'], total_pages, source['output'])

if __name__ == '__main__':
    run_crawler(total_pages=1)
