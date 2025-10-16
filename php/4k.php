<?php
header('Content-Type: application/json; charset=utf-8');
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 基础常量定义
define('BASE_URL', 'https://www.4kvm.org');
define('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');
define('LOG_FILE', __DIR__ . '/parser_log.txt');
define('CACHE_DIR', __DIR__ . '/cache/');
define('REAL_URL_CACHE_DIR', __DIR__ . '/real_url_cache/');
define('CACHE_TTL', 3600);
define('REAL_URL_CACHE_TTL', 86400); // 24小时缓存
define('COOKIE_FILE', __DIR__ . '/4kvm_cookie.txt');

// 确保缓存目录存在
function ensure_cache_dir() {
    if (!is_dir(CACHE_DIR)) {
        mkdir(CACHE_DIR, 0777, true);
    }
    if (!is_dir(REAL_URL_CACHE_DIR)) {
        mkdir(REAL_URL_CACHE_DIR, 0777, true);
    }
}

// 日志记录函数
function log_message($message) {
    $timestamp = date('Y-m-d H:i:s');
    $log_entry = "[$timestamp] $message" . PHP_EOL;
    file_put_contents(LOG_FILE, $log_entry, FILE_APPEND);
}

// 真实URL缓存函数
function get_real_url_cache($key) {
    $cache_file = REAL_URL_CACHE_DIR . md5($key) . '.cache';
    if (file_exists($cache_file) && time() - filemtime($cache_file) < REAL_URL_CACHE_TTL) {
        return file_get_contents($cache_file);
    }
    return false;
}

function set_real_url_cache($key, $data) {
    ensure_cache_dir();
    $cache_file = REAL_URL_CACHE_DIR . md5($key) . '.cache';
    return file_put_contents($cache_file, $data);
}

// 批量获取真实详情页地址（并发处理）
function batch_get_real_detail_urls($urls) {
    log_message("batch_get_real_detail_urls: 开始批量处理 " . count($urls) . " 个URL");
    
    $results = [];
    $mh = curl_multi_init();
    $handles = [];
    
    // 创建所有curl句柄
    foreach ($urls as $index => $url) {
        // 先检查缓存
        $cached_url = get_real_url_cache($url);
        if ($cached_url !== false) {
            $results[$index] = $cached_url;
            log_message("batch_get_real_detail_urls: 缓存命中 - $url -> $cached_url");
            continue;
        }
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_USERAGENT, USER_AGENT);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
        curl_setopt($ch, CURLOPT_TIMEOUT, 8);
        curl_setopt($ch, CURLOPT_HEADER, false);
        
        $handles[$index] = $ch;
        curl_multi_add_handle($mh, $ch);
    }
    
    // 如果没有需要处理的URL，直接返回
    if (empty($handles)) {
        curl_multi_close($mh);
        return $results;
    }
    
    // 执行并发请求
    $running = null;
    do {
        curl_multi_exec($mh, $running);
        curl_multi_select($mh);
    } while ($running > 0);
    
    // 处理所有响应
    foreach ($handles as $index => $ch) {
        $original_url = $urls[$index];
        $html = curl_multi_getcontent($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        
        if ($http_code === 200 && !empty($html)) {
            $real_url = parse_real_url_from_html($html, $original_url);
            if ($real_url) {
                // 缓存结果
                set_real_url_cache($original_url, $real_url);
                $results[$index] = $real_url;
                log_message("batch_get_real_detail_urls: 解析成功 - $original_url -> $real_url");
            } else {
                // 解析失败，使用兜底方案
                $fallback_url = str_replace('/tvshows/', '/seasons/', $original_url);
                $results[$index] = $fallback_url;
                log_message("batch_get_real_detail_urls: 解析失败，使用兜底 - $fallback_url");
            }
        } else {
            // 请求失败，使用兜底方案
            $fallback_url = str_replace('/tvshows/', '/seasons/', $original_url);
            $results[$index] = $fallback_url;
            log_message("batch_get_real_detail_urls: 请求失败，使用兜底 - $fallback_url, 状态码: $http_code");
        }
        
        curl_multi_remove_handle($mh, $ch);
        curl_close($ch);
    }
    
    curl_multi_close($mh);
    log_message("batch_get_real_detail_urls: 批量处理完成");
    return $results;
}

