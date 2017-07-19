#! /bin/sh
if ! which puppet &> /dev/null; then
    yum install -y epel-release
    rpm -ivh https://yum.puppetlabs.com/puppetlabs-release-el-6.noarch.rpm
    yum install -y puppet
fi
