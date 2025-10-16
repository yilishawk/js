<?php
// 设置目标ID列表
$ids = ['shaanxi', 'cctv', 'hongkong', 'weishi', 'taiwan'];
// ID到组名的映射
$groupNames = [
    'shaanxi' => '陕西频道',
    'cctv' => '央视频道', 
    'hongkong' => '香港频道',
    'weishi' => '卫视频道',
    'taiwan' => '台湾频道'
];

$allChannels = [];

// 遍历每个ID
foreach ($ids as $id) {
    echo "正在爬取 {$groupNames[$id]}...\n";
    
    $page = 1;
    $hasMorePages = true;
    
    while ($hasMorePages && $page <= 10) { // 限制最多10页，防止无限循环
        $url = "https://www.nettvpro.xyz/{$id}/list_{$page}.html";
        
        // 初始化cURL
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);
        curl_setopt($ch, CURLOPT_USERAGENT, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        
        // 执行请求
        $html = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        // 检查请求是否成功
        if ($httpCode !== 200 || empty($html)) {
            echo "  第 {$page} 页获取失败，停止爬取\n";
            $hasMorePages = false;
            break;
        }
        
        // 创建DOMDocument对象
        $dom = new DOMDocument();
        libxml_use_internal_errors(true);
        $dom->loadHTML($html);
        libxml_clear_errors();
        
        // 创建XPath对象
        $xpath = new DOMXPath($dom);
        
        // 提取频道列表
        $channelNodes = $xpath->query('//div[@class="channals-list"]');
        
        if ($channelNodes->length === 0) {
            echo "  第 {$page} 页没有找到频道，停止爬取\n";
            $hasMorePages = false;
            break;
        }
        
        $pageChannels = [];
        foreach ($channelNodes as $node) {
            // 提取标题
            $titleNode = $xpath->query('.//h4', $node)->item(0);
            if (!$titleNode) continue;
            
            $title = trim($titleNode->textContent);
            
            // 提取链接
            $linkNode = $xpath->query('.//a', $node)->item(0);
            if (!$linkNode) continue;
            
            $href = $linkNode->getAttribute('href');
            
            // 补全链接
            if (strpos($href, 'http') !== 0) {
                if (strpos($href, '/') === 0) {
                    $fullUrl = 'https://www.nettvpro.xyz' . $href;
                } else {
                    $fullUrl = 'https://www.nettvpro.xyz/' . $id . '/' . $href;
                }
            } else {
                $fullUrl = $href;
            }
            
            $pageChannels[] = [
                'title' => $title,
                'url' => $fullUrl
            ];
        }
        
        echo "  第 {$page} 页找到 " . count($pageChannels) . " 个频道\n";
        
        if (!isset($allChannels[$id])) {
            $allChannels[$id] = [];
        }
        $allChannels[$id] = array_merge($allChannels[$id], $pageChannels);
        
        // 检查是否有下一页（通过查找分页元素或判断当前页是否有数据）
        $page++;
        
        // 添加延迟，避免请求过快
        sleep(1);
    }
}

// 生成TXT格式输出
header('Content-Type: text/plain; charset=utf-8');

$output = '';
foreach ($allChannels as $id => $channels) {
    if (empty($channels)) continue;
    
    $groupName = $groupNames[$id] ?? $id;
    $output .= "{$groupName},#genre#\n";
    
    foreach ($channels as $channel) {
        $output .= "{$channel['title']},video://{$channel['url']}\n";
    }
    $output .= "\n";
}

// 保存到文件
$filename = 'channels.txt';
file_put_contents($filename, $output);

// 输出统计信息
$totalChannels = 0;
foreach ($allChannels as $channels) {
    $totalChannels += count($channels);
}

echo "\n爬取完成！\n";
echo "总共爬取 {$totalChannels} 个频道\n";
echo "文件已保存为: {$filename}\n\n";

// 输出内容预览
echo $output;
?>