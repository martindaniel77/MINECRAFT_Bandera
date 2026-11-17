# ==============================================================================
# MINECRAFT CTF - VULNERABLE SECURITY LAB PLATFORM
# Desarrollado por: Thorfinn777, Martyn777, Sassyjack777
# Autores del Laboratorio: Thorfinn777, Martyn777, Sassyjack777
# ==============================================================================

import os
import re
import sqlite3
import base64
import json
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_from_directory
from werkzeug.utils import secure_filename

from database import get_db_connection
from bot import bot_instance, PIGLIN_SECRET_TOKEN
from sandbox import run_sandboxed
from cave_data import run_cave_command
from end_ad import run_powerview_command

# Autores oficiales del laboratorio
LAB_AUTHORS = ['Thorfinn777', 'Martyn777', 'Sassyjack777']
LAB_AUTHORS_STR = 'Thorfinn777, Martyn777, Sassyjack777'

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'minecraft_dvwa_secret_key_2026_kali')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
# Los assets se revalidan siempre (ETag/304) para que los cambios de imagenes
# y CSS se vean de inmediato sin quedar atrapados en la cache del navegador.
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# ------------------------------------------------------------------------------
# DICCIONARIO OFICIAL DE BANDERAS DEL CTF (Formato Flag{...})
# ------------------------------------------------------------------------------
FLAGS = {
    'overworld': {
        'iron': 'FLAG{MINECRAFT_IRON_INGOT_C3S4R_X0R_M1N3D}',
        'diamond': 'FLAG{MINECRAFT_DIAMOND_SQL1_Y58_UNLOCKED}',
        'portal': 'FLAG{MINECRAFT_NETHER_PORTAL_METADATA_IGNITED}'
    },
    'nether': {
        'gold': 'FLAG{MINECRAFT_PIGLIN_XSS_GOLD_BARTERED}',
        'blaze': 'FLAG{MINECRAFT_BLAZE_ROD_RECETA_EJECUTADA}',
        'pearl': 'FLAG{MINECRAFT_ENDER_PEARL_PRIV_ESCALATION}'
    },
    'the_end': {
        'crystals': 'FLAG{MINECRAFT_END_CRYSTALS_CVE_SHATTERED}',
        'dragon': 'FLAG{MINECRAFT_ENDER_DRAGON_SLAIN_COMMAND_INJECTION}',
        'egg': 'FLAG{MINECRAFT_FINAL_DRAGON_EGG_VICTORY_GG}'
    }
}

ITEM_NAMES = {
    'iron': 'Lingote de Hierro',
    'diamond': 'Diamante',
    'portal': 'Portal al Nether',
    'gold': 'Lingote de Oro',
    'blaze': 'Vara de Blaze',
    'pearl': 'Ojo de Ender',
    'crystals': 'Cristales del End Destruidos',
    'dragon': 'Ender Dragón Derrotado',
    'egg': 'Huevo de Dragón'
}

# Orden oficial de las dimensiones. Para entrar a una dimensión hay que tener
# las 3 banderas de la dimensión anterior; no basta con una sola.
DIMENSION_SEQUENCE = ['overworld', 'nether', 'the_end']


def dimension_is_complete(inv, dimension):
    """Devuelve True solo si están las 3 banderas de la dimensión."""
    return all(step in inv for step in FLAGS[dimension])


def previous_dimension_is_complete(inv, dimension):
    """True si la dimensión anterior está completa (Overworld siempre lo está)."""
    index = DIMENSION_SEQUENCE.index(dimension)
    if index == 0:
        return True
    return dimension_is_complete(inv, DIMENSION_SEQUENCE[index - 1])

def get_inventory():
    if 'inventory' not in session:
        session['inventory'] = []
    return session['inventory']

XP_PER_FLAG = 10
HINT_COST = 20
INITIAL_XP = 0

def get_xp():
    if 'xp' not in session:
        session['xp'] = INITIAL_XP
    return session['xp']

def get_student_score():
    inv = get_inventory()
    # 150 puntos por cada bandera resuelta + XP acumulada
    return (len(inv) * 150) + get_xp()

def get_unlocked_hints():
    if 'unlocked_hints' not in session:
        session['unlocked_hints'] = []
    return session['unlocked_hints']


def get_piglin_trace():
    """Identificador de esta sesión para no mostrar capturas de otros jugadores."""
    if 'piglin_trace' not in session:
        session['piglin_trace'] = uuid.uuid4().hex
        session.modified = True
    return session['piglin_trace']


