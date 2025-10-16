globalThis.verifyLogin = function (url) {
  let cnt = 0;
  let cookie = '';
  let r = Math.random();
  let yzm_url = getHome(url) + '/index.php/verify/index.html';
  log(`验证码链接:${yzm_url}`);
  let submit_url = getHome(url) + '/index.php/ajax/verify_check';
  log(`post登录链接:${submit_url}`);
  while (cnt < OCR_RETRY) {
    try {
      let { cookie, html } = reqCookie(yzm_url + '?r=' + r, { toBase64: true });
      let code = OcrApi.classification(html);
      log(`第${cnt + 1}次验证码识别结果:${code}`);
      html = post(submit_url, {
        headers: { Cookie: cookie },
        body: 'type=search&verify=' + code,
      });
      html = JSON.parse(html);

      if (html.code === 1) {
        log(`第${cnt + 1}次验证码提交成功`);
        log(cookie);
        return cookie // 需要返回cookie
      } else if (html.code !== 1 && cnt + 1 >= OCR_RETRY) {
        cookie = ''; // 需要清空返回cookie
      }
    } catch (e) {
      log(`第${cnt + 1}次验证码提交失败:${e.message}`);
      if (cnt + 1 >= OCR_RETRY) {
        cookie = '';
      }
    }
    cnt += 1
  }
  return cookie
};

globalThis.getrandom = function (word) {
  function getrandom(url) {
    const string = url.substring(8, url.length);
    const substr = pipibase64_decode(string);
    return UrlDecode(substr.substring(8, (substr.length) - 8));
  }
  function UrlDecode(zipStr) {
    var uzipStr = "";
    for (var i = 0; i < zipStr.length; i++) {
      var chr = zipStr.charAt(i);
      if (chr == "+") {
        uzipStr += " ";
      } else if (chr == "%") {
        var asc = zipStr.substring(i + 1, i + 3);
        if (parseInt("0x" + asc) > 0x7f) {
          uzipStr += decodeURI("%" + asc.toString() + zipStr.substring(i + 3, i + 9).toString());
          i += 8;
        } else {
          uzipStr += AsciiToString(parseInt("0x" + asc));
          i += 2;
        }
      } else {
        uzipStr += chr;
      }
    }

    return uzipStr;
  }
  function StringToAscii(str) {
    return str.charCodeAt(0).toString(16);
  }
  function AsciiToString(asccode) {
    return String.fromCharCode(asccode);
  }
  function pipibase64_decode(data) {
    var b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";
    var o1, o2, o3, h1, h2, h3, h4, bits, i = 0,
      ac = 0,
      dec = "",
      tmp_arr = [];
    if (!data) {
      return data;
    }
    data += '';
    do { // unpack four hexets into three octets using index points in b64
      h1 = b64.indexOf(data.charAt(i++));
      h2 = b64.indexOf(data.charAt(i++));
      h3 = b64.indexOf(data.charAt(i++));
      h4 = b64.indexOf(data.charAt(i++));
      bits = h1 << 18 | h2 << 12 | h3 << 6 | h4;
      o1 = bits >> 16 & 0xff;
      o2 = bits >> 8 & 0xff;
      o3 = bits & 0xff;
      if (h3 == 64) {
        tmp_arr[ac++] = String.fromCharCode(o1);
      } else if (h4 == 64) {
        tmp_arr[ac++] = String.fromCharCode(o1, o2);
      } else {
        tmp_arr[ac++] = String.fromCharCode(o1, o2, o3);
      }
    } while (i < data.length);
    dec = tmp_arr.join('');
    return dec;
  }
  return getrandom(word)
};

