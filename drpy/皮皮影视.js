var rule = {
	title:'南柯电影网',
	模板:'mxpro',
	host:'http://www.pipixia.vip/',
    //host:'https://nkvlog.us/',
    hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});HOST = jsp.pdfh(html,".section-row-rSide:eq(1)&&a&&href");log(HOST);',
	url:'http://www.ppxys.vip/s/fyclass//page/fypage.html',
     searchUrl: '/vodsearch.html?wd=**',
	filterable:0,//是否启用分类筛选,
	filter_url:'{{fl.cateId}}{{fl.area}}{{fl.by}}{{fl.class}}{{fl.lang}}{{fl.letter}}/fypage/{{fl.year}}',
	filter: {
		"1":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"1"},{"n":"动作片","v":"6"},{"n":"喜剧片","v":"7"},{"n":"爱情片","v":"8"},{"n":"科幻片","v":"9"},{"n":"恐怖片","v":"10"},{"n":"剧情片","v":"11"},{"n":"战争片","v":"12"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"2":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"2"},{"n":"国产剧","v":"13"},{"n":"港台剧","v":"14"},{"n":"日韩剧","v":"15"},{"n":"欧美剧","v":"16"},{"n":"其他剧","v":"20"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"3":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"4":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}]
	},
	filter_def:{
		1:{cateId:'1'},
		2:{cateId:'2'},
		3:{cateId:'3'},
		4:{cateId:'4'}
	},
      headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6788.76 Safari/537.36',
  },
      class_name:'电视剧&电影&短剧&综艺',
  tab_remove:'失效',
   class_url:'1&2&3&4',

	//class_parse:'.navbar-items li:gt(1):lt(6);a&&Text;a&&href;/(\\d+).html',
      推荐: 'body&&.module;.module-poster-items-base a.module-poster-item;a&&title;.lazyload&&data-original;.module-item-note&&Text;a&&href',
       一级: 'a.module-poster-item.module-item;a&&title;.lazyload&&data-original;.module-item-note&&Text;a&&href',
      二级: {
    title: '.module-info-heading h1&&Text;.module-info-tag-link:eq(2)&&Text',
    img: '.module-item-pic&&img&&data-original',
    desc:  '.module-info-item:eq(2)&&Text;.module-info-tag .module-info-tag-link:eq(0) a&&title;.module-info-tag-link:eq(1) a&&title;.slide-info.hide:eq(2)&&Text;.slide-info.hide:eq(3)&&Text',
    content: 'p&&Text',
    tabs: '.module-tab-item.tab-item.active span',
    lists: '.player-list .module-play-list-content:eq(#id) a',
  },
lazy: "js:\n  let html = request(input);\n  let hconf = html.match(/r player_.*?=(.*?)</)[1];\n  let json = JSON5.parse(hconf);\n  let url = json.url;\n  if (json.encrypt == '1') {\n    url = unescape(url);\n  } else if (json.encrypt == '2') {\n    url = unescape(base64Decode(url));\n  }\n  if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {\n    input = {\n      parse: 0,\n      jx: 0,\n      url: url,\n    };\n  } else {\n    input = url && url.startsWith('http') && tellIsJx(url) ? {parse:0,jx:1,url:url}:input;\n  }",
搜索: '.module-card-item.module-item;.lazyload&&alt;.lazyload&&data-original;.module-item-note&&Text;a&&href',
}
