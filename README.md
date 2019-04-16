## Movie API
### Requirements:
- python 3.7
- postgres 11.2

### API address:
- https://movie-api-jrafa.herokuapp.com

### How to setup project locally?
- Clone  project's repository:
```git clone https://github.com/jrafa/movie-api.git ```
- Install dependencies: ```pipenv install``` and  ```pipenv install --dev```
- Activate Pipenv shell: ```pipenv shell```
- Create database in Postgres. For example: movie 
- Create file ```.env``` with variables which are in example config ```.env.example```
- Run db migration: ```python manage.py migrate``` 
- Run project: ```python manage.py runserver```
- In directory http-client are endpoints. You can run them in Pycharm.