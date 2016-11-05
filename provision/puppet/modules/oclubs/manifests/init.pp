class oclubs (
    $secrets,
) {
    package { 'git':
        ensure => installed,
    }

    include ::redis

    package { 'nginx':
        ensure  => present,
        require => Package['epel-release']
    }

    service { 'nginx':
        ensure  => running,
        enable  => true,
        require => Package['nginx'],
    }

    file { '/var/nginx':
        ensure  => directory,
        owner   => 'nginx',
        group   => 'nginx',
        before  => Service['nginx'],
        require => Package['nginx'],
    }

    file { '/etc/nginx/conf.d/default.conf':
        ensure => file,
        mode   => '0644',
        owner  => 'root',
        group  => 'root',
        source => '/srv/oclubs/repo/provision/nginx.conf',
        notify => Service['nginx']
    }

    yumrepo { 'MariaDB':
        # baseurl  => 'http://yum.mariadb.org/10.1/centos6-amd64',
        baseurl  => 'https://mirrors.tuna.tsinghua.edu.cn/mariadb/yum/10.1/centos6-amd64/',
        descr    => 'The MariaDB repository',
        enabled  => 1,
        gpgcheck => 1,
        gpgkey   => 'https://yum.mariadb.org/RPM-GPG-KEY-MariaDB',
        before   => Class['::mysql'],
    }

    include ::mysql::server
    include ::mysql::client
    include ::mysql::bindings

    exec { 'sql-import':
        command => "/usr/bin/mysql -u root -p'${secrets[mysql_password]}' < /srv/oclubs/repo/oclubs-tables.sql",
        unless  => "/usr/bin/mysql -u root -p'${secrets[mysql_password]}' oclubs < /dev/null",
        require => Service['::mysql::server'],
    }

    include ::elasticsearch

    elasticsearch::instance { 'node-1': }

    include ::selinux

    vcsrepo { '/srv/oclubs/pyenv':
        source   => 'https://github.com/yyuu/pyenv.git',
        depth    => 1,
        provider => git,
    }

    file { '/home/vagrant/.bash_profile':
        ensure  => file,
        mode    => '0644',
        owner   => 'vagrant',
        group   => 'vagrant',
        source  => '/srv/oclubs/repo/provision/vagrant_bash_profile',
        require => Vcsrepo['/srv/oclubs/pyenv'],
    }

    exec { 'pyenv-init':
        command     => '/srv/oclubs/pyenv/bin/pyenv init -',
        environment => 'PYENV_ROOT=/srv/oclubs/pyenv',
        creates     => '/srv/oclubs/pyenv/versions/',
        require     => Vcsrepo['/srv/oclubs/pyenv'],
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
        command     => '/srv/oclubs/pyenv/bin/pyenv install /srv/oclubs/repo/provision/python-pyenv',
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
        source => '/srv/oclubs/repo/provision/pip.conf',
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
        command => '/srv/oclubs/pyenv/versions/python-pyenv/bin/pip-sync /srv/oclubs/repo/requirements.txt',
        tries   => 5,
        timeout => 1800,
        require => [
            Package['MariaDB-devel'],
            Exec['pyenv-install-python'],
            Exec['install-pip-tools']
        ],
    }

    group { 'pythond':
        ensure  => present,
    }

    user { 'uwsgi':
        ensure  => present,
        comment => 'uWSGI service user',
        home    => '/srv/oclubs',
        shell   => '/sbin/nologin',
        groups  => 'pythond',
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
        source  => '/srv/oclubs/repo/provision/uwsgi.ini',
        require => Exec['pip-install-requirements'],
        notify  => Service['uwsgi']
    }

    file { '/etc/init.d/uwsgi':
        ensure  => file,
        mode    => '0755',
        owner   => 'root',
        group   => 'root',
        source  => '/srv/oclubs/repo/provision/uwsgi',
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
        target => '/srv/oclubs/repo/oclubs'
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
        mode    => '0640',
        owner   => 'root',
        group   => 'pythond',
        source  => '/srv/oclubs/repo/provision/secrets.ini'
    }

    file { '/srv/oclubs/siteconfig.ini':
        ensure  => file,
        replace => 'no',
        mode    => '0664',
        owner   => 'root',
        group   => 'pythond',
        source  => '/srv/oclubs/repo/provision/siteconfig.ini'
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
        source => '/srv/oclubs/repo/provision/iptables',
        notify => Service['iptables']
    }


    user { 'celery':
        ensure  => present,
        comment => 'Celery service user',
        home    => '/srv/oclubs',
        shell   => '/bin/bash',
        groups  => 'pythond',
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
        source => '/srv/oclubs/repo/provision/celeryd-config',
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
        source => '/srv/oclubs/repo/provision/celerybeat-config',
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
        source => '/srv/oclubs/repo/provision/postfix-main.cf',
        notify => Service['postfix'],
    }

    service { 'postfix':
        ensure => running,
        enable => true,
    }


    file { '/home/vagrant/.my.cnf':
        ensure => file,
        mode   => '0600',
        owner  => 'vagrant',
        group  => 'vagrant',
        source => '/srv/oclubs/repo/provision/my.cnf',
    }

    file { '/usr/local/bin/pyshell':
        ensure => file,
        mode   => '0755',
        owner  => 'root',
        group  => 'root',
        source => '/srv/oclubs/repo/provision/pyshell.sh',
    }
}
