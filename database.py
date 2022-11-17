from MySQLdb import Connect
import os

def get_db_connection():
    return Connect(
        user = os.environ.get('DOKKU_MARIADB_JAMPACK_DB_ENV_MYSQL_USER'),
        password = os.environ.get('DOKKU_MARIADB_JAMPACK_DB_ENV_MYSQL_PASSWORD'),
        host = os.environ.get('DOKKU_MARIADB_JAMPACK_DB_PORT_3306_TCP_ADDR'),
        db = os.environ.get('DOKKU_MARIADB_JAMPACK_DB_ENV_MYSQL_DATABASE')
    )
