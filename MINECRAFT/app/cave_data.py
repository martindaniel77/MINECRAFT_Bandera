# ==============================================================================
# MINECRAFT CTF - DATOS Y MOTOR DE LA CONSOLA DE LAS CUEVAS (Actividad 3)
# Desarrollado por: Thorfinn777, Martyn777, Sassyjack777
#
# La consola NO ejecuta una shell real ni toca el sistema de archivos.
# Solo resuelve comandos contra el diccionario CAVE_ROUTES.
# ==============================================================================

import posixpath
import shlex
import textwrap

CAVE_ROOT = '/cueva'
MAX_COMMAND_LENGTH = 200
PORTAL_FLAG_PLACEHOLDER = '@@PORTAL_FLAG@@'


def _txt(text):
    """Normaliza el contenido de un archivo falso."""
    return textwrap.dedent(text).strip('\n') + '\n'


# ------------------------------------------------------------------------------
# CUEVAS DISPONIBLES
# ------------------------------------------------------------------------------
CAVE_ROUTES = {
    'hielo': {
        'files': {
            'registro_expedicion.txt': _txt("""
                EXPEDICIÓN 12 — CUEVA DE HIELO
                El agua de esta cueva nunca llegó a la lava: se congeló antes.
                Encontramos hielo azul, carámbanos y un explorador atrapado en el hielo.
                No hay obsidiana. No hay portal. Solo frío.
            """),
            'explorador_congelado.txt': _txt("""
                Un aventurero con armadura de cuero.
                En su mano hay una tablilla de arcilla congelada.
                No se puede leer completa.
            """),
            'tablilla_congelada.txt': _txt("""
                Tablilla de arcilla atrapada en el hielo.
                La escarcha cubre casi todo, pero se alcanza a leer:

                FLAG{MINECRAFT_NETHER_PORTAL_HIELO_APAGADO}

                El resto está partido.
            """),
        }
    },
    'estalactitas': {
        'files': {
            'registro_geologo.txt': _txt("""
                INFORME GEOLÓGICO
                Estalactitas de piedra caliza, algunas de más de diez bloques.
                El suelo está cubierto de puntas. Un paso en falso y caes.
                No hay vetas de obsidiana ni rastros de construcción.
            """),
            'estalactita.txt': _txt("""
                Muestra de estalactita.
                Composición: piedra, agua filtrada, siglos de paciencia.
                Valor para el portal: ninguno.
            """),
            'sonido.txt': _txt("""
                Se escuchan pasos en la oscuridad.
                Probablemente murciélagos. Probablemente.
            """),
        }
    },
    'luminosa': {
        'files': {
            'registro_buceador.txt': _txt("""
                CUEVA LUMINOSA
                Musgo, bayas brillantes y un estanque de agua cristalina.
                Hay axolotes. Uno rosado me siguió toda la tarde.
                No hay lava, no hay obsidiana, no hay llave.
            """),
            'axolote.txt': _txt("""
                Axolote común.
                Le gustan las cuevas luminosas y las personas que no llevan armas.
                No sabe nada del portal.
            """),
            'bayas_luminosas.txt': _txt("""
                Bayas de brillo. Iluminan la cueva.
                Se pueden comer. No sirven para encender obsidiana.
            """),
        }
    },
    'bruja': {
        'files': {
            'caldero_oxidado.txt': _txt("""
                Un caldero de hierro volcado, cubierto de musgo.
                Todavía huele a azufre. No es de esta cueva.
            """),
            'escritos_de_la_bruja.txt': _txt("""
                ESCRITOS DE LA BRUJA — fragmento
                El caldero de la fortaleza del Nether no es un adorno.
                Acepta recetas de cualquier visitante y las ejecuta sin revisar la extensión.
                El secreto del Blaze no vive en la carpeta de subidas:
                está en /secret/blaze_rod.txt.
                Una receta .py que abra esa ruta y la imprima bastará.
            """),
            'nota_del_aprendiz.txt': _txt("""
                La bruja decía que el caldero obedece a quien escribe la receta correcta.
                Yo solo sé preparar pociones de curación.
                Ella no me dejó leer la página arrancada.
            """),
        }
    },
    'lago-de-lava': {
        'files': {
            'orilla_del_lago.txt': _txt("""
                LAGO DE LAVA — ORILLA SUR
                El calor no deja acercarse.
                En la orilla hay bloques de obsidiana que no pertenecen a la cueva.
                Alguien construyó un marco aquí hace mucho tiempo.
            """),
            'protocolo_ignicion.txt': _txt("""
                PROTOCOLO DE IGNICIÓN — RUINAS DEL PORTAL
                1. La obsidiana conserva la llave desde la primera era.
                2. No mojar la piedra: el agua borra la inscripción.
                3. La llave está grabada en el bloque central, bajo la ceniza.
            """),
            'llave_ignicion.txt': PORTAL_FLAG_PLACEHOLDER + '\n',
            'obsidiana_grabada.txt': _txt("""
                Símbolos antiguos sobre obsidiana seca.
                El calor de la lava los preservó; el agua nunca llegó hasta aquí.
            """),
        }
    },
}


