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

* [openid_connect](openid_connect) (Python 2.7/3.x) - Low-level Python OIDC Client library + wrappers for legacy protocols
* [django_profile_oidc](django_profile_oidc) (Python 3.x) - User profile containing standard OIDC user info
* [django_extauth](django_extauth) (Python 3.x) - Federated authentication support for Django, based on openid_connect library.

We're also considering following external projects as the core components of Aiakos:

* [django-oidc-provider](https://github.com/juanifioren/django-oidc-provider) (Python 2.7/3.x) - Django OIDC Provider library

## Client libraries
Any standards-compliant OpenID Connect library may be used.

We also provide our own library for Django projects:
* [django_auth_oidc](django_auth_oidc) (Python 2.7/3.x) - Django authentication module for authentication using only a single OpenID Provider

## Deployment

The recommended way to deploy aiakos is to use the official docker container - [aiakos/aiakos](https://hub.docker.com/r/aiakos/aiakos).

### Deployment configuration
Deployment configuration should be provided by environment variables:

* [DJANGO_SECRET_KEY](https://docs.djangoproject.com/en/1.10/ref/settings/#secret-key) - random string
* HOSTNAME - domain at which Aiakos will be available
* DATABASE_URL (required for stateful deployments) - postgres://user:password@hostname/dbname
* USE_X_FORWARDED_PROTO (optional, default: 0) - set to 1 if deploying behind a reverse proxy
* DEBUG (optional, default: 0) - set to 1 to display debug information; don't ever enable this on public deployments
* BOOTSTRAP_THEME_URL (optional) - Bootstrap theme to use, you can find many free ones at [bootswatch.com](https://bootswatch.com/)
* BOOTSTRAP_THEME_INTEGRITY (optional) - Integrity checksum of the Bootstrap theme
* HOME_URL (optional) - URL to redirect to when a logged in user accesses /; by default he'll get redirected to the app list view

### Migration
Use `django-admin migrate` to set up / update the database.

### Initial user account
Use `django-admin createsuperuser` to create first user account.

TODO Automatically create root:root user account as a migration.

## Configuration
OpenID Clients and external OpenID Providers can be configured in the Django admin panel - available at /admin.

## Example client
You can find an example client in [example_client_django](example_client_django) subdirectory.
