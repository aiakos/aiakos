set -e
virtualenv3 .upenv
. .upenv/bin/activate
pip install .[MySQL,PostgreSQL]
pip uninstall --yes aiakos
pip freeze > requirements.txt
echo 'git+https://gitlab.com/aiakos/django-modular-user.git' >> requirements.txt
rm -Rf .upenv
