install:
	python3 manage.py makemigrations music
	python3 manage.py makemigrations
	python3 manage.py migrate
	python3 manage.py loaddata initial_data


migrations:
	python3 manage.py makemigrations users
	python3 manage.py makemigrations music
	python3 manage.py migrate

restore-migrations:
	python3 manage.py flush
	python3 manage.py makemigrations users
	python3 manage.py makemigrations music
	python3 manage.py migrate
	python3 manage.py loaddata initial_data
