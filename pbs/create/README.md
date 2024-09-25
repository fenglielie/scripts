# PBS本地自动化

下面是为PBS作业提交加上的一些自动化脚本。

## 生成项目快照

因为PBS脚本执行时间很长，在执行过程中修改源代码可能会产生影响，
我们必须拷贝整个项目（例如名为`demo`）到其它位置（例如`~/pbshome/`）中，在拷贝的快照中提交作业，这样我们对代码的后续修改和现有作业的执行不会产生相互影响。
如果当前项目是一个干净的Git项目，也可以选择直接进行本地仓库的克隆，因为`.gitignore`的存在，两种行为并不是等价的。

在生成项目快照时，我们可以记录一些关键信息，例如：

- 设置快照名称，自动加上时间戳作为拷贝后的文件夹名称，放置在`~/pbshome/demo/`位置下
  - 不提供名称时，文件夹名称形如：`snapsho-2024-06-18-11-03`
  - 提供名称并且不是git克隆行为时，文件夹名称形如：`snapshot-testmail-2024-06-18-11-03`
  - 提供名称并且是git克隆行为时，还会加上哈希值，文件夹名称形如：`snapshot-testmail-2024-06-18-11-03-bc9716f`
- 在拷贝文件夹中创建专门的日志文件`pbs.log`：（如果日志文件已经存在，则不会做任何修改）
  - 记录生成快照的拷贝/克隆行为
  - 记录作业的描述，目标

通过`create_snapshot`脚本实现，最简单的调用命令如下
```bash
create_snapshot
create_snapshot -N name
```

还可以加上作业的描述和目标
```bash
create_snapshot -N name --desc desc_string --todo todo_string
```


为了便于可视化操作（查看图片），选择将`~/pbshome`通过ssh挂载到`vlab`上（要先创建`~/pbshome`目录）
```bash
sudo apt install sshfs

sshfs ustc:~/pbshome ~/pbshome
```

取消挂载
```bash
fusermount -u <path>
```


## 生成PBS脚本

我们可以使用脚本自动化生成PBS脚本，只需要通过选项或者交互式地传递一些关键信息即可，这些信息包括：

- 作业名称（对应自动生成的PBS脚本名为`<作业名称>.job`）
- 队列名称
- 使用的节点数（会自动占满每一个节点的所有核）
- 执行命令

其中：

- 前几个选项如果不通过命令行传入，会交互式地提示用户填写；
- 执行命令选项是可选的，如果不在命令行中提供执行命令，会在最后提示用户必须在PBS脚本中手动添加执行命令。

通过`create_pbs`脚本实现，最简单的调用命令如下
```bash
create_pbs
```

可以直接加上可选参数
```bash
create_pbs -N <jobname> -q <queue_name> -l <nodes_num> -r <command>
```

例如
```bash
create_pbs -N testmail -q cu2 -l 1 -r "./a.out"
```
