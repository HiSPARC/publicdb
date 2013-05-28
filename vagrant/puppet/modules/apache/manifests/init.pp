class apache {
  package { "apache2":
    ensure => present,
  }
  
  package { "libapache2-mod-wsgi":
    ensure => present,
    require => Package["apache2"]
  }

  service { "apache2":
    ensure => running,
    require => Package["libapache2-mod-wsgi"]
  }
    exec { "create_django_publicdb":
     command => "mkdir -p /var/www/django_publicdb",
      }
 
  file { "/var/www/django_publicdb":
    ensure => link,
    owner  => "vagrant",
    group  => "vagrant",
    target => "/vagrant/django_publicdb",
    notify => Service['apache2'],
    force  => true
  }
 
  file { "/etc/apache2/httpd.conf":
    ensure => link,
    target => "/vagrant/vagrant/puppet/modules/apache/manifests/hisparc.conf",
    owner  => vagrant,
    group  => vagrant,
    notify => Service['apache2'],
    force  => true
  }
}
