#!/bin/sh

# shellcheck disable=SC2164
cd /home/code

python manage.py makemigrations --skip-checks --noinput
python manage.py migrate --skip-checks --noinput
python manage.py collectstatic --noinput
python manage.py loaddata /home/code/fixtures/pairs.json

exec "$@"