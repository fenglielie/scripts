# PBS自动化邮件通知

PBS作业完成时的自动邮件通知的完整实现方案如下。

## 本地作业记录和自检

第一部分，在服务器上维护一个简单的作业记录系统：

- 包括管理脚本`~/scripts/pbs_manager`和记录文件`~/scripts/pbs_records.txt`（需要将`pbs_manager`所在路径添加到`PATH`）
- 记录文件中的条目包括作业id（纯数字）和作业根目录（绝对路径）
- 提交作业后，需要手动执行脚本将作业id和作业根目录添加到作业记录文件中，例如`pbs_manager add 12223 -d .`，这里`-d`选项指定目录，缺省时默认使用执行命令时的当前目录，在添加记录时会检查作业id的唯一性和目录的合法性
- 可以手动查询当前的所有记录：`pbs_manager list`
- 可以移除特定的记录，提供对应的作业id即可：`pbs_manager del 12223`
- 无参数调用`pbs_manager`会进行自检

自检的逻辑如下：

- 在shell中调用`qstat`命令，获取并检查返回的字符串，正常情况下，记录文件中的所有作业id都应该在`qstat`的返回值中出现，如果没有出现，说明作业已经结束
- 对于已经结束的作业，我们需要处理记录文件中的对应条目：
  - 在作业根目录下检索以作业id结尾的文件，它们是PBS系统的标准输出和错误输出文件，例如`demo.o12223`和`demo.e12223`
  - 将检索得到的两个作业输出文件通过`scp`传递到`vlab`的固定位置`~/pbsdata`
  - 通过`ssh`在`vlab`中执行发送通知邮件的任务（具体细节见邮件发送环节）
  - 在记录文件中删除此条目

注意：因为下一个环节的`crontab`在自动执行脚本时会缺少相关的环境变量，因此这里在脚本中的`qstat`必须使用完整命令形式。

## 定时任务

第二部分，我们需要使用`crontab`定时调用`pbs_manager`进行自检，具体做法如下：

使用`crontab -e`编辑定时任务，向其中加入两行
```
* * * * * /bin/bash -c '~/scripts/pbs_manager 2>&1 | while IFS= read -r line; do echo "$(date +\%Y-\%m-\%d\ \%H:\%M:\%S) $line"; done >> ~/scripts/pbs_manager.log'
5 12 * * 2 /bin/bash -c 'cat /dev/null > ~/scripts/pbs_manager.log'
```

解释一下，第一个定时任务每分钟执行一次，每次无参数调用`pbs_manager`，将这个命令的所有输出加上时间戳，以追加方式输出到定时任务的日志文件`~/scripts/pbs_manager.log`，在绝大部分时间的记录形如
```
2024-06-18 11:32:01 No records found for checking.
2024-06-18 11:33:01 No records found for checking.
2024-06-18 11:34:01 No records found for checking.
```

在自检发现任务结束并触发邮件发送行为时的记录形如
```
2024-06-18 11:19:01 Welcome to Vlab
2024-06-18 11:19:02 Welcome to Vlab
2024-06-18 11:19:02 Welcome to Vlab
2024-06-18 11:19:03 Email sent successfully
2024-06-18 11:19:03 Processed record: 24408
2024-06-18 11:19:03 Record deleted.
```

第二个定时任务会在每周二中午12:05触发，自动清空日志文件。


## 发送邮件

> 因为服务器本身的网络受限，我选择了通过`ssh`将必要数据传递给`vlab`服务器，并且在`vlab`上调用脚本发送邮件的间接方案。

第三部分，在`vlab`上的邮件生成与发送

- 发送邮件的脚本为`~/scripts/send_mail.py`（Python3）
- 发送邮件涉及的配置文件为`~/scripts/config.ini`（存储发件邮箱，收件邮箱，授权密码等）

脚本的使用方式例如（这里执行命令所在的位置是用户家目录，即ssh登陆后的默认位置）
```bash
python3 scripts/send_mail.py --subject "PBS-NOTICE" --body_start "PBS-Job-Finished" --config scripts/config.ini --files file1.txt file2.txt
```

其中：

- `--subject`是必选的邮件标题（不能含有空格，否则解析错误）
- `--body_start`是可选的正文开头部分（不能含有空格，否则解析错误）
- `--config`是可选的，指定发送邮件使用的配置文件
- `--files`是可选的，用于生成邮件正文的文本文件
  - 至多支持三个文件
  - 对每个文件的长度有限制，超过限制的文件中间部分会被省略
  - 文件不存在或者打开失败不影响邮件的发送，会在邮件正文最后保留错误记录


在第一部分中，脚本在自检发现任务结束后，就会通过`ssh`登陆到`vlab`并调用上面形式的命令来发送邮件，注意这里的文件也是预先通过`scp`传递到`~/pbsdata`的，不能使用原本的路径。
