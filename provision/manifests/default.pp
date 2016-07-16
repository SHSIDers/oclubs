Package {
    provider => 'yum'
}

exec { 'yum-update':
    command => 'yum -y update',
    path    => '/usr/bin',
}

package { 'epel-release':
    ensure => present,
}

package { 'redis':
    ensure  => present,
    require => Package['epel-release']
}

service { 'redis':
    ensure  => running,
    enable  => true,
    require => Package['redis'],
}

package { 'nginx':
    ensure  => present,
    require => Package['epel-release']
}

service { 'nginx':
    ensure  => running,
    enable  => true,
    require => Package['nginx'],
}

file { '/etc/nginx/conf.d/default.conf':
    ensure => file,
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
    source => '/vagrant/provision/nginx.conf',
    notify => Service['nginx']
}

yumrepo { 'MariaDB':
    baseurl  => 'http://yum.mariadb.org/10.1/centos6-amd64',
    descr    => 'The name repository',
    enabled  => 1,
    gpgcheck => 1,
    gpgkey   => 'https://yum.mariadb.org/RPM-GPG-KEY-MariaDB',
}

package { [
    'MariaDB-server',
    'MariaDB-client',
    'MariaDB-devel'
]:
    ensure  => present,
    require => [
        Package['epel-release'],
        Yumrepo['MariaDB'],
    ],
}

# package { [
#     'mysql-server',
#     'mysql',
#     'mysql-devel'
# ]:
#     ensure  => present,
#     require => Package['epel-release'],
# }

service { 'mysql':
    ensure  => running,
    # name    => 'mysqld', # for mysql only, not mariadb
    enable  => true,
    require => Package['MariaDB-server'],
    # require => Package['mysql-server'],
}

exec { 'sql-import':
    command => '/usr/bin/mysql -u root < /vagrant/oclubs-tables.sql',
    require => [
        Service['mysql'],
        Package['MariaDB-client'],
        # Package['mysql'],
    ]
}

file { '/etc/selinux/config':
    ensure => file,
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
    source => '/vagrant/provision/selinux',
}

package { [
    'python-pip',
    'python-devel',
    'zlib-devel',
    'openssl-devel',
    'libffi-devel'
]:
    ensure  => present,
    require => Package['epel-release'],
    before  => Exec['pip-install-requirements'],
}

exec { 'pip-install-requirements':
    command => 'pip install -Ur /vagrant/requirements.txt',
    path    => '/usr/bin',
    tries   => 5,
}

user { 'uwsgi':
    ensure  => present,
    comment => 'uWSGI service user',
    home    => '/srv',
    shell   => '/sbin/nologin',
    require => Exec['pip-install-requirements'],
}

file { '/var/run/uwsgi':
    ensure  => directory,
    owner   => 'uwsgi',
    group   => 'nginx',
    require => User['uwsgi'],
}

file { '/var/log/uwsgi':
    ensure  => directory,
    owner   => 'uwsgi',
    group   => 'uwsgi',
    require => User['uwsgi'],
}

file { '/etc/uwsgi':
    ensure  => directory,
    owner   => 'root',
    group   => 'root',
    require => Exec['pip-install-requirements'],
}

file { '/etc/uwsgi/uwsgi.ini':
    ensure  => file,
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    source  => '/vagrant/provision/uwsgi.ini',
    require => Exec['pip-install-requirements'],
    notify  => Service['uwsgi']
}

file { '/etc/init.d/uwsgi':
    ensure  => file,
    mode    => '0755',
    owner   => 'root',
    group   => 'root',
    source  => '/vagrant/provision/uwsgi',
    require => File['/etc/uwsgi'],
    notify  => Service['uwsgi']
}

service { 'uwsgi':
    ensure  => running,
    enable  => true,
    require => [
        Exec['pip-install-requirements'],
        User['uwsgi'],
        File['/var/run/uwsgi'],
        File['/var/log/uwsgi'],
        File['/etc/uwsgi/uwsgi.ini'],
    ]
}

file { '/srv/oclubs':
    ensure => link,
    target => '/vagrant/oclubs'
}

service { 'iptables':
    ensure => running,
    enable => true,
}


file { '/etc/sysconfig/iptables':
    ensure => file,
    mode   => '0600',
    owner  => 'root',
    group  => 'root',
    source => '/vagrant/provision/iptables',
    notify => Service['iptables']
}
