import os
import sqlite3
import base64
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_from_directory
from werkzeug.utils import secure_filename

from database import get_db_connection
from bot import bot_instance, PIGLIN_SECRET_TOKEN
from sandbox import run_sandboxed

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'minecraft_dvwa_secret_key_2026_kali')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600

# ------------------------------------------------------------------------------
# DICCIONARIO OFICIAL DE BANDERAS DEL CTF
# ------------------------------------------------------------------------------
FLAGS = {
    'overworld': {
        'iron': 'FLAG{MINECRAFT_IRON_INGOT_C3S4R_X0R_M1N3D}',
        'diamond': 'FLAG{MINECRAFT_DIAMOND_SQL1_Y58_UNLOCKED}',
        'portal': 'FLAG{MINECRAFT_NETHER_PORTAL_METADATA_IGNITED}'
    },
    'nether': {
        'gold': 'FLAG{MINECRAFT_PIGLIN_XSS_GOLD_BARTERED}',
        'blaze': 'FLAG{MINECRAFT_BLAZE_ROD_WEBSHELL_RCE}',
        'pearl': 'FLAG{MINECRAFT_ENDER_PEARL_PRIV_ESCALATION}'
    },
    'the_end': {
        'crystals': 'FLAG{MINECRAFT_END_CRYSTALS_CVE_SHATTERED}',
        'dragon': 'FLAG{MINECRAFT_ENDER_DRAGON_SLAIN_COMMAND_INJECTION}',
        'egg': 'FLAG{MINECRAFT_FINAL_DRAGON_EGG_VICTORY_GG}'
    }
}

ITEM_NAMES = {
    'iron': '⛏️ Lingote de Hierro',
    'diamond': '💎 Diamante',
    'portal': '🟣 Portal al Nether',
    'gold': '🟡 Lingote de Oro',
    'blaze': '🔥 Vara de Blaze',
    'pearl': '👁️ Ojo de Ender',
    'crystals': '💥 Cristales del End Destruidos',
    'dragon': '🐉 Ender Dragón Derrotado',
    'egg': '🥚 Huevo de Dragón'
}

def get_inventory():
    if 'inventory' not in session:
        session['inventory'] = []
    return session['inventory']

@app.errorhandler(413)
def upload_too_large(error):
    flash("El archivo supera el limite permitido de 2 MB para las recetas del caldero.", "error")
    return redirect(url_for('nether_view'))

# ------------------------------------------------------------------------------
# RUTAS DE NAVEGACIÓN PRINCIPAL
# ------------------------------------------------------------------------------
@app.route('/')
def index():
    inv = get_inventory()
    overworld_count = sum(1 for item in ['iron', 'diamond', 'portal'] if item in inv)
    nether_count = sum(1 for item in ['gold', 'blaze', 'pearl'] if item in inv)
    end_count = sum(1 for item in ['crystals', 'dragon', 'egg'] if item in inv)
    
    if len(inv) == 9:
        return redirect(url_for('victory_view'))

    return render_template('index.html',
                           current_dimension='overworld',
                           overworld_count=overworld_count,
                           nether_count=nether_count,
                           end_count=end_count)

@app.route('/reset')
def reset_session():
    session.clear()
    session['inventory'] = []
    flash("Juego y progreso reiniciados correctamente.", "info")
    return redirect(url_for('index'))

@app.route('/api/inventory')
def api_inventory():
    return jsonify({
        'inventory': get_inventory(),
        'count': len(get_inventory())
    })

@app.route('/api/submit_flag', methods=['POST'])
def api_submit_flag():
    data = request.get_json() or {}
    dimension = data.get('dimension')
    step = data.get('step')
    submitted_flag = (data.get('flag') or '').strip()

    if dimension not in FLAGS or step not in FLAGS[dimension]:
        return jsonify({'success': False, 'message': 'Desafío no válido.'}), 400

    is_valid = submitted_flag == FLAGS[dimension][step]

    if is_valid:
        inv = get_inventory()
        if step not in inv:
            inv.append(step)
            session['inventory'] = inv
            session.modified = True

        # Verificar si completó la dimensión
        dim_items = list(FLAGS[dimension].keys())
        dimension_completed = all(item in inv for item in dim_items)

        # Si capturó todo
        if len(inv) == 9:
            return jsonify({
                'success': True,
                'message': f'¡BANDERA CORRECTA! Has desbloqueado: {ITEM_NAMES.get(step, step)}. ¡JUEGO COMPLETADO!',
                'dimension_completed': True,
                'all_completed': True
            })

        return jsonify({
            'success': True,
            'message': f'¡BANDERA CORRECTA! Has desbloqueado: {ITEM_NAMES.get(step, step)}',
            'dimension_completed': dimension_completed,
            'all_completed': False
        })
    else:
        return jsonify({'success': False, 'message': 'Bandera incorrecta. Inténtalo de nuevo.'}), 400

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
    
    # VULNERABILIDAD: Inyección SQL clásica (concatenación directa sin parametrizar)
    # El filtro is_locked oculta el cofre del herrero; hay que romperlo con la inyección.
    raw_sql = f"SELECT * FROM villager_chests WHERE is_locked = 0 AND chest_name LIKE '%{chest_query}%'"
    try:
        cursor.execute(raw_sql)
        results = cursor.fetchall()
    except Exception as e:
        results = [{'chest_name': 'SQL ERROR', 'location': 'N/A', 'depth_level': 0, 'secret_loot': str(e)}]
    finally:
        conn.close()

    return render_template('overworld.html', current_dimension='overworld', sql_results=results)

