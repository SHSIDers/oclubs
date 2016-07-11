#!/bin/bash -ex

sed -i -e 's/\(^SELINUX=\).*$/\1permissive/' /etc/selinux/config

yum update -y
yum install -y epel-release

yum install -y redis nginx
service redis start
chkconfig redis on
service nginx start
chkconfig nginx on

cat > /etc/yum.repos.d/MariaDB.repo << EOF
[mariadb]
name = MariaDB
baseurl = http://yum.mariadb.org/10.1/centos6-amd64
gpgkey=https://yum.mariadb.org/RPM-GPG-KEY-MariaDB
gpgcheck=1
EOF

yum install -y MariaDB-server MariaDB-client MariaDB-devel
service mysql start
chkconfig mysql on

yum install -y python-pip python-devel

yum install -y zlib-devel openssl-devel

RETRY_MAX=5
for i in $(seq 1 $RETRY_MAX); do
    [ "$i" != "1" ] && echo "$(tput setaf 3)Retrying (attempt #$i):" "$@" "$(tput sgr0)" >&2
    pip install -Ur /vagrant/requirements.txt
    EXIT_CODE=$?
    [ "$EXIT_CODE" == "0" ] && break
    echo "$(tput setaf 1)Command failed with code $EXIT_CODE.$(tput sgr0)" >&2
done

adduser uwsgi | true

if [ ! -d /var/run/uwsgi ]; then mkdir /var/run/uwsgi; fi
chown uwsgi:nginx /var/run/uwsgi
if [ ! -d /var/log/uwsgi ]; then mkdir /var/log/uwsgi; fi
chown uwsgi:uwsgi /var/log/uwsgi
if [ ! -d /etc/uwsgi ]; then mkdir /etc/uwsgi; fi

# cat > /etc/init/uwsgi.conf << EOF
# description "uWSGI"
# start on runlevel [2345]
# stop on runlevel [!2345]
# respawn

# setuid uwsgi
# setgid nginx

# exec /usr/bin/uwsgi --ini /etc/uwsgi/uwsgi.ini
# EOF
# cat > /etc/systemd/system/uwsgi.service << EOF
# [Unit]
# Description=uWSGI
# After=network.target

# [Service]
# User=uwsgi
# Group=nginx
# WorkingDirectory=/srv
# ExecStart=/usr/bin/uwsgi --ini /etc/uwsgi/uwsgi.ini
# Restart=on-failure
# EOF

cp /vagrant/provision/uwsgi /etc/init.d/uwsgi
chmod 755 /etc/init.d/uwsgi

cat > /etc/uwsgi/uwsgi.ini << EOF
[uwsgi]
socket = /var/run/uwsgi/uwsgi.sock
pidfile = /var/run/uwsgi/uwsgi.pid
chmod-socket = 660
force-cwd = /srv
module = oclubs.app:app
uid = uwsgi
gid = nginx
master = true
die-on-term = true
processes = 4
threads = 2
logger = file:/var/log/uwsgi/uwsgi.log
EOF

if [ ! -L /srv/oclubs ]; then ln -s /vagrant/oclubs /srv/oclubs; fi
service uwsgi start
service uwsgi reload
chkconfig uwsgi on

cp /vagrant/provision/nginx.conf /etc/nginx/conf.d/default.conf
service nginx reload

cat > /etc/sysconfig/iptables << EOF
# Firewall configuration written by system-config-firewall
# Manual customization of this file is not recommended.
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
-A INPUT -p icmp -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 22 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 80 -j ACCEPT
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A FORWARD -j REJECT --reject-with icmp-host-prohibited
COMMIT
EOF
service iptables reload

mysql -u root < /vagrant/oclubs-tables.sql