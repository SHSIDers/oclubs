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

$redis_password = 'rhupwegPadroc)QuaysDigdobGotachOpbaljiebGadMyn1Drojryt'

exec { 'redis-set-pw':
    command => "/bin/sed -ie 's/# requirepass foobared/requirepass ${redis_password}/' /etc/redis.conf",
    notify  => Service['redis'],
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

$mysql_password = 'TacOrnibVeeHoFrej2RindofDic5faquavrymebZaidEytCojPhuanEr'

exec { 'db-set-root-pw':
    command => "/usr/bin/mysqladmin -u root password ${mysql_password}",
    unless  => "/usr/bin/mysqladmin -u root -p${mysql_password} status",
    require => Service['mysql'],
}

exec { 'sql-import':
    command => "/usr/bin/mysql -u root -p${mysql_password} < /vagrant/oclubs-tables.sql",
    require => Exec['db-set-root-pw'],
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

file { '/etc/selinux/config':
    ensure => file,
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
    source => '/vagrant/provision/selinux',
}

package { 'git':
    ensure => installed,
    before => Exec['git-clone-pyenv'],
}

exec { 'git-clone-pyenv':
    command => '/usr/bin/git clone --depth=1 https://github.com/yyuu/pyenv.git /srv/oclubs/pyenv',
    creates => '/srv/oclubs/pyenv',
    require => File['/srv/oclubs'],
}

file { '/home/vagrant/.bash_profile':
    ensure  => file,
    mode    => '0644',
    owner   => 'vagrant',
    group   => 'vagrant',
    source  => '/vagrant/provision/vagrant_bash_profile',
    require => Exec['git-clone-pyenv'],
}

exec { 'pyenv-init':
    command     => '/srv/oclubs/pyenv/bin/pyenv init -',
    environment => 'PYENV_ROOT=/srv/oclubs/pyenv',
    creates     => '/srv/oclubs/pyenv/versions/',
    require     => Exec['git-clone-pyenv'],
}

# everything needed to compile python
package { [
    'patch',
    'zlib-devel',
    'bzip2-devel',
    'openssl-devel',
    'sqlite-devel',
    'readline-devel'
]:
    ensure => present,
    before => Exec['pyenv-install-python'],
}

exec { 'pyenv-install-python':
    command     => '/srv/oclubs/pyenv/bin/pyenv install /vagrant/provision/python-pyenv',
    environment => 'PYENV_ROOT=/srv/oclubs/pyenv',
    creates     => '/srv/oclubs/pyenv/versions/python-pyenv/',
    require     => [
        Exec['pyenv-init'],
        Service['nginx'],
    ],
}

file { '/root/.pip':
    ensure => directory,
}

file { '/root/.pip/pip.conf':
    ensure => file,
    source => '/vagrant/provision/pip.conf',
    before => Exec['install-pip-tools'],
}

exec { 'install-pip-tools':
    command => '/srv/oclubs/pyenv/versions/python-pyenv/bin/pip install pip-tools',
    creates => '/srv/oclubs/pyenv/versions/python-pyenv/bin/pip-sync',
    tries   => 5,
    require => Exec['pyenv-install-python'],
}

package { [
    'python-devel',
    # 'zlib-devel',
    # 'openssl-devel',
    'libffi-devel',
    'libjpeg-turbo-devel',
    'libpng-devel',
]:
    ensure  => present,
    require => Package['epel-release'],
    before  => Exec['pip-install-requirements'],
}

exec { 'pip-install-requirements':
    command => '/srv/oclubs/pyenv/versions/python-pyenv/bin/pip-sync /vagrant/requirements.txt',
    tries   => 5,
    require => [
        Package['MariaDB-devel'],
        Exec['pyenv-install-python'],
        Exec['install-pip-tools']
    ],
}

user { 'uwsgi':
    ensure  => present,
    comment => 'uWSGI service user',
    home    => '/srv/oclubs',
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
    ensure => directory,
}

file { '/srv/oclubs/oclubs':
    ensure => link,
    target => '/vagrant/oclubs'
}

file { '/srv/oclubs/images':
    ensure => directory,
    mode   => '0755',
    owner  => 'uwsgi',
    group  => 'nginx'
}

file { '/srv/oclubs/secrets.ini':
    ensure  => file,
    replace => 'no',
    mode    => '0644',
    owner   => 'root',
    group   => 'root',
    source  => '/vagrant/provision/secrets.ini'
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


user { 'celery':
    ensure  => present,
    comment => 'Celery service user',
    home    => '/srv/oclubs',
    shell   => '/bin/bash',
    require => Exec['pip-install-requirements'],
    before  => Service['celeryd'],
}

exec { 'get-celeryd':
    command => '/usr/bin/wget https://github.com/celery/celery/raw/3.1/extra/generic-init.d/celeryd -O /etc/init.d/celeryd',
    creates => '/etc/init.d/celeryd'
}

file { '/etc/init.d/celeryd':
    ensure  => file,
    replace => 'no',
    mode    => '0755',
    owner   => 'root',
    group   => 'root',
    notify  => Service['celeryd'],
    require => Exec['get-celeryd']
}

file { '/etc/default/celeryd':
    ensure => file,
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
    source => '/vagrant/provision/celeryd-config',
    notify => Service['celeryd'],
}

service { 'celeryd':
    ensure => running,
    enable => true,
}

exec { 'get-celerybeat':
    command => '/usr/bin/wget https://github.com/celery/celery/raw/3.1/extra/generic-init.d/celerybeat -O /etc/init.d/celerybeat',
    creates => '/etc/init.d/celerybeat'
}

file { '/etc/init.d/celerybeat':
    ensure  => file,
    replace => 'no',
    mode    => '0755',
    owner   => 'root',
    group   => 'root',
    notify  => Service['celerybeat'],
    require => Exec['get-celerybeat']
}

file { '/etc/default/celerybeat':
    ensure => file,
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
    source => '/vagrant/provision/celerybeat-config',
    notify => Service['celerybeat'],
}

service { 'celerybeat':
    ensure  => running,
    enable  => true,
    require => Service['celeryd']
}


package { 'postfix':
    ensure => present,
    before => Package['epel-release'],
}

file { '/etc/postfix/main.cf':
    ensure => file,
    mode   => '0644',
    owner  => 'root',
    group  => 'root',
    source => '/vagrant/provision/postfix-main.cf',
    notify => Service['postfix'],
}

service { 'postfix':
    ensure => running,
    enable => true,
}
