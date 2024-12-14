cd ./tcx_bot/
sudo docker build -t tcx-bot-img .
sudo docker run -d --name tcx-bot-container --restart unless-stopped --env-file .env tcx-bot-img
sudo docker logs -f tcx-bot-container

Чистка ненужных контейнеров и образов:
sudo docker container prune
sudo docker image prune -a
