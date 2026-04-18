echo "parando o container"
docker compose down -v

sleep 3

echo "inciianso o container"
docker compose -f docker-compose.yml up --build -d

sleep 10

echo "criando user"
docker compose exec web python manage.py seed_mvp
