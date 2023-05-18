# seconds-backend
The Django backed for the seconds app


docker-compose up --build -d
docker exec -it seconds-backend_web_1 bash

Then inside docker:
./manage.py migrate
./manage.py createsuperuser --username gitaar9 --email thijs.eker@gmail.com
./manage.py shell

Then inside shell
from seconds.word.models import Word
Word.load_words()

And possibly:
from seconds.word.models import OptionalEnglishWord, OptionalWord
OptionalWord.load_optional_words()
OptionalEnglishWord.load_optional_english_nouns()

Go to localhost:8000/admin/
and create an Application with:
client_id = 1
client_type = confidential
authorization_grant_type = resource owner password based
client_secret = 2



# How to deploy
install docker: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04

mkdir /projects
cd /projects
git clone https://github.com/gitaar9/seconds-backend.git
git clone https://github.com/gitaar9/seconds-frontend.git
sudo ufw allow 8000

vim seconds/settings.py
and change
    1. secret key
    2. ip to right ip
    3. debug to False


# For frontend
scp -r /samsung_hdd/Files/Projects/seconds-frontend/dist root@$ip:/projects/seconds-frontend
run make up in the nginx_docker folder