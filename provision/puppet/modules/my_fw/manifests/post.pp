# Source: https://forge.puppet.com/puppetlabs/firewall#setup
class my_fw::post {
  Firewall {
    before => undef,
  }
  firewall { '999 drop all':
    proto  => 'all',
    action => 'drop',
  }
}
