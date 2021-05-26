# Grimm-backend

> Technology makes tomorrow better.

## Introduction

This is a charitable projects, the purpose is to help visually impaired people, and this project is cloned from 

> git@github.com:Grimm-Source/Grimm.git

## Preparation

python 3.6+

mysql


## Getting started

```bash
$ sudo yum install python3
$ virtualenv -p /usr/bin/python3 venv
$ source ./venv/bin/activate
$ pip install -r requirements.txt
```


## Changelog

Detailed changes for each release are documented in the [release notes](https://github.com/SincerelyUnique/grimm-backend/releases).


## Online Demo

[Preview](http://104.243.21.35:5000/)


## License
[MIT](https://github.com/SincerelyUnique/grimm-backend/blob/main/license)

Copyright (c) 2017-present Grimm

## Features Usage

### 1.flask_migrate

```bash
$ set FLASK_APP=manage.py
$ flask db init  # Just execute it at the first time
$ flask db migrate -m "Initial migration."
$ flask db upgrade
```

reference doc:

[Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/)

[Alembic autogenerate documentation](http://alembic.zzzcomputing.com/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect)
