var rule = {
  title: '',
  //host: 'https://888.qkw2.cc/',
   host: 'https://www.91qkw.cc/',
  hostJs:'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});HOST = jsp.pdfh(html,"#nice p:eq(0) a&&href");log(HOST);',
  url: '/show/fyfilter.html',
  searchUrl: '/search/-------------.html?wd=**&submit=',
  searchable: 2,
  quickSearch: 0,
  filterable: 1,
  filter_url:'{{fl.cateId}}-{{fl.area}}-{{fl.by}}------fypage---{{fl.year}}',
  filter: {"1":[{"key":"cateId","name":"按类型","value":[{"n":"全部","v":"1"},{"n":"动作片","v":"6"},{"n":"喜剧片","v":"7"},{"n":"爱情片","v":"8"},{"n":"科幻片","v":"9"},{"n":"恐怖片","v":"10"},{"n":"剧情片","v":"11"},{"n":"战争片","v":"12"},{"n":"奇幻片","v":"21"},{"n":"纪录片","v":"22"},{"n":"悬疑片","v":"25"},{"n":"犯罪片","v":"26"},{"n":"惊悚片","v":"27"}]},{"key":"area","name":"按地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"新加坡","v":"新加坡"},{"n":"马来西亚","v":"马来西亚"},{"n":"印度","v":"印度"},{"n":"英国","v":"英国"},{"n":"法国","v":"法国"},{"n":"加拿大","v":"加拿大"},{"n":"西班牙","v":"西班牙"},{"n":"俄罗斯","v":"俄罗斯"},{"n":"其它","v":"其它"}]},{"key":"year","name":"按年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"}]},{"key":"by","name":"按排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],"2":[{"key":"cateId","name":"按类型","value":[{"n":"全部","v":"2"},{"n":"国产剧","v":"13"},{"n":"短剧","v":"28"},{"n":"港台剧","v":"14"},{"n":"日韩剧","v":"15"},{"n":"欧美剧","v":"16"},{"n":"海外剧","v":"20"}]},{"key":"area","name":"按地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"新加坡","v":"新加坡"},{"n":"马来西亚","v":"马来西亚"},{"n":"印度","v":"印度"},{"n":"英国","v":"英国"},{"n":"法国","v":"法国"},{"n":"加拿大","v":"加拿大"},{"n":"西班牙","v":"西班牙"},{"n":"俄罗斯","v":"俄罗斯"},{"n":"其它","v":"其它"}]},{"key":"year","name":"按年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"}]},{"key":"by","name":"按排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],"3":[{"key":"area","name":"按地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"大陆"},{"n":"中国香港","v":"中国香港"},{"n":"中国台湾","v":"中国台湾"},{"n":"美国","v":"美国"},{"n":"韩国","v":"韩国"},{"n":"日本","v":"日本"},{"n":"泰国","v":"泰国"},{"n":"新加坡","v":"新加坡"},{"n":"马来西亚","v":"马来西亚"},{"n":"印度","v":"印度"},{"n":"英国","v":"英国"},{"n":"法国","v":"法国"},{"n":"加拿大","v":"加拿大"},{"n":"西班牙","v":"西班牙"},{"n":"俄罗斯","v":"俄罗斯"},{"n":"其它","v":"其它"}]},{"key":"year","name":"按年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"},{"n":"2003","v":"2003"},{"n":"2002","v":"2002"}]},{"key":"按排序","name":"按排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}]
  },
  headers: {
    'User-Agent': 'MOBILE_UA',
  },
  	filter_def:{
        13:{cateId:'13'},
		1:{cateId:'1'},
		2:{cateId:'2'},
		3:{cateId:'3'}
	},
      class_name:'国产剧&电影&电视剧&综艺',//静态分类名称拼接
    class_url:'13&1&2&3',
  //class_parse: '.stui-header__menu.clearfix li;a&&Text;a&&href;/(\\d+).html',
  play_parse: true,
  lazy: "js:\n  let html = request(input);\n  let hconf = html.match(/r player_.*?=(.*?)</)[1];\n  let json = JSON5.parse(hconf);\n  let url = json.url;\n  if (json.encrypt == '1') {\n    url = unescape(url);\n  } else if (json.encrypt == '2') {\n    url = unescape(base64Decode(url));\n  }\n  if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {\n    input = {\n      parse: 0,\n      jx: 0,\n      url: url,\n    };\n  } else {\n    input = url && url.startsWith('http') && tellIsJx(url) ? {parse:0,jx:1,url:url}:input;\n  }",
  limit: 6,
  double: true,
  //tab_rename:{'无需安装任何插件奇奇秒播源':'奇奇秒播源',},
  推荐: 'ul.stui-vodlist.tab-pane;li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
  一级: 'ul.stui-vodlist.clearfix li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
  二级: {
    title: '.stui-content__thumb .pic&&title;.stui-content__detail p.data:eq(3) a:eq(0)&&Text',
    img: '.stui-content__thumb .lazyload&&data-original',
    desc: '.stui-content__detail p.data:eq(0)&&Text;.stui-content__detail p.data:eq(3) a:eq(2)&&Text;.stui-content__detail p.data:eq(3) a:eq(1)&&Text;.stui-content__detail p.data:eq(1)&&Text;.stui-content__detail p.data:eq(2)&&Text',
    content: '.stui-content__detail p.desc.hidden-xs&&Text',
    tabs: '.stui-pannel__head.clearfix;.title&&Text',
    lists: '.stui-content__playlist.clearfix:eq(#id) li',
  },
  搜索: '.stui-vodlist.clearfix li;a&&title;.lazyload&&data-original;.pic-text&&Text;a&&href;.detail&&Text',
}
