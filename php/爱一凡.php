<?php
header('Content-Type: application/json; charset=utf-8');
error_reporting(0);

define('API_BASE', 'https://api.5ik.top');
define('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36');
define('CACHE_DIR', __DIR__ . '/cache/');
define('CACHE_TTL', 3600);

if (!is_dir(CACHE_DIR)) mkdir(CACHE_DIR, 0777, true);

function cache_get($k) {
    $f = CACHE_DIR . md5($k) . '.json';
    return file_exists($f) && (time() - filemtime($f)) < CACHE_TTL ? file_get_contents($f) : false;
}
function cache_set($k, $d) {
    file_put_contents(CACHE_DIR . md5($k) . '.json', $d);
}
function api_get($url, $cache = true) {
    if ($cache) {
        $c = cache_get($url);
        if ($c !== false) return $c;
    }
    $ch = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_USERAGENT => USER_AGENT,
        CURLOPT_HTTPHEADER => [
            'Origin: https://www.5ik.top',
            'Referer: https://www.5ik.top/',
            'Accept: application/json',
            'X-Requested-With: XMLHttpRequest'
        ]
    ]);
    $r = curl_exec($ch);
    curl_close($ch);
    if ($cache && $r) cache_set($url, $r);
    return $r ?: '';
}

$TYPE_MAP = ['movie' => 'movie', 'drama' => 'drama','variety' => 'variety', 'short' => 'short'];

// ==================== 搜索功能（支持普通搜索 + 快速搜索 quick=true） ====================
$extend = $_GET['extend'] ?? '';
$wd     = $_GET['wd'] ?? '';
$quick  = $_GET['quick'] ?? '';

if ($extend === '' && !empty($wd)) {
    $keyword = trim($wd);
    $search_url = API_BASE . "/api/list/gettitlegetdata?SearchCriteria=" . urlencode($keyword);
    $json = api_get($search_url, !empty($quick));
    $data = json_decode($json, true);

    $list = [];
    if ($data && $data['ret'] == 200 && !empty($data['data']['list'])) {
        foreach ($data['data']['list'] as $v) {
            $list[] = [
                "vod_id"      => $v['mediaKey'],
                "vod_name"    => $v['title'] ?? '未知标题',
                "vod_pic"     => $v['coverImgUrl'] ?? '',
                "vod_remarks" => $v['updateStatus'] ?? $v['regional'] ?? '5ik影视'
            ];
        }
    }
    echo json_encode(["list" => $list], JSON_UNESCAPED_UNICODE);
    exit;
}

// ==================== 播放解析（已修复编码/未编码双兼容） ====================
$flag = $_GET['flag'] ?? '';
$rawPlayParam = $_GET['play'] ?? '';
$episodeId = $_GET['episodeId'] ?? $_GET['ep'] ?? '';

$mediaKey = '';

if (!empty($flag) && $flag !== '默认线路') {
    echo json_encode(["url"=>"","parse"=>0,"jx"=>0,"error"=>"只支持flag=默认线路"], JSON_UNESCAPED_UNICODE);
    exit;
}

if ($flag === '默认线路' && !empty($rawPlayParam)) {
    if (!empty($episodeId)) {
        $mediaKey = $rawPlayParam;
    }
    elseif (strpos($rawPlayParam, '%26') !== false || strpos($rawPlayParam, '&') !== false) {
        $decodedValue = urldecode($rawPlayParam);
        $paramPairs = explode('&', $decodedValue);
        $mediaKey = $paramPairs[0];
        for ($i = 1; $i < count($paramPairs); $i++) {
            if (strpos($paramPairs[$i], '=') !== false) {
                list($k, $v) = explode('=', $paramPairs[$i], 2);
                if ($k == 'episodeId' || $k == 'ep') {
                    $episodeId = $v;
                    break;
                }
            }
        }
    }
}

if ($flag === '默认线路' && $mediaKey && $episodeId) {
    $play_url = API_BASE . "/api/video/getplaydata"
        . "?mediaKey=" . urlencode($mediaKey)
        . "&videoId=" . $episodeId
        . "&videoType=1&liveLine=&System=h5&AppVersion=1.0&SystemVersion=h5&version=H3"
        . "&DeviceId=13ad12e02b9933302c87f6e7872a9068"
        . "&i18n=0&uid=129507530&gid=1"
        . "&token=1234bc0965e4440b81befc8838a4f2c7"
        . "&sign=22123479cbcf4be629ab18f9bd1b7d48c4fddb2aaf3e42f5b4f31061b2d0e6b2_5f049e480273981058544501dad7d50f"
        . "&expire=1764839454.49322&login_uid=129507530&pub=1764645066&vv=17d6334e4fdee80ffeecbe07991f1288";

    $json = api_get($play_url, false);
    $data = json_decode($json, true);

    if ($data && $data['ret'] == 200 && !empty($data['data']['list'])) {
        $candidates = array_filter($data['data']['list'], fn($item) => !empty(trim($item['mediaUrl'] ?? '')));
        if (!empty($candidates)) {
            usort($candidates, fn($a,$b) => ($b['resolution']??0) <=> ($a['resolution']??0));
            $real_url = $candidates[0]['mediaUrl'];
            echo json_encode([
                "header" => json_encode(["User-Agent"=>USER_AGENT,"Referer"=>"https://www.5ik.top/"]),
                "url" => $real_url,
                "parse" => 0,
                "jx" => 0
            ], JSON_UNESCAPED_UNICODE);
            exit;
        }
    }
    echo json_encode(["url"=>"","parse"=>0,"jx"=>0], JSON_UNESCAPED_UNICODE);
    exit;
}

