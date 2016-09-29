FROM python:2.7
MAINTAINER Henk-Jan van Hasselaar <hj.vanhasselaar@lukkien.com>

ENV DJANGO_SETTINGS_MODULE="tests._sandbox.settings.docker"

RUN mkdir -p /opt/sandbox/public/{static,media} && \
	mkdir -p /var/log/{nginx,supervisor} && \
	apt-get update && \
	apt-get install -y nginx python-pip supervisor gettext && \
	apt-get autoremove -y && apt-get clean -y && \
	pip install --upgrade uwsgi --use-wheel

RUN echo "daemon off;" >> /etc/nginx/nginx.conf

COPY ./docker/uwsgi.ini /opt/sandbox/etc/uwsgi.ini
COPY ./docker/nginx.conf /etc/nginx/sites-enabled/default
COPY ./docker/supervisor.conf /etc/supervisor/conf.d/supervisord.conf

ADD ./dist /tmp
ADD . /opt/sandbox/code

RUN pip install --upgrade `find /tmp/ -name '*.tar.gz' | tail -1` --use-wheel

RUN ./opt/sandbox/code/manage.py migrate --noinput && \
    ./opt/sandbox/code/manage.py collectstatic --noinput && \
    ./opt/sandbox/code/manage.py loaddata /opt/sandbox/code/tests/_sandbox/fixtures/users.json

EXPOSE 80
CMD ["/usr/bin/supervisord"]
