import subprocess
import threading

try:
    import resource
except ImportError:
    resource = None

MAX_OUTPUT_CHARS = 4096
WALL_TIMEOUT_SECONDS = 5
ACQUIRE_TIMEOUT_SECONDS = 6
MAX_CONCURRENT_EXECUTIONS = 1

CPU_SECONDS = 2
FILE_SIZE_BYTES = 1024 * 1024
PROCESS_COUNT = 16
OPEN_FILES = 32

_execution_slots = threading.BoundedSemaphore(MAX_CONCURRENT_EXECUTIONS)


def _limit_child():
    if resource is None:
        return None
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
    resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_SIZE_BYTES, FILE_SIZE_BYTES))
    resource.setrlimit(resource.RLIMIT_NPROC, (PROCESS_COUNT, PROCESS_COUNT))
    resource.setrlimit(resource.RLIMIT_NOFILE, (OPEN_FILES, OPEN_FILES))
    return None


_PREEXEC_FN = _limit_child if resource is not None else None


def _truncate(text):
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + f"\n[...salida truncada a {MAX_OUTPUT_CHARS} caracteres...]"


def run_sandboxed(command, shell=False, timeout=WALL_TIMEOUT_SECONDS):
    if not _execution_slots.acquire(timeout=ACQUIRE_TIMEOUT_SECONDS):
        return '', 'Error: el servidor de juego esta ocupado con otra ejecucion, reintenta en un momento.'

    try:
        completed = subprocess.run(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            preexec_fn=_PREEXEC_FN,
        )
        return _truncate(completed.stdout.decode('utf-8', errors='ignore')), None
    except subprocess.TimeoutExpired as expired:
        partial = (expired.output or b'').decode('utf-8', errors='ignore')
        return _truncate(partial), f'Error: la ejecucion supero los {timeout} segundos y fue cancelada.'
    except Exception as error:
        return '', f'Error ejecutando receta: {error}'
    finally:
        _execution_slots.release()