// 从HTML中解析真实URL
function parse_real_url_from_html($html, $original_url) {
    $dom = new DOMDocument();
    $load_result = @$dom->loadHTML(mb_convert_encoding($html, 'HTML-ENTITIES', 'UTF-8'));
    
    if (!$load_result) {
        return false;
    }
    
    $xpath = new DOMXPath($dom);
    
    // 方法1: 尝试XPath提取
    $real_url_nodes = $xpath->query("//div[@id='episodes']//div[@id='seasons']//a/@href");
    if ($real_url_nodes->length > 0) {
        $real_url = $real_url_nodes->item(0)->nodeValue;
        return normalize_url($real_url);
    }
    
    // 方法2: 正则表达式提取
    if (preg_match('/href\s*=\s*[\'"](https?:\/\/www\.4kvm\.org\/seasons\/[^"\']+)[\'"]/i', $html, $matches)) {
        return $matches[1];
    }
    
    // 方法3: 查找包含"seasons"的链接
    if (preg_match('/<a[^>]+href=[\'"](https?:\/\/www\.4kvm\.org\/seasons\/[^"\']+)[\'"]/i', $html, $matches)) {
        return $matches[1];
    }
    
    return false;
}

// URL处理函数
function add_scheme_if_missing($url) {
    if (empty($url)) return $url;
    if (preg_match('/^(https?:|data:)/i', $url)) return $url;
    if (substr($url, 0, 2) === '//') return 'https:' . $url;
    if (substr($url, 0, 4) === 'www.') return 'https://' . $url;
    return 'https://' . ltrim($url, '/');
}

function clean_baidu_proxy_url($url) {
    if (preg_match('/^(https?:\/\/(gimg[0-2]\.baidu\.com|bj\.bcebos\.com)\/gimg\/)(.*)(&amp;|&)?(src|url)=([^&]+)/i', $url, $matches)) {
        $real_url = urldecode($matches[6]);
        return add_scheme_if_missing($real_url);
    }
    $parsed = parse_url($url);
    if (isset($parsed['query'])) {
        parse_str($parsed['query'], $params);
        if (isset($params['src'])) return add_scheme_if_missing(urldecode($params['src']));
        if (isset($params['url'])) return add_scheme_if_missing(urldecode($params['url']));
    }
    return $url;
}

function normalize_url($url, $base_url = BASE_URL) {
    $url = clean_baidu_proxy_url($url);
    if (strpos($url, 'data:image') === 0) return $url;
    $parsed_url = parse_url($url);
    if (!empty($parsed_url['scheme'])) return $url;
    if (substr($url, 0, 2) === '//') return 'https:' . $url;
    if (substr($url, 0, 1) === '/') return $base_url . $url;
    return $base_url . '/' . $url;
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
    ensure_cache_dir();
    $cache_file = CACHE_DIR . md5($key) . '.cache';
    return file_put_contents($cache_file, $data);
}

// 获取页面内容（集成缓存）
function fetchPage($url, $useCache = false) {
    $cache_key = $url;
    if ($useCache) {
        $cached_data = get_cache($cache_key);
        if ($cached_data !== false) {
            log_message("fetchPage: 使用缓存 - $url");
            return $cached_data;
        }
    }
    
    log_message("fetchPage: 获取新内容 - $url");
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_USERAGENT, USER_AGENT);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    curl_setopt($ch, CURLOPT_COOKIEFILE, COOKIE_FILE);
    curl_setopt($ch, CURLOPT_COOKIEJAR, COOKIE_FILE);
    $response = curl_exec($ch);
    $curl_errno = curl_errno($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($curl_errno) {
        log_message("fetchPage: curl错误 - $url, 错误码: $curl_errno");
        throw new Exception("curl错误: $curl_errno", $curl_errno);
    }
    if ($http_code >= 400) {
        log_message("fetchPage: HTTP错误 - $url, 状态码: $http_code");
        throw new Exception("HTTP错误: $http_code", $http_code);
    }
    
    if ($useCache) {
        set_cache($cache_key, $response);
        log_message("fetchPage: 保存新缓存 - $url");
    }
    return $response;
}

// 提取短标识ID
function extract_short_id($url) {
    log_message("extract_short_id: 开始提取 - $url");
    $parsed = parse_url($url);
    $path = $parsed['path'] ?? '';
    
    if (preg_match('/(movies|seasons|tvshows|detail)\/([^\/]+)/i', $path, $matches)) {
        $vod_id = $matches[1] . '_' . $matches[2];
        log_message("extract_short_id: 提取成功 - $vod_id, 原始URL: $url");
        return $vod_id;
    }
    
    $vod_id = 'unknown_' . md5($url);
    log_message("extract_short_id: 提取失败，使用默认值 - $vod_id, 原始URL: $url");
    return $vod_id;
}

// ==================== 播放地址解析核心函数 ====================

/**
 * 播放地址解析函数（优化版）
 * 基于正确的解析逻辑，返回精简格式
 */