def save_student_progress():
    """Persiste inventario, XP y pistas desbloqueadas del estudiante logueado."""
    student = session.get('student_name')
    if not student:
        return
    try:
        conn = get_db_connection()
        conn.execute('''
            UPDATE student_profiles
            SET score = ?, flags_solved = ?, inventory_json = ?, xp = ?,
                unlocked_hints_json = ?, last_active = CURRENT_TIMESTAMP
            WHERE credential = ?
        ''', (get_student_score(), len(get_inventory()), json.dumps(get_inventory()),
              get_xp(), json.dumps(get_unlocked_hints()), student))
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_leaderboard_data():
    try:
        conn = get_db_connection()
        rows = conn.execute('SELECT rank_pos, team_name, badge_icon, score, is_crown FROM leaderboard_teams ORDER BY rank_pos ASC').fetchall()
        teams = [dict(row) for row in rows]
        conn.close()
    except Exception:
        teams = [
            {'rank_pos': 1, 'team_name': 'BlockSec', 'badge_icon': 'creeper', 'score': 1250, 'is_crown': 1},
            {'rank_pos': 2, 'team_name': 'CyberMine', 'badge_icon': 'grass', 'score': 1100, 'is_crown': 0},
            {'rank_pos': 3, 'team_name': 'TeamCraft', 'badge_icon': 'diamond', 'score': 980, 'is_crown': 0},
            {'rank_pos': 4, 'team_name': 'RedstoneSec', 'badge_icon': 'redstone', 'score': 920, 'is_crown': 0},
            {'rank_pos': 5, 'team_name': 'MineGuardians', 'badge_icon': 'pickaxe', 'score': 870, 'is_crown': 0}
        ]

    # Si el estudiante ha iniciado sesión, incorporarlo dinámicamente en el ranking
    current_student = session.get('student_name')
    if current_student:
        student_score = get_student_score()
        user_team = {
            'rank_pos': 6,
            'team_name': f'{current_student} (Tú)',
            'badge_icon': 'steve',
            'score': student_score,
            'is_crown': 0,
            'is_current_user': True
        }
        teams.append(user_team)
        teams.sort(key=lambda t: t['score'], reverse=True)
        for idx, t in enumerate(teams):
            t['rank_pos'] = idx + 1
            t['is_crown'] = 1 if idx == 0 else 0
        teams = teams[:6]

    return teams

def build_dimensions_info(inv):
    return [
        {
            'id': 'overworld',
            'title': '1. Dimensión Overworld',
            'subtitle': 'El Mundo Exterior',
            'badge': 'Nivel: Fácil',
            'badge_class': 'green',
            'icon': '🌲',
            'icon_img': 'img/Diemncion del over word_grass_block.png',
            'theme_color': '#22c55e',
            'url': url_for('overworld_view'),
            'is_locked': False,
            'lock_msg': '',
            'solved_count': sum(1 for x in ['iron', 'diamond', 'portal'] if x in inv),
            'total_count': 3,
            'description': 'La dimensión introductoria. Aquí aprenderás los fundamentos del análisis estático de archivos, criptografía clásica y explotación de inyección SQL en bases de datos.',
            'challenges': [
                {
                    'num': 1,
                    'name': 'Lingote de Hierro',
                    'type': 'Esteganografía & Cifrado César (ROT-13) / Base64',
                    'solved': 'iron' in inv,
                    'description': 'Descarga el mapa de la cueva e inspecciona sus metadatos ocultos con exiftool para decodificar la bandera.',
                    'url': url_for('overworld_view')
                },
                {
                    'num': 2,
                    'name': 'Cofre Diamante en Y=-58',
                    'type': "Inyección SQL clásica (' OR 1=1 --)",
                    'solved': 'diamond' in inv,
                    'description': 'Manipula la consulta de búsqueda de cofres de la aldea para burlar el bloqueo de seguridad y saquear el cofre profundo.',
                    'url': url_for('overworld_view')
                },
                {
                    'num': 3,
                    'name': 'Consola de las Cuevas',
                    'type': 'Enumeración de rutas y lectura de archivos (allowlist)',
                    'solved': 'portal' in inv,
                    'description': 'Recorre cinco cuevas con una consola restringida a ls, cat y ayuda para encontrar la llave de ignición y una pista para el Nether.',
                    'url': url_for('overworld_view')
                }
            ]
        },
        {
            'id': 'nether',
            'title': '2. Dimensión Nether',
            'subtitle': 'El Inframundo',
            'badge': 'Nivel: Medio',
            'badge_class': 'blue',
            'icon': '🔥',
            'icon_img': 'img/Dimencion del nether_netherrack.png',
            'theme_color': '#ef4444',
            'url': url_for('nether_view'),
            'is_locked': not dimension_is_complete(inv, 'overworld'),
            'lock_msg': '¡Requiere completar las 3 banderas del Overworld!',
            'solved_count': sum(1 for x in ['gold', 'blaze', 'pearl'] if x in inv),
            'total_count': 3,
            'description': 'El entorno de explotación web. Dominarás ataques de Stored XSS contra bots simulados, subida de archivos maliciosos a ejecución remota de código (RCE) y escalada de privilegios.',
            'challenges': [
                {
                    'num': 1,
                    'name': 'Lingote de Oro',
                    'type': 'Stored XSS & Robo de Cookies de Sesión',
                    'solved': 'gold' in inv,
                    'description': 'Inyecta código JavaScript en las notas de trueque para que el Piglin Guard envíe su cookie privada de tesorero.',
                    'url': url_for('nether_view')
                },
                {
                    'num': 2,
                    'name': 'Varas de Blaze',
                    'type': 'Carga Arbitraria de Archivos (File Upload) a RCE',
                    'solved': 'blaze' in inv,
                    'description': 'Sube una receta .py al caldero; se ejecutará automáticamente y revelará el secreto del Blaze.',
                    'url': url_for('nether_view')
                },
                {
                    'num': 3,
                    'name': 'Ojo de Ender',
                    'type': 'Violación de Mínimo Privilegio & Parameter Tampering',
                    'solved': 'pearl' in inv,
                    'description': 'Modifica los parámetros de rol en la petición HTTP para usurpar privilegios de ender_master en el altar.',
                    'url': url_for('nether_view')
                }
            ]
        },
        {
            'id': 'the_end',
            'title': '3. Dimensión The End',
            'subtitle': 'El Fin del Mundo - Boss Final',
            'badge': 'Nivel: Difícil',
            'badge_class': 'purple',
            'icon': '🌌',
            'icon_img': 'img/Dimencion del end_end_stone.png',
            'theme_color': '#a855f7',
            'url': url_for('the_end_view'),
            'is_locked': not dimension_is_complete(inv, 'nether'),
            'lock_msg': '¡Requiere completar las 3 banderas del Nether!',
            'solved_count': sum(1 for x in ['crystals', 'dragon', 'egg'] if x in inv),
            'total_count': 3,
            'description': 'El desafío final. Explotarás vulnerabilidades CVE simuladas, ejecutarás inyección de comandos en el sistema operativo del servidor y enumerarás Active Directory con PowerView para localizar el Huevo de Dragón.',
            'challenges': [
                {
                    'num': 1,
                    'name': 'Cristales del End',
                    'type': 'Explotación de Vulnerabilidad CVE simulada',
                    'solved': 'crystals' in inv,
                    'description': 'Envía la sobrecarga de telemetría para sabotear los cristales curativos del dragón mediante un backdoor emulado.',
                    'url': url_for('the_end_view')
                },
                {
                    'num': 2,
                    'name': 'Derrotar al Ender Dragón',
                    'type': 'Command Injection en SO (Shell Execution)',
                    'solved': 'dragon' in inv,
                    'description': 'Aprovecha la falta de sanitización en el comando de disparo para concatenar la lectura de /secret/dragon_slain.txt.',
                    'url': url_for('the_end_view')
                },
                {
                    'num': 3,
                    'name': 'Huevo de Dragón',
                    'type': 'Enumeración de Active Directory con PowerView',
                    'solved': 'egg' in inv,
                    'description': 'Usa la consola PowerView para enumerar usuarios, grupos, equipos y recursos compartidos del dominio end.local, y lee el archivo del Huevo en el share del servidor de archivos.',
                    'url': url_for('the_end_view')
                }
            ]
        }
    ]

