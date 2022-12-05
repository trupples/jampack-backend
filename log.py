from database import get_db_connection

def log(what):
	print('LOG:', what)
	db_connection = get_db_connection()
	cur = db_connection.cursor()
	cur.execute('insert into Logs(what) values (%s)', [repr(what)])
	cur.close()
	db_connection.commit()
	db_connection.close()
