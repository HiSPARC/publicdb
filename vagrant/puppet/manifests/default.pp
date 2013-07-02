Exec {
    path => "/usr/local/bin:/usr/local/sbin:/bin:/sbin:/usr/bin:/usr/sbin:/vagrant"
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

exec { 'get_hdf5':
    command => "bash hdf5.sh",
    user => "vagrant",
    require => Exec['get_python_setuptools'],
    logoutput => on_failure,
}

exec { 'get_git':
    command => "bash git.sh",
    user => "vagrant",
    logoutput => on_failure
}

exec { 'get_bazaar':
    command => "bash bazaar.sh",
    user => "vagrant",
    require => Exec['get_git'],
    logoutput => on_failure
}

exec { 'get_virt1':
    command => "bash virtualenv_files.sh",
    user => "vagrant",
    require => Exec['get_bazaar'],
    logoutput => on_failure
}

exec { 'get_virt2':
    command => "bash virtualenv_pip.sh",
    user => "vagrant",
    require => Exec['get_virt1'],
    logoutput => on_failure
}

exec { 'get_virt3':
    command => "bash virtualenv_pip2.sh",
    user => "vagrant",
    require => Exec['get_virt2'],
    logoutput => on_failure
}

exec { 'get_virt4':
    command => "bash virtualenv_pip3.sh",
    user => "vagrant",
    require => Exec['get_virt3'],
    logoutput => on_failure
}

exec { 'get_virt_scipy':
    command => "bash virtualenv_pip_scipy.sh",
    user => "vagrant",
    require => Exec['get_virt4'],
    logoutput => on_failure
}

exec { 'get_virt_sapphire':
    command => "bash virtualenv_pip_sapphire.sh",
    user => "vagrant",
    require => Exec['get_virt_scipy'],
    logoutput => on_failure
}

exec { 'get_virt_sql':
    command => "bash virtualenv_pip_sql.sh",
    user => "vagrant",
    require => Exec['get_virt_scipy'],
    logoutput => on_failure
}

exec { 'get_vir3':
    command => "bash virtualenv_last.sh",
    user => "vagrant",
    require => Exec['get_virt_sql'],
    logoutput => on_failure
}