@app.context_processor
def inject_brand_and_authors():
    logo_src = None
    for ext in ('png', 'webp', 'jpg', 'jpeg', 'svg', 'gif'):
        if os.path.exists(os.path.join(app.static_folder, 'img', f'logo_shield.{ext}')):
            logo_src = f'img/logo_shield.{ext}'
            break
        elif os.path.exists(os.path.join(app.static_folder, 'img', f'logo_creeper.{ext}')):
            logo_src = f'img/logo_creeper.{ext}'
            break

    current_student = session.get('student_name')
    inv = get_inventory()

    # Siguiente dimensión desbloqueada: el botón aparece en la barra superior
    # cuando ya se puede avanzar, sin obligar a volver a la pestaña Desafíos.
    # Se exige la dimensión completa (3/3), no una sola bandera.
    next_dimension = None
    if dimension_is_complete(inv, 'the_end'):
        next_dimension = {
            'id': 'victory',
            'icon': '🏆',
            'icon_img': 'img/Desafios_nether_star.png',
            'name': 'Victoria',
            'url': url_for('victory_view'),
            'theme': 'victory',
        }
    elif dimension_is_complete(inv, 'nether'):
        next_dimension = {
            'id': 'the_end',
            'icon': '🌌',
            'icon_img': 'img/Dimencion del end_end_stone.png',
            'name': 'The End',
            'url': url_for('the_end_view'),
            'theme': 'the_end',
        }
    elif dimension_is_complete(inv, 'overworld'):
        next_dimension = {
            'id': 'nether',
            'icon': '🔥',
            'icon_img': 'img/Dimencion del nether_netherrack.png',
            'name': 'Nether',
            'url': url_for('nether_view'),
            'theme': 'nether',
        }

    return {
        'logo_src': logo_src,
        'lab_authors': LAB_AUTHORS,
        'lab_authors_str': LAB_AUTHORS_STR,
        'current_student': current_student,
        'is_authenticated': current_student is not None,
        'student_score': get_student_score(),
        'solved_flags_count': len(inv),
        'next_dimension': next_dimension,
        'player_xp': get_xp(),
        'hint_cost': HINT_COST,
        'xp_per_flag': XP_PER_FLAG,
    }

@app.after_request
def add_lab_headers(response):
    response.headers['X-Lab-Developers'] = LAB_AUTHORS_STR
    response.headers['X-Lab-Platform'] = 'Minecraft CTF Security Lab'
    return response

