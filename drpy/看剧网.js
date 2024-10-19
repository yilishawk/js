var rule = {
  title: '',
  host: 'http://www.kanjuba.tv',
  //url: '/fyclass/indexfypage.html[/fyclass/index.html]',
  url: '/fyfilter/indexfypage.html[/fyfilter/index.html]',
  searchUrl: '/search.php?page=fypage&searchword=**&searchtype=',
  searchable: 0,
  quickSearch: 0,
  filterable: 1,
  filter_url:'{{fl.cateId}}',
  filter: {
  "dy": [
    {
      "key": "cateId",
      "name": "按分类",
      "value": [
        {
          "n": "全部",
          "v": "dy"
        },
        {
          "n": "动作片",
          "v": "dongzuo"
        },
        {
          "n": "爱情片",
          "v": "aiqing"
        },
        {
          "n": "科幻片",
          "v": "kehuan"
        },
        {
          "n": "恐怖片",
          "v": "kongbu"
        },
        {
          "n": "喜剧片",
          "v": "xiju"
        },
        {
          "n": "剧情片",
          "v": "juqing"
        }
      ]
    }
  ],
  "tv": [
    {
      "key": "cateId",
      "name": "按分类",
      "value": [
        {
          "n": "全部",
          "v": "tv"
        },
        {
          "n": "国产剧",
          "v": "guochan"
        },
        {
          "n": "港台剧",
          "v": "tangtai"
        },
        {
          "n": "欧美剧",
          "v": "oumei"
        },
        {
          "n": "日韩剧",
          "v": "rihan"
        }
      ]
    }
  ]
},
  	filter_def:{
    guochan:{cateId:'guochan'},
		dy:{cateId:'dy'},
		tv:{cateId:'tv'},
		zy:{cateId:'zy'},
    dm:{cateId:'dm'},
	},
  headers: {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-A536E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36 uacq',
    'referer': 'www.kanjuba.tv',
    'Host': 'www.kanjuba.tv',
    'sec-ch-ua-platform': 'iOS',
    'Cookie': 'recente2024=%5B%7B%22vod_name%22%3A%22%E5%94%90%E6%9C%9D%E8%AF%A1%E4%BA%8B%E5%BD%95%E4%B9%8B%E8%A5%BF%E8%A1%8C%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwenhi.com%2Fguochan%2Ftangchaoguishiluzhixixing%2Fplay-0-0.html%22%2C%22vod_part%22%3A%22%E7%AC%AC01%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%22%E5%9B%9B%E6%B5%B7%E9%87%8D%E6%98%8E%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwenhi.com%2Fguochan%2Fsihaizhongming%2Fplay-1-2.html%22%2C%22vod_part%22%3A%22%E7%AC%AC03%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%22%E5%B0%8F%E5%A4%AB%E5%A6%BB2024%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwenhi.com%2Fguochan%2Fxiaofuqi2024%2Fplay-0-0.html%22%2C%22vod_part%22%3A%22%E7%AC%AC01%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%22%E4%BB%99%E5%B8%9D%E5%BD%92%E6%9D%A5%E5%BD%93%E8%B5%98%E5%A9%BF%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwenhi.com%2Fguochan%2Fxiandiguilaidangzhuixu%2Fplay-0-2.html%22%2C%22vod_part%22%3A%22%E7%AC%AC03%E9%9B%86%22%7D%2C%7B%22vod_name%22%3A%22%E5%B9%B8%E7%A6%8F%E8%8D%89%22%2C%22vod_url%22%3A%22http%3A%2F%2Fwenhi.com%2Fguochan%2Fxingfucao%2Fplay-1-0.html%22%2C%22vod_part%22%3A%22%E7%AC%AC01%E9%9B%86%22%7D%5D; PHPSESSID=np5on3n30n0gugklfd2kpruut6',
  },
   //class_parse: 'ul.type-slide.clearfix li;a&&Text;a&&href;.*/(.*?)/index.html',
  class_name:'国产剧&电影&电视剧&动漫&综艺',
  class_url:'guochan&dy&tv&dm&zy',
  play_parse: true,
  tab_rename:{'奇艺视频':'琪琪云','优酷视频':'悠悠云','芒果视频':'果果云','腾讯视频':'腾腾云'},
lazy: "js:\n  let html = request(input);\n  let hconf = html.match(/r player_.*?=(.*?)</)[1];\n  let json = JSON5.parse(hconf);\n  let url = json.url;\n  if (json.encrypt == '1') {\n    url = unescape(url);\n  } else if (json.encrypt == '2') {\n    url = unescape(base64Decode(url));\n  }\n  if (/\\.(com/v2/m3u8?pt|pcvideoaliyun.titan.mgtv.com|m3u8|mp4|m4a|mp3)/.test(url)) {\n    input = {\n      parse: 0,\n      jx: 0,\n      url: url,\n    };\n  } else {\n    input = url && url.startsWith('http') && tellIsJx(url) ? {parse:0,jx:1,url:url}:input;\n  }",
  limit: 6,
  	    //sniffer:1,
    //辅助嗅探规则
    //isVideo:"http((?!http).){26,}\\.(com/v2/m3u8?pt=m3u8|pcvideoaliyun.titan.mgtv.com|m3u8|mp4|flv|avi|mkv|wmv|mpg|mpeg|mov|ts|3gp|rm|rmvb|asf|m4a|mp3|wma)",
  //cate_exclude:'国产剧|午夜剧场|wuyejuchang|xiezhen|伦理片|写真',
  推荐: 'ul.stui-vodlist.clearfix;li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
  double: true,
  一级: '.stui-vodlist.clearfix li;a&&title;a&&data-original;.pic-text&&Text;a&&href',
  二级: {
    title: 'h1&&Text;.stui-content__detail p:eq(3)&&a:eq(0)&&Text',
    img: '.stui-content__thumb .lazyload&&data-original',
    desc: '.stui-content__detail p:eq(0)&&Text;.stui-content__detail p:eq(3)&&a:eq(3)&&Text;.stui-content__detail p:eq(3)&&a:eq(2)&&Text',
    content: '.stui-content__detail p:eq()&&span:eq(1)&&Text',
    tabs: '.stui-pannel__head.bottom-line h3',
    lists: '.stui-pannel-box .stui-pannel_bd.col-pd.clearfix:eq(#id) li',
  },
  搜索: '.col-lg-wide-75 .stui-vodlist__media.col-pd.clearfix li;a&&title;.lazyload&&data-original;.pic-text.text-right&&Text;a&&href',
}
