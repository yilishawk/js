<?php
header('Content-Type: application/json; charset=utf-8');
error_reporting(E_ALL);
ini_set('display_errors', 1);

// ============================ 配置区域 - 需要修改 ============================
// 网站基础配置
define('BASE_URL', 'https://example.com'); // 修改为目标网站域名
define('SITE_NAME', '示例网站'); // 修改为网站名称
define('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36');

// 缓存配置
define('CACHE_DIR', __DIR__ . '/cache/');
define('CACHE_TTL', 3600); // 缓存时间(秒)
define('LOG_FILE', __DIR__ . '/parser_log.txt');

// 分类配置 - 根据目标网站分类修改
$categories = [
    ['type_id' => 'movie', 'type_name' => '电影'],
    ['type_id' => 'tv', 'type_name' => '电视剧'],
    ['type_id' => 'cartoon', 'type_name' => '动漫'],
    ['type_id' => 'variety', 'type_name' => '综艺']
];

// XPath配置 - 根据目标网站HTML结构修改
$xpath_config = [
    // 列表页配置
    'list' => [
        'items' => "//div[@class='video-list']//div[@class='item']", // 视频项容器
        'title' => ".//h3/a/text()", // 标题
        'link' => ".//h3/a/@href", // 详情页链接
        'image' => ".//img/@src", // 封面图
        'remarks' => ".//span[@class='update']/text()", // 更新状态/备注
    ],
    
    // 详情页配置
    'detail' => [
        'title' => "//h1[@class='title']/text()", // 标题
        'image' => "//div[@class='poster']/img/@src", // 封面图
        'year' => "//span[contains(text(),'年份')]/following-sibling::text()", // 年份
        'area' => "//span[contains(text(),'地区')]/following-sibling::text()", // 地区
        'type' => "//span[contains(text(),'类型')]/following-sibling::text()", // 类型
        'actor' => "//span[contains(text(),'演员')]/following-sibling::text()", // 演员
        'director' => "//span[contains(text(),'导演')]/following-sibling::text()", // 导演
        'description' => "//div[@class='description']/text()", // 简介
        'status' => "//span[contains(text(),'状态')]/following-sibling::text()", // 状态
    ],
    
    // 播放列表配置
    'playlist' => [
        'sources' => "//div[@class='play-source']//li", // 播放源
        'source_name' => ".//text()", // 播放源名称
        'episodes' => ".//ul/li/a", // 剧集列表
        'episode_name' => "./text()", // 剧集名称
        'episode_url' => "./@href", // 剧集链接
    ],
    
    // 搜索页配置
    'search' => [
        'items' => "//div[@class='search-result']//div[@class='item']", // 搜索结果项
        'title' => ".//h3/a/text()", // 标题
        'link' => ".//h3/a/@href", // 链接
        'image' => ".//img/@src", // 图片
        'remarks' => ".//span[@class='type']/text()", // 备注
    ]
];

// 分类URL映射 - 根据目标网站URL结构修改
$category_urls = [
    'movie' => "/movie/list/{page}.html",
    'tv' => "/tv/list/{page}.html", 
    'cartoon' => "/cartoon/list/{page}.html",
    'variety' => "/variety/list/{page}.html"
];

// 搜索URL - 根据目标网站搜索URL修改
$search_url = "/search?keyword={keyword}&page={page}";

// ============================ 核心函数 - 一般不需要修改 ============================
// 确保目录存在
function ensure_dir($dir) {
    if (!is_dir($dir)) {
        mkdir($dir, 0777, true);
        chmod($dir, 0777);
    }
}

// 日志记录
function log_message($message) {
    $timestamp = date('Y-m-d H:i:s');
    $log_entry = "[$timestamp] $message" . PHP_EOL;
    file_put_contents(LOG_FILE, $log_entry, FILE_APPEND);
}

// URL处理函数
function normalize_url($url, $base_url = BASE_URL) {
    if (empty($url)) return '';
    
    // 已经是完整URL
    if (preg_match('/^(https?:|data:)/i', $url)) return $url;
    
    // 协议相对URL
    if (substr($url, 0, 2) === '//') return 'https:' . $url;
    
    // 相对URL
    if (substr($url, 0, 1) === '/') return $base_url . $url;
    
    // 其他情况
    return $base_url . '/' . ltrim($url, '/');
}

// 缓存函数
function get_cache($key) {
    $cache_file = CACHE_DIR . md5($key) . '.cache';
    if (file_exists($cache_file) && time() - filemtime($cache_file) < CACHE_TTL) {
        return file_get_contents($cache_file);
    }
    return false;
}

function set_cache($key, $data) {
    ensure_dir(CACHE_DIR);
    $cache_file = CACHE_DIR . md5($key) . '.cache';
    return file_put_contents($cache_file, $data);
}