def build_routes(portal_flag):
    """Devuelve una copia de las cuevas con la bandera real inyectada."""
    routes = {}
    for route_id, route in CAVE_ROUTES.items():
        files = {}
        for filename, content in route['files'].items():
            files[filename] = content.replace(PORTAL_FLAG_PLACEHOLDER, portal_flag)
        routes[route_id] = {'files': files}
    return routes


# ------------------------------------------------------------------------------
# RESOLUCIÓN DE RUTAS
# ------------------------------------------------------------------------------
def _normalize_path(raw_path):
    """Convierte una ruta relativa o absoluta en una ruta canónica bajo /cueva.

    Devuelve None si la ruta intenta salir de la cueva o contiene caracteres
    que no pertenecen a este laboratorio.
    """
    path = (raw_path or '').strip()
    if not path:
        return CAVE_ROOT
    if '\\' in path or '\x00' in path:
        return None

    if not path.startswith('/'):
        path = f'{CAVE_ROOT}/{path}'

    normalized = posixpath.normpath(path)
    if normalized.startswith('//'):
        normalized = '/' + normalized.lstrip('/')

    if normalized != CAVE_ROOT and not normalized.startswith(CAVE_ROOT + '/'):
        return None
    return normalized


def _split_target(normalized):
    """Devuelve (cueva, archivo) a partir de una ruta canónica."""
    if normalized == CAVE_ROOT:
        return None, None
    relative = normalized[len(CAVE_ROOT) + 1:]
    parts = relative.split('/')
    if len(parts) == 1:
        return parts[0], None
    if len(parts) == 2:
        return parts[0], parts[1]
    return None, None


def _result(output, kind='text', ok=True):
    return {'ok': ok, 'kind': kind, 'output': output}


def _error(message):
    return _result(message, kind='error', ok=False)


def _help_text():
    return textwrap.dedent("""
        Comandos disponibles:
          ls [ruta]      Lista las cuevas o los archivos de una cueva.
          cat <archivo>  Muestra el contenido de un archivo.
          help           Muestra esta ayuda.
          clear          Limpia la pantalla.

        Solo puedes moverte por /cueva. No existe cd: usa rutas absolutas
        (/cueva/lago-de-lava/llave_ignicion.txt) o relativas a /cueva.
    """).strip('\n')


def _command_ls(args, routes):
    if len(args) > 1:
        return _error('ls: demasiados argumentos. Uso: ls [ruta]')

    target = args[0] if args else CAVE_ROOT
    normalized = _normalize_path(target)
    if normalized is None:
        return _error('ls: esa ruta no pertenece a la cueva.')

    if normalized == CAVE_ROOT:
        names = sorted(f'{route_id}/' for route_id in routes)
        return _result('\n'.join(names), kind='list')

    route_id, filename = _split_target(normalized)
    if route_id not in routes:
        return _error('ls: no existe esa cueva.')

    if filename is None:
        files = sorted(routes[route_id]['files'])
        return _result('\n'.join(files), kind='list')

    if filename in routes[route_id]['files']:
        return _error('ls: eso es un archivo, no una cueva. Prueba con cat.')
    return _error('ls: no existe ese archivo ni esa cueva.')


def _command_cat(args, routes):
    if not args:
        return _error('cat: falta el archivo. Uso: cat <archivo>')
    if len(args) > 1:
        return _error('cat: este laboratorio solo permite un archivo por vez.')

    normalized = _normalize_path(args[0])
    if normalized is None:
        return _error('cat: esa ruta no pertenece a la cueva.')

    route_id, filename = _split_target(normalized)
    if route_id is None:
        return _error('cat: /cueva es una cueva, no un archivo.')
    if route_id not in routes:
        return _error('cat: no existe esa cueva.')
    if filename is None:
        return _error('cat: eso es una cueva, no un archivo.')
    if filename not in routes[route_id]['files']:
        return _error('cat: no existe ese archivo en la cueva.')

    return _result(routes[route_id]['files'][filename], kind='text')


def run_cave_command(raw_command, portal_flag):
    """Interpreta un comando de la consola y devuelve la respuesta para la web."""
    command = (raw_command or '').strip()

    if len(command) > MAX_COMMAND_LENGTH:
        return _error(f'El comando supera el límite de {MAX_COMMAND_LENGTH} caracteres.')

    if not command:
        return _result('')

    try:
        parts = shlex.split(command, posix=True)
    except ValueError:
        return _error('Comillas sin cerrar. Revisa el comando.')

    if not parts:
        return _result('')

    name = parts[0].lower()
    args = parts[1:]
    routes = build_routes(portal_flag)

    if name == 'help':
        return _result(_help_text(), kind='help')
    if name == 'ls':
        return _command_ls(args, routes)
    if name == 'cat':
        return _command_cat(args, routes)
    if name == 'clear':
        return {'ok': True, 'kind': 'text', 'output': '', 'clear': True}

    return _error('Comando no permitido. Solo ls, cat, help y clear.')
