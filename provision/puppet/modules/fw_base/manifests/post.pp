# Source: https://forge.puppet.com/puppetlabs/firewall#setup
class fw_base::post {
  Firewall {
    before => undef,
  }
  firewall { '999 drop all':
    proto  => 'all',
    action => 'drop',
  }
}
