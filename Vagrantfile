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

  config.vm.define "publicdb" do |machine|
    machine.vm.box = "CentOS6"
    machine.vm.box_url = "packer/CentOS6/packer_virtualbox-iso_virtualbox.box"

    machine.vm.hostname = "publicdb.localdomain"
    machine.vm.network "private_network", ip: "192.168.99.11"
    machine.vm.network "forwarded_port", id: "ssh", guest: 22, host: 2023
    machine.vm.network "forwarded_port", guest: 80, host: 8081
  end

  config.vm.define "vpn" do |machine|
    machine.vm.box = "CentOS6"
    machine.vm.box_url = "packer/CentOS6/packer_virtualbox-iso_virtualbox.box"

    machine.vm.hostname = "vpn.localdomain"
    machine.vm.network "private_network", ip: "192.168.99.12"
    machine.vm.network "forwarded_port", id: "ssh", guest: 22, host: 2024
    machine.vm.network "forwarded_port", guest: 80, host: 8082
  end

  config.vm.define "datastore" do |machine|
    machine.vm.box = "CentOS6"
    machine.vm.box_url = "packer/CentOS6/packer_virtualbox-iso_virtualbox.box"

    machine.vm.hostname = "datastore.localdomain"
    machine.vm.network "private_network", ip: "192.168.99.13"
    machine.vm.network "forwarded_port", id: "ssh", guest: 22, host: 2025
    machine.vm.network "forwarded_port", guest: 80, host: 8083
  end

  config.vm.provider :virtualbox do |vb|
      vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  end

  if Vagrant::Util::Platform.windows? then
      provisioner = :ansible_local
      inventory_path = "provisioning/ansible_inventory_local"
  else
      provisioner = :ansible
      inventory_path = "provisioning/ansible_inventory"
  end

  config.vm.provision provisioner do |ansible|
    ansible.inventory_path = inventory_path
    ansible.playbook = "provisioning/playbook.yml"
  end

  config.ssh.username = "hisparc"
end
