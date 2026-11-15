# ==============================================================================
# MINECRAFT CTF - DATABASE INITIALIZER & MODELS
# Desarrollado por: Thorfinn777, Martyn777, Sassyjack777
# ==============================================================================

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'minecraft_ctf.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    # Optimizaciones de SQLite para bajo I/O en máquinas virtuales (VirtualBox):
    # - WAL (Write-Ahead Logging): lectura y escritura concurrentes sin bloqueo
    # - synchronous=NORMAL: reduce llamadas costosas a fsync en discos virtuales
    # - temp_store=MEMORY: almacena ordenamientos y tablas temporales en memoria
    # - cache_size=-2000: caché en RAM de ~2MB
    conn.execute('PRAGMA journal_mode = WAL;')
    conn.execute('PRAGMA synchronous = NORMAL;')
    conn.execute('PRAGMA busy_timeout = 5000;')
    conn.execute('PRAGMA temp_store = MEMORY;')
    conn.execute('PRAGMA cache_size = -2000;')
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

    # Tabla 4: Tokens robados al Piglin Guard (reto de XSS Stored)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stolen_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_id INTEGER,
            captured_data TEXT NOT NULL,
            captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla 5: Perfiles de estudiantes y progreso con credencial única
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credential TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            team_name TEXT DEFAULT 'MinecraftStudent',
            score INTEGER DEFAULT 0,
            flags_solved INTEGER DEFAULT 0,
            inventory_json TEXT DEFAULT '[]',
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla 6: Equipos precargados para el Ranking (como en la imagen del CTF)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rank_pos INTEGER NOT NULL,
            team_name TEXT NOT NULL,
            badge_icon TEXT NOT NULL,
            score INTEGER NOT NULL,
            is_crown INTEGER DEFAULT 0
        )
    ''')

    # Poblar cofres iniciales si está vacía
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

    cursor.execute('SELECT COUNT(*) FROM leaderboard_teams')
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO leaderboard_teams (rank_pos, team_name, badge_icon, score, is_crown)
            VALUES (?, ?, ?, ?, ?)
        ''', [
            (1, 'BlockSec', 'creeper', 1250, 1),
            (2, 'CyberMine', 'grass', 1100, 0),
            (3, 'TeamCraft', 'diamond', 980, 0),
            (4, 'RedstoneSec', 'redstone', 920, 0),
            (5, 'MineGuardians', 'pickaxe', 870, 0)
        ])

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("[+] Base de datos SQLite de Minecraft CTF inicializada con éxito.")
    print("[+] Desarrollado por: Thorfinn777, Martyn777, Sassyjack777")
