Vagrant.configure("2") do |config|

    config.vm.box = "bento/ubuntu-22.04"
  
    config.ssh.insert_key = false
    config.ssh.forward_agent = true
  
    
    config.vm.provider "virtualbox" do |vb|
      vb.cpus = 2
      vb.memory = "2048"
      # vb.gui = true
      # vb.customize ['modifyvm', :id, '--cableconnected1', 'on']
      # vb.customize ["modifyvm", :id, "--uart1", "0x3F8", "4"]
      # vb.customize ["modifyvm", :id, "--uartmode1", "file", File::NULL]
    end
    # config.ssh.private_key_path = "~/.ssh/id_rsa"
    # config.ssh.forward_agent = true
    config.vm.network "public_network"
    
    # config.vm.boot_timeout = 600
  
  # admin
  config.vm.synced_folder "./src", "/var/www/src", create:"true", mount_options: ["dmode=777","fmode=777"], type: "virtualbox"
  config.vm.synced_folder "mandc-ecorange", "/var/www/sc-framework", create:"true", mount_options: ["dmode=777","fmode=777"], type: "virtualbox"

  end
  