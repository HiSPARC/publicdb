class python {
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

    exec { 'get_bazaar':
        command => "bash bazaar.sh",
        user => "vagrant",
        logoutput => on_failure
    }


}
