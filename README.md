# seconds-backend
The Django backed for the seconds app


docker-compose up --build -
docker exec -it seconds-backend_web_1 bash

Then inside docker:
./manage.py migrate
./manage.py shell

Then inside shell
from seconds.word.models import Word
Word.load_words()
from seconds.user.models import User