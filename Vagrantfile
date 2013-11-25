# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "SLC5.9"
  config.vm.box_url = "veewee/SLC5.9.box"

  config.vm.provision :ansible do |ansible|
    ansible.playbook = "provisioning/playbook.yml"
  end
  config.ssh.username = "hisparc"
end
