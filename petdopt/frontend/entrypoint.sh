#!/bin/sh
# Podmienia placeholdery na zmienne środowiskowe
: "${PET_API:=http://localhost:5001/pets}"
: "${USER_API:=http://localhost:5002/users}"

sed -i "s|__PET_API__|$PET_API|g" /usr/share/nginx/html/index.html
sed -i "s|__USER_API__|$USER_API|g" /usr/share/nginx/html/index.html

# Uruchamia nginx jako główny proces
exec nginx -g 'daemon off;'

# docker build -t dduda261/frontend:env \
#   --build-arg PET_API=http://petdopt.local/pets \
#   --build-arg USER_API=http://petdopt.local/users \
#   .
