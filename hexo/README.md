## hexo 自动化脚本

这里是为了简化博客使用流程所使用的自动化脚本，大致分成两类：

- 备份与提交：提供bash脚本和等价的powershell脚本
  - 备份：`backup.sh`，`backup.ps1`
  - 推送：`deploy.sh`，`deploy.ps1`
- 博客格式检查：使用Python脚本实现
  - 内容格式检查：`blogcheck.py`，关注列表开头空行，代码结尾空行等影响渲染的格式细节
  - 头部信息检查：`headcheck.py`，检查博客分类是否与文件系统中的实际位置匹配，分类名称和标签名称的合法性等