@app.errorhandler(413)
def upload_too_large(error):
    flash("El archivo supera el límite permitido de 2 MB para las recetas del caldero.", "error")
    return redirect(url_for('nether_view'))

# ------------------------------------------------------------------------------
# AUTENTICACIÓN CON UNA SOLA CREDENCIAL (DISEÑADO PARA ESTUDIANTES)
# ------------------------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        credential = ''
        if request.is_json:
            data = request.get_json() or {}
            credential = (data.get('credential') or '').strip()
        else:
            credential = (request.form.get('credential') or '').strip()

        if not credential:
            msg = "Por favor ingresa tu Gamertag o Código de Estudiante."
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, "error")
            return redirect(url_for('login'))

        # Autenticación con solo 1 credencial (sin contraseña)
        previous_credential = session.get('student_credential')
        if previous_credential != credential:
            # Otra persona en el mismo navegador: no debe heredar las capturas
            # del Piglin ni la traza de la sesión anterior.
            session.pop('piglin_trace', None)
        session['student_name'] = credential
        session['student_credential'] = credential
        session['logged_in'] = True

        # Registrar o recuperar progreso del estudiante en SQLite
        try:
            conn = get_db_connection()
            row = conn.execute('SELECT * FROM student_profiles WHERE credential = ?', (credential,)).fetchone()
            if row:
                # Inventario: conserva lo que ya había en la sesión y añade lo guardado.
                try:
                    saved_inv = json.loads(row['inventory_json'] or '[]')
                    inv = get_inventory()
                    for item in saved_inv:
                        if item not in inv:
                            inv.append(item)
                    session['inventory'] = inv
                    session.modified = True
                except Exception:
                    pass

                # XP: si la sesión aún no ha ganado/gastado XP, restaura el saldo guardado.
                try:
                    saved_xp = row['xp']
                    if saved_xp is not None and get_xp() == INITIAL_XP:
                        session['xp'] = int(saved_xp)
                        session.modified = True
                except Exception:
                    pass

                # Pistas ya investigadas: no se vuelven a cobrar al recargar.
                try:
                    saved_hints = json.loads(row['unlocked_hints_json'] or '[]')
                    hints = get_unlocked_hints()
                    for hint in saved_hints:
                        if hint not in hints:
                            hints.append(hint)
                    session['unlocked_hints'] = hints
                    session.modified = True
                except Exception:
                    pass
            else:
                conn.execute('''
                    INSERT INTO student_profiles
                        (credential, display_name, team_name, score, flags_solved,
                         inventory_json, xp, unlocked_hints_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (credential, credential, f'Team {credential}', get_student_score(),
                      len(get_inventory()), json.dumps(get_inventory()), get_xp(),
                      json.dumps(get_unlocked_hints())))
            conn.commit()
            conn.close()
        except Exception:
            pass

        # Persiste el estado combinado (por ejemplo, progreso anónimo + perfil).
        save_student_progress()

        success_msg = f"¡Bienvenido, {credential}! Sesión iniciada con éxito en Minecraft CTF."
        if request.is_json:
            return jsonify({
                'success': True,
                'message': success_msg,
                'student_name': credential,
                'score': get_student_score(),
                'redirect_url': url_for('index')
            })

        flash(success_msg, "success")
        next_page = request.args.get('next') or url_for('index')
        return redirect(next_page)

    return render_template('login.html', current_dimension='overworld')

@app.route('/logout')
def logout():
    student = session.pop('student_name', None)
    session.pop('student_credential', None)
    session.pop('logged_in', None)
    # Cada jugador debe empezar sin capturas del Piglin heredadas.
    session.pop('piglin_trace', None)
    if student:
        flash(f"Sesión cerrada correctamente. ¡Hasta pronto, {student}!", "info")
    return redirect(url_for('index'))

# ------------------------------------------------------------------------------
# RUTAS DE NAVEGACIÓN PRINCIPAL
# ------------------------------------------------------------------------------
@app.route('/')
def index():
    inv = get_inventory()
    overworld_count = sum(1 for item in ['iron', 'diamond', 'portal'] if item in inv)
    nether_count = sum(1 for item in ['gold', 'blaze', 'pearl'] if item in inv)
    end_count = sum(1 for item in ['crystals', 'dragon', 'egg'] if item in inv)
    
    if dimension_is_complete(inv, 'the_end'):
        return redirect(url_for('victory_view'))

    leaderboard = get_leaderboard_data()
    dimensions = build_dimensions_info(inv)

    return render_template('index.html',
                           current_dimension='overworld',
                           overworld_count=overworld_count,
                           nether_count=nether_count,
                           end_count=end_count,
                           leaderboard=leaderboard,
                           dimensions=dimensions,
                           xp=get_xp())

@app.route('/desafios')
def desafios_view():
    inv = get_inventory()
    dimensions = build_dimensions_info(inv)
    return render_template('desafios.html', dimensions=dimensions, current_dimension='overworld', inventory=inv)

@app.route('/ranking')
def ranking_view():
    teams = get_leaderboard_data()
    return render_template('ranking.html', teams=teams, current_dimension='overworld')

@app.route('/guia')
def guia_view():
    return render_template('guia.html', current_dimension='overworld')

@app.route('/acerca-de')
def acerca_de_view():
    return render_template('acerca_de.html', current_dimension='overworld')

@app.route('/reset')
def reset_session():
    session.clear()
    session['inventory'] = []
    session['xp'] = INITIAL_XP
    session['unlocked_hints'] = []
    flash("Juego y progreso reiniciados correctamente.", "info")
    return redirect(url_for('index'))

@app.route('/api/inventory')
def api_inventory():
    return jsonify({
        'inventory': get_inventory(),
        'count': len(get_inventory()),
        'xp': get_xp(),
        'unlocked_hints': get_unlocked_hints(),
        'hint_cost': HINT_COST
    })

@app.route('/api/unlock_hint', methods=['POST'])
def api_unlock_hint():
    data = request.get_json() or {}
    challenge = (data.get('challenge') or '').strip()
    if not challenge:
        return jsonify({'success': False, 'message': 'Desafío no especificado.'}), 400

    hints = get_unlocked_hints()
    current_xp = get_xp()

    if challenge in hints:
        return jsonify({
            'success': True,
            'already_unlocked': True,
            'xp': current_xp,
            'message': 'Esta pista ya ha sido desbloqueada.'
        })

    if current_xp < HINT_COST:
        return jsonify({
            'success': False,
            'xp': current_xp,
            'message': f'XP insuficiente. Necesitas {HINT_COST} XP para desbloquear esta pista (tienes {current_xp} XP). ¡Consigue banderas para ganar XP!'
        }), 400

    new_xp = current_xp - HINT_COST
    session['xp'] = new_xp
    if challenge not in hints:
        hints.append(challenge)
    session['unlocked_hints'] = hints
    session.modified = True
    save_student_progress()

    return jsonify({
        'success': True,
        'already_unlocked': False,
        'xp': new_xp,
        'cost': HINT_COST,
        'message': f'¡Pista desbloqueada! Se consumieron {HINT_COST} XP.'
    })

@app.route('/api/submit_flag', methods=['POST'])
def api_submit_flag():
    data = request.get_json() or {}
    dimension = data.get('dimension')
    step = data.get('step')
    submitted_flag = (data.get('flag') or '').strip()

    if dimension not in FLAGS or step not in FLAGS[dimension]:
        return jsonify({'success': False, 'message': 'Desafío no válido.'}), 400

    inv = get_inventory()
    if not previous_dimension_is_complete(inv, dimension):
        previous = DIMENSION_SEQUENCE[DIMENSION_SEQUENCE.index(dimension) - 1]
        return jsonify({
            'success': False,
            'message': f'Debes completar las 3 banderas de {previous.upper()} antes de validar banderas de esta dimensión.'
        }), 403

    expected_flag = FLAGS[dimension][step].strip()
    is_valid = (submitted_flag == expected_flag) or (submitted_flag.upper() == expected_flag.upper())

    if is_valid:
        earned_xp = 0
        if step not in inv:
            inv.append(step)
            session['inventory'] = inv
            session['xp'] = get_xp() + XP_PER_FLAG
            earned_xp = XP_PER_FLAG
            session.modified = True
            save_student_progress()

        dimension_completed = dimension_is_complete(inv, dimension)

        if dimension_is_complete(inv, 'the_end'):
            return jsonify({
                'success': True,
                'message': '¡¡BANDERA FINAL CONQUISTADA!! Has completado los 9 desafíos de Minecraft CTF.',
                'item_name': ITEM_NAMES.get(step, step),
                'earned_xp': earned_xp,
                'current_xp': session['xp'],
                'xp': session['xp'],
                'dimension_completed': True,
                'game_won': True,
                'all_completed': True,
                'redirect_url': url_for('victory_view')
            })

        return jsonify({
            'success': True,
            'message': f'¡CORRECTO! Has desbloqueado el ítem: {ITEM_NAMES.get(step, step)} (+{earned_xp} XP).',
            'item_name': ITEM_NAMES.get(step, step),
            'earned_xp': earned_xp,
            'current_xp': session['xp'],
            'xp': session['xp'],
            'dimension_completed': dimension_completed,
            'game_won': False
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Bandera incorrecta. Recuerda el formato: Flag{...} e investiga a fondo el desafío.'
        }), 400

# ------------------------------------------------------------------------------
# DIMENSIÓN 1: OVERWORLD (FÁCIL)
# ------------------------------------------------------------------------------
@app.route('/overworld')
def overworld_view():
    return render_template('overworld.html', current_dimension='overworld')

@app.route('/overworld/diamond/search', methods=['POST'])
def overworld_diamond_search():
    chest_query = request.form.get('chest_query', '')
    conn = get_db_connection()
    cursor = conn.cursor()

    sql = f"SELECT chest_name, location, depth_level, secret_loot, is_locked FROM villager_chests WHERE chest_name LIKE '%{chest_query}%' AND is_locked = 0"
    
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        error_msg = None
    except Exception as e:
        results = []
        error_msg = f"Error SQL: {str(e)}"
    finally:
        conn.close()

    return render_template('overworld.html',
                           current_dimension='overworld',
                           diamond_results=results,
                           query_executed=sql,
                           sql_error=error_msg)


@app.route('/overworld/cueva')
def overworld_cave():
    return render_template('cueva.html', current_dimension='overworld')


@app.route('/overworld/cueva/terminal', methods=['POST'])
def overworld_cave_terminal():
    payload = request.get_json(silent=True) or {}
    raw_command = payload.get('command', '')
    result = run_cave_command(raw_command, FLAGS['overworld']['portal'])
    return jsonify(result)

# ------------------------------------------------------------------------------
# DIMENSIÓN 2: NETHER (MEDIO)
# ------------------------------------------------------------------------------
def _nether_context():
    conn = get_db_connection()

    # Tanto el tablón como las capturas se limitan a las ofertas de ESTA
    # sesión. Antes se leían todas las filas de SQLite y por eso el token del
    # Piglin aparecía siempre, incluso para otros jugadores y tras reiniciar
    # el servicio.
    trace = session.get('piglin_trace')
    if trace:
        offers = conn.execute('''
            SELECT id, player_name, offered_item, note_to_piglin, status, created_at
            FROM piglin_trade_offers
            WHERE session_trace = ?
            ORDER BY id DESC LIMIT 10
        ''', (trace,)).fetchall()
        stolen = conn.execute('''
            SELECT st.id, st.offer_id, st.captured_data, st.captured_at
            FROM stolen_tokens st
            JOIN piglin_trade_offers o ON o.id = st.offer_id
            WHERE o.session_trace = ?
            ORDER BY st.id DESC LIMIT 5
        ''', (trace,)).fetchall()
    else:
        offers = []
        stolen = []

    conn.close()
    return offers, stolen


def _stolen_tokens_with_flags(rows):
    """Añade la flag extraída del token capturado para validarla manualmente.

    El tablón muestra el payload escapado y la flag, pero no autocompleta el
    formulario de validación: el jugador debe copiarla y enviarla a mano.
    """
    stolen_tokens = []
    for token in rows:
        captured = token['captured_data'] or ''
        match = re.search(r'FLAG\{[^}]+\}', captured)
        if not match:
            continue
        stolen_tokens.append({
            'id': token['id'],
            'captured_data': captured,
            'flag': match.group(0),
        })
    return stolen_tokens


@app.route('/nether')
def nether_view():
    inv = get_inventory()
    if not dimension_is_complete(inv, 'overworld'):
        flash("Debes completar las 3 banderas del Overworld (Lingote de Hierro, Diamante y Portal) para entrar al Nether.", "error")
        return redirect(url_for('overworld_view'))

    offers, stolen = _nether_context()
    stolen_tokens = _stolen_tokens_with_flags(stolen)

    context = {
        'current_dimension': 'nether',
        'offers': offers,
        'stolen_tokens': stolen_tokens,
    }
    uploaded_file = request.args.get('uploaded_file')
    if uploaded_file:
        context['upload_success'] = True
        context['uploaded_filename'] = uploaded_file
    return render_template('nether.html', **context)

@app.route('/nether/gold/submit_offer', methods=['POST'])
def nether_gold_submit_offer():
    inv = get_inventory()
    if not dimension_is_complete(inv, 'overworld'):
        flash("Debes completar las 3 banderas del Overworld antes de comerciar con los Piglins.", "error")
        return redirect(url_for('overworld_view'))

    player_name = request.form.get('player_name', 'Steve')
    offered_item = request.form.get('offered_item', 'Manzanas')
    note_to_piglin = request.form.get('note_to_piglin', '')
    trace = get_piglin_trace()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO piglin_trade_offers (player_name, offered_item, note_to_piglin, session_trace)
        VALUES (?, ?, ?, ?)
    ''', (player_name, offered_item, note_to_piglin, trace))
    offer_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # El bot revisa exactamente la oferta recién creada. Así, tras reiniciar,
    # no reinterpreta ofertas antiguas ni asocia la captura a otro jugador.
    bot_instance.trigger_visit(offer_id=offer_id)
    flash("Tu oferta ha sido entregada al Piglin Guard. ¡Espera su inspección!", "success")
    # La vista muestra un aviso y consulta /nether/gold/tokens hasta que el bot
    # termine, para que el jugador no tenga que refrescar a mano.
    return redirect(url_for('nether_view', awaiting=1))

