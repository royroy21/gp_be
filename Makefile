# Put any command that doesn't create a file here (almost all of the commands)
.PHONY: \
	attach \
	bash \
    black \
    black_check \
	chown \
	clear_cache \
	clear_pyc \
	help \
	isort \
	isort_check \
	lint \
	migrate \
	migrations \
	mypy \
	psql \
	manage \
	shell \
	test \
	up \
	update_requirements \

usage:
	@echo "Available commands:"
	@echo "attach..........................Attach to django container. Useful for when using ipdb"
	@echo "bash............................Enter django server with bash shell prompt"
	@echo "black...........................Format Python code"
	@echo "black_check.....................Checks Python code formatting without making changes"
	@echo "chown...........................Change ownership of files to own user"
	@echo "clear_cache.....................Clears redis cache"
	@echo "clear_pyc.......................Remove all pyc files"
	@echo "help............................Display available commands"
	@echo "isort...........................Sort Python imports"
	@echo "isort_check.....................Checks Python import are sorted correctly without making changes"
	@echo "lint............................Run lint checking against the project"
	@echo "manage..........................Django's manage.py command"
	@echo "migrate.........................Run Django migrations"
	@echo "migrations......................Create Django migrations"
	@echo "mypy............................Run mypy type hint inspection against project"
	@echo "psql............................Connect to postgis server"
	@echo "shell...........................Django's shell plus command"
	@echo "test............................Run tests for the project"
	@echo "up..............................docker-compose up"
	@echo "update_requirements.............Update requirements file after adding a dependency"

PROJECT_DIR=gp_be

attach:
	@docker attach ${PROJECT_DIR}_django_1

bash:
	@docker-compose run --rm django bash ${ARGS}

black:
	@docker-compose run --rm django black -l 79 . ${ARGS}

black_check:
	$(MAKE) black ARGS="--check"

chown:
	@docker-compose run --rm django chown -R "`id -u`:`id -u`" "/code/${ARGS}"

clear_cache:
	$(MAKE) manage ARGS="clear_cache ${ARGS}"

clear_pyc:
	@docker-compose run --rm django find . -name '*.pyc' -delete

help:
	$(MAKE) usage

isort:
	@docker-compose run --rm django isort . ${ARGS}

isort_check:
	$(MAKE) isort ARGS="--check"

lint:
	@docker-compose run --rm django flake8 . ${ARGS}

manage:
	@docker-compose run --rm ${OPTIONS} django python3 ${PYTHON_ARGS} project/manage.py ${ARGS}

migrate:
	$(MAKE) manage ARGS="migrate ${ARGS}"

migrations:
	$(MAKE) manage ARGS="makemigrations ${ARGS}"

mypy:
	# Using --no-incremental to avoid bug https://github.com/typeddjango/django-stubs/issues/760.
	# This results in mypy not using cache meaning it's pretty slow. Fix later.
	@docker-compose run --rm django mypy --no-incremental --config-file mypy.ini . ${ARGS}

PG_DB_HOST=postgres
PG_DB_PORT=5432
PG_DB_NAME=postgres
PG_DB_USER=postgres
PG_DB_PASSWORD=postgres

psql:
	@docker-compose run --rm -e PGPASSWORD=$(PG_DB_PASSWORD) postgres psql -h $(PG_DB_HOST) -p $(PG_DB_PORT) -U $(PG_DB_USER) -d $(PG_DB_NAME) $(ARGS)

shell:
	$(MAKE) manage ARGS="shell_plus --ipython ${ARGS}"

test:
	$(MAKE) manage ARGS="test project${ARGS} --settings=project.settings.test"

up:
	@docker-compose up ${ARGS}

update_requirements:
	@docker-compose run --rm django pip freeze > requirements.txt
