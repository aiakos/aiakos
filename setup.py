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
		"Django==1.10",
		"openid-connect",
		"gunicorn",
		"dj-database-url",
		"dj-email-url",
		"django-crispy-forms",
		"django-oidc-provider",
		"google-auth",
		"pycrypto",
		"pycryptodomex",
		"pyjwkest",
		"PyYAML",
		"raven",
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
