var rule={
	title:'农民影视',
	host:'https://www.freeokk.me',
	//host:'https://www.nmdvd.com/',
	//hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":MOBILE_UA}});let src = jsp.pdfh(html,"body&&a:eq(0)&&href");print(src);HOST=src',
	url:'/show/fyfilter.html',
	tab_exclude:'排序',
	filterable:1,//是否启用分类筛选,
	filter_url:'{{fl.cateId}}-{{fl.area}}--{{fl.class}}-{{fl.lang}}----{{fl.page}}---{{fl.year}}',
	filter: {
		"1":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"动作片","v":"动作"},{"n":"喜剧片","v":"喜剧"},{"n":"爱情片","v":"爱情"},{"n":"科幻片","v":"科幻"},{"n":"恐怖片","v":"恐怖"},{"n":"剧情片","v":"剧情"},{"n":"战争片","v":"战争"},{"n":"惊悚片","v":"惊悚"},{"n":"奇幻片","v":"奇幻"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"香港","v":"香港"},{"n":"台湾","v":"台湾"},{"n":"美国","v":"美国"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"新加坡","v":"新加坡"},{"n":"马来西亚","v":"马来西亚"},{"n":"印度","v":"印度"},{"n":"英国","v":"英国"},{"n":"法国","v":"法国"},{"n":"加拿大","v":"加拿大"},{"n":"西班牙","v":"西班牙"},{"n":"俄罗斯","v":"俄罗斯"},{"n":"其它","v":"其它"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"粤语","v":"粤语"},{"n":"英语","v":"英语"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"},{"n":"1999","v":"1999"},{"n":"1998","v":"1998"},{"n":"1997","v":"1997"},{"n":"1996","v":"1996"},{"n":"1995","v":"1995"},{"n":"1994","v":"1994"},{"n":"1993","v":"1993"},{"n":"1992","v":"1992"},{"n":"1991","v":"1991"},{"n":"1990","v":"1990"},{"n":"1989","v":"1989"},{"n":"1988","v":"1988"},{"n":"1987","v":"1987"},{"n":"1986","v":"1986"},{"n":"1985","v":"1985"},{"n":"1984","v":"1984"},{"n":"1983","v":"1983"},{"n":"1982","v":"1982"},{"n":"1981","v":"1981"},{"n":"1980","v":"1980"},{"n":"1979","v":"1979"},{"n":"1978","v":"1978"},{"n":"1977","v":"1977"},{"n":"1976","v":"1976"},{"n":"1975","v":"1975"},{"n":"1974","v":"1974"},{"n":"1973","v":"1973"},{"n":"1972","v":"1972"},{"n":"1971","v":"1971"},{"n":"1970","v":"1970"},{"n":"1969","v":"1969"},{"n":"1968","v":"1968"},{"n":"1967","v":"1967"},{"n":"1966","v":"1966"},{"n":"1965","v":"1965"},{"n":"1964","v":"1964"},{"n":"1963","v":"1963"},{"n":"1962","v":"1962"},{"n":"1961","v":"1961"},{"n":"1960","v":"1960"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"2":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"古装","v":"古装"},{"n":"战争","v":"战争"},{"n":"喜剧","v":"喜剧"},{"n":"犯罪","v":"犯罪"},{"n":"动作","v":"动作"},{"n":"奇幻","v":"奇幻"},{"n":"剧情","v":"剧情"},{"n":"历史","v":"历史"},{"n":"经典","v":"经典"},{"n":"乡村","v":"乡村"},{"n":"情景","v":"情景"},{"n":"网剧","v":"网剧"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"香港","v":"香港"},{"n":"台湾","v":"台湾"},{"n":"美国","v":"美国"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"新加坡","v":"新加坡"},{"n":"马来西亚","v":"马来西亚"},{"n":"印度","v":"印度"},{"n":"英国","v":"英国"},{"n":"法国","v":"法国"},{"n":"加拿大","v":"加拿大"},{"n":"西班牙","v":"西班牙"},{"n":"俄罗斯","v":"俄罗斯"},{"n":"其它","v":"其它"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"国语"},{"n":"粤语","v":"粤语"},{"n":"英语","v":"英语"}]},{"key":"year","name":"年代","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"},{"n":"2001","v":"2001"},{"n":"2000","v":"2000"},{"n":"1999","v":"1999"},{"n":"1998","v":"1998"},{"n":"1997","v":"1997"},{"n":"1996","v":"1996"},{"n":"1995","v":"1995"},{"n":"1994","v":"1994"},{"n":"1993","v":"1993"},{"n":"1992","v":"1992"},{"n":"1991","v":"1991"},{"n":"1990","v":"1990"},{"n":"1989","v":"1989"},{"n":"1988","v":"1988"},{"n":"1987","v":"1987"},{"n":"1986","v":"1986"},{"n":"1985","v":"1985"},{"n":"1984","v":"1984"},{"n":"1983","v":"1983"},{"n":"1982","v":"1982"},{"n":"1981","v":"1981"},{"n":"1980","v":"1980"},{"n":"1979","v":"1979"},{"n":"1978","v":"1978"},{"n":"1977","v":"1977"},{"n":"1976","v":"1976"},{"n":"1975","v":"1975"},{"n":"1974","v":"1974"},{"n":"1973","v":"1973"},{"n":"1972","v":"1972"},{"n":"1971","v":"1971"},{"n":"1970","v":"1970"},{"n":"1969","v":"1969"},{"n":"1968","v":"1968"},{"n":"1967","v":"1967"},{"n":"1966","v":"1966"},{"n":"1965","v":"1965"},{"n":"1964","v":"1964"},{"n":"1963","v":"1963"},{"n":"1962","v":"1962"},{"n":"1961","v":"1961"},{"n":"1960","v":"1960"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}]
	},
	filter_def:{
		1:{cateId:'1'},
		2:{cateId:'2'}
	},
	searchUrl:'/index.php?m=vod-search&wd=**',
	searchable:2,//是否启用全局搜索,
    headers:{
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.61 Chrome/126.0.6478.61 Not/A)Brand/8 Safari/537.36',
        'Cookie': ''
    },
