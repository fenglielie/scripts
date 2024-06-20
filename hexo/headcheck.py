import os
import re
import sys
import yaml

error_count = 0


def read_yaml_header(file_path):
    """读取Markdown文件头部的YAML元数据"""
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # 找到YAML头部
    if lines[0].strip() == "---":
        header = []
        for line in lines[1:]:
            if line.strip() == "---":
                break
            header.append(line)

        header_text = "".join(header)
        return parse_yaml(header_text)
    else:
        return {}


def parse_yaml(yaml_text):
    """解析YAML文本并返回一个字典"""
    return yaml.safe_load(yaml_text)


def check_file_path(file_path, root_dir):
    """检查文件路径与分类是否匹配，并验证合法性"""
    global error_count

    relative_path = os.path.relpath(file_path, root_dir)
    # 将相对路径分成目录和文件名
    path_parts = os.path.dirname(relative_path).split(os.sep)

    # 读取文件头部的YAML元数据
    header = read_yaml_header(file_path)
    if "categories" in header:
        categories = header["categories"]

        # 定义正则表达式，匹配小写英文字母和数字的组合
        category_pattern = re.compile(r"^[a-z0-9]+$")

        # 检查分类和路径部分的合法性
        for part in path_parts + categories:
            if not category_pattern.match(part):
                error_count += 1
                print(
                    f"Error[{error_count}]: Invalid name '{part}' in file '{file_path}'. "
                    f"Only lowercase letters and digits are allowed."
                )

        # 检查目录结构是否与分类列表匹配
        if path_parts != categories:
            error_count += 1
            print(
                f"Error[{error_count}]: File '{file_path}' has categories {categories} but its path is '{relative_path}'."
            )

    # 检查tags的合法性
    if "tags" in header:
        if header["tags"]:
            tags = header["tags"]

            # 定义正则表达式，匹配大小写英文字母、数字、连字符和下划线
            tag_pattern = re.compile(r"^[a-zA-Z0-9_-]+$")

            # 检查tags中的每个tag
            for tag in tags:
                if not tag_pattern.match(tag):
                    error_count += 1
                    print(
                        f"Error[{error_count}]: Invalid tag '{tag}' in file '{file_path}'. \n"
                        f"Tags can only contain letters, numbers, hyphens, and underscores."
                    )
        else:
            error_count += 1
            print(f"Error[{error_count}]: Empty in tags in file '{file_path}'.")


def main():
    root_dir = "source/_posts"
    # 遍历根目录下的所有文件
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                check_file_path(file_path, root_dir)


if __name__ == "__main__":
    main()

    if error_count == 0:
        print("headcheck: pass")

    sys.exit(error_count)
