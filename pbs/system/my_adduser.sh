#!/bin/bash

if [[ -z $1 || -z $2 ]]; then
	echo "Usage: $0 <username> <password> [group]"
	exit 1
fi

# 参数获取
my_username=$1
my_password=$2
group=$3


# 设置默认组名
if [[ -z $group ]]; then
	group=$my_username
fi

# 设置默认用户主目录
home="/home/$my_username"

# 创建组（如果不存在）
if ! getent group $group > /dev/null; then
    groupadd $group
fi

# 创建用户
useradd -m -d $home -s /bin/bash -g $group $my_username

# 设置用户密码
echo "$my_password" | passwd --stdin $my_username

# 确保NIS服务器配置生效
if [ -d /var/yp ]; then
	cd /var/yp
	make
	cd -
fi

# 配置无密码SSH登录
su - $my_username -c 'ssh-keygen -f ~/.ssh/id_rsa -N ""'

# 配置authorized_keys
cat $home/.ssh/id_rsa.pub >> $home/.ssh/authorized_keys
chmod 644 $home/.ssh/authorized_keys

# 复制known_hosts
if [ -f /root/my_adduser_dir/known_hosts ]; then
	cp /root/my_adduser_dir/known_hosts $home/.ssh/known_hosts
fi

chown -R $my_username:$group $home/.ssh/

# 附加自定义bash配置
if [ -f /root/my_adduser_dir/bash.sh ]; then
	cat /root/my_adduser_dir/bash.sh >> $home/.bashrc
	chown $my_username:$group $home/.bashrc
fi

echo "User $my_username created and configured successfully."
