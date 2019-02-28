# -*- mode: ruby -*-

MACHINES = {
  publicdb: {hostname: "publicdb.localdomain", ip: "192.168.99.11", ssh: 2021, http: 8081, https:8443},
  vpn: {hostname: "vpn.localdomain", ip: "192.168.99.12", ssh: 2022, http: 8082, https:8444},
  datastore: {hostname: "datastore.localdomain", ip: "192.168.99.13", ssh: 2023, http: 8083, https:8445}
}

Vagrant.configure("2") do |config|

  config.vm.box = "CentOS7"
  config.vm.box_url = "packer/CentOS7/packer_virtualbox-iso_virtualbox.box"

  MACHINES.each do | ansible_host, values |
    config.vm.define ansible_host do |machine|
      machine.vm.hostname = values[:hostname]
      machine.vm.network :private_network, ip: values[:ip]
      machine.vm.network :forwarded_port, id: "ssh", guest: 22, host: values[:ssh]
      machine.vm.network :forwarded_port, id: "http", guest: 80, host: values[:http]
      machine.vm.network :forwarded_port, id: "https", guest: 443, host: values[:https]
    end
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
    if provisioner == :ansible_local then
      # force required upgrade of ansible on guest
      ansible.install = true
      ansible.version = "latest"
    end
    ansible.compatibility_mode = "2.0"
    ansible.inventory_path = inventory_path
    ansible.playbook = "provisioning/playbook.yml"
  end

  config.ssh.username = "hisparc"
end
