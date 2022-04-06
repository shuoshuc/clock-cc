# Setup website gui on 8000
FROM python:3.8
EXPOSE 8000
RUN mkdir /web
COPY ./ /web
WORKDIR /web/
CMD python -m http.server 8000 & sleep infinity
