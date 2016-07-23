Package {
    provider => 'yum'
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
    descr    => 'The MariaDB repository',
    enabled  => 1,
    gpgcheck => 1,
    gpgkey   => 'https://yum.mariadb.org/RPM-GPG-KEY-MariaDB',
}

exec { 'install-mariadb':
    command => '/usr/bin/yum -y localinstall /vagrant/MariaDB-10.1.14-centos6-x86_64-server.rpm /vagrant/MariaDB-10.1.14-centos6-x86_64-client.rpm',
    creates => '/usr/bin/mysql',
    timeout => 1800,
    require => Package['MariaDB-devel'],
}

package { 'MariaDB-devel':
    ensure  => present,
    require => [
        Package['epel-release'],
        Yumrepo['MariaDB'],
    ],
}

service { 'mysql':
    ensure  => running,
    enable  => true,
    require => Exec['install-mariadb'],
}

package { 'java-1.8.0-openjdk':
    ensure  => present,
    require => Package['epel-release'],
}

yumrepo { 'Elasticsearch':
    baseurl  => 'http://packages.elastic.co/elasticsearch/2.x/centos',
    descr    => 'Elasticsearch repository for 2.x packages',
    enabled  => 1,
    gpgcheck => 1,
    gpgkey   => 'http://packages.elastic.co/GPG-KEY-elasticsearch',
}

# package { 'elasticsearch':
#     ensure  => present,
#     require => Yumrepo['Elasticsearch'],
# }

exec { 'install-elasticsearch':
    command => '/usr/bin/yum -y localinstall /vagrant/elasticsearch-2.3.4.rpm',
    creates => '/etc/elasticsearch/',
    timeout => 1800,
    require => [
        Package['java-1.8.0-openjdk'],
        Yumrepo['Elasticsearch'],
    ],
}

file { '/etc/elasticsearch/elasticsearch.yml':
    ensure  => file,
    mode    => '0750',
    owner   => 'root',
    group   => 'elasticsearch',
    source  => '/vagrant/provision/elasticsearch.yml',
    require => Exec['install-elasticsearch'],
    notify  => Service['elasticsearch'],
}

service { 'elasticsearch':
    ensure => running,
    enable => true,
}

exec { 'sql-import':
    command => '/usr/bin/mysql -u root < /vagrant/oclubs-tables.sql',
    require => Service['mysql'],
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
    'libffi-devel',
    'libjpeg-turbo-devel',
    'libpng-devel',
]:
    ensure  => present,
    require => Package['epel-release'],
    before  => Exec['pip-install-requirements'],
}

exec { 'pip-install-requirements':
    command => 'pip install -r /vagrant/requirements.txt',
    path    => '/usr/bin',
    tries   => 5,
    require => Package['MariaDB-devel'],
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

file { '/srv/oclubs/images':
    ensure => directory,
    owner  => 'uwsgi',
    group  => 'uwsgi'
}

file { '/srv/oclubs/secrets.ini':
    ensure => file,
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
    source => '/vagrant/provision/secrets.ini'
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
