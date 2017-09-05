set -e
virtualenv3 .upenv
. .upenv/bin/activate
pip install .[MySQL,PostgreSQL]
pip uninstall --yes aiakos
pip freeze > requirements.txt
echo 'git+https://gitlab.com/aiakos/django-modular-user.git@d8ec0f8cfd6ddf99551c38e687ed7eb65bc7f062' >> requirements.txt
rm -Rf .upenv
