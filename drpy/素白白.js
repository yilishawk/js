var rule = {
  title: '',
  host: 'https://subaibai.vip',
  hostJs: 'print(HOST);let html=request(HOST,{headers:{"User-Agent":PC_UA}});HOST = jsp.pdfh(html,".link&&a&&href");log(HOST);',
  url: '/fyclass/page/fypage',
  searchUrl: '/search?q=**',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  // 修正中文引号为英文（原内容实际已正确，此处保持原样）
  class_name: '国产剧&电影&电视剧&热门电影&高分电影&动漫电影&香港电影&欧美剧&港台剧', 
  class_url: 'domestic-drama&new-movie&tv-drama&hot-month&high-movie&cartoon-movie&hongkong-movie&american-drama&korean-drama',
  play_parse: true,
  lazy: `js:
const { input } = this;
let html, parsedUrl;
try {
  html = await request(input);
  // 检测 AES 加密（优先处理）
  if (html.includes('function dncry') && html.includes('md5.AES.decrypt')) {
    const keyMatch = html.match(/md5.enc.Utf8.parse\\("([^"]+)"\\)/g);
    const key = keyMatch[0].replace('md5.enc.Utf8.parse("', '');
    const iv = keyMatch[1].replace('md5.enc.Utf8.parse("', '').padEnd(16, '0').substr(0, 16);
    const encryptedData = html.match(/var\\s+[a-zA-Z0-9]+\\="([^"]+)/)[1];
    const decrypted = md5.AES.decrypt(encryptedData, md5.enc.Utf8.parse(key), {
      iv: md5.enc.Utf8.parse(iv),
      mode: md5.mode.CBC,
      padding: md5.pad.Pkcs7
    }).toString(md5.enc.Utf8);
    parsedUrl = decrypted.match(/"url":"([^"]+)"/)[1].replace(/\\\\/g, '');
  }
  // 处理基础加密类型（encrypt: 0/1/2）
  if (!parsedUrl) {
    const playerMatch = html.match(/var\\s+player_.+?=(\\{.*?});/);
    if (playerMatch) {
      const config = JSON.parse(playerMatch[1]);
      let { url, encrypt } = config;
      if (encrypt === '1') url = unescape(url);
      else if (encrypt === '2') url = unescape(base64Decode(url));
      parsedUrl = url;
    }
  }
  // 判断链接类型
  const isDirectUrl = /m3u8|mp4/.test(parsedUrl || input);
  return { parse: isDirectUrl ? 0 : 1, url: parsedUrl || input };
} catch (e) {
  return { parse: 1, url: input };
}`,  // 使用模板字符串优化多行字符串
  limit: 6,
  推荐: '.bt_img;ul&&li;.lazy&&alt;.lazy&&data-original;.jidi&&span&&Text;.dytit&&a&&href',
  double: true,
  一级: '.bt_img&&ul&&li;img&&alt;img&&data-original;.qb&&Text;a&&href',
  二级: {
    title: 'h1&&Text',
    img: '.dyimg&&img&&src',
    desc: '.moviedteail_list&&li:eq(1)&&a&&Text;.moviedteail_list&&li:eq(5)&&a&&title;.moviedteail_list&&li:eq(7)&&a&&title',
    content: '.yp_context&&Text',
    tabs: '.mi_paly_box .ypxingq_t',
    lists: '.paly_list_btn:eq(0) a' // 修正选择器索引
  },
  搜索: '.search_list&&ul&&li:eq(0);img&&alt;img&&data-original;.jidi&&Text;a&&href;.module-info-item-content&&Text'
}