@app.route('/nether/gold/offers')
def nether_gold_offers():
    conn = get_db_connection()
    cursor = conn.cursor()
    # No se expone session_trace: es interno para vincular la captura.
    offers = cursor.execute('''
        SELECT id, player_name, offered_item, note_to_piglin, status, created_at
        FROM piglin_trade_offers ORDER BY id DESC LIMIT 10
    ''').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in offers])

@app.route('/nether/gold/tokens')
def nether_gold_tokens():
    """Estado ligero para que la tarjeta detecte cuándo el bot ya exfiltró la cookie."""
    trace = session.get('piglin_trace')
    if not trace:
        return jsonify({'captured': False, 'flags': []})

    conn = get_db_connection()
    rows = conn.execute('''
        SELECT st.captured_data
        FROM stolen_tokens st
        JOIN piglin_trade_offers o ON o.id = st.offer_id
        WHERE o.session_trace = ?
        ORDER BY st.id DESC LIMIT 20
    ''', (trace,)).fetchall()
    conn.close()

    flags = []
    for row in rows:
        match = re.search(r'FLAG\{[^}]+\}', row['captured_data'] or '')
        if match:
            flags.append(match.group(0))

    return jsonify({'captured': bool(flags), 'flags': flags})

@app.route('/nether/gold/leak')
def nether_gold_leak():
    cookie_data = request.args.get('cookie', '')
    offer_id = request.args.get('offer_id', type=int)
    token_verified = False
    flag = None

    if PIGLIN_SECRET_TOKEN in cookie_data:
        token_verified = True
        flag = FLAGS['nether']['gold']

    # Guardamos la exfiltración una sola vez por oferta, para que las visitas
    # repetidas del bot no llenen el registro de duplicados y cada jugador
    # tenga asociada su propia captura.
    if cookie_data:
        conn = get_db_connection()
        cursor = conn.cursor()
        if offer_id is not None:
            exists_offer = cursor.execute(
                'SELECT 1 FROM piglin_trade_offers WHERE id = ?',
                (offer_id,)
            ).fetchone()
            if not exists_offer:
                offer_id = None

        dedupe_id = offer_id if offer_id is not None else -1
        exists = cursor.execute(
            'SELECT 1 FROM stolen_tokens WHERE captured_data = ? AND COALESCE(offer_id, -1) = ? LIMIT 1',
            (cookie_data, dedupe_id)
        ).fetchone()
        if not exists:
            cursor.execute(
                'INSERT INTO stolen_tokens (offer_id, captured_data) VALUES (?, ?)',
                (offer_id, cookie_data)
            )
            conn.commit()
        conn.close()

    return jsonify({
        'status': 'received',
        'token_verified': token_verified,
        'flag': flag
    })

