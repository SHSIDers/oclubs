# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "centos/7"
  config.vm.hostname = "oclubs.shs.cn"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.network "private_network", ip: "192.168.8.201"

  config.vm.provider :virtualbox do |vb|
    # Display the VirtualBox GUI when booting the machine
    # vb.gui = true

    # Customize the amount of memory on the VM:
    vb.memory = "1024"
  end

  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/srv/oclubs/repo", type: "virtualbox",
    owner: "root", group: "root", create: true

  config.vm.provision :shell,
    inline: "which puppet &> /dev/null || ( yum install -y epel-release; yum install -y puppet )"
  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = 'provision/puppet/manifests'
    puppet.manifest_file = 'site.pp'
    puppet.hiera_config_path = 'provision/puppet/hiera.yaml'
    puppet.module_path = 'provision/puppet/modules'

    puppet.options = [
      '--verbose',
      '--debug',
    ]

    puppet.facter = {
      'environment' => ENV['PUPPET_ENVIRONMENT'] || 'vagrant',
    }
  end
end