// 获取页面内容
function fetch_page($url, $use_cache = false) {
    $cache_key = $url;
    
    if ($use_cache) {
        $cached = get_cache($cache_key);
        if ($cached !== false) {
            log_message("使用缓存: $url");
            return $cached;
        }
    }
    
    log_message("获取页面: $url");
    
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_USERAGENT => USER_AGENT,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 10,
        CURLOPT_ENCODING => 'gzip,deflate'
    ]);
    
    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $error = curl_error($ch);
    curl_close($ch);
    
    if ($error) {
        log_message("CURL错误: $error - $url");
        throw new Exception("网络请求失败: $error");
    }
    
    if ($http_code >= 400) {
        log_message("HTTP错误: $http_code - $url");
        throw new Exception("页面访问失败，状态码: $http_code");
    }
    
    if ($use_cache) {
        set_cache($cache_key, $response);
    }
    
    return $response;
}

// XPath解析
function parse_xpath($html, $xpath_queries, $context = null) {
    $dom = new DOMDocument();
    @$dom->loadHTML(mb_convert_encoding($html, 'HTML-ENTITIES', 'UTF-8'));
    $xpath = new DOMXPath($dom);
    
    $result = [];
    
    foreach ($xpath_queries as $key => $query) {
        if ($context) {
            $nodes = $xpath->query($query, $context);
        } else {
            $nodes = $xpath->query($query);
        }
        
        if ($nodes && $nodes->length > 0) {
            if (strpos($key, '[]') !== false) {
                // 数组类型结果
                $clean_key = str_replace('[]', '', $key);
                $result[$clean_key] = [];
                foreach ($nodes as $node) {
                    $result[$clean_key][] = trim($node->nodeValue);
                }
            } else {
                // 单个结果
                $result[$key] = trim($nodes->item(0)->nodeValue);
            }
        } else {
            $result[$key] = '';
        }
    }
    
    return $result;
}

// 提取视频ID
function extract_vod_id($url) {
    $parsed = parse_url($url);
    $path = $parsed['path'] ?? '';
    
    // 尝试从URL路径中提取ID
    if (preg_match('/(\d+)\.html$/', $path, $matches)) {
        return 'vod_' . $matches[1];
    }
    
    // 备用方案：使用MD5
    return 'vod_' . md5($url);
}

// 生成视频列表
function generate_video_list($data) {
    global $xpath_config;
    
    $list = [];
    
    foreach ($data['items'] as $item) {
        $parsed = parse_xpath($item, $xpath_config['list'], $item);
        
        $vod_id = extract_vod_id($parsed['link']);
        $vod_name = $parsed['title'] ?? '未知标题';
        $vod_pic = normalize_url($parsed['image'] ?? '');
        $vod_remarks = $parsed['remarks'] ?? '';
        
        $list[] = [
            'vod_id' => $vod_id,
            'vod_name' => $vod_name,
            'vod_pic' => $vod_pic,
            'vod_remarks' => $vod_remarks
        ];
    }
    
    return ['list' => $list];
}

// 生成视频详情
function generate_video_detail($data) {
    global $xpath_config;
    
    $parsed = parse_xpath($data['html'], $xpath_config['detail']);
    
    $vod_id = $data['vod_id'];
    $vod_name = $parsed['title'] ?? '未知标题';
    $vod_pic = normalize_url($parsed['image'] ?? '');
    $vod_year = $parsed['year'] ?? '';
    $vod_area = $parsed['area'] ?? '';
    $type_name = $parsed['type'] ?? '';
    $vod_actor = $parsed['actor'] ?? '';
    $vod_director = $parsed['director'] ?? '';
    $vod_content = $parsed['description'] ?? '暂无简介';
    $vod_remarks = $parsed['status'] ?? '';
    
    // 解析播放列表
    $play_from = [];
    $play_url = [];
    
    $source_nodes = $xpath_config['playlist']['sources'] ? 
        (new DOMXPath($data['dom']))->query($xpath_config['playlist']['sources']) : [];
    
    foreach ($source_nodes as $source_index => $source_node) {
        $source_name = parse_xpath($source_node, ['name' => $xpath_config['playlist']['source_name']], $source_node)['name'] ?? 
                      "播放源" . ($source_index + 1);
        
        $episodes = [];
        $episode_nodes = (new DOMXPath($data['dom']))->query($xpath_config['playlist']['episodes'], $source_node);
        
        foreach ($episode_nodes as $ep_index => $ep_node) {
            $ep_name = parse_xpath($ep_node, ['name' => $xpath_config['playlist']['episode_name']], $ep_node)['name'] ?? 
                      "第" . ($ep_index + 1) . "集";
            $ep_url = parse_xpath($ep_node, ['url' => $xpath_config['playlist']['episode_url']], $ep_node)['url'] ?? '';
            
            if ($ep_url) {
                $episodes[] = $ep_name . "$" . normalize_url($ep_url);
            }
        }
        
        if (!empty($episodes)) {
            $play_from[] = $source_name;
            $play_url[] = implode("#", $episodes);
        }
    }
    
    // 如果没有解析到播放列表，使用默认播放地址
    if (empty($play_from)) {
        $play_from[] = "默认播放源";
        $play_url[] = "正片$" . $data['url'];
    }
    
    return ['list' => [[
        'type_name' => $type_name,
        'vod_id' => $vod_id,
        'vod_name' => $vod_name,
        'vod_remarks' => $vod_remarks,
        'vod_year' => $vod_year,
        'vod_area' => $vod_area,
        'vod_actor' => $vod_actor,
        'vod_director' => $vod_director,
        'vod_content' => $vod_content,
        'vod_play_from' => implode('$$$', $play_from),
        'vod_play_url' => implode('$$$', $play_url)
    ]]];
}

