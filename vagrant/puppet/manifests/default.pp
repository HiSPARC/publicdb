Exec {
    path => "/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin"
}

exec { "apt-update":
    command => "apt-get update"
}

Exec["apt-update"] -> Package <| |>

include hdf5
include mysql
include sqlite
include git
include apache
include python