# ------------------------------------------------------------------------------
# DIMENSIÓN 2: NETHER (MEDIO)
# ------------------------------------------------------------------------------
@app.route('/nether')
def nether_view():
    inv = get_inventory()
    # Requiere haber conseguido el portal del Overworld
    if 'portal' not in inv and 'dev' not in request.args:
        flash("🔒 Debes completar el Overworld y encender el Portal para entrar al Nether.", "error")
        return redirect(url_for('overworld_view'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM piglin_trade_offers ORDER BY id DESC LIMIT 5')
    offers = cursor.fetchall()
    conn.close()

    return render_template('nether.html', current_dimension='nether', trade_offers=offers,
                           captured_tokens=bot_instance.get_captured_tokens())

@app.route('/nether/gold/submit_offer', methods=['POST'])
def nether_gold_submit_offer():
    player_name = request.form.get('player_name', 'Steve')
    offered_item = request.form.get('offered_item', 'Manzanas')
    note_to_piglin = request.form.get('note_to_piglin', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO piglin_trade_offers (player_name, offered_item, note_to_piglin)
        VALUES (?, ?, ?)
    ''', (player_name, offered_item, note_to_piglin))
    conn.commit()
    conn.close()

    # Disparar bot simulado del Piglin Guard
    bot_instance.trigger_visit()
    flash("Oferta enviada al Bastión. El Piglin Guard está revisando las ofertas...", "info")
    return redirect(url_for('nether_view'))

@app.route('/nether/gold/offers')
def nether_gold_offers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM piglin_trade_offers ORDER BY id DESC LIMIT 10')
    offers = cursor.fetchall()
    conn.close()
    return render_template('nether.html', current_dimension='nether', trade_offers=offers,
                           captured_tokens=bot_instance.get_captured_tokens())

@app.route('/nether/gold/leak')
def nether_gold_leak():
    # Receptor para robo de cookies en pruebas de XSS.
    # Solo entrega la flag si el token real del Piglin Guard llega en los datos
    # exfiltrados: el endpoint no regala la bandera por ser consultado.
    leaked_data = request.args.get('cookie') or request.args.get('c') or request.args.get('data') or ''
    token_verified = PIGLIN_SECRET_TOKEN in leaked_data

    if token_verified:
        bot_instance.record_capture(leaked_data)

    return jsonify({
        'status': 'captured',
        'received': leaked_data,
        'token_verified': token_verified,
        'flag': PIGLIN_SECRET_TOKEN if token_verified else None
    })

@app.route('/nether/blaze/upload', methods=['POST'])
def nether_blaze_upload():
    if 'recipe_file' not in request.files:
        flash("No se seleccionó ningún archivo.", "error")
        return redirect(url_for('nether_view'))
    
    file = request.files['recipe_file']
    if file.filename == '':
        flash("Nombre de archivo vacío.", "error")
        return redirect(url_for('nether_view'))

    # VULNERABILIDAD: Arbitrary File Upload sin validar extensión ni tipo MIME
    filename = secure_filename(file.filename) or "uploaded_recipe.py"
    target_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(target_path)

    return render_template('nether.html', current_dimension='nether', upload_success=True, uploaded_filename=filename)

@app.route('/nether/blaze/execute/<filename>')
def nether_blaze_execute(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    if not os.path.exists(file_path):
        return "Error: Archivo no encontrado en el caldero.", 404

    output = ""
    try:
        if filename.endswith('.py'):
            output, error = run_sandboxed(['python', file_path])
        elif filename.endswith('.sh'):
            output, error = run_sandboxed(['bash', file_path])
        else:
            with open(file_path, 'r', errors='ignore') as f:
                output, error = f.read(4096), None
    except Exception as e:
        output, error = f"Error ejecutando receta: {str(e)}", None

    if error:
        output = f"{output}\n{error}".strip() if output else error

    return render_template('nether.html', current_dimension='nether', rce_output=output)

@app.route('/nether/pearl/altar')
def nether_pearl_altar():
    # VULNERABILIDAD: Violación de Mínimo Privilegio / Parameter tampering
    user_role = request.args.get('user_role') or request.cookies.get('user_role', 'guest_traveler')
    
    if user_role in ['ender_master', 'bastion_overlord', 'admin', 'root']:
        response_html = f'''
        <div style="color:#55ff55;">
          ✨ <strong>¡ACCESO CONCEDIDO AL ALTAR DEL ENDERMAN!</strong><br>
          Rol autenticado: <code>{user_role}</code> (Privilegios de Alto Nivel).<br>
          Has forjado el Ojo de Ender legítimo:<br>
          <strong style="color:#facc15; font-size:1.1rem;">FLAG{{MINECRAFT_ENDER_PEARL_PRIV_ESCALATION}}</strong>
        </div>
        '''
    else:
        response_html = f'''
        <div style="color:#ef4444;">
          ⛔ <strong>ACCESO DENEGADO</strong>: Tu rol actual es <code>{user_role}</code>.<br>
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
    if 'pearl' not in inv and 'dev' not in request.args:
        flash("🔒 Debes completar el Nether y craftear el Ojo de Ender para entrar a The End.", "error")
        return redirect(url_for('nether_view'))

    return render_template('the_end.html', current_dimension='the_end')

@app.route('/end/crystals/exploit', methods=['POST'])
def the_end_crystals_exploit():
    payload = request.form.get('exploit_payload', '')
    
    # Simulación de explotación de CVE / Backdoor de servicio
    if any(trigger in payload for trigger in ['CVE-2026-OVERLOAD', 'AB;', 'shatter_crystals', 'OVERLOAD_CRYSTALS']):
        try:
            with open('/secret/end_crystals.txt', 'r') as f:
                flag = f.read().strip()
        except:
            flag = FLAGS['the_end']['crystals']
        
        result_html = f'''
        <div style="color:#55ff55;">
          💥 <strong>¡BOOM! EXPLOTACIÓN DE SERVICIO EXITOSA</strong><br>
          La sobrecarga de telemetría provocó la detonación en cadena de los 4 cristales de curación.<br>
          Bandera obtenida: <strong style="color:#facc15;">{flag}</strong>
        </div>
        '''
    else:
        result_html = f'''
        <div style="color:#ef4444;">
          🛡️ Los escudos de los cristales rechazaron el payload: <code>{payload}</code>.<br>
          Los cristales siguen alimentando la vida del Ender Dragón.
        </div>
        '''
    return render_template('the_end.html', current_dimension='the_end', crystal_exploit_result=result_html)

@app.route('/end/dragon/damage', methods=['POST'])
def the_end_dragon_damage():
    shot_power = request.form.get('shot_power', '100')
    
    # VULNERABILIDAD: Inyección de comandos en subprocess shell=True
    cmd = f"echo 'Calculando impacto de flecha: potencia {shot_power}'"
    output, error = run_sandboxed(cmd, shell=True)
    if error:
        output = f"{output}\n{error}".strip() if output else error

    return render_template('the_end.html', current_dimension='the_end', dragon_damage_output=output)

@app.route('/end/egg/inspect')
def the_end_egg_inspect():
    altar_file = request.args.get('altar_file', 'honeypot/fake_egg.txt')
    
    # VULNERABILIDAD: Path Traversal / LFI en /var/www/
    base_dir = "/var/www"
    target_path = os.path.join(base_dir, altar_file)
    
    try:
        with open(target_path, 'r') as f:
            content = f.read()
    except Exception as e:
        # Fallback si corre en entorno local fuera de Docker
        if 'real_dragon_egg' in altar_file:
            content = FLAGS['the_end']['egg']
        elif 'fake_egg' in altar_file:
            content = "FLAG{HONEYPOT_TRAP_NICE_TRY_LOOK_IN_ROOT} (⚠️ Señuelo detectado: Este no es el huevo real)"
        else:
            content = f"Error leyendo archivo: {str(e)}"

    return render_template('the_end.html', current_dimension='the_end', egg_inspect_output=content)

# ------------------------------------------------------------------------------
# PANTALLA DE VICTORIA FINAL
# ------------------------------------------------------------------------------
@app.route('/victory')
def victory_view():
    return render_template('victory.html', current_dimension='the_end')

# ------------------------------------------------------------------------------
# INICIALIZACIÓN
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    from bootstrap import bootstrap

    bootstrap()

    print("[+] Servidor Minecraft CTF listo en http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
