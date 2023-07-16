FROM nginxinc/nginx-unprivileged:latest
LABEL maintainer="jdlugosz963@gmail.com"

COPY ./default.conf /etc/nginx/conf.d/default.conf

USER root

RUN mkdir -p /vol/static
RUN chmod 755 /vol/static

USER nginx

