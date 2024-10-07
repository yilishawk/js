var rule = {
  title: '西瓜',
  host: 'https://www.a6club.com/',
  //url: '/index.php/vod/show/id/fyclass/page/fypage.html',
  url: '/index.php/vod/show/fyfilter.html',
  searchUrl: '/index.php/vod/search/page/fypage/wd/**.html',
  searchable: 2,
  quickSearch: 0,
  filterable: 1,
  headers: {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.61 Chrome/126.0.6478.61 Not/A)Brand/8 Safari/537.36',
  },
  filter_url:'by/{{fl.by or "time"}}/id/{{fl.cateId}}/page/fypage/year/{{fl.year}}',
  	filter: {
		"20":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"20"},{"n":"喜剧片","v":"22"},{"n":"爱情片","v":"23"},{"n":"科幻片","v":"24"},{"n":"恐怖片","v":"25"},{"n":"剧情片","v":"26"},{"n":"战争片","v":"27"},{"n":"动画片","v":"31"},{"n":"冒险片","v":"30"},{"n":"犯罪片","v":"29"},{"n":"动作片","v":"21"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"37":[{"key":"cateId","name":"类型","value":[{"n":"全部","v":"37"},{"n":"国产剧","v":"38"},{"n":"港台剧","v":"39"},{"n":"日韩剧","v":"41"},{"n":"欧美剧","v":"40"}]},{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"3":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}],
		"4":[{"key":"year","name":"年份","value":[{"n":"全部","v":""},{"n":"2024","v":"2024"},{"n":"2023","v":"2023"},{"n":"2022","v":"2022"},{"n":"2021","v":"2021"},{"n":"2020","v":"2020"},{"n":"2019","v":"2019"},{"n":"2018","v":"2018"},{"n":"2017","v":"2017"},{"n":"2016","v":"2016"},{"n":"2015","v":"2015"},{"n":"2014","v":"2014"},{"n":"2013","v":"2013"},{"n":"2012","v":"2012"},{"n":"2011","v":"2011"},{"n":"2010","v":"2010"},{"n":"2009","v":"2009"},{"n":"2008","v":"2008"},{"n":"2007","v":"2007"},{"n":"2006","v":"2006"},{"n":"2005","v":"2005"},{"n":"2004","v":"2004"}]},{"key":"by","name":"排序","value":[{"n":"时间","v":"time"},{"n":"人气","v":"hits"},{"n":"评分","v":"score"}]}]
	},
	filter_def:{
                                38:{cateId:'38'},
		20:{cateId:'20'},
		37:{cateId:'37'},
		45:{cateId:'45'}
	},
    class_name:'国产剧&电视剧&电影&综艺',//静态分类名称拼接
    class_url:'38&37&20&45',//静态分类标识拼接
  //class_parse: '.border-shadow&&.movie-list-header;.movie-list-title&&Text;a&&href;.*/(.*?).html',
  play_parse: true,
  lazy:`js:
        var html = JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
        var url = html.url;
        if (html.encrypt == '1') {
            url = unescape(url)
        } else if (html.encrypt == '2') {
            url = unescape(base64Decode(url))
        }
        if (/\\.m3u8|\\.mp4/.test(url)) {
            input = {
                jx: 0,
                url: url,
                parse: 0
            }
        } else if (/youku|iqiyi|v\\.qq\\.com|pptv|sohu|le\\.com|1905\\.com|mgtv|bilibili|ixigua/.test(url)) {
            let play_Url = /bilibili/.test(url) ? 'https://pl.a6club.com/player/analysis.php?v=' : 'https://www.ckplayer.vip/jiexi/?url='; // type0的parse
            input = {
                jx: 0,
                url: url,
                playUrl: play_Url,
                parse: 1,
                header: JSON.stringify({
                    'user-agent': 'Mozilla/5.0',
                }),
            }
        } else {
            input
        }
    `,
  limit: 6,
  double: true,
  推荐: '.movie-list-body.flex;.movie-list-item;.movie-title.txtHide&&Text;.Lazy.br&&data-original;.movie-rating.cor4&&Text;a&&href',
  一级: '.movie-list-body&&.movie-list-item;.movie-title.txtHide&&Text;.Lazy.br&&data-original;.movie-rating.cor4&&Text;a&&href',
  二级: {
    title: 'h1.movie-title&&Text;.fed-deta-content&&.fed-part-rows&&li&&Text',
    img: '.poster&&img&&src',
    desc: '.fed-deta-content&&.fed-part-rows&&li:eq(1)&&Text;.fed-deta-content&&.fed-part-rows&&li:eq(2)&&Text;.fed-deta-content&&.fed-part-rows&&li:eq(3)&&Text',
    content: '.summary.detailsTxt&&Text',
    tabs: '#tag&&a',
    tab_text: '.titleName&&Text',
    lists: '.content_playlist.flex.wrap:eq(#id) li',
  },
  搜索: '.vod-search-list;.txtHide&&Text;.Lazy.br&&data-original;.cor4&&Text;a&&href;.fed-deta-content&&Text',
}
