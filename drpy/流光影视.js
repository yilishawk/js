var rule = {
  title: '',
  host: 'https://www.gyf.lol/',
  //detailUrl: '/index.php/vod/detail/id/fyid',
  url: '/index.php/vod/show/fyfilter.html',
  searchUrl: '/index.php/ajax/suggest?mid=1&wd=**',
  searchable: 2,
  quickSearch: 0,
  filterable: 1,
  	filter_url: '{{fl.area}}{{fl.by}}{{fl.class}}/id/{{fl.cateId}}/page/fypage/{{fl.lang}}{{fl.year}}',
	filter: {"1":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"喜剧","v":"/class/喜剧"},{"n":"爱情","v":"/class/爱情"},{"n":"恐怖","v":"/class/恐怖"},{"n":"动作","v":"/class/动作"},{"n":"科幻","v":"/class/科幻"},{"n":"剧情","v":"/class/剧情"},{"n":"战争","v":"/class/战争"},{"n":"警匪","v":"/class/警匪"},{"n":"犯罪","v":"/class/犯罪"},{"n":"动画","v":"/class/动画"},{"n":"奇幻","v":"/class/奇幻"},{"n":"武侠","v":"/class/武侠"},{"n":"冒险","v":"/class/冒险"},{"n":"枪战","v":"/class/枪战"},{"n":"恐怖","v":"/class/恐怖"},{"n":"悬疑","v":"/class/悬疑"},{"n":"惊悚","v":"/class/惊悚"},{"n":"经典","v":"/class/经典"},{"n":"青春","v":"/class/青春"},{"n":"文艺","v":"/class/文艺"},{"n":"其他微电影","v":"/class/其他微电影"},{"n":"古装","v":"/class/古装"},{"n":"历史","v":"/class/历史"},{"n":"运动","v":"/class/运动"},{"n":"农村","v":"/class/农村"},{"n":"儿童","v":"/class/儿童"},{"n":"网络电影","v":"/class/网络电影"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"大陆","v":"/area/大陆"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"美国","v":"/area/美国"},{"n":"法国","v":"/area/法国"},{"n":"英国","v":"/area/英国"},{"n":"日本","v":"/area/日本"},{"n":"韩国","v":"/area/韩国"},{"n":"德国","v":"/area/德国"},{"n":"泰国","v":"/area/泰国"},{"n":"印度","v":"/area/印度"},{"n":"意大利","v":"/area/意大利"},{"n":"西班牙","v":"/area/西班牙"},{"n":"加拿大","v":"/area/加拿大"},{"n":"其他","v":"/area/其他"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":"/index.php/vod/show/id/1.html"},{"n":"国语","v":"/lang/国语"},{"n":"英语","v":"/lang/英语"},{"n":"粤语","v":"/lang/粤语"},{"n":"闽南语","v":"/lang/闽南语"},{"n":"韩语","v":"/lang/韩语"},{"n":"日语","v":"/lang/日语"},{"n":"法语","v":"/lang/法语"},{"n":"德语","v":"/lang/德语"},{"n":"其它","v":"/lang/其它"}]},{"key":"year","name":"","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"},{"n":"1999","v":"/year/1999"},{"n":"1998","v":"/year/1998"},{"n":"1997","v":"/year/1997"},{"n":"1995","v":"/year/1995"},{"n":"1994","v":"/year/1994"},{"n":"1993","v":"/year/1993"},{"n":"1992","v":"/year/1992"},{"n":"1991","v":"/year/1991"},{"n":"1990","v":"/year/1990"}]},{"key":"by","name":"排序","value":[{"n":"按时间排序","v":"/by/time"},{"n":"按人气排序","v":"/by/hits"},{"n":"按评分排序","v":"/by/score"}]}],"2":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"古装","v":"/class/古装"},{"n":"战争","v":"/class/战争"},{"n":"青春偶像","v":"/class/青春偶像"},{"n":"喜剧","v":"/class/喜剧"},{"n":"家庭","v":"/class/家庭"},{"n":"犯罪","v":"/class/犯罪"},{"n":"动作","v":"/class/动作"},{"n":"奇幻","v":"/class/奇幻"},{"n":"剧情","v":"/class/剧情"},{"n":"历史","v":"/class/历史"},{"n":"经典","v":"/class/经典"},{"n":"乡村","v":"/class/乡村"},{"n":"情景","v":"/class/情景"},{"n":"商战","v":"/class/商战"},{"n":"网剧","v":"/class/网剧"},{"n":"其他","v":"/class/其他"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"内地","v":"/area/内地"},{"n":"韩国","v":"/area/韩国"},{"n":"香港","v":"/area/香港"},{"n":"台湾","v":"/area/台湾"},{"n":"日本","v":"/area/日本"},{"n":"美国","v":"/area/美国"},{"n":"泰国","v":"/area/泰国"},{"n":"印度","v":"/area/印度"},{"n":"英国","v":"/area/英国"},{"n":"马来西亚","v":"/area/马来西亚"},{"n":"加拿大","v":"/area/加拿大"},{"n":"俄罗斯","v":"/area/俄罗斯"},{"n":"新加坡","v":"/area/新加坡"},{"n":"其他","v":"/area/其他"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"/lang/国语"},{"n":"英语","v":"/lang/英语"},{"n":"粤语","v":"/lang/粤语"},{"n":"闽南语","v":"/lang/闽南语"},{"n":"韩语","v":"/lang/韩语"},{"n":"日语","v":"/lang/日语"},{"n":"其它","v":"/lang/其它"}]},{"key":"year","name":"时间","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"},{"n":"1999","v":"/year/1999"},{"n":"1998","v":"/year/1998"},{"n":"1997","v":"/year/1997"},{"n":"1995","v":"/year/1995"},{"n":"1994","v":"/year/1994"},{"n":"1993","v":"/year/1993"},{"n":"1992","v":"/year/1992"},{"n":"1991","v":"/year/1991"},{"n":"1990","v":"/year/1990"}]},{"key":"by","name":"时间排序","value":[{"n":"按时间排序","v":"/by/time"},{"n":"按人气排序","v":"/by/hits"},{"n":"按评分排序","v":"/by/score"}]}],"3":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"选秀","v":"/class/选秀"},{"n":"情感","v":"/class/情感"},{"n":"访谈","v":"/class/访谈"},{"n":"播报","v":"/class/播报"},{"n":"旅游","v":"/class/旅游"},{"n":"音乐","v":"/class/音乐"},{"n":"美食","v":"/class/美食"},{"n":"纪实","v":"/class/纪实"},{"n":"曲艺","v":"/class/曲艺"},{"n":"生活","v":"/class/生活"},{"n":"游戏互动","v":"/class/游戏互动"},{"n":"财经","v":"/class/财经"},{"n":"求职","v":"/class/求职"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"内地","v":"/area/内地"},{"n":"港台","v":"/area/港台"},{"n":"日韩","v":"/area/日韩"},{"n":"欧美","v":"/area/欧美"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":""},{"n":"国语","v":"/lang/国语"},{"n":"英语","v":"/lang/英语"},{"n":"粤语","v":"/lang/粤语"},{"n":"闽南语","v":"/lang/闽南语"},{"n":"韩语","v":"/lang/韩语"},{"n":"日语","v":"/lang/日语"},{"n":"其它","v":"/lang/其它"}]},{"key":"year","name":"全部时间","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"},{"n":"1999","v":"/year/1999"},{"n":"1998","v":"/year/1998"},{"n":"1997","v":"/year/1997"},{"n":"1995","v":"/year/1995"},{"n":"1994","v":"/year/1994"},{"n":"1993","v":"/year/1993"},{"n":"1992","v":"/year/1992"},{"n":"1991","v":"/year/1991"},{"n":"1990","v":"/year/1990"}]},{"key":"by","name":"排序","value":[{"n":"按时间排序","v":"/by/time"},{"n":"按人气排序","v":"/by/hits"},{"n":"按评分排序","v":"/by/score"}]}],"4":[{"key":"class","name":"剧情","value":[{"n":"全部","v":""},{"n":"情感","v":"/class/情感"},{"n":"科幻","v":"/class/科幻"},{"n":"热血","v":"/class/热血"},{"n":"推理","v":"/class/推理"},{"n":"搞笑","v":"/class/搞笑"},{"n":"冒险","v":"/class/冒险"},{"n":"萝莉","v":"/class/萝莉"},{"n":"校园","v":"/class/校园"},{"n":"动作","v":"/class/动作"},{"n":"机战","v":"/class/机战"},{"n":"运动","v":"/class/运动"},{"n":"战争","v":"/class/战争"},{"n":"少年","v":"/class/少年"},{"n":"少女","v":"/class/少女"},{"n":"社会","v":"/class/社会"},{"n":"原创","v":"/class/原创"},{"n":"亲子","v":"/class/亲子"},{"n":"益智","v":"/class/益智"},{"n":"励志","v":"/class/励志"},{"n":"其他","v":"/class/其他"}]},{"key":"area","name":"地区","value":[{"n":"全部","v":""},{"n":"国产","v":"/area/国产"},{"n":"日本","v":"/area/日本"},{"n":"欧美","v":"/area/欧美"},{"n":"其他","v":"/area/其他"}]},{"key":"lang","name":"语言","value":[{"n":"全部","v":"/index.php/vod/show/id/4.html"},{"n":"国语","v":"/lang/国语"},{"n":"英语","v":"/lang/英语"},{"n":"粤语","v":"/lang/粤语"},{"n":"闽南语","v":"/lang/闽南语"},{"n":"韩语","v":"/lang/韩语"},{"n":"日语","v":"/lang/日语"},{"n":"其它","v":"/lang/其它"}]},{"key":"year","name":"时间","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"},{"n":"1999","v":"/year/1999"},{"n":"1998","v":"/year/1998"},{"n":"1997","v":"/year/1997"},{"n":"1995","v":"/year/1995"},{"n":"1994","v":"/year/1994"},{"n":"1993","v":"/year/1993"},{"n":"1992","v":"/year/1992"},{"n":"1991","v":"/year/1991"},{"n":"1990","v":"/year/1990"}]},{"key":"by","name":"排序","value":[{"n":"按时间排序","v":"/by/time"},{"n":"按人气排序","v":"/by/hits"},{"n":"按评分排序","v":"/by/score"}]}],"5":[{"key":"year","name":"时间","value":[{"n":"全部","v":""},{"n":"2024","v":"/year/2024"},{"n":"2023","v":"/year/2023"},{"n":"2022","v":"/year/2022"},{"n":"2021","v":"/year/2021"},{"n":"2020","v":"/year/2020"},{"n":"2009","v":"/year/2009"},{"n":"2008","v":"/year/2008"},{"n":"2007","v":"/year/2007"},{"n":"2006","v":"/year/2006"},{"n":"2005","v":"/year/2005"},{"n":"2004","v":"/year/2004"},{"n":"2003","v":"/year/2003"},{"n":"2002","v":"/year/2002"},{"n":"2001","v":"/year/2001"},{"n":"2000","v":"/year/2000"},{"n":"1999","v":"/year/1999"},{"n":"1998","v":"/year/1998"},{"n":"1997","v":"/year/1997"},{"n":"1995","v":"/year/1995"},{"n":"1994","v":"/year/1994"},{"n":"1993","v":"/year/1993"},{"n":"1992","v":"/year/1992"},{"n":"1991","v":"/year/1991"},{"n":"1990","v":"/year/1990"}]},{"key":"by","name":"排序","value":[{"n":"按时间排序","v":"/by/time"},{"n":"按人气排序","v":"/by/hits"},{"n":"按评分排序","v":"/by/score"}]}]},
  	filter_def:{
		2:{cateId:'2'},
		1:{cateId:'1'},
    	3:{cateId:'3'},
        4:{cateId:'4'},
        21:{cateId:'21'},
	},
  headers: {
    'User-Agent': 'UC_UA',
    'Cookie': ''
  },
  class_name:'电视剧&电影&综艺&短剧',
  tab_remove:'失效',
   class_url:'2&1&3&21',
  play_parse: true,
  lazy:`js:
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        var from = html.from;
        if (html.encrypt == '1') {
            url = unescape(url)
        }else if(/lzm3u8/.test(input)){
    play_Url='json:https://jx.m3u8.biz/gg.php?url=';
    input={jx:0,url:input,playUrl:play_Url,parse:1}
} else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/m3u8|mp4/.test(url)) {
            input = url
        } else {
            var jx =request(HOST + "/static/player/" + from + ".js").match(/ src="(.*?)'/)[1];
			log(jx)
            let con=request(jx.replace('index','ec')+ url, {headers: {'Referer': HOST}}).match(/let ConFig.*}/)[0];
			log(con)
			eval(con+'\\nrule.ConFig=ConFig')
			function ec(str, uid) {
				eval(getCryptoJS());
				return CryptoJS.enc.Utf8.stringify(CryptoJS.AES.decrypt(str, CryptoJS.enc.Utf8.parse('2890' + uid + 'tB959C'), {
					iv: CryptoJS.enc.Utf8.parse('2F131BE91247866E'),
					mode: CryptoJS.mode.CBC,
					padding: CryptoJS.pad.Pkcs7
				}));
			};
			//log(rule.ConFig.url)
			//log(rule.ConFig.config.uid)
			let purl=ec(rule.ConFig.url, rule.ConFig.config.uid);
			//log(purl)
			input = {
			   jx: 0,
			   url: purl,
			   parse:0,
			}
        }`,
  //lazy: "js:\n  let html = request(input);\n  let hconf = html.match(/r player_.*?=(.*?)</)[1];\n  let json = JSON5.parse(hconf);\n  let url = json.url;\n  if (json.encrypt == '1') {\n    url = unescape(url);\n  } else if (json.encrypt == '2') {\n    url = unescape(base64Decode(url));\n  }\n  if (/\\.(m3u8|mp4|m4a|mp3)/.test(url)) {\n    input = {\n      parse: 0,\n      jx: 0,\n      url: url,\n    };\n  } else {\n    input = url && url.startsWith('http') && tellIsJx(url) ? {parse:0,jx:1,url:url}:input;\n  }",
  limit: 6,
  tab_remove:['海外云'],
  tab_order:['蓝光X[仅支持夸克、Alook浏览器]','闪电蓝光[跨域/仅支持夸克浏览器或APP]','蓝光LK','蓝光N','蓝光F[APP专享]','资源库','木耳蓝光'],
  double: true,
  推荐: 'body&&.flex.wrap.border-box.list-b-hide;.public-list-box;.time-title&&title;img&&data-src;.public-prt.hide&&Text;a&&href',
       一级: '.public-r .public-pic-b;.time-title&&title;img&&data-src;.public-prt.hide&&Text;a&&href',
        二级: {
    title: '.detail-info.rel h3&&Text;.module-info-tag-link:eq(2)&&a:eq(3)&&Text',
    img: '.detail-pic&&img&&data-src',
    desc:  '.slide-info.hide:eq(1)&&Text;.slide-info.hide:eq(3)&&Text;.slide-info.hide:eq(0)&& span:eq(1) Text;.slide-info.hide:eq(2)&&Text;.slide-info.hide:eq(2)&&Text',
    content: '#height_limit&&Text',
    tabs: '.anthology-tab .swiper-wrapper a',
    lists: '.anthology-list-play.size:eq(#id) li',
  },
  搜索: 'json:list;name;pic;vod_remarks;id;vod_play_from',
}
