class oclubs () {
    $secrets = hiera_hash('oclubs::secrets', undef)

    package { 'git':
        ensure => installed,
    }

    include ::redis

    include ::nginx

    include ::mysql::server
    include ::mysql::client
    include ::mysql::bindings

    exec { 'sql-import':
        command => "/usr/bin/mysql -u root -p'${secrets[mariadb_pw]}' < /srv/oclubs/repo/oclubs-tables.sql",
        unless  => "/usr/bin/mysql -u root -p'${secrets[mariadb_pw]}' oclubs < /dev/null",
        require => Class['::mysql::server'],
    }

    include ::elasticsearch
    elasticsearch::instance { 'node-1': }

    include ::selinux

    include ::python
    python::virtualenv { '/srv/oclubs/venv' :
        ensure => present,
        owner  => 'root',
        group  => 'root',
    }

    exec { 'upgrade-pip':
        command => '/srv/oclubs/venv/bin/pip install -U pip',
        # If we have pip-sync, this step is already done
        creates => '/srv/oclubs/venv/bin/pip-sync',
        require => Python::Virtualenv['/srv/oclubs/venv'],
    }

    exec { 'install-pip-tools':
        command => '/srv/oclubs/venv/bin/pip install pip-tools',
        creates => '/srv/oclubs/venv/bin/pip-sync',
        require => Exec['upgrade-pip'],
    }

    exec { 'pip-install-requirements':
        command => '/srv/oclubs/venv/bin/pip-sync /srv/oclubs/repo/requirements.txt',
        tries   => 5,
        timeout => 1800,
        require => [
            Class['::mysql::bindings'],
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

    package { 'uwsgi-plugin-python':
        ensure => present,
        before => Class['::uwsgi'],
    }

    include ::uwsgi

    file { '/srv/oclubs':
        ensure => directory,
    }

    file { '/srv/oclubs/oclubs':
        ensure => link,
        target => '/srv/oclubs/repo/oclubs',
        before => [
            Class['::uwsgi'],
            # Class['::celery'],
        ]
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


    include ::firewall
    include ::my_fw::pre
    include ::my_fw::post

    firewall { '100 Allow inbound SSH':
        dport  => 22,
        proto  => tcp,
        action => accept,
    }
    firewall { '101 Allow inbound HTTP':
        dport  => 80,
        proto  => tcp,
        action => accept,
    }

    #
    #
    # user { 'celery':
    #     ensure  => present,
    #     comment => 'Celery service user',
    #     home    => '/srv/oclubs',
    #     shell   => '/bin/bash',
    #     groups  => 'pythond',
    #     require => Exec['pip-install-requirements'],
    #     before  => Service['celeryd'],
    # }
    #
    # exec { 'get-celeryd':
    #     command => '/usr/bin/wget https://github.com/celery/celery/raw/3.1/extra/generic-init.d/celeryd -O /etc/init.d/celeryd',
    #     creates => '/etc/init.d/celeryd'
    # }
    #
    # file { '/etc/init.d/celeryd':
    #     ensure  => file,
    #     replace => 'no',
    #     mode    => '0755',
    #     owner   => 'root',
    #     group   => 'root',
    #     notify  => Service['celeryd'],
    #     require => Exec['get-celeryd']
    # }
    #
    # file { '/etc/default/celeryd':
    #     ensure => file,
    #     mode   => '0644',
    #     owner  => 'root',
    #     group  => 'root',
    #     source => '/srv/oclubs/repo/provision/celeryd-config',
    #     notify => Service['celeryd'],
    # }
    #
    # service { 'celeryd':
    #     ensure => running,
    #     enable => true,
    # }
    #
    # exec { 'get-celerybeat':
    #     command => '/usr/bin/wget https://github.com/celery/celery/raw/3.1/extra/generic-init.d/celerybeat -O /etc/init.d/celerybeat',
    #     creates => '/etc/init.d/celerybeat'
    # }
    #
    # file { '/etc/init.d/celerybeat':
    #     ensure  => file,
    #     replace => 'no',
    #     mode    => '0755',
    #     owner   => 'root',
    #     group   => 'root',
    #     notify  => Service['celerybeat'],
    #     require => Exec['get-celerybeat']
    # }
    #
    # file { '/etc/default/celerybeat':
    #     ensure => file,
    #     mode   => '0644',
    #     owner  => 'root',
    #     group  => 'root',
    #     source => '/srv/oclubs/repo/provision/celerybeat-config',
    #     notify => Service['celerybeat'],
    # }
    #
    # service { 'celerybeat':
    #     ensure  => running,
    #     enable  => true,
    #     require => Service['celeryd']
    # }
    #
    #
    include ::postfix

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
