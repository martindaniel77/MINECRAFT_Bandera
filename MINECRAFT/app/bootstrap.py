import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOCK_PATH = os.path.join(APP_DIR, '.init.lock')

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

_NO_LOCK = object()


def _acquire_init_lock():
    try:
        import fcntl
    except ImportError:
        return _NO_LOCK

    handle = open(LOCK_PATH, 'w')
    try:
        fcntl.flock(handle, fcntl.LOCK_EX)
    except OSError:
        handle.close()
        return None
    return handle


def bootstrap():
    from database import init_db
    from init_assets import create_stego_map, create_portal_blueprints, create_svg_icons

    lock = _acquire_init_lock()
    if lock is None:
        return False

    try:
        init_db()
        create_stego_map()
        create_portal_blueprints()
        create_svg_icons()
    finally:
        if lock is not _NO_LOCK:
            lock.close()
    return True


if __name__ == '__main__':
    bootstrap()
    print("[+] Base de datos y assets de Minecraft CTF inicializados correctamente.")
