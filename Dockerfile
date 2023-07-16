FROM python:3
LABEL maintainer="jdlugosz963@gmail.com"

WORKDIR /usr/src/app

COPY ./scripts /usr/src/scripts
RUN chmod +x /usr/src/scripts/*
ENV PATH /usr/src/scripts:$PATH

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./restaurant_orders/ .


RUN useradd nonrootuser

RUN mkdir -p /vol/web/static
RUN chown -R nonrootuser:nonrootuser /vol
RUN chmod -R 755 /vol

RUN chown -R nonrootuser:nonrootuser /usr/src

USER nonrootuser

CMD ["entrypoint.sh"]
