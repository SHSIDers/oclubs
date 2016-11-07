class oclubs {
    include oclubs::assertions

    class { '::oclubs::baseservices': }->
    class { '::oclubs::pythond': }->
    class { '::oclubs::user': }
}
