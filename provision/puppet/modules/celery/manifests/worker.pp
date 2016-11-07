define celery::worker(
    $app,
    $working_dir,
    $user,
    $group,
    $beat = false,
    $bin_path = '/usr/bin/celery',
    $nodes = 1,
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
        content => template('celery/worker_systemd.erb'),
        notify  => Service[$name],
    }

    service { $name:
        ensure => running,
        enable => true,
    }

    if $beat {
        file { "/etc/systemd/system/${name}beat.service":
            ensure  => file,
            mode    => '0644',
            owner   => 'root',
            group   => 'root',
            content => template('celery/beat_systemd.erb'),
            notify  => Service["${name}beat"],
        }

        service { "${name}beat":
            ensure => running,
            enable => true,
        }
    }

    logrotate::rule { $name:
        path          => "/var/log/${name}/*.log",
        rotate_every  => 'day',
        rotate        => 52,
        compress      => true,
        delaycompress => true,
        ifempty       => false,
        copytruncate  => true,
    }
}
