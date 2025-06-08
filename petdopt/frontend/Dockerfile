FROM nginx:alpine

# Ustawiamy zmienne środowiskowe
ENV PET_API=http://localhost:5001/pets
ENV USER_API=http://localhost:5002/users

COPY index.html /usr/share/nginx/html/index.html
COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
