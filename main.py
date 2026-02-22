import requests
import re

# 1. 定义源地址和目标关键词
url = "https://raw.githubusercontent.com/jn950/live/main/tv/holive.m3u"
include_groups = ["卫视", "央视"]
exclude_groups = ["卫视频道", "央视频道"]

def filter_m3u():
    try:
        # 获取源数据
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.splitlines()
        
        output = ["#EXTM3U"]
        skip_next = False
        
        # 2. 逻辑处理：m3u 通常由 #EXTINF 和 URL 两行组成一对
        for i in range(len(lines)):
            line = lines[i].strip()
            
            if line.startswith("#EXTINF"):
                # 提取 group-title 的值
                group_match = re.search(r'group-title="([^"]+)"', line)
                if group_match:
                    group_name = group_match.group(1)
                    
                    # 关键逻辑：在包含列表里，且不在排除列表里
                    if group_name in include_groups and group_name not in exclude_groups:
                        output.append(line)
                        # 如果这行匹配成功，下一行的 URL 也要保留
                        if i + 1 < len(lines):
                            output.append(lines[i+1])
        
        # 3. 保存结果
        with open("live.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        
        print("过滤完成！已生成 live.m3u")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    filter_m3u()
