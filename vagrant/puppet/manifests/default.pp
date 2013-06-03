Exec {
    path => "/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:usr/local/src/:usr/local/src/hisparc:/vagrant"
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
  
exec { 'get_mysql':
    command => "bash mysql.sh",
    user => "vagrant",
    logoutput => on_failure
}
exec { "create_static":
 command => "sudo mkdir -p /var/www/static",
}

exec { "adjust_static":
 command => "bash adjustments.sh",
 user => "vagrant",
 require => Exec['create_static']
  }
  
exec { "sqlite_devel":
 command => "bash sqlite_devel.sh",
 user => "vagrant",
 require => Exec['get_mysql'] 
}

exec { "recompile_python":
 command => "bash recompile_python.sh",
 user => "vagrant",
 require => Exec['sqlite_devel'],
 logoutput => on_failure
}


exec { "syncdb":
command => "bash syncdb.sh",
user => "vagrant",
require => Exec['recompile_python'],
logoutput => on_failure
}

exec { "collectstatic":
command => "bash migrate.sh",
user => "vagrant",
require => Exec["syncdb"],
logoutput => on_failure
}