def _run_recipe_file(filename):
    safe_name = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    if not os.path.exists(file_path):
        return None

    try:
        if safe_name.endswith('.py'):
            output, error = run_sandboxed(['python', file_path])
        elif safe_name.endswith('.sh'):
            output, error = run_sandboxed(['bash', file_path])
        else:
            with open(file_path, 'r', errors='ignore') as f:
                output, error = f.read(4096), None
    except Exception as e:
        output, error = '', f"Error ejecutando receta: {str(e)}"

    if error:
        output = f"{output}\n{error}".strip() if output else error
    return output


@app.route('/nether/blaze/upload', methods=['POST'])
def nether_blaze_upload():
    inv = get_inventory()
    if not dimension_is_complete(inv, 'overworld'):
        flash("Debes completar las 3 banderas del Overworld antes de usar el caldero del Nether.", "error")
        return redirect(url_for('overworld_view'))

    if 'recipe_file' not in request.files:
        flash("No se seleccionó ningún archivo.", "error")
        return redirect(url_for('nether_view'))

    file = request.files['recipe_file']
    if file.filename == '':
        flash("El nombre del archivo está vacío.", "error")
        return redirect(url_for('nether_view'))

    filename = secure_filename(file.filename)
    if not filename:
        flash("El nombre del archivo no es válido.", "error")
        return redirect(url_for('nether_view'))

    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)

    output = _run_recipe_file(filename)
    if output is None:
        flash("La receta se guardó, pero no se pudo ejecutar.", "error")
        return redirect(url_for('nether_view'))

    offers, stolen = _nether_context()
    return render_template('nether.html',
                           current_dimension='nether',
                           offers=offers,
                           stolen_tokens=_stolen_tokens_with_flags(stolen),
                           upload_success=True,
                           uploaded_filename=filename,
                           rce_output=output)

