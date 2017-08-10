class oclubs::baseservices {
    $secrets = hiera_hash('oclubs::secrets', undef)

    include ::gcc

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


    include ::firewall
    include ::fw_base::pre
    include ::fw_base::post

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

    include ::logrotate

    if $::environment == 'production' {
        firewall { '102 Allow inbound HTTPS':
            dport  => 443,
            proto  => tcp,
            action => accept,
        }
    }
}
