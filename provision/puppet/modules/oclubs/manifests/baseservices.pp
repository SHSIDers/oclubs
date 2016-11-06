class oclubs::baseservices {
    $secrets = hiera_hash('oclubs::secrets', undef)

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

    file { '/home/vagrant/.my.cnf':
        ensure => file,
        mode   => '0600',
        owner  => 'vagrant',
        group  => 'vagrant',
        source => '/srv/oclubs/repo/provision/my.cnf',
    }

    include ::elasticsearch
    elasticsearch::instance { 'node-1': }

    include ::selinux


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

    include ::postfix
}
