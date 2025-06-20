FROM nginx:alpine

ARG PET_API
ARG USER_API

ENV PET_API=$PET_API
ENV USER_API=$USER_API

COPY index.html /usr/share/nginx/html/index.html
COPY login.html /usr/share/nginx/html/login.html
COPY script.js /usr/share/nginx/html/script.js 
COPY callback.html /usr/share/nginx/html/callback.html
COPY entrypoint.sh /entrypoint.sh
COPY nginx.conf /etc/nginx/nginx.conf

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
