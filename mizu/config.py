import secrets
from os import environ as env
import os


APP_NAME = env.get('MIZU_APP_NAME', 'mizu')
DEBUG = True if env.get('MIZU_DEBUG', 'false').lower() == 'true' else False
IP = env.get('MIZU_IP', '0.0.0.0')
PORT = env.get('MIZU_PORT', 8080)
SECRET_KEY = env.get('MIZU_SECRET_KEY', default=''.join(secrets.token_hex(16)))

SQLALCHEMY_DATABASE_URI = env.get('MIZU_DATABASE_URI', 'sqlite:///{}'.format(os.path.join(os.getcwd(), 'data.db')))

OIDC_ISSUER = env.get('MIZU_OIDC_ISSUER', 'https://sso.csh.rit.edu/auth/realms/csh')
OIDC_CLIENT_ID = env.get('MIZU_OIDC_CLIENT_ID', 'drink')
OIDC_CLIENT_SECRET = env.get('MIZU_OIDC_CLIENT_SECRET', '')

LDAP_URL = env.get('MIZU_LDAP_URL', 'ldaps://ldap.csh.rit.edu:636')
LDAP_BIND_DN = env.get('MIZU_BIND_DN',
'krbprincipalname=drink/drink.csh.rit.edu@CSH.RIT.EDU,cn=services,cn=accounts,dc=csh,dc=rit,dc=edu')
LDAP_BIND_PW = env.get('MIZU_BIND_PW', '')

MACHINE_API_TOKEN = env.get('MIZU_MACHINE_API_TOKEN', '')

