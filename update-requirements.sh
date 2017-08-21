set -e
virtualenv3 .upenv
. .upenv/bin/activate
pip install .[MySQL,PostgreSQL]
pip uninstall --yes aiakos python-jose
pip freeze > requirements.txt
echo 'git+https://gitlab.com/aiakos/django-modular-user.git' >> requirements.txt
echo 'git+https://github.com/mpdavis/python-jose.git@b54c12aa54b76d34942f537418399d689d828099' >> requirements.txt
rm -Rf .upenv