class_parse: 'ul.navbar-items.swiper-wrapper li;a&&Text;a&&href;/type/(.*?).html',
	// class_parse: '#topnav li:lt(4);a&&Text;a&&href;.*/(.*?).html',
    //class_name:'电影&连续剧&综艺&动漫&短剧',//静态分类名称拼接
    //class_url:'1&2&3&4&26',//静态分类标识拼接
	play_parse: true,
               lazy: "js:\n  let html = request(input);\n  let hconf = html.match(/r player_.*?=(.*?)</)[1];\n  let json = JSON5.parse(hconf);\n  let url = json.url;\n  if (json.encrypt == '1') {\n    url = unescape(url);\n  } else if (json.encrypt == '2') {\n    url = unescape(base64Decode(url));\n  }\n  if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {\n    input = {\n      parse: 0,\n      jx: 0,\n      url: url,\n    };\n  } else {\n    input = url && url.startsWith('http') && tellIsJx(url) ? {parse:0,jx:1,url:url}:input;\n  }",
	limit:6,
	推荐: 'body a.module-poster-item.module-item;a&&title;.lazyload&&data-original;.module-item-note&&Text;a&&href',
  一级: 'body a.module-poster-item.module-item;a&&title;.lazyload&&data-original;.module-item-note&&Text;a&&href',
	 二级: {
    title: 'h1&&Text;.module-info-tag-link:eq(-1)&&Text',
    img: '.lazyload&&data-original||data-src||src',
    desc: '.module-info-item:eq(-2)&&Text;.module-info-tag-link&&Text;.module-info-tag-link:eq(1)&&Text;.module-info-item:eq(2)&&Text;.module-info-item:eq(1)&&Text',
    content: '.module-info-introduction&&Text',
    tabs: '.module-tab-item',
    lists: '.module-play-list:eq(#id) a',
    tab_text: 'div--small&&Text',
  },
  搜索: 'body .module-item;.module-card-item-title&&Text;.lazyload&&data-original;.module-item-note&&Text;a&&href;.module-info-item-content&&Text',
}