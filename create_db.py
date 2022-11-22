import mysql.connector

mydb = mysql.connector.connect(
    host="localhost", user="root", passwd="waifu122")

my_cursor = mydb.cursor()

#my_cursor.execute("CREATE DATABASE SIS6")

my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)
