#! /bin/bash
which certbot &> /dev/null || ( yum install -y epel-release; yum install -y certbot certbot-nginx )

mkdir -p /etc/letsencrypt/

cat > /etc/letsencrypt/cli.ini << EOF
email = oclubs@hotmail.com
server = https://acme-v01.api.letsencrypt.org/directory
# server = https://acme-staging.api.letsencrypt.org/directory
EOF

systemctl stop nginx || true
certbot certonly --standalone --text --agree-tos -d oclubs.shs.cn -n
CERTBOT_EXITCODE=$?
if [[ $CERTBOT_EXITCODE == 0 ]]; then
    if ! grep 'httpredir-nginx-cfg' /srv/oclubs/repo/provision/puppet/hieradata/local.yaml &> /dev/null; then
        cat >> /srv/oclubs/repo/provision/puppet/hieradata/local.yaml << 'EOF'
httpredir-nginx-cfg: |-
  # SSL and HTTP redirect configuration
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/oclubs.shs.cn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/oclubs.shs.cn/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;

    # Redirect non-https traffic to https
    if ($scheme != "https") {
        return 301 https://$host$request_uri;
    }
EOF
    fi
fi
systemctl start nginx || true

if which certbot &> /dev/null; then
    cat > /etc/cron.daily/certbot << EOF
#! /bin/bash
certbot renew &> /dev/null || true
EOF
    chmod a+x /etc/cron.daily/certbot
fi
