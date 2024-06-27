flask --app webapp init-db

flask --app webapp run --debug

pip install -e .

pytest

coverage run -m pytest
coverage report
coverage html

python -m build --wheel

python -c 'import secrets; print(secrets.token_hex())'


pip install waitress
waitress-serve --call 'webapp:create_app'

pip uninstall webapp