import mysql.connector

my_db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='YOUR PASSWORD'
)

my_cursor = my_db.cursor()
my_cursor.execute(
    "CREATE DATABASE our_users"
)

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)
