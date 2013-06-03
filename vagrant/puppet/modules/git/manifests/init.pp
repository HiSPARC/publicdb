class git {
    exec { 'get_git':
    command => "bash git.sh",
    user => "vagrant",
    logoutput => on_failure
    }
}