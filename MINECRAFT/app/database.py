import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'minecraft_ctf.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabla 1: Cofres de los aldeanos (Para el reto de SQL Injection en Overworld)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS villager_chests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chest_name TEXT NOT NULL,
            location TEXT NOT NULL,
            depth_level INTEGER NOT NULL,
            secret_loot TEXT NOT NULL,
            is_locked INTEGER NOT NULL
        )
    ''')

    # Tabla 2: Ofertas de tradeo con Piglins (Para el reto de XSS Stored en Nether)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS piglin_trade_offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            offered_item TEXT NOT NULL,
            note_to_piglin TEXT NOT NULL,
            status TEXT DEFAULT 'Pending Review',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla 3: Registro de telemetría de cristales de The End
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS end_crystals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pillar_id TEXT UNIQUE NOT NULL,
            frequency INTEGER NOT NULL,
            shield_status TEXT NOT NULL,
            health INTEGER NOT NULL
        )
    ''')

    # Poblar datos iniciales si está vacía
    cursor.execute('SELECT COUNT(*) FROM villager_chests')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO villager_chests (chest_name, location, depth_level, secret_loot, is_locked)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            ('Cofre del Granjero', 'X: 120, Z: -45', 64, '3x Trigo, 2x Manzanas', 0),
            ('Cofre del Pescador', 'X: 155, Z: -12', 62, '1x Caña de pescar gastada', 0),
            ('Cofre del Bibliotecario', 'X: 98, Z: -80', 65, 'Libro Encantado (Protección I)', 0),
            ('Cofre Oculto del Herrero', 'X: 42, Z: -350', -58, 'FLAG{MINECRAFT_DIAMOND_SQL1_Y58_UNLOCKED}', 1),
            ('Cofre Abandonado en Mina', 'X: -210, Z: 512', 12, '8x Carbón, 4x Antorchas', 0)
        ])

    # Tabla 4: Tokens robados al Piglin Guard (reto de XSS Stored).
    # Se guardan en la base de datos y no en memoria porque gunicorn ejecuta
    # varios workers: cada proceso tiene su propia copia de la RAM.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stolen_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_id INTEGER,
            captured_data TEXT NOT NULL,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('SELECT COUNT(*) FROM end_crystals')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO end_crystals (pillar_id, frequency, shield_status, health)
            VALUES (?, ?, ?, ?)
        ''', [
            ('CRISTAL_ALPHA', 4401, 'ACTIVE', 100),
            ('CRISTAL_BETA', 4402, 'ACTIVE', 100),
            ('CRISTAL_GAMMA', 4403, 'ACTIVE', 100),
            ('CRISTAL_OMEGA', 4404, 'ACTIVE', 100)
        ])

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("[+] Base de datos SQLite de Minecraft CTF inicializada con éxito.")
