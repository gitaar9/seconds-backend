# seconds-backend
The Django backed for the seconds app


docker-compose up --build -
docker exec -it seconds-backend_web_1 bash

Then inside docker:
./manage.py migrate
./manage.py createsuperuser --username gitaar9 --email thijs.eker@gmail.com
./manage.py shell

Then inside shell
from seconds.word.models import Word
Word.load_words()

Go to localhost:8000/admin/
and create an Application with:
client_id = 1
client_type = confidential
authorization_grant_type = resource owner password based
client_secret = 2