var rule = {
  title: '',
  host: 'https://www.xxmsrj.com/',
  url: '/index.php/vod/type/id/fyclass/fypage.html',
  searchUrl: '/index.php/vod/search.html?wd=**',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  headers: {
    'User-Agent': 'UC_UA',
    'Cookie': 'PHPSESSID=dkr9a0rfvj8bsv362hbbquivn3'
  },
    class_name:'国产剧&电影&电视剧&动漫&综艺',//静态分类名称拼接
    class_url:'13&1&2&3&4',//静态分类标识拼接
  play_parse: true,
  lazy: "js:\n  let html = request(input);\n  let hconf = html.match(/r player_.*?=(.*?)</)[1];\n  let json = JSON5.parse(hconf);\n  let url = json.url;\n  if (json.encrypt == '1') {\n    url = unescape(url);\n  } else if (json.encrypt == '2') {\n    url = unescape(base64Decode(url));\n  }\n  if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {\n    input = {\n      parse: 0,\n      jx: 0,\n      url: url,\n    };\n  } else {\n    input = url && url.startsWith('http') && tellIsJx(url) ? {parse:0,jx:1,url:url}:input;\n  }",
  limit: 6,
  double: true,
  推荐: '.vod-list .col-xs-4;.vod-item;h3&&Text;.lazyload&&data-original;.text-row-1&&Text;a&&href',
  一级: '.vod-item;h3&&Text;.lazyload&&data-original;.text-row-1&&Text;a&&href',
  二级: {
    title: 'h1.text-row-2&&Text;.detail-info-desc.row&&li:eq(1)&&Text',
    img: '.detail-img&&img&&data-original',
    desc: '.detail-info-desc.row&&li:eq(3)&&Text;.detail-info-desc.row&&li:eq(5)&&Text;.detail-info-desc.row&&li:eq(6)&&Text',
    content: '.detail-info-desc.row&&li:eq(9)&&Text',
    tabs: 'ul.tab-box.swiper-wrapper&&li',
    lists: '.ewave-playlist-sort-content:eq(#id) li',
  },
  搜索: '.search-item.row;h2&&Text;.lazyload&&data-original;.fed-list-remarks&&Text;a&&href;.fed-deta-content&&Text',
}