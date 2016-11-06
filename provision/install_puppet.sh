#! /bin/sh
which puppet &> /dev/null || ( yum install -y epel-release; yum install -y puppet )
