define celery::beat(
    $app,
    $working_dir,
    $user,
    $group,
    $beat = false,
    $bin_path = '/usr/bin/celery',
    $opts = '',
) {
    if ! defined(User[$user]) {
        user { $user:
            ensure  => present,
            comment => 'Celery service user',
            home    => $working_dir,
            shell   => '/bin/bash',
            groups  => $group,
            before  => Service[$name],
        }
    }

    file { "/var/log/${name}":
        ensure => directory,
        owner  => $user,
        group  => $group,
        before => Service[$name],
    }

    file { "/etc/systemd/system/${name}.service":
        ensure  => file,
        mode    => '0644',
        owner   => 'root',
        group   => 'root',
        content => template('celery/beat_systemd.erb'),
        notify  => Service[$name],
    }

    service { $name:
        ensure => running,
        enable => true,
    }
}
