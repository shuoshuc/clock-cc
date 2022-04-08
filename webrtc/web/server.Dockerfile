# Setup website gui on 5000
FROM python:3.8
EXPOSE 5000
RUN pip install flask
RUN mkdir /web
COPY ./ /web
WORKDIR /web/
CMD python web.py server & sleep infinity
