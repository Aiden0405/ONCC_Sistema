import psycopg2  
conn = psycopg2.connect(dbname='ONCC_Sistema', user='postgres', password='29654518', host='localhost')  
cur = conn.cursor()  
cur.execute('DROP TABLE IF EXISTS alembic_version CASCADE;')  
conn.commit()  
cur.close()  
conn.close()  
print('--- TABLA ELIMINADA CON EXITO ---') 
