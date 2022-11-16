import mariadb
import os

db_connection = mariadb.connect(
    user = os.environ.get('DOKKU_MARIADB_JAMPACK_DB_ENV_MYSQL_USER'),
    password = os.environ.get('DOKKU_MARIADB_JAMPACK_DB_ENV_MYSQL_PASSWORD'),
    host = os.environ.get('DOKKU_MARIADB_JAMPACK_DB_PORT_3306_TCP_ADDR'),
    database = os.environ.get('DOKKU_MARIADB_JAMPACK_DB_ENV_MYSQL_DATABASE')
)
