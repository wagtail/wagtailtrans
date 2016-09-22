FROM python:2.7
MAINTAINER Henk-Jan van Hasselaar <hj.vanhasselaar@lukkien.com>
ENV DJANGO_SETTINGS_MODULE="wagtail.wagtailtrans.tests.settings.docker"

RUN mkdir -p /opt/sandbox/public/media && \
	mkdir -p /opt/sandbox/public/static && \
	mkdir -p /var/log/nginx /var/log/supervisor && \
	apt-get update && \
	apt-get install -y nginx python-pip supervisor gettext && \
	apt-get autoremove -y && apt-get clean -y && \
	pip install --upgrade uwsgi --use-wheel

COPY ./docker/uwsgi.ini /opt/sandbox/etc/uwsgi.ini
COPY ./docker/nginx.conf /etc/nginx/sites-enabled/default
COPY ./docker/supervisor.conf /etc/supervisor/conf.d/supervisord.conf
COPY ./wagtail/wagtailtrans/tests/sandbox/fixtures/users.json /tmp/users.json

RUN echo "daemon off;" >> /etc/nginx/nginx.conf

ADD ./dist /tmp
RUN pip install --upgrade `find /tmp/ -name '*.tar.gz' | tail -1` --use-wheel && \
    wagtailtrans.py migrate && \
    wagtailtrans.py loaddata /tmp/users.json && \
    mkdir /usr/local/lib/python2.7/site-packages/wagtail/wagtailtrans/tests/static/ && \
    wagtailtrans.py collectstatic --no-input


EXPOSE 22 80
CMD ["/usr/bin/supervisord"]
