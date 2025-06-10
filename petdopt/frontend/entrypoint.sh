#!/bin/sh
# Podmienia placeholdery na zmienne środowiskowe
: "${PET_API:=http://localhost:5001/pets}"
: "${USER_API:=http://localhost:5002/users}"

for file in /usr/share/nginx/html/*.html; do
  sed -i "s|__PET_API__|$PET_API|g" "$file"
  sed -i "s|__USER_API__|$USER_API|g" "$file"
done

# Uruchamia nginx jako główny proces
exec nginx -g 'daemon off;'

# docker build -t dduda261/frontend:env \
#   --build-arg PET_API=http://petdopt.local/pets \
#   --build-arg USER_API=http://petdopt.local/users \
#   ./frontend
# docker build -t dduda261/pet-service:latest ./pet-service
# docker build -t dduda261/user-service:latest ./user-service

# docker push dduda261/frontend:env
# docker push dduda261/pet-service:latest
# docker push dduda261/user-service:latest

# kubectl apply -f kubernetes/
