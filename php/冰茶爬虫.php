<?php
// 直接从原地址爬取并融合 bc（冰茶） + catvod 源
// 生成融合后的M3U列表（分组区分、移除公告/广告、排序优化）
// 上传到服务器，访问域名+文件名即可看到完整列表

// 原地址（严格按照你的要求，不用代理服务器）
$bc_config_url = 'https://bc.188766.xyz/?ip=&haiwai=true';  // 配置JSON
//$catvod_url = 'https://live.catvod.com/tv.m3u';             // catvod M3U

header('Content-Type: text/plain; charset=utf-8');
header('Cache-Control: no-cache');

// cURL 获取函数（支持UA和头）
function get_content($url, $ua = null, $headers = []) {
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    if ($ua) {
        curl_setopt($ch, CURLOPT_USERAGENT, $ua);
    }
    if (!empty($headers)) {
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    }
    $content = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($http_code != 200 || empty($content)) {
        echo "获取失败: $url (HTTP $http_code)\n";
        return false;
    }
    return $content;
}

// 1. 获取冰茶源（需要特定UA）
$bc_ua = 'bingcha/1.1 (mianfeifenxiang)';
$bc_json = get_content($bc_config_url, $bc_ua, ['Accept: application/json']);

if (!$bc_json || !($data = json_decode($bc_json, true)) || empty($data['lives'][0]['url'])) {
    echo "冰茶配置获取失败或解析错误\n";
    $bc_content = '';
} else {
    $bc_live_url = $data['lives'][0]['url'];  // 通常是 ?ip=&json=true
    $bc_content = get_content($bc_live_url, $bc_ua, ['Accept: application/vnd.apple.mpegurl']);
    if (!$bc_content) {
        $bc_content = '';
    }
}

// 2. 获取catvod源
$catvod_content = get_content($catvod_url);
if (!$catvod_content) {
    $catvod_content = '';
}

// 如果两个源都失败，直接退出
if (empty($bc_content) && empty($catvod_content)) {
    echo "两个源都无法获取数据，请检查原地址是否可用\n";
    exit;
}

// 解析并处理M3U（收集到分组数组）
function parse_m3u($content, $prefix, $is_bc = false) {
    $groups = [];
    $lines = explode("\n", trim($content));
    $current_inf = '';
    $skip_next = false;

    foreach ($lines as $line) {
        $line = trim($line);
        if (empty($line) || strpos($line, '#EXTM3U') === 0) continue;

        if ($skip_next) {
            $skip_next = false;
            continue;
        }

        if (strpos($line, '#EXTINF') === 0) {
            // 移除冰茶公告
            if ($is_bc && (strpos($line, '公告') !== false || strpos($line, '免费分享') !== false || strpos($line, '奸商太多') !== false)) {
                $skip_next = true;
                continue;
            }

            // 移除catvod温馨提示
            if (!$is_bc && (strpos($line, '温馨提示') !== false || strpos($line, '免費訂閲') !== false)) {
                $skip_next = true;
                continue;
            }

            // 处理group-title
            if (preg_match('/group-title="([^"]*)"/', $line, $m)) {
                $orig_group = $m[1];
                if ($is_bc && $orig_group === '粤语频道') {
                    $orig_group = '香港台';
                }
                $new_group = $prefix . ' ' . $orig_group;
            } else {
                $new_group = $prefix . ' 未分组';
            }

            $current_inf = preg_replace('/group-title="[^"]*"/', 'group-title="' . $new_group . '"', $line);
        } elseif ($current_inf && $line[0] !== '#') {
            if (!isset($groups[$new_group])) $groups[$new_group] = [];
            $groups[$new_group][] = $current_inf . "\n" . $line;
            $current_inf = '';
        }
    }
    return $groups;
}

$bc_groups = empty($bc_content) ? [] : parse_m3u($bc_content, '冰茶', true);
$catvod_groups = empty($catvod_content) ? [] : parse_m3u($catvod_content, 'catvod', false);

// 合并分组
$all_groups = array_merge_recursive($bc_groups, $catvod_groups);

// 优先排序
$priority = [
    '冰茶 央视频道', 'catvod 央视频道',
    '冰茶 卫视频道', 'catvod 卫视频道',
    '冰茶 超清频道',
    '冰茶 香港台', 'catvod 香港频道',
    '冰茶 台湾频道', 'catvod 台湾频道',
];

$other = array_diff_key($all_groups, array_flip($priority));
ksort($other);
$sorted_groups = array_merge(array_intersect_key($all_groups, array_flip($priority)), $other);

// 输出
echo '#EXTM3U x-tvg-url="https://static.188766.xyz/e.xml" catchup="append" catchup-source="?playseek=${(b)yyyyMMddHHmmss}-${(e)yyyyMMddHHmmss}"' . "\n\n";

foreach ($sorted_groups as $group => $channels) {
    foreach ($channels as $channel) {
        echo $channel . "\n\n";
    }
}

echo "# 融合完成：冰茶源 " . count($bc_groups) . " 组，catvod源 " . count($catvod_groups) . " 组\n";
?>
