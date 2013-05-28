Exec {
    path => "/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:usr/local/src/:usr/local/src/hisparc"
    }
    
    
exec { 'get_python':
    command => "bash python.sh",
    user => "vagrant",
    logoutput => on_failure
    }
    
exec { 'get_python_setuptools':
    command => "bash python_tools.sh",
    user => "vagrant",
    logoutput => on_failure
    }

exec { 'get_httpd':
command => "bash apache.sh",
user => "vagrant",
logoutput => on_failure
}

exec { 'get_bazaar':
command => "bash bazaar.sh",
user => "vagrant",
logoutput => on_failure
}

exec { 'get_hdf5':
command => "bash hdf5.sh",
user => "vagrant",
logoutput => on_failure
}

exec { 'get_git':
command => "bash git.sh",
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
  target => "/vagrant/vagrant/puppet/modules/apache/manifests/hisparc.conf",
  owner  => vagrant,
  group  => vagrant,
  force  => true
  }