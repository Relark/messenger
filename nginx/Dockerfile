FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf
COPY ./default.conf /etc/nginx/conf.d/ 
COPY ./static /static/
COPY ./certs /certs/
EXPOSE 80
EXPOSE 443