var rule = {
  title: '耐看',
  host: 'https://nkvod.com',
  url: '/show/fyclass-----------.html',
  searchUrl: '/nk/-------------.html?wd=**',
    detailUrl: '/detail/fyid.html',
  searchable: 2,
  quickSearch: 0,
  filterable: 0,
  filter: '',
  filter_url: '',
  filter_def: {},
  headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.6788.76 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
   },
  timeout: 5000,
  class_parse: '.swiper-wrapper&&li;a&&Text;a&&href;.*/(.*?)-----------.html',
  cate_exclude: '首页|更多',
  play_parse: true,
  double: false,
  预处理: $js.toString(() => {
    let html = request(rule.host);
    let scripts = pdfa(html, 'script');
    let img_script = scripts.find(it => pdfh(it, 'script&&src').includes('rdul.js'));
    if (img_script) {
      let img_url = img_script.match(/src="(.*?)"/)[1];
      let img_html = request(img_url);
      let img_host = img_html.match(/'(.*?)'/)[1];
      rule.图片替换 = rule.host + '=>' + img_host;
    }
  }),
  推荐: $js.toString(() => {
    const html = request(input, { headers: rule.headers });
    let d = [];
    let data = pdfa(html, 'body&&.public-list-box');
    data.forEach((it) => {
      d.push({
        title: pdfh(it, 'a&&title'),
        pic_url: pd(it, 'img&&data-src'),
        desc: pdfh(it, '.public-list-subtitle&&Text'),
        url: /detail\/(.*?)\.html/g.exec(pd(it, 'a&&href'))[1],
      })
    });
    setResult(d);
  }),
  一级: $js.toString(() => {
const pg = MY_PAGE; // 页面参数
const tid = MY_CATE; // 分类参数
const timestamp = Math.ceil(new Date().getTime() / 1000); // 当前时间戳（秒级）

// 加密密钥生成函数
const encodeKey = (timestamp) => {
  const salt = 'DCC147D11943AF75'; // 固定盐值
  const str = `DS${timestamp}`; // 拼接时间戳
  const res = CryptoJS.MD5(`${str}${salt}`).toString(); // MD5 加密
  return res;
};

// 请求的 URL
const url = `${rule.host}/index.php/api/vod`;

// 构造请求体
const requestBody = {
  type: tid,
  class: '', // 根据需要设置
  area: '', // 根据需要设置
  lang: '', // 根据需要设置
  version: '', // 根据需要设置
  state: '', // 根据需要设置
  letter: '', // 根据需要设置
  page: pg,
  time: timestamp,
  key: encodeKey(timestamp),
};

// 发起 POST 请求
const html_str = post(url, {
  headers: rule.headers,
  body: requestBody,
});

// 解析响应数据
const resp = JSON.parse(html_str);
const data = resp.list || []; // 确保有默认值
const d = []; // 存储格式化后的数据

data.forEach((it) => {
  d.push({
    title: it.vod_name,
    pic_url: it.vod_pic,
    desc: it.vod_remarks,
    url: it.vod_id,
  });
});

// 设置结果
setResult(d);
  }),
二级: $js.toString(() => {
    // 检查 rule.host 是否已经包含 "/detail/" 或 ".html"
    const url = `${rule.host}${rule.host.includes('/detail/') ? '' : '/detail/'}${orId}${rule.host.includes('.html') ? '' : '.html'}`;
    const html = request(url, { headers: rule.headers });

    let playFroms = pdfa(html, '.anthology-tab a').map(item => pdfh(item, "a--span&&Text"));
    let playUrls = [];
    const indexList = pdfa(html, '.anthology-list .anthology-list-box');

    indexList.forEach((lines) => {
        const tmpUrls = [];
        const line = pdfa(lines, 'ul.anthology-list-play li.box');
        line.forEach((play) => {
            const index = pdfh(play, 'a&&Text');
            const url = pdfh(play, 'a&&href');
            tmpUrls.push(`${index}$${url}`);
        });
        playUrls.push(tmpUrls.join('#'));
    });
    const d = {
      vod_name: pdfh(html, 'h3.slide-info-title.hide&&Text'),
      vod_pic: pdfh(html, '.mask-1&&data-src'),
      vod_content: pdfh(html, '#height_limit&&Text'),
      vod_play_from: playFroms.join('$$$'),
      vod_play_url: playUrls.join('$$$'),
    }
    VOD = d;
  }),
  搜索: '.public-list-box;.thumb-txt.cor4.hide&&Text;img:eq(-1)&&data-src;a&&Text;.public-list-exp&&href;/(\\d+)',
  lazy: $js.toString(() => {
    // 1. 获取 player_aaa 参数
    const url = `${rule.host}${input}`;
    const html = request(url);
    const script = pdfa(html, '.player-left script');
    const scriptContent = script.filter((e) => e.includes("player_aaaa"))[0];
    const scriptRegex = /var player_aaaa=({[^;]+})/;
    const scriptMatch = scriptContent.match(scriptRegex);
    if (!scriptMatch || !scriptMatch[1]) {
      input = { url, parse: 1 }
    };
    const player_aaaa = JSON.parse(scriptMatch[1]);

    // 2.获取播放器链接
    const playerUrl = `https://op.xn--it-if7c19g5s4bps5c.com/pi.php?url=${player_aaaa.url}`;
    const playerHtml = request(playerUrl);
    const playerScript = pdfa(playerHtml, 'body script');
    const playerScriptContent = playerScript.filter((e) => e.includes("config"))[0];
    const playerScriptRegex = /var config = ({[^;]+})/;
    const playerScriptMatch = playerScriptContent.match(playerScriptRegex);
    if (!playerScriptMatch || !playerScriptMatch[1]) {
      input = { url, parse: 1 }
    };
    const playerConfigStr = playerScriptMatch[1];
    const playerConfigJson = new Function(`return ${playerConfigStr}`)();
    const realUrl = playerConfigJson.url;

    if (/m3u8|mp4|flv|mpd/.test(realUrl)) {
      input = { url: realUrl, parse: 0 }
    } else {
      input = { url, parse: 1 }
    }
  })
}
