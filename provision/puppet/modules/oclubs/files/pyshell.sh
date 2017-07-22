#! /bin/bash
exec /usr/bin/sudo -- /usr/bin/sudo -u uwsgi /srv/oclubs/venv/bin/python /srv/oclubs/repo/shell.py "$@"
