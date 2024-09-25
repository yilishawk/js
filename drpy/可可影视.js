var rule = {
  title: '可可影视',
  host: 'https://www.keke6.app/',
  url: '/show/fyclass-----3-fypage.html',
  searchUrl: '/search?os=pc&k=**',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
              headers: {//网站的请求头,完整支持所有的,常带ua和cookies
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; ) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.61 Chrome/126.0.6478.61 Not/A)Brand/8 Safari/537.36', // "Cookie": "searchneed=ok"
            },
      class_name:'电影&电视剧&短剧&综艺',//静态分类名称拼接
    class_url:'1&2&6&4',//静态分类标识拼接
  图片替换:'https://www.keke6.app/=>https://61.147.93.252:15002/',
  //class_parse: '.fs-margin.menu li:gt(1):lt(8);a&&Text;a&&href;/(\\d+)',
  tab_remove: ['4K(高峰不卡)'],
  tab_order:['蓝光①','自建1','黑采','YZ','LZ','FF','BF'],
  tab_rename:{'BF':'暴风','YZ':'优质','ZL':'自建1','LZ':'量子','FF':'非凡','HME':'黑采'},
  play_parse: true,
    lazy:`js:var html=JSON.parse(request(input).match(/r player_.*?=(.*?)</)[1]);
    log(html);
    var url=html.url;
    if(html.encrypt=='1'){
    url=unescape(url)
    }else if(html.encrypt=='2'){
    url=unescape(base64Decode(url))
    }
    if(/hmrvideo|ffzy|cdnlz|rrcdnbf3|playback|lyhuicheng/.test(url)){
    input={jx:0,url:'https://bfq.nnsvip.cn/player/ec.php?code=cj&if=1&url='+url,parse:1,header:JSON.stringify({'user-agent':'Mozilla/5.0'})}
    }else if(/qq|iqiyi/.test(url)){
    input={jx:0,url:'https://jx.m3u8.tv/jiexi/?url='+url,parse:1,header:JSON.stringify({'user-agent':'Mozilla/5.0'})}
    }else{
    input
    }`,
  limit: 6,
  double: true,
  推荐: '.swiper.myCarouselSwiper .swiper-slide;body a;.carousel-item-title&&Text;img&&data-original;.tag&&Text;a&&href',
  一级: '.module-item;img:eq(1)&&alt;img:eq(1)&&data-original;.v-item-bottom span:eq(1)&&Text;a&&href',
  二级: {
    title: 'strong:eq(2)&&Text;.detail-tags-item:eq(5)&&Text',
    img: '.detail-pic&&img&&data-original',
    desc: '.detail-info-row-main:eq(3)&&Text;.detail-tags-item&&Text;.detail-tags-item:eq(2)&&Text;.detail-info-row-main:eq(1)&&Text;.detail-info-row-main:eq(0)&&Text',
    content: '.detail-desc&&Text',
    tabs: '.swiper-slide.source-swiper-slide',
    lists: '.episode-list:eq(#id) a',
    tab_text: 'span:eq(1)&&Text',
  },
  搜索: '.search-result-item;img:eq(1)&&alt;img:eq(1)&&data-original;.v-item-bottom span:eq(1)&&Text;a&&href',
}
