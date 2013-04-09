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
    require => Package["apache2"],
  }

  file { "/var/www":
    ensure => link,
    target => "/vagrant/django_publicdb",
    notify => Service['apache2'],
    force  => true
  }
 
  file { "/etc/apache2/httpd.conf":
    ensure => link,
    target => "/vagrant/vagrant_hisparc/puppet/modules/apache/manifests/hisparc.conf",
    notify => Service['apache2'],
    force  => true
  }
}
