# Aiakos - OpenID Connect Provider

Aiakos is an OpenID Connect server that supports both local and federated authentication. It's meant to be used as a single, centralized gateway to all your services, so that you can manage your users in a single place, they can benefit from Single Sign-On, and your apps don't need to worry about authentication.

## Local auth
Users can log in using login and password.

## Federated auth
Users can log in using external, standards-compliant OpenID Providers (like Google). Aiakos also supports some legacy (non-OIDC) OAuth2 servers, like GitHub and GitLab.

## Two Factor Authentication
TODO We're going to support TOTP.

## Components
Currently, this repo contains multiple packages; they'll get split into multiple repos when the project matures.

* [django_profile_oidc](django_profile_oidc) (Python 3.x) - User profile containing standard OIDC user info
* [django_extauth](django_extauth) (Python 3.x) - Federated authentication support for Django, based on openid_connect library.
* [aiakos.openid_provider](aiakos/openid_provider) (Python 3.x) - OAuth 2 + OIDC Provider library

## Client libraries
Any standards-compliant OpenID Connect library may be used.

We also provide our own client libraries:
* [openid-connect](https://gitlab.com/aiakos/python-openid-connect) (Python 2.7/3.x) - Low-level Python OIDC Client library + wrappers for legacy protocols
* [django-auth-oidc](https://gitlab.com/aiakos/django-auth-oidc) (Python 2.7/3.x) - Django authentication module for authentication using only a single OpenID Provider

## Deployment

The recommended way to deploy aiakos is to use the official docker container - [aiakos/aiakos](https://hub.docker.com/r/aiakos/aiakos).

### Deployment configuration
Aiakos is using [dj12](https://gitlab.com/aiakos/dj12) for twelve-factor configuration support.

See [dj12 usage](https://gitlab.com/aiakos/dj12#usage) for a list of supported options. Note that we are not using cache right now.

#### Aiakos-specific options

* HOME_URL (optional) - URL to redirect to when a logged in user accesses /; by default he'll get redirected to the app list view
* BOOTSTRAP_THEME_URL (optional) - Bootstrap theme to use, you can find many free ones at [bootswatch.com](https://bootswatch.com/)
* BOOTSTRAP_THEME_INTEGRITY (optional) - Integrity checksum of the Bootstrap theme

### Migration
Use `django-admin migrate` to set up / update the database.

### Initial user account
Use `django-admin createsuperuser` to create first user account.

TODO Automatically create root:root user account as a migration.

## Deploying to Heroku

```sh
$ heroku create
$ git push heroku master

$ heroku run python -m aiakos migrate
$ heroku run python -m aiakos creatersakey
$ heroku run python -m aiakos createsuperuser
$ heroku open
```

## Configuration
OpenID Clients and external OpenID Providers can be configured in the Django admin panel - available at /admin.

## Example client
You can find an example client in the [example-client-django](https://gitlab.com/aiakos/example-client-django) repo.

## Development
Please set up a git hook that'll automatically enforce project's style:

	git config core.hooksPath githooks/

## License
Aiakos is dual-licenced; you may choose the terms of the [MIT License](LICENSE) or the [BSD 2-Clause License](LICENSE.BSD).