function parse_play_url($play_url) {
    log_message("parse_play_url: 开始解析播放地址 - $play_url");
    
    // 验证play地址有效性
    if (empty($play_url) || strpos($play_url, '4kvm.org/artplayer') === false) {
        log_message("parse_play_url: 无效的播放地址格式");
        throw new Exception("无效的播放地址格式");
    }
    
    // 解析play地址参数
    $playQuery = parse_url($play_url, PHP_URL_QUERY);
    $playParams = [];
    if ($playQuery) parse_str($playQuery, $playParams);
    log_message("parse_play_url: 解析参数 - " . json_encode($playParams));
    
    // 检查必要参数（电影只需要id和mvsource，电视剧需要id、source和ep）
    $isMovie = isset($playParams['mvsource']);
    $requiredPlayParams = $isMovie ? ['id', 'mvsource'] : ['id', 'source', 'ep'];
    $missingPlayParams = array_diff($requiredPlayParams, array_keys($playParams));
    
    if (!empty($missingPlayParams)) {
        log_message("parse_play_url: 缺少必要参数: " . implode(', ', $missingPlayParams));
        throw new Exception("播放地址缺少必要参数: " . implode(', ', $missingPlayParams));
    }
    
    try {
        // 1. 请求播放页源码
        log_message("parse_play_url: 请求播放页源码");
        $playHtml = fetchPage($play_url, false); // 不使用缓存，确保获取最新
        
        if (empty($playHtml)) {
            log_message("parse_play_url: 播放页获取失败");
            throw new Exception("无法获取播放页内容");
        }
        
        // Log HTML length to diagnose truncation
        log_message("parse_play_url: 播放页源码长度: " . strlen($playHtml));
        
        // 2. 提取POST参数
        log_message("parse_play_url: 提取POST参数");
        $postParams = extract_post_params($playHtml);
        
        if (!$postParams) {
            log_message("parse_play_url: POST参数提取失败");
            throw new Exception("无法提取播放参数");
        }
        
        // 3. 发送POST请求获取真实m3u8地址
        log_message("parse_play_url: 发送POST请求到: " . $postParams['source']);
        $postBody = json_encode($postParams);
        $postHeaders = [
            "Content-Type: application/json",
            "User-Agent: " . USER_AGENT,
            "Referer: " . $play_url,
            "Origin: " . BASE_URL
        ];
        
        $postResponse = fetch_post_data($postParams['source'], $postBody, $postHeaders);
        
        if (empty($postResponse)) {
            log_message("parse_play_url: POST请求无响应");
            throw new Exception("播放服务器无响应");
        }
        
        // Log raw POST response for debugging
        log_message("parse_play_url: POST响应内容: " . substr($postResponse, 0, 500)); // Limit to 500 chars for brevity
        
        // 4. 解析POST响应
        $responseData = json_decode($postResponse, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            log_message("parse_play_url: JSON解析失败: " . json_last_error_msg());
            throw new Exception("播放数据解析失败");
        }
        
        if (empty($responseData) || !isset($responseData['ok']) || !$responseData['ok'] || empty($responseData['url'])) {
            log_message("parse_play_url: 响应数据无效: " . $postResponse);
            throw new Exception("播放地址获取失败");
        }
        
        $realM3u8Url = $responseData['url'];
        log_message("parse_play_url: 成功获取M3U8地址: " . $realM3u8Url);
        
        // 验证M3U8地址有效性
        if (!validate_m3u8_url($realM3u8Url)) {
            log_message("parse_play_url: M3U8地址验证失败: $realM3u8Url");
            throw new Exception("播放地址验证失败");
        }
        
        return $realM3u8Url;
        
    } catch (Exception $e) {
        log_message("parse_play_url: 解析异常: " . $e->getMessage());
        throw $e;
    }
}

/**
 * 提取POST参数（基于正确代码逻辑）
 */
function extract_post_params($html) {
    log_message("extract_post_params: 开始提取POST参数");
    
    $params = [];
    $requiredKeys = ['expires', 'client', 'nonce', 'token', 'source'];
    
    // 使用正则表达式匹配getRealMp4函数体
    $bodyPattern = '/getRealMp4\(\)\s*\{[\s\S]*?const\s+body\s*=\s*\{([\s\S]*?)\}[\s\S]*?return\s+new\s+Promise/is';
    
    if (!preg_match($bodyPattern, $html, $matches)) {
        log_message("extract_post_params: 未找到getRealMp4函数");
        return false;
    }
    
    $bodyContent = $matches[1];
    log_message("extract_post_params: 找到函数体内容");
    
    // 提取各个参数
    foreach ($requiredKeys as $key) {
        $pattern = '/' . preg_quote($key) . ':\s*["\']([^"\']+)["\']/is';
        if (!preg_match($pattern, $bodyContent, $val)) {
            log_message("extract_post_params: 缺少参数: $key");
            return false;
        }
        $params[$key] = trim($val[1]);
    }
    
    // 验证source有效性
    if (strpos($params['source'], 'play.gotomymv.life/ws/') === false || 
        strpos($params['source'], '.svg') === false) {
        log_message("extract_post_params: source参数格式无效: " . $params['source']);
        return false;
    }
    
    log_message("extract_post_params: 成功提取所有参数");
    return $params;
}

