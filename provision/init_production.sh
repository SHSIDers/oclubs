#! /bin/bash

set -e

set_hostname() {
    if [[ $HOSTNAME != 'oclubs.shs.cn' ]]; then
        # Translated from: https://github.com/mitchellh/vagrant/blob/master/plugins/guests/redhat/cap/change_host_name.rb
        local name=oclubs.shs.cn
        local basename=oclubs

        # Update sysconfig
        sed -i "s/\\(HOSTNAME=\\).*/\\1${name}/" /etc/sysconfig/network

        # Update DNS
        sed -i "s/\\(DHCP_HOSTNAME=\\).*/\\1\"${basename}\"/" /etc/sysconfig/network-scripts/ifcfg-*

        # Set the hostname - use hostnamectl if available
        echo "${name}" > /etc/hostname
        if command -v hostnamectl &> /dev/null; then
            hostnamectl set-hostname --static "${name}"
            hostnamectl set-hostname --transient "${name}"
        else
            hostname -F /etc/hostname
        fi

        # Remove comments and blank lines from /etc/hosts
        sed -i'' -e 's/#.*$//' -e '/^$/d' /etc/hosts

        # Prepend ourselves to /etc/hosts
        grep -w "${name}" /etc/hosts || {
            sed -i'' "1i 127.0.0.1\\t${name}\\t${basename}" /etc/hosts
        }

        # Restart network
        service network restart
    fi
}

clone_repo() {
    which git &> /dev/null || yum install -y git

    if [[ ! -d /srv/oclubs/repo ]]; then
        mkdir -p /srv/oclubs
        git clone git@github.com:zhuyifei1999/oclubs.git /srv/oclubs/repo
        pushd /srv/oclubs/repo
        git checkout centos7 || true # FIXME: remove this line when merged into master
        git submodule update --init --recursive --remote
        popd
    fi
}

init_hiera() {
    if [[ ! -f /srv/oclubs/repo/provision/puppet/hieradata/environment/production.yaml ]]; then
        echo 'The script will create a new POXIX user for logging into the backend.'
        echo 'Please refer to https://help.ubuntu.com/community/RootSudo and'
        echo 'https://wiki.centos.org/TipsAndTricks/BecomingRoot for more information.'

        local USERNAME PASSWORD

        set +e
        while true; do
            echo -n 'Username: '
            read USERNAME

            if [[ -z $USERNAME ]]; then
                echo 'Username cannot be empty'
                continue
            elif ! [[ $USERNAME =~ ^[A-Za-z0-9]+$ ]]; then
                echo 'Alphanumeric username only'
                continue
            elif getent passwd $USERNAME &> /dev/null; then
                echo "$USERNAME is already used. Is it reserved system user?"
                continue
            else
                break
            fi
        done
        set -e

        while true; do
            if PASSWORD=`openssl passwd -1`; then
                break
            fi
        done
        set -e

        gen_pw() {
            cat /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c "`shuf -i 50-60 -n 1`" || true
        }

        local REDIS_PW MARIADB_PW ENCRYPT_KEY FLASK_KEY
        REDIS_PW=`gen_pw`
        MARIADB_PW=`gen_pw`
        ENCRYPT_KEY=`head -c 16 /dev/urandom | od -A n -v -t x1 | tr -d ' \n'`
        FLASK_KEY=`gen_pw`

        touch /srv/oclubs/repo/provision/puppet/hieradata/environment/production.yaml
        chmod 600 /srv/oclubs/repo/provision/puppet/hieradata/environment/production.yaml

        cat > /srv/oclubs/repo/provision/puppet/hieradata/environment/production.yaml << EOF
---
redis::requirepass: '$REDIS_PW'

mysql::server::root_password: '$MARIADB_PW'

oclubs::secrets:
    encrypt_key: '$ENCRYPT_KEY'
    flask_key: '$FLASK_KEY'
    # FIXME
    # db2_conn: 'DATABASE=;HOSTNAME=;PORT=;PROTOCOL=TCPIP;UID=;PWD=' # Ask this from your IT teacher
    # sendgrid_key: '' # Sendgrid API key for sending emails reliably to hard-to-contact services such as Gmail

oclubs::users:
    $USERNAME:
        uid: '3001'
        gid: '3001'
        password: '$PASSWORD'
        groups:
            - wheel
        # FIXME
        # sshkeys:
        #     - 'Put your ssh public key here'

oclubs::aliases:
    no-reply: /dev/null
    creators:
        - oclubs@outlook.com

    clubsadmin:
        - creators
        - $USERNAME
        # FIXME
        # Put the email addresses of other admins here

    # FIXME
    # $USERNAME: Put your email address here, if you wish to receive email on an external mailbox (Gmail, Hotmail, etc.)
    # Note: Gmail may not work due to the great firewall
EOF
    fi
}

install_run_puppet() {
    sh /srv/oclubs/repo/provision/install_puppet.sh

    cat > /usr/sbin/run_puppet << 'EOF'
#! /bin/sh

if [[ $UID -ne 0 ]]; then
    exec sudo $0 "$@"
fi

FACTOR_environment=production puppet apply --verbose --debug --modulepath /srv/oclubs/repo/provision/puppet/modules:/etc/puppet/modules --hiera_config=/srv/oclubs/repo/provision/puppet/hiera.yaml --detailed-exitcodes --manifestdir /srv/oclubs/repo/provision/puppet/manifests /srv/oclubs/repo/provision/puppet/manifests/site.pp

EXITCODE=$?
if [[ $EXITCODE -ne 0 && $EXITCODE -ne 2 ]]; then
    echo -e '\e[1m\e[91mThe puppet run exited with an error.\e[0m\e[39m'
fi
exit $EXITCODE
EOF
    chmod 755 /usr/sbin/run_puppet
    set +e
    /usr/sbin/run_puppet
    set -e

}


main() {
    if [[ $UID -ne 0 ]]; then
        echo -e '\e[1m\e[91mYou must be root to run this setup.\e[0m\e[39m'
        exit 1
    fi

    echo -e '\e[1mSetting hostname to oclubs.shs.cn...\e[0m'; set_hostname; echo
    echo -e '\e[1mCloning oclubs repository...\e[0m'; clone_repo; echo
    echo -e '\e[1mInitializing hieradata...\e[0m'; init_hiera; echo
    echo -e '\e[1mRunning puppet...\e[0m'; install_run_puppet; echo

    echo 'The initializing script has completed. There are still things to work on manually before the setup is complete:'
    echo '1. Edit /srv/oclubs/repo/provision/puppet/hieradata/environment/production.yaml and rerun puppet with `$ sudo run_puppet`'
    echo '   a. Fill in the missing secrets.'
    echo '   b. Create accounts for other maintainers.'
    echo '   c. Upload the ssh keys.'
    echo '   d. Complete the email aliases.'
    echo '2. After every maintainer can successfully ssh in via private key, disable password login in /etc/ssh/sshd_config.'
    echo '3. If necessary, create admin accounts via `$ new_user --type ADMIN`, and refresh student database.'
}

main