// ==================== 分类列表（新增二级过滤支持） ====================
$ac = $_GET['ac'] ?? '';
$t  = $_GET['t'] ?? '';
$pg = max(1, (int)($_GET['pg'] ?? 1));
$subcat = $_GET['subcat'] ?? 0;  // 新增：二级分类 ID
$ext = $_GET['ext'] ?? '';  // 忽略 ext

if (!empty($ext)) {
    error_log("Ext param ignored: $ext");
}

if ($ac === 'detail' && isset($TYPE_MAP[$t])) {
    $titleid = $TYPE_MAP[$t];
    $secondary_code = $titleid;  // 用于 getfiltertagsdata

    // 如果有 subcat，调用过滤列表 API
    if (!empty($subcat) && $subcat != 0) {
        $api = API_BASE . "/api/list/getconditionfilterdata?titleid={$titleid}&classifyId={$subcat}&page={$pg}&size=24";
    } else {
        $api = API_BASE . "/api/list/getconditionfilterdata?titleid={$titleid}&page={$pg}&size=24";
    }
    $json = api_get($api);
    $res = json_decode($json, true);
    $list = [];
    if ($res && $res['ret'] == 200 && !empty($res['data']['list'])) {
        foreach ($res['data']['list'] as $v) {
            $list[] = [
                "vod_id"      => $v['mediaKey'],
                "vod_name"    => $v['title'],
                "vod_pic"     => $v['coverImgUrl'],
                "vod_remarks" => $v['updateStatus'] ?: ($v['updateMsg'] ?? '')
            ];
        }
    }
    echo json_encode(["list" => $list], JSON_UNESCAPED_UNICODE);
    exit;
}

// ==================== 详情页 ====================
$ids = $_GET['ids'] ?? '';
if ($ac === 'detail' && $ids !== '') {
    $url = API_BASE . "/api/video/videodetails?autoplay=false&mediaKey=" . urlencode($ids) . "&System=h5&AppVersion=1.0&SystemVersion=h5&version=H3";
    $json = api_get($url);
    $res = json_decode($json, true);
    if (!$res || $res['ret'] != 200 || empty($res['data']['detailInfo'])) {
        echo json_encode(["list" => []]);
        exit;
    }
    $info = $res['data']['detailInfo'];
    $episodes = $info['episodes'] ?? [];
    $play_urls = [];
    foreach ($episodes as $ep) {
        $title = $ep['episodeTitle'] ?? '第' . (count($play_urls) + 1) . '集';
        $link = urlencode($ids) . "&episodeId=" . $ep['episodeId'];
        $play_urls[] = "$title$$link";
    }
    $result = [
        "vod_id" => $ids,
        "vod_name" => $info['title'] ?? '未知',
        "vod_pic" => $info['coverImgUrl'] ?? '',
        "type_name" => $info['typeName'] ?? '',
        "vod_year" => '',
        "vod_area" => $info['regional'] ?? '',
        "vod_remarks" => $info['updateStatus'] ?? '',
        "vod_actor" => $info['actor'] ?? $info['starring'] ?? '',
        "vod_director" => $info['director'] ?? '',
        "vod_content" => trim(preg_replace('/\s+/', ' ', strip_tags($info['introduce'] ?? ''))),
        "vod_play_from" => "默认线路",
        "vod_play_url" => implode("#", $play_urls)
    ];
    echo json_encode(["list" => [$result]], JSON_UNESCAPED_UNICODE);
    exit;
}

// ==================== 首页分类 ====================
$class = [
    ["type_id" => "drama", "type_name" => "电视剧"],
    ["type_id" => "movie", "type_name" => "电影"],
    ["type_id" => "short", "type_name" => "短剧"],
    ["type_id" => "variety", "type_name" => "综艺"]
];
echo json_encode(["code" => 1, "msg" => "ok", "class" => $class], JSON_UNESCAPED_UNICODE);
?>