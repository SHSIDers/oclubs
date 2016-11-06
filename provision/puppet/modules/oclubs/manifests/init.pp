class oclubs {
    class { '::oclubs::baseservices': } -> class { '::oclubs::pythond': }
}