@app.route('/nether/blaze/execute/<filename>')
def nether_blaze_execute(filename):
    inv = get_inventory()
    if not dimension_is_complete(inv, 'overworld'):
        flash("Debes completar las 3 banderas del Overworld antes de ejecutar recetas en el Nether.", "error")
        return redirect(url_for('overworld_view'))

    output = _run_recipe_file(filename)
    if output is None:
        return "Error: Archivo no encontrado en el caldero.", 404

    offers, stolen = _nether_context()
    return render_template('nether.html',
                           current_dimension='nether',
                           offers=offers,
                           stolen_tokens=_stolen_tokens_with_flags(stolen),
                           upload_success=True,
                           uploaded_filename=secure_filename(filename),
                           rce_output=output)

@app.route('/nether/pearl/altar')
def nether_pearl_altar():
    inv = get_inventory()
    if not dimension_is_complete(inv, 'overworld'):
        flash("Debes completar las 3 banderas del Overworld antes de acceder al altar del Enderman.", "error")
        return redirect(url_for('overworld_view'))

    user_role = request.args.get('user_role') or request.cookies.get('user_role', 'guest_traveler')
    
    if user_role in ['ender_master', 'bastion_overlord', 'admin', 'root']:
        response_html = f'''
        <div style="color:#55ff55;">
          <strong>¡ACCESO CONCEDIDO AL ALTAR DEL ENDERMAN!</strong><br>
          Rol autenticado: <code>{user_role}</code> (Privilegios de Alto Nivel).<br>
          Has forjado el Ojo de Ender legítimo:<br>
          <strong style="color:#facc15; font-size:1.1rem;">FLAG{{MINECRAFT_ENDER_PEARL_PRIV_ESCALATION}}</strong>
        </div>
        '''
    else:
        response_html = f'''
        <div style="color:#ef4444;">
          <strong>ACCESO DENEGADO</strong>: Tu rol actual es <code>{user_role}</code>.<br>
          Solo los usuarios con rol <code>ender_master</code> o <code>bastion_overlord</code> pueden forjar el Ojo de Ender.
        </div>
        '''
    return render_template('nether.html', current_dimension='nether', altar_response=response_html)

