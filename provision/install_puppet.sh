#! /bin/sh
which puppet &> /dev/null || ( yum install -y epel-release; yum install -y puppet rubygem-deep_merge )
