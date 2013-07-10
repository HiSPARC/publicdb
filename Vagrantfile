# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "SLC5.9"
  config.vm.box_url = "veewee/SLC5.9.box"

  config.vm.network :private_network, ip: "192.168.10.10"

  config.vm.provision :ansible do |ansible|
    ansible.playbook = "playbook.yml"
    ansible.inventory_file = "ansible_hosts"
  end
end
