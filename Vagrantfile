# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.define "vagrant" do |machine|
    machine.vm.box = "CentOS6"
    machine.vm.box_url = "packer/CentOS6/packer_virtualbox-iso_virtualbox.box"

    machine.vm.hostname = "vagrant.localdomain"
    machine.vm.network "private_network", ip: "192.168.99.10"
    machine.vm.network "forwarded_port", id: "ssh", guest: 22, host: 2022
    machine.vm.network "forwarded_port", guest: 80, host: 8080
  end

  config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  end

  config.vm.provision :ansible do |ansible|
    ansible.inventory_path = "provisioning/ansible_inventory"
    ansible.playbook = "provisioning/playbook.yml"
    ansible.host_key_checking = false
    ansible.ask_vault_pass = true
  end
  config.ssh.username = "hisparc"
end
