var rule = {
  title: '',
  host: 'https://www.aikanys.vip/',
  hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});HOST = jsp.pdfh(html,".links li:eq(1) a&&href");log(HOST);',
  url: '/vodtype/fyclass-fypage/',
  searchUrl: '/rss/sm.index.xml?wd=**',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100',
  },
  class_parse: 'ul.top-bar-menu.swiper-wrapper li:gt(0):lt(20);a:eq(0)&&Text;a:eq(0)&&href;.*/(.*?)/',
  cate_exclude:'伦理剧',
  play_parse: true,
  lazy: "js:\n  let html = request(input);\n  let hconf = html.match(/r player_.*?=(.*?)</)[1];\n  let json = JSON5.parse(hconf);\n  let url = json.url;\n  if (json.encrypt == '1') {\n    url = unescape(url);\n  } else if (json.encrypt == '2') {\n    url = unescape(base64Decode(url));\n  }\n  if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {\n    input = {\n      parse: 0,\n      jx: 0,\n      url: url,\n    };\n  } else {\n    input = url && url.startsWith('http') && tellIsJx(url) ? {parse:0,jx:1,url:url}:input;\n  }",
  limit: 6,
  double: true,
  推荐: 'body&&.col-xs-4.col-md-3;div.video-content-item;.text-overflow&&title;a&&data-original;.ml-xs-0.mr-xs-0&&Text;a&&href',

  一级: 'div.video-content-item;.text-overflow&&title;a&&data-original;.ml-xs-0.mr-xs-0&&Text;a&&href',
  二级: {
    title: '.mb-0 h1&&Text;.row:eq(0) li:eq(0) p&&Text',
    img: '.block-image.feaimg .lazyload&&data-original',
    desc: 'ul.row li:eq(1) p&&Text;.ewave-collapse-item .row:eq(1) li:eq(1) p&&Text;ul.row:eq(1) li:eq(0) p&&Text;.row p:eq(0)&&Text;.ewave-collapse-item p&&Text',
    content: '.ewave-collapse-item p:eq(7)&&Text',
    tabs: '.ewave-playlist-tab .swiper-wrapper li',
    lists: '.ewave-playlist-sort-content.playlist:eq(#id) li',
  },
  		搜索:`js:
		pdfh = jsp.pdfh, pdfa = jsp.pdfa, pd = jsp.pd;
		let d = [];
		var html = request(input);
		let list = pdfa(html, "rss&&item");
		for (var i = 0; i < list.length; i++) {
			var title = list[i].match(/\\<title\\>(.*?)\\<\\/title\\>/)[1];
			var desc = pdfh(list[i], 'description&&Text');
			var cont = pdfh(list[i], 'pubdate&&Text');
			var url = list[i].match(/\\<link\\>(.*?)\\n/)[1];
			d.push({
				title: title,
				desc: desc,
				content: cont,
				url: url
			})
		}
		setResult(d)
	`,
}