/**
 * 发送POST请求获取数据
 */
function fetch_post_data($url, $postBody, $headers = []) {
    log_message("fetch_post_data: 发送POST请求到: $url");
    
    $ch = curl_init();
    $defaultHeaders = [
        "User-Agent: " . USER_AGENT,
        "Accept: application/json, */*"
    ];
    
    $finalHeaders = array_merge($defaultHeaders, $headers);
    
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => $postBody,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => true,
        CURLOPT_SSL_VERIFYPEER => false,
        CURLOPT_SSL_VERIFYHOST => false,
        CURLOPT_TIMEOUT => 20,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_HTTPHEADER => $finalHeaders,
        CURLOPT_ENCODING => "gzip, deflate",
        CURLOPT_COOKIEFILE => COOKIE_FILE,
        CURLOPT_COOKIEJAR => COOKIE_FILE
    ]);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $curlError = curl_error($ch);
    curl_close($ch);
    
    if ($curlError) {
        log_message("fetch_post_data: CURL错误: " . $curlError);
        return '';
    }
    
    if ($httpCode !== 200) {
        log_message("fetch_post_data: HTTP错误代码: " . $httpCode);
        return '';
    }
    
    log_message("fetch_post_data: POST请求成功，响应长度: " . strlen($response));
    return $response;
}

/**
 * 验证M3U8地址格式
 */
function validate_m3u8_url($url) {
    if (empty($url)) {
        return false;
    }
    
    // 检查是否为有效的URL格式
    if (!filter_var($url, FILTER_VALIDATE_URL)) {
        return false;
    }
    
    // Relax validation to allow URLs with m3u8 in path or query
    if (stripos($url, 'm3u8') === false) {
        return false;
    }
    
    return true;
}

// ==================== 主逻辑处理 ====================

try {
    $request_uri = $_SERVER['REQUEST_URI'];
    log_message("主请求: 开始处理 - $request_uri");
    
    // 1. 播放地址接口: 支持 ?flag=播放源名&play=播放地址
    $flag = $_GET['flag'] ?? '';
    $play_url = $_GET['play'] ?? '';
    if (!empty($flag) && !empty($play_url)) {
        log_message("处理播放地址请求: flag=$flag, play=$play_url");
        
        // 解析play地址参数
        $playQuery = parse_url($play_url, PHP_URL_QUERY);
        $playParams = [];
        if ($playQuery) parse_str($playQuery, $playParams);
        log_message("初始 play_params: " . json_encode($playParams));
        
        // 检查并附加参数（movie: mvsource, TV: source 和 ep）
        $separator = (strpos($play_url, '?') !== false) ? '&' : '?';
        
        // Handle movie URLs with mvsource
        if (isset($_GET['mvsource']) && !isset($playParams['mvsource'])) {
            $play_url .= $separator . 'mvsource=' . rawurlencode($_GET['mvsource']);
            log_message("附加 mvsource 参数: {$_GET['mvsource']}, 新 play_url: $play_url");
            $separator = '&';
        }
        
        // Handle TV show URLs with source and ep
        if (isset($_GET['source']) && !isset($playParams['source'])) {
            $play_url .= $separator . 'source=' . rawurlencode($_GET['source']);
            log_message("附加 source 参数: {$_GET['source']}, 新 play_url: $play_url");
            $separator = '&';
        }
        
        if (isset($_GET['ep']) && !isset($playParams['ep'])) {
            $play_url .= $separator . 'ep=' . rawurlencode($_GET['ep']);
            log_message("附加 ep 参数: {$_GET['ep']}, 新 play_url: $play_url");
        }
        
        try {
            $m3u8Url = parse_play_url($play_url);
            
            // 验证地址是否可访问
            $ch = curl_init();
            curl_setopt($ch, CURLOPT_URL, $m3u8Url);
            curl_setopt($ch, CURLOPT_NOBODY, true);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
            curl_setopt($ch, CURLOPT_USERAGENT, USER_AGENT);
            curl_setopt($ch, CURLOPT_TIMEOUT, 15);
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, false);
            curl_exec($ch);
            $m3u8HttpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);
            
            if ($m3u8HttpCode === 200) {
                $response = [
                    'header' => json_encode([
                        'User-Agent' => USER_AGENT
                    ]),
                    'url' => $m3u8Url,
                    'parse' => 0,
                    'jx' => 0
                ];
                
                log_message("播放地址返回成功: $m3u8Url");
                echo json_encode($response, JSON_UNESCAPED_UNICODE);
                exit;
            } else {
                log_message("M3U8地址验证失败: 状态码=$m3u8HttpCode, URL=$m3u8Url");
                throw new Exception("播放地址不可用");
            }
            
        } catch (Exception $e) {
            log_message("播放地址解析异常: " . $e->getMessage());
            $response = [
                'header' => json_encode([
                    'User-Agent' => USER_AGENT
                ]),
                'url' => '',
                'parse' => 0,
                'jx' => 0
            ];
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
        }
    }
    
    // 2. 搜索接口: 支持 ?wd= 关键词参数
    $keyword = $_GET['wd'] ?? '';
    if (!empty($keyword)) {
        log_message("处理搜索接口请求: 关键词=$keyword");
        $page = max(1, intval($_GET['page'] ?? 1));
        $limit = 20;
        
        $searchUrl = BASE_URL . "/xssearch?s=" . urlencode($keyword);
        log_message("搜索请求URL: $searchUrl");
        $html = fetchPage($searchUrl);
        
        $dom = new DOMDocument();
        @$dom->loadHTML(mb_convert_encoding($html, 'HTML-ENTITIES', 'UTF-8'));
        $xpath = new DOMXPath($dom);
        $articles = $xpath->query("//div[contains(@class, 'result-item')]/article");
        $searchResult = []; 
        
        foreach ($articles as $article) {
            $titleNode = $xpath->query(".//div[contains(@class, 'title')]/a", $article);
            $vod_name = $titleNode->length > 0 ? trim($titleNode->item(0)->textContent) : '';
            $href = $titleNode->length > 0 ? $titleNode->item(0)->getAttribute('href') : '';
            $realHref = normalize_url($href);
            
            $imageNode = $xpath->query(".//div[contains(@class, 'thumbnail')]//img/@src", $article);
            $vod_pic = $imageNode->length > 0 ? normalize_url($imageNode->item(0)->nodeValue) : '';
            
            $updateNode = $xpath->query(".//div[contains(@class, 'meta')]//span[contains(@class, 'rating')]", $article);
            $vod_remarks = $updateNode->length > 0 ? trim($updateNode->item(0)->textContent) : '';
            
            $vod_id = extract_short_id($realHref);
            if (strpos($vod_id, 'tvshows_') === 0) {
                $vod_id = str_replace('tvshows_', 'seasons_', $vod_id);
            }
            
            $searchResult[] = [
                'vod_id' => $vod_id,
                'vod_name' => $vod_name,
                'vod_pic' => $vod_pic,
                'vod_remarks' => $vod_remarks
            ];
        }
        
        $response = [
            'list' => $searchResult
        ];
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }

    // 3. 列表接口: 支持 ?t=分类&ac=detail&pg=页码 访问方式
    $ac = $_GET['ac'] ?? '';
    $category = $_GET['t'] ?? '';
    $page = max(1, intval($_GET['pg'] ?? 1));
    $ext = $_GET['ext'] ?? '';
    
    if ($ac === 'detail' && !empty($category)) {
        log_message("处理列表接口请求: t=$category, pg=$page, ext=$ext");
        
        $categoryMap = [
            'movies' => "movies/page/{$page}",
            'guochan' => "classify/guochan/page/{$page}",
            'meiju' => "classify/meiju/page/{$page}",
            'hanju' => "classify/hanju/page/{$page}"
        ];
        
        if (!isset($categoryMap[$category])) {
            log_message("无效的分类参数: $category");
            throw new Exception("无效的分类参数", 400);
        }
        
        $target_url = BASE_URL . '/' . $categoryMap[$category];
        log_message("列表请求URL: $target_url");
        $html = fetchPage($target_url, true);
        
        $dom = new DOMDocument();
        @$dom->loadHTML(mb_convert_encoding($html, 'HTML-ENTITIES', 'UTF-8'));
        $xpath = new DOMXPath($dom);
        $articles = $xpath->query("//div[contains(@class, 'items') or @id='archive-content']/article");
        $videoList = [];
        $urls_to_resolve = []; // 需要解析真实地址的URL列表
        
        // 第一步：收集所有需要处理的URL
        foreach ($articles as $article) {
            $titleNode = $xpath->query(".//div[contains(@class, 'poster')]/img/@alt", $article);
            $vod_name = $titleNode->length > 0 ? trim($titleNode->item(0)->nodeValue) : '';
            
            $hrefNode = $xpath->query(".//div[contains(@class, 'poster')]/a/@href", $article);
            $href = $hrefNode->length > 0 ? $hrefNode->item(0)->nodeValue : '';
            $normalized_href = normalize_url($href);
            
            $imageNode = $xpath->query(".//div[contains(@class, 'poster')]/img/@src", $article);
            $vod_pic = $imageNode->length > 0 ? normalize_url($imageNode->item(0)->nodeValue) : '';
            
            $updateNode = $xpath->query(".//div[contains(@class, 'update')]", $article);
            $vod_remarks = $updateNode->length > 0 ? trim($updateNode->item(0)->textContent) : '';
            
            $videoList[] = [
                'vod_name' => $vod_name,
                'original_href' => $normalized_href,
                'vod_pic' => $vod_pic,
                'vod_remarks' => $vod_remarks
            ];
            
            // 如果是非movies分类且需要跳转的URL，加入解析列表
            if ($category !== 'movies' && strpos($normalized_href, '/tvshows/') !== false) {
                $urls_to_resolve[] = $normalized_href;
            }
        }
        
        // 第二步：批量并发获取真实地址
        $real_urls = [];
        if (!empty($urls_to_resolve)) {
            log_message("开始批量解析 " . count($urls_to_resolve) . " 个真实地址");
            $real_urls = batch_get_real_detail_urls($urls_to_resolve);
        }
        
        // 第三步：构建最终结果
        $finalVideoList = [];
        $real_urls_index = 0;
        
        foreach ($videoList as $video) {
            $realHref = $video['original_href'];
            
            // 如果是需要跳转的URL，使用解析后的真实地址
            if ($category !== 'movies' && strpos($video['original_href'], '/tvshows/') !== false) {
                if (isset($real_urls[$real_urls_index])) {
                    $realHref = $real_urls[$real_urls_index];
                    $real_urls_index++;
                }
            }
            
            $vod_id = extract_short_id($realHref);
            if (strpos($vod_id, 'tvshows_') === 0) {
                $vod_id = str_replace('tvshows_', 'seasons_', $vod_id);
            }
            
            $finalVideoList[] = [
                'vod_id' => $vod_id,
                'vod_name' => $video['vod_name'],
                'vod_pic' => $video['vod_pic'],
                'vod_remarks' => $video['vod_remarks']
            ];
        }
        
        $response = [
            'list' => $finalVideoList
        ];
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }

    // 4. 详情接口: 支持 ?ac=detail&ids= 访问方式
    $vod_id = $_GET['ids'] ?? '';
    if ($ac === 'detail' && !empty($vod_id)) {
        log_message("处理详情接口请求: ids=$vod_id");
        
        $idParts = explode('_', $vod_id, 2);
        if (count($idParts) !== 2) {
            log_message("无效的ID格式: $vod_id");
            throw new Exception("无效的视频ID格式", 400);
        }
        list($type, $id) = $idParts;
        
        $detailUrl = BASE_URL . "/{$type}/{$id}";
        log_message("详情页URL: $detailUrl");
        $html = fetchPage($detailUrl);
        
        $dom = new DOMDocument();
        @$dom->loadHTML(mb_convert_encoding($html, 'HTML-ENTITIES', 'UTF-8'));
        $xpath = new DOMXPath($dom);
        
        $vod_name = $xpath->query("//h1")->length > 0 ? trim($xpath->query("//h1")->item(0)->textContent) : '';
        $vod_pic = $xpath->query("//div[contains(@class, 'poster')]//img/@src")->length > 0 
            ? normalize_url(trim($xpath->query("//div[contains(@class, 'poster')]//img/@src")->item(0)->nodeValue)) 
            : '';
        
        // 初始化元数据
        $metaData = [
            'type_name' => '未知',
            'vod_director' => '未知',
            'vod_actor' => '未知',
            'vod_year' => '未知',
            'vod_area' => '未知',
            'vod_content' => '暂无剧情介绍',
            'vod_remarks' => '',
            'vod_play_from' => '',
            'vod_play_url' => ''
        ];
        
        // 提取简介 (vod_content)
        $contentNode = $xpath->query("//div[@itemprop='description' and contains(@class, 'wp-content')]//p");
        if ($contentNode->length > 0) {
            $metaData['vod_content'] = trim($contentNode->item(0)->textContent);
            $metaData['vod_content'] = preg_replace('/\s+/', ' ', $metaData['vod_content']);
        }
        
        // 提取类型 (type_name) 从 <meta name="keywords">
        $keywordsNode = $xpath->query("//meta[@name='keywords']/@content");
        if ($keywordsNode->length > 0) {
            $keywords = explode(',', $keywordsNode->item(0)->nodeValue);
            $metaData['type_name'] = trim($keywords[0]) ?: '未知';
        }
        
        // 提取导演 (vod_director)
        $directorNode = $xpath->query("//div[@id='cast' and contains(@class, 'sbox')]//h2[contains(text(), '导演') or contains(text(), '制片人')]/following-sibling::div[contains(@class, 'persons')]//div[@itemprop='director' or @itemprop='producer']/meta[@itemprop='name']/@content");
        if ($directorNode->length > 0) {
            $metaData['vod_director'] = trim($directorNode->item(0)->nodeValue);
        }
        
        // 提取演员 (vod_actor)
        $actorNodes = $xpath->query("//div[@id='cast' and contains(@class, 'sbox')]//h2[contains(text(), '演员')]/following-sibling::div[contains(@class, 'persons')]//div[@itemprop='actor']/meta[@itemprop='name']/@content");
        $actors = [];
        foreach ($actorNodes as $node) {
            $actorName = trim($node->nodeValue);
            if ($actorName && !in_array($actorName, $actors)) {
                $actors[] = $actorName;
            }
        }
        $metaData['vod_actor'] = !empty($actors) ? implode(',', $actors) : '未知';
        
        // 提取年份 (vod_year)
        $yearNode = $xpath->query("//div[@id='episodes']//span[@class='title']/i[contains(text(), ',')]");
        if ($yearNode->length > 0 && preg_match('/(\d{4})/', $yearNode->item(0)->textContent, $matches)) {
            $metaData['vod_year'] = $matches[1];
        } else {
            $metaNode = $xpath->query("//meta[@name='description']/@content");
            if ($metaNode->length > 0 && preg_match('/(\d{4})/', $metaNode->item(0)->nodeValue, $matches)) {
                $metaData['vod_year'] = $matches[1];
            }
        }
        
        // 提取地区 (vod_area)
        $areaNode = $xpath->query("//div[contains(@class, 'custom_fields')]//b[contains(text(), '国家') or contains(text(), '地区')]/following-sibling::span[@class='valor']");
        if ($areaNode->length > 0) {
            $metaData['vod_area'] = trim($areaNode->item(0)->textContent);
        } else {
            $metaNode = $xpath->query("//meta[@name='description']/@content");
            if ($metaNode->length > 0 && preg_match('/(中国大陆|香港|台湾|美国|日本|韩国|越南|泰国|[^\s,]+?)(?:[\s,]|$)/', $metaNode->item(0)->nodeValue, $matches)) {
                $metaData['vod_area'] = $matches[1];
            }
        }
        
        // 提取备注 (vod_remarks)
        $isTvShow = in_array($type, ['tvshows', 'seasons']);
        if ($isTvShow) {
            $remarksNode = $xpath->query("//div[@id='episodes']//span[@class='title']/i[contains(text(), '更新至')]");
            if ($remarksNode->length > 0 && preg_match('/更新至(\d+)集/', $remarksNode->item(0)->textContent, $matches)) {
                $metaData['vod_remarks'] = '更新至 ' . $matches[1] . ' 集';
            } else {
                $metaData['vod_remarks'] = '更新中';
            }
        } else {
            $metaData['vod_remarks'] = '已完结';
        }
        
        $vod_play_from = [];
        $vod_play_url = [];
        
        if ($isTvShow) {
            $vueData = ['ifsrc' => '', 'videourls' => []];
            if (preg_match('/<script[^>]*>.*?new\s+Vue\s*\((\{.*?\})\);?\s*<\/script>/s', $html, $vueMatches)) {
                $vueInit = $vueMatches[1];
                if (preg_match('/ifsrc\s*:\s*[\'"]([^\'"]+)[\'"]/', $vueInit, $ifsrcMatch)) {
                    $vueData['ifsrc'] = $ifsrcMatch[1];
                }
                if (preg_match('/videourls\s*:\s*(\[[\s\S]*?\]\s*(?=,|\}))/', $vueInit, $videoUrlsMatch)) {
                    $jsArray = trim($videoUrlsMatch[1]);
                    $jsArray = str_replace("'", '"', $jsArray);
                    $jsArray = preg_replace('/(\w+):/', '"$1":', $jsArray);
                    $jsArray = preg_replace('/,\s*]/', ']', $jsArray);
                    $vueData['videourls'] = json_decode($jsArray, true) ?: [];
                }
            }
            
            $sources = [];
            if (!empty($vueData['ifsrc']) && !empty($vueData['videourls'])) {
                foreach ($vueData['videourls'] as $index => $seasonList) {
                    if (is_array($seasonList)) {
                        $episodes = [];
                        foreach ($seasonList as $episodeIndex => $episode) {
                            $epNum = $episode['name'] ?? ($episodeIndex + 1);
                            $urlIndex = $episode['url'] ?? $episodeIndex;
                            $episodeUrl = normalize_url($vueData['ifsrc'] . "&source=$index&ep=" . $urlIndex);
                            $episodes[] = "$epNum$$episodeUrl";
                        }
                        $sourceName = count($vueData['videourls']) > 1 ? "播放源" . ($index + 1) : "默认线路";
                        $vod_play_from[] = $sourceName;
                        $vod_play_url[] = implode("#", $episodes);
                    }
                }
            } else {
                // 无Vue兜底 - 生成自建片源 + 提取总集数生成剧集链接
                if (preg_match('/更新到\s*(\d+)\s*(episodes|集)/i', $html, $totalMatches)) {
                    $totalEpisodes = intval($totalMatches[1]);
                } else {
                    $totalEpisodes = 20; // 默认20
                }
                log_message("详情页兜底: TV总集数 $totalEpisodes, id=$id");
                $episodes = [];
                for ($i = 0; $i < $totalEpisodes; $i++) {
                    $epNum = $i + 1;
                    $episodeUrl = BASE_URL . "/artplayer?id=" . $id . "&source=0&ep=" . $i;
                    $episodes[] = "$epNum$$episodeUrl";
                }
                $sourceName = "自建片源";
                $vod_play_from[] = $sourceName;
                $vod_play_url[] = implode("#", $episodes);
            }
        } else {
            // Movies 加兜底检查源数
            $sourceNodes = $xpath->query("//ul[@id='playeroptionsul']/li[contains(@class, 'dooplay_player_option')]");
            $episodes = [];
            if ($sourceNodes->length > 0) {
                foreach ($sourceNodes as $index => $sourceNode) {
                    $dataPost = $sourceNode->getAttribute('data-post');
                    $episodeUrl = normalize_url(BASE_URL . "/artplayer?id={$dataPost}&mvsource=$index");
                    $episodes[] = "1$$episodeUrl";
                }
            } else {
                // 兜底空源
                $episodes = [];
            }
            $sourceName = $sourceNodes->length > 1 ? "播放源1" : "默认线路";
            $vod_play_from[] = $sourceName;
            $vod_play_url[] = implode("#", $episodes);
        }
        
        // 使用正确的分隔符
        $metaData['vod_play_from'] = implode('$$$', $vod_play_from);
        $metaData['vod_play_url'] = implode('$$$', $vod_play_url);
        
        $response = [
            'list' => [
                array_merge($metaData, [
                    'vod_id' => $vod_id,
                    'vod_name' => $vod_name,
                    'vod_pic' => $vod_pic,
                ])
            ]
        ];
        echo json_encode($response, JSON_UNESCAPED_UNICODE);
        exit;
    }

    // 5. 播放地址解析（旧方式，兼容保留）
    $currentFileName = basename(__FILE__);
    $pathParts = explode('/', trim(parse_url($request_uri, PHP_URL_PATH), '/'));
    $isPlayRequest = (count($pathParts) >= 2 && $pathParts[0] === $currentFileName && strpos($pathParts[1], 'https://') === 0);

    if ($isPlayRequest) {
        log_message("处理播放地址解析请求: $request_uri");
        $playerUrl = urldecode($pathParts[1]);
        
        // 解析playerUrl参数
        $playQuery = parse_url($playerUrl, PHP_URL_QUERY);
        $playParams = [];
        if ($playQuery) parse_str($playQuery, $playParams);
        log_message("旧方式初始 play_params: " . json_encode($playParams));
        
        // 检查并附加参数
        $separator = (strpos($playerUrl, '?') !== false) ? '&' : '?';
        
        // Handle movie URLs with mvsource
        if (isset($_GET['mvsource']) && !isset($playParams['mvsource'])) {
            $playerUrl .= $separator . 'mvsource=' . rawurlencode($_GET['mvsource']);
            log_message("旧方式附加 mvsource: {$_GET['mvsource']}, 新 playerUrl: $playerUrl");
            $separator = '&';
        }
        
        // Handle TV show URLs with source and ep
        if (isset($_GET['source']) && !isset($playParams['source'])) {
            $playerUrl .= $separator . 'source=' . rawurlencode($_GET['source']);
            log_message("旧方式附加 source: {$_GET['source']}, 新 playerUrl: $playerUrl");
            $separator = '&';
        }
        
        if (isset($playParams['source']) && isset($_GET['ep']) && !isset($playParams['ep'])) {
            $playerUrl .= $separator . 'ep=' . rawurlencode($_GET['ep']);
            log_message("旧方式附加 ep: {$_GET['ep']}, 新 playerUrl: $playerUrl");
        }
        
        try {
            $m3u8Url = parse_play_url($playerUrl);
            
            $response = [
                'header' => json_encode([
                    'User-Agent' => USER_AGENT
                ]),
                'url' => $m3u8Url,
                'parse' => 0,
                'jx' => 0
            ];
            log_message("旧方式播放地址返回成功: $m3u8Url");
            echo json_encode($response, JSON_UNESCAPED_UNICODE);
            exit;
            
        } catch (Exception $e) {
            log_message("旧方式播放地址解析失败: " . $e->getMessage());
            throw new Exception("未找到有效的播放地址", 404);
        }
    }

    // 6. 分类接口（默认）
    log_message("默认请求: 返回分类接口数据 - $request_uri");
    $categories = [
        [
            'type_id' => 'movies',
            'type_name' => '电影'
        ],
        [
            'type_id' => 'guochan', 
            'type_name' => '国产剧'
        ],
        [
            'type_id' => 'meiju', 
            'type_name' => '美剧'
        ],
        [
            'type_id' => 'hanju', 
            'type_name' => '韩剧'
        ]
    ];
    $response = [
        'code' => 1,
        'msg' => '分类列表',
        'class' => $categories
    ];
    echo json_encode($response, JSON_UNESCAPED_UNICODE);
    exit;

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