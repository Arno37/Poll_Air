import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('PG_HOST'),
    database=os.getenv('PG_DATABASE'),
    user=os.getenv('PG_USER'),
    password=os.getenv('PG_PASSWORD'),
    port=os.getenv('PG_PORT')
)

cursor = conn.cursor()
cursor.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'polluants';")
print(cursor.fetchall())

cursor.execute("SELECT * FROM polluants LIMIT 3;")
print(cursor.fetchall())

cursor.close()
conn.close()