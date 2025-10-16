<?php
// 设置目标URL
$url = 'http://free.cnlive.club/channels.json';

// 初始化cURL
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

// 执行请求并获取数据
$json_data = curl_exec($ch);
curl_close($ch);

// 解析JSON数据
$data = json_decode($json_data, true);

// 检查数据是否有效
if (json_last_error() !== JSON_ERROR_NONE || !isset($data['channels'])) {
    die('无法获取或解析JSON数据');
}

// 按group分组数据
$grouped = [];
foreach ($data['channels'] as $channel) {
    $group = $channel['group'] ?? '其他';
    // 修改playUrl：替换或添加参数为?q=36.44.99.42
    $playUrl = $channel['playUrl'];
    
    // 移除现有参数并添加新参数
    $baseUrl = strtok($playUrl, '?'); // 获取问号前的部分
    $playUrl = $baseUrl . '?q=36.44.99.42';
    
    $grouped[$group][] = [
        'name' => $channel['name'],
        'playUrl' => $playUrl
    ];
}

// 格式化输出
$output = '';
$groups = ['中国', '香港', '台湾', '新加坡', '马来西亚', '印度尼西亚', '印度', '泰国', '英国', '韩国', '日本', '电影频道', '纪录频道', '新闻频道', '儿童频道', '体育频道'];
foreach ($groups as $group) {
    if (isset($grouped[$group])) {
        $output .= "{$group},#genre#\n";
        foreach ($grouped[$group] as $channel) {
            $output .= "{$channel['name']},{$channel['playUrl']}\n";
        }
    }
}

// 保存到TXT文件
$filename = 'channels.txt';
file_put_contents($filename, $output);

// 输出TXT内容
echo $output;
?>