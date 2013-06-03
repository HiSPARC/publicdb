class apache {
    exec { 'get_httpd':
    command => "bash apache.sh",
    user => "vagrant",
    logoutput => on_failure
    }

 
    file { "/var/www/django_publicdb":
      owner  => "vagrant",
      group  => "vagrant",
      target => "/vagrant/django_publicdb",
      force  => true
    }
    file { "/etc/httpd/httpd.conf":
      owner  => "vagrant",
      group  => "vagrant",
      target => "/vagrant/vagrant/puppet/modules/apache/manifests/hisparc.conf",
      force  => true
    }
}
