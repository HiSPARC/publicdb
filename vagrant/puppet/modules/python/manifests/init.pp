class python {

  package { "python-debian":
    ensure => present,
  }
  
  package { "python-dev":
    ensure => present,
    require => Package["python-debian"]
  }
  
  package { "python-mysqldb":
    ensure => present,
    require => Package["python-debian", "mysql-server"]
  }

  package { "python-pip":
    ensure => present,
    require => Package["python-dev"]
  }
  
  package { "Django":
    ensure => "1.4.3",
    provider => pip,
    require => Package["python-pip"]
  }
  
  package { "Cython":
    ensure => "0.16",
    provider => pip,
    require => Package["python-pip"]
  }
  
  package { "South":
    ensure => "0.7.3",
    provider => pip,
    require => Package["python-pip"]
  }
  
  package { "ipython":
    ensure => "0.12.1",
    provider => pip,
    require => Package["python-pip"]
  }  
  
  package { "numpy":
    ensure => "1.6.2",
    provider => pip,
    require => Package["python-pip"]
  }
  
  package { "numexpr":
    ensure => "2.0.1",
    provider => pip,
    require => Package["numpy"]
  }
  
  package { "recaptcha-client":
    ensure => "1.0.6",
    provider => pip,
    require => Package["python-pip"]
  }
  
  package { "pytables":
    ensure => installed,
    name => 'tables',
    provider => pip,
    require => [Package["python-pip"], Package["numexpr"], Package["Cython"], Package["numpy"], Package["libhdf5-serial-dev"] ]
  }
  
  package { "wsgiref":
    ensure => "0.1.2",
    provider => pip,
    require => Package["python-pip"]
  }
    exec { "create_static":
     command => "mkdir -p /var/www/static",
      }
   file { '/var/www/static':
     ensure  => 'present',
     mode   => '0777',
     owner   => "vagrant",
     group   => "vagrant",
     require => Exec["create_static"]    
  }
  
  exec { "syncdb":
    command => "python /var/www/manage.py syncdb --noinput --migrate",
    user => "vagrant",
    require => Package["pytables"],
    logoutput => on_failure
    }
    
  exec { "collectstatic":
    command => "python /var/www/manage.py collectstatic --noinput",
    user => "vagrant",
    require => exec["syncdb"],
    logoutput => on_failure
    }
    
    

}
