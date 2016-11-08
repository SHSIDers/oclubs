class oclubs::user {
    $secrets = hiera_hash('oclubs::secrets', undef)
    $timestamp = strip(generate('/bin/date'))

    file { '/usr/local/bin/pyshell':
        ensure => file,
        mode   => '0755',
        owner  => 'root',
        group  => 'root',
        source => 'puppet:///modules/oclubs/pyshell.sh',
    }

    if $::environment == 'vagrant' {
        file { '/home/vagrant/.my.cnf':
            ensure  => file,
            mode    => '0600',
            owner   => 'vagrant',
            group   => 'vagrant',
            content => template('oclubs/my.cnf.erb'),
        }
    }

    include ::motd

    create_resources('accounts::user', hiera_hash('oclubs::users', {}))

    $aliases = hiera_hash('oclubs::aliases', {})
    # TODO: Puppet 4 supports .each & lambda
    # $aliases.each |$key, $value| {
    #     mailalias { $key:
    #         recipient => $value,
    #         notify    => Exec['newaliases'],
    #     }
    # }
    define oclubs::user::alias () {
        $aliases = hiera_hash('oclubs::aliases', {})
        mailalias { $name:
            recipient => $aliases[$name],
            notify    => Exec['newaliases'],
        }
    }
    $aliaskeys = keys($aliases)
    oclubs::user::alias { $aliaskeys: }

    if ! defined(Exec['newaliases']) {
        exec { 'newaliases':
            command     => '/usr/bin/newaliases',
            refreshonly => true,
        }
    }

    file { '/etc/sudoers.d/agentforward':
        ensure  => present,
        content => 'Defaults>root env_keep+=SSH_AUTH_SOCK',
    }
}
