from setuptools import setup, find_packages


with open('README.md') as f:
	readme = f.read()


setup(
	name="aiakos",
	version="0.0.0",
	description="Aiakos - OpenID Connect Provider",
	long_description=readme,
	author="Aiakos Contributors",
	author_email="aiakos@aiakosauth.com",
	url="https://gitlab.com/aiakos/aiakos/",
	keywords="django,auth,oauth,openid,oidc,social,ldap",

	install_requires=[
		"Django>=1.11,<1.11.99",
		"openid-connect",
		"gevent",
		"gunicorn",
		"dj12>=0.2",
		"django-crispy-forms",
		"google-auth",
		"PyYAML",
		"raven",
		"whitenoise",
		"Werkzeug",
		"django_inlinecss",
		'djangorestframework',
		'django-filter',
		'markdown',
		'python-jose>=1.4.0',
		'cached_property',
	],

	extras_require={
		'MySQL': ["mysqlclient"],
		'PostgreSQL': ["psycopg2"],
	},

	packages=find_packages(exclude=['example_client_django']),
	include_package_data=True,

	zip_safe=True,
	classifiers=[
		'Intended Audience :: System Administrators',
		'Topic :: System :: Systems Administration :: Authentication/Directory',
	]
)
