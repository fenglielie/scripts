## 构建脚本使用说明

2024年7月14日

## 概述

这是一个用于创建 LaTeX 笔记或报告的 Python 脚本。它支持从配置文件加载模板信息，并根据用户指定的日期和选项生成相应的目录结构和文件。
脚本包括如下功能

- 根据配置文件中定义的模板类型和日期选项生成目录和文件。
- 下载主模板文件和类文件（支持零个以及多个类文件）。
- 替换主模板文件的名称，并替换其中的标题和作者信息（如果在配置中提供了作者名）。
- 可选地创建备注文件。
- 检查和验证根目录的有效性（根目录可以从命令行或配置文件中获取，要求必须为脚本所在目录或脚本执行目录）。

## 使用说明

脚本的使用方式如下
```bash
python ./create.py template_type [--remark REMARK] [--date DATE] [--move MOVE]
        [--config CONFIG_FILE] [--root ROOT_DIRECTORY] [--name NAME]
```
包括如下参数

- `template_type`: 模板类型，必选参数，例如 `note` 或 `report`。
- `--remark REMARK`: 可选参数，指定备注文件的名称。
- `--date DATE`: 可选参数，指定生成文件的日期，格式为 `YYYY-MM-DD`。
- `--move MOVE`: 可选参数，指定相对于今天的日期偏移量，例如 `-1` 表示昨天，`1` 表示明天。（`--date`和`--move`不允许同时设置）
- `--config CONFIG_FILE`: 可选参数，指定配置文件的路径，默认为 `./.config/create_config.json`。
- `--root ROOT_DIRECTORY`: 可选参数，指定根目录的路径，用于存储生成的文件。如果未指定，则从配置文件中读取。
- `--name NAME`: 可选参数，指定名称，用于替换默认的文件夹名称和主文件名称中的日期部分，仍然保持前缀。

## 使用示例

1. 使用默认配置文件和根目录：

```bash
python ./create.py note --remark important_notes --date 2024-07-15
```

2. 指定自定义配置文件和根目录：

```bash
python ./create.py report --remark daily_report --date 2024-07-15 --config /path/to/my/config.json --root /path/to/root/directory
```

## 配置文件示例

```json
{
  "_config": {
    "rootDirectory": "/path/to/root/directory"
  },
  "note": {
    "mainTemplateUrl": "https://github.com/example/note_template.tex",
    "classFileUrl": "https://github.com/example/class_file.cls",
    "Author": "John Doe",
    "directoryPrefix": "note-"
  },
  "report": {
    "mainTemplateUrl": "https://github.com/example/report_template.tex",
    "classFileUrl": [
      "https://github.com/example/class_file1.cls",
      "https://github.com/example/class_file2.cls"
    ],
    "Author": "Jane Smith",
    "directoryPrefix": "report-"
  }
}
```
