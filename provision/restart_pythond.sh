#! /bin/sh
for SERVICE in uwsgi celeryd celerybeat
do
    service $SERVICE restart &> /dev/null || true
done