# ------------------------------------------------------------------------------
# DIMENSIÓN 3: THE END (DIFÍCIL - BOSS FINAL)
# ------------------------------------------------------------------------------
@app.route('/the_end')
def the_end_view():
    inv = get_inventory()
    if not dimension_is_complete(inv, 'nether'):
        flash("Debes completar las 3 banderas del Nether (Lingote de Oro, Vara de Blaze y Ojo de Ender) para entrar a The End.", "error")
        return redirect(url_for('nether_view'))

    return render_template('the_end.html', current_dimension='the_end')

@app.route('/end/crystals/exploit', methods=['POST'])
def the_end_crystals_exploit():
    inv = get_inventory()
    if not dimension_is_complete(inv, 'nether'):
        flash("Debes completar las 3 banderas del Nether antes de atacar los cristales.", "error")
        return redirect(url_for('nether_view'))

    payload = request.form.get('exploit_payload', '')
    
    if any(trigger in payload for trigger in ['CVE-2026-OVERLOAD', 'AB;', 'shatter_crystals', 'OVERLOAD_CRYSTALS']):
        try:
            with open('/secret/end_crystals.txt', 'r') as f:
                flag = f.read().strip()
        except:
            flag = FLAGS['the_end']['crystals']
        
        result_html = f'''
        <div style="color:#55ff55;">
          <strong>¡BOOM! EXPLOTACIÓN DE SERVICIO EXITOSA</strong><br>
          La sobrecarga de telemetría provocó la detonación en cadena de los 4 cristales de curación.<br>
          Bandera obtenida: <strong style="color:#facc15;">{flag}</strong>
        </div>
        '''
    else:
        result_html = f'''
        <div style="color:#ef4444;">
          Los escudos de los cristales rechazaron el payload: <code>{payload}</code>.<br>
          Los cristales siguen alimentando la vida del Ender Dragón.
        </div>
        '''
    return render_template('the_end.html', current_dimension='the_end', crystal_exploit_result=result_html)

@app.route('/end/dragon/damage', methods=['POST'])
def the_end_dragon_damage():
    inv = get_inventory()
    if not dimension_is_complete(inv, 'nether'):
        flash("Debes completar las 3 banderas del Nether antes de atacar al Ender Dragón.", "error")
        return redirect(url_for('nether_view'))

    shot_power = request.form.get('shot_power', '100')
    
    cmd = f"echo 'Calculando impacto de flecha: potencia {shot_power}'"
    output, error = run_sandboxed(cmd, shell=True)
    if error:
        output = f"{output}\n{error}".strip() if output else error

    return render_template('the_end.html', current_dimension='the_end', dragon_damage_output=output)

@app.route('/end/powerview/terminal', methods=['POST'])
def the_end_powerview_terminal():
    inv = get_inventory()
    if not dimension_is_complete(inv, 'nether'):
        return jsonify({
            'ok': False,
            'kind': 'error',
            'output': 'Debes completar las 3 banderas del Nether antes de usar la consola PowerView de The End.'
        }), 403

    payload = request.get_json(silent=True) or {}
    raw_command = payload.get('command', '')
    result = run_powerview_command(raw_command, FLAGS['the_end']['egg'])
    return jsonify(result)

# ------------------------------------------------------------------------------
# PANTALLA DE VICTORIA FINAL
# ------------------------------------------------------------------------------
@app.route('/victory')
def victory_view():
    inv = get_inventory()
    if not dimension_is_complete(inv, 'the_end'):
        flash("Debes completar las 3 banderas de The End para ver la pantalla de victoria.", "error")
        return redirect(url_for('the_end_view'))

    return render_template('victory.html', current_dimension='victory')

# ------------------------------------------------------------------------------
# INICIALIZACIÓN
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    from bootstrap import bootstrap
    bootstrap()

    print("[+] Servidor Minecraft CTF listo en http://0.0.0.0:8080")
    print(f"[+] Desarrollado por: {LAB_AUTHORS_STR}")
    app.run(host='0.0.0.0', port=8080, debug=False)