// 生成分类列表
function generate_categories() {
    global $categories;
    
    return [
        'code' => 1,
        'msg' => SITE_NAME . ' - 分类列表',
        'class' => $categories
    ];
}

// ============================ 主逻辑 - 一般不需要修改 ============================
try {
    $request_uri = $_SERVER['REQUEST_URI'];
    log_message("请求开始: $request_uri");
    
    // 播放地址接口
    $flag = $_GET['flag'] ?? '';
    $play_url = $_GET['play'] ?? '';
    if (!empty($flag) && !empty($play_url)) {
        log_message("播放地址请求: flag=$flag, play=$play_url");
        
        $response = [
            'header' => json_encode(['User-Agent' => USER_AGENT]),
            'url' => $play_url,
            'parse' => 0,
            'jx' => 0
        ];
        
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }
    
    // 搜索接口
    $keyword = $_GET['wd'] ?? '';
    if (!empty($keyword)) {
        log_message("搜索请求: 关键词=$keyword");
        $page = max(1, intval($_GET['page'] ?? 1));
        
        $search_url_filled = str_replace(
            ['{keyword}', '{page}'], 
            [urlencode($keyword), $page], 
            $search_url
        );
        
        $html = fetch_page(BASE_URL . $search_url_filled, true);
        $dom = new DOMDocument();
        @$dom->loadHTML(mb_convert_encoding($html, 'HTML-ENTITIES', 'UTF-8'));
        
        $xpath = new DOMXPath($dom);
        $items = $xpath->query($xpath_config['search']['items']);
        
        $data = ['items' => []];
        foreach ($items as $item) {
            $data['items'][] = $item;
        }
        
        $response = generate_video_list($data);
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }
    
    // 列表接口
    $ac = $_GET['ac'] ?? '';
    $category = $_GET['t'] ?? '';
    $page = max(1, intval($_GET['pg'] ?? 1));
    
    if ($ac === 'detail' && !empty($category)) {
        log_message("列表请求: t=$category, pg=$page");
        
        if (!isset($category_urls[$category])) {
            throw new Exception("无效的分类: $category");
        }
        
        $list_url = str_replace('{page}', $page, $category_urls[$category]);
        $html = fetch_page(BASE_URL . $list_url, true);
        $dom = new DOMDocument();
        @$dom->loadHTML(mb_convert_encoding($html, 'HTML-ENTITIES', 'UTF-8'));
        
        $xpath = new DOMXPath($dom);
        $items = $xpath->query($xpath_config['list']['items']);
        
        $data = ['items' => []];
        foreach ($items as $item) {
            $data['items'][] = $item;
        }
        
        $response = generate_video_list($data);
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }
    
    // 详情接口
    $vod_id = $_GET['ids'] ?? '';
    if ($ac === 'detail' && !empty($vod_id)) {
        log_message("详情请求: ids=$vod_id");
        
        // 从vod_id中提取原始URL或构建详情页URL
        // 这里需要根据实际情况实现，以下为示例
        $detail_url = BASE_URL . "/detail/" . str_replace('vod_', '', $vod_id) . ".html";
        
        $html = fetch_page($detail_url, true);
        $dom = new DOMDocument();
        @$dom->loadHTML(mb_convert_encoding($html, 'HTML-ENTITIES', 'UTF-8'));
        
        $data = [
            'html' => $html,
            'dom' => $dom,
            'vod_id' => $vod_id,
            'url' => $detail_url
        ];
        
        $response = generate_video_detail($data);
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }
    
    // 默认返回分类列表
    log_message("默认请求: 返回分类列表");
    $response = generate_categories();
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    
} catch (Exception $e) {
    $errorMsg = "错误: " . $e->getMessage() . " (代码: " . $e->getCode() . ")";
    log_message($errorMsg);
    $response = [
        'code' => $e->getCode() ?: 500,
        'msg' => $e->getMessage(),
        'error' => true
    ];
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
}
?>