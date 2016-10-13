# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "centos/6"
  config.vm.hostname = "oclubs.shs.cn"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.network "private_network", ip: "192.168.8.201"

  config.vm.provider "virtualbox" do |vb|
    # Display the VirtualBox GUI when booting the machine
    # vb.gui = true

    # Customize the amount of memory on the VM:
    vb.memory = "1024"
  end

  if Vagrant::Util::Platform.windows? then
    config.vm.synced_folder ".", "/vagrant", type: "smb",
      owner: "root", group: "root"
  else
    config.vm.synced_folder ".", "/vagrant", type: "rsync",
      rsync__exclude: [".git/"], rsync__chown: false,
      owner: "root", group: "root"
  end

  config.vm.provision :shell, inline: "which puppet > /dev/null || ( yum install -y puppet && yum install -y epel-release )"
  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "provision/manifests"

    puppet.options = [
      '--verbose',
      '--debug',
    ]

    # Windows's Command Prompt has poor support for ANSI escape sequences.
    # puppet.options << '--color=false' if Vagrant::Util::Platform.windows?
  end
end
