from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}")

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE polluants ADD COLUMN nom_polluant VARCHAR(100)"))
    conn.execute(text("UPDATE polluants SET nom_polluant = 'Dioxyde d''azote' WHERE code_polluant = 'NO2'"))
    conn.execute(text("UPDATE polluants SET nom_polluant = 'Particules fines PM10' WHERE code_polluant = 'PM10'"))
    conn.execute(text("UPDATE polluants SET nom_polluant = 'Particules fines PM2.5' WHERE code_polluant = 'PM2.5'"))
    conn.execute(text("UPDATE polluants SET nom_polluant = 'Ozone' WHERE code_polluant = 'O3'"))
    conn.execute(text("UPDATE polluants SET nom_polluant = 'Dioxyde de soufre' WHERE code_polluant = 'SO2'"))
    conn.commit()
    print("✅ Colonne nom_polluant ajoutée et remplie")