# `next.py` 使用说明文档

`next.py` 是一个用于创建目录/笔记模板和管理 `.info` 文件的工具。它支持创建目录、下载文件、生成空文件、读取和更新 `.info` 文件，并提供按需显示 `.info` 文件信息的功能。以下是详细的使用说明。

> 脚本执行依赖request模块，可以使用`pyinstaller -F ./next.py`基于脚本创建单个可执行文件，使用更加方便。

## **1. 脚本功能**

- **创建**: 根据模板配置创建目录及文件。
- **索引**: 索引并显示 `.info` 文件的信息。



## **2. 命令行参数**

### **`create` 命令**

用于创建目录和文件。

- **`directory`**: 要创建的目录路径（必需），如果创建的目录已经存在，脚本会提示错误并退出。

- **`--config`**: 配置文件路径，默认值为 `.config/next_config.json`。

- **`-t` 或 `--type`**: 模板类型，必须从配置文件中的可用模板类型中选择。

- **`-m` 或 `--message`**: 可选的消息，会被写入 `.info` 文件的详细信息`Detail`中。

**示例**:

```bash
python next.py create my_directory -t my_template -m "This is an optional message."
```

### **`index` 命令**

用于索引和显示 `.info` 文件的信息。

- **`--root`**: 查找 `.info` 文件的根目录。默认值为当前目录 `.`。

- **`-l` 或 `--limit`**: 限制显示的时间最近的条目数量，默认值为 5。

- **`--filter-type`**: 按类型过滤条目。

- **`--filter-name`**: 按名称过滤条目。

- **`-c` 或 `--compact`**: 使用单行紧凑格式输出。

- **`-r` 或 `--reverse`**: 以倒序显示条目，默认最新的条目在最前面显示，倒序则出现在最后。

**示例**:

```bash
python next.py index --root my_directory -l 10 --filter-type "Report" -c
```


## **3. 配置文件格式**

配置文件是一个 JSON 文件，定义不同模板的具体配置。模板配置可以包含文件名和对应的 URL 或 `null`（表示创建空文件）。

**示例配置文件 (`next_config.json`)**:

```json
{
    "my_template": {
        "file1.txt": "http://example.com/file1.txt",
        "file2.txt": null
    },
    "another_template": {
        "doc.tex": "http://example.com/doc.tex"
    }
}
```

## **4. `.info` 文件格式**

`.info` 文件包含以下字段：

- **`Date`**: 日期和时间。
- **`Type`**: 模板类型。
- **`Path`**: 目录的绝对路径。
- **`Detail`**: 额外的详细信息（可选）。

**示例 `.info` 文件内容**:

```
Date: 2024-09-08 12:34:56
Type: my_template
Path: /absolute/path/to/directory
Detail: This is a sample detail text.
```
