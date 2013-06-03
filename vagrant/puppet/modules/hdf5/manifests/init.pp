class hdf5 {
    exec { 'get_hdf5':
    command => "bash hdf5.sh",
    user => "vagrant",
    logoutput => on_failure
    }
}