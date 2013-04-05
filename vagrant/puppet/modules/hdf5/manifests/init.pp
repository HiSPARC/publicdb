class hdf5 {
    package { "hdf5-tools":
        ensure => installed,
    }

    package { "libhdf5-serial-dev":
        ensure => installed,
        require => Package["hdf5-tools"]
    }
}