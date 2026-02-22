import requests
import re

# 1. 定义源地址和目标关键词
url = "https://raw.githubusercontent.com/jn950/live/main/tv/holive.m3u"
# 允许保留的原始分组
include_groups = ["卫视", "央视"]
# 明确排除的分组（虽然上面的 include_groups 已经做了精确匹配，但这可以作为双重保险）
exclude_groups = ["卫视频道", "央视频道"]

def filter_m3u():
    try:
        # 获取源数据
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.splitlines()
        
        output = ["#EXTM3U"]
        
        # 2. 逻辑处理
        for i in range(len(lines)):
            line = lines[i].strip()
            
            if line.startswith("#EXTINF"):
                # 提取原始 group-title 和 tvg-name
                group_match = re.search(r'group-title="([^"]+)"', line)
                tvg_name_match = re.search(r'tvg-name="([^"]+)"', line)
                
                group_name = group_match.group(1) if group_match else ""
                tvg_name = tvg_name_match.group(1) if tvg_name_match else ""
                
                # --- 新增逻辑：处理“陕西”分组 ---
                if "陕西" in tvg_name:
                    # 如果名字里有陕西，强制修改 group-title 为“陕西”
                    new_line = re.sub(r'group-title="[^"]+"', 'group-title="陕西"', line)
                    output.append(new_line)
                    if i + 1 < len(lines):
                        output.append(lines[i+1])
                
                # --- 原有逻辑：保留卫视和央视 ---
                elif group_name in include_groups and group_name not in exclude_groups:
                    output.append(line)
                    if i + 1 < len(lines):
                        output.append(lines[i+1])
        
        # 3. 保存结果（文件名需与 YAML 中的 git add 对应）
        with open("live.m3u", "w", encoding="utf-8") as f:
            f.write("\n".join(output))
        
        print("处理完成！已生成 live.m3u")

    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    filter_m3u()
