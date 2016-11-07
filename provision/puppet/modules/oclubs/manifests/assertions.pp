class oclubs::assertions {
    unless $::operatingsystem == 'CentOS' and $::operatingsystemmajrelease == '7' {
        fail('oClubs backend code is designed for CentOS 7 only')
    }

    $secrets = hiera_hash('oclubs::secrets', undef)
    if empty($secrets[encrypt_key]) {
        fail('oclubs::secrets encrypt_key required')
    }
    if empty($secrets[flask_key]) {
        fail('oclubs::secrets flask_key required')
    }
    if empty($secrets[mariadb_pw]) {
        fail('oclubs::secrets mariadb_pw required')
    }
    if empty($secrets[redis_pw]) {
        fail('oclubs::secrets redis_pw required')
    }

    if $::environment != 'vagrant' and empty(hiera_hash('oclubs::users', {})) {
        fail('oclubs::users required for non-vagrant environment')
    }
}
