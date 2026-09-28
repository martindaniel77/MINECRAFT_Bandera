import subprocess
import threading
import time

try:
    import resource
except ImportError:
    resource = None

MAX_OUTPUT_BYTES = 16384
MAX_OUTPUT_CHARS = 4096
CHUNK_BYTES = 2048
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


def _drain(stream, sink, overflow):
    collected = 0
    try:
        while True:
            chunk = stream.read(CHUNK_BYTES)
            if not chunk:
                return
            sink.append(chunk)
            collected += len(chunk)
            if collected >= MAX_OUTPUT_BYTES:
                overflow.set()
                return
    except Exception:
        return


def _terminate(process):
    try:
        process.kill()
    except Exception:
        return
    try:
        process.wait(timeout=2)
    except Exception:
        return


def _decode(buffer):
    return b"".join(buffer).decode('utf-8', errors='ignore')


def _truncate(text):
    if len(text) <= MAX_OUTPUT_CHARS:
        return text
    return text[:MAX_OUTPUT_CHARS] + f"\n[...salida truncada a {MAX_OUTPUT_CHARS} caracteres...]"


def run_sandboxed(command, shell=False, timeout=WALL_TIMEOUT_SECONDS):
    if not _execution_slots.acquire(timeout=ACQUIRE_TIMEOUT_SECONDS):
        return '', 'Error: el servidor de juego esta ocupado con otra ejecucion, reintenta en un momento.'

    process = None
    reader = None

    try:
        process = subprocess.Popen(
            command,
            shell=shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=_PREEXEC_FN,
        )

        buffer = []
        overflow = threading.Event()
        reader = threading.Thread(target=_drain, args=(process.stdout, buffer, overflow), daemon=True)
        reader.start()

        timed_out = False
        deadline = time.monotonic() + timeout

        while process.poll() is None:
            if overflow.is_set() or time.monotonic() >= deadline:
                break
            time.sleep(0.02)

        if process.poll() is None:
            timed_out = not overflow.is_set()
            _terminate(process)

        reader.join(timeout=2)
        output = _truncate(_decode(buffer))

        if overflow.is_set():
            return output, f'Error: la salida supero el limite de {MAX_OUTPUT_BYTES} bytes y fue truncada para proteger el servidor.'
        if timed_out:
            return output, f'Error: la ejecucion supero los {timeout} segundos y fue cancelada.'
        return output, None
    except Exception as error:
        return '', f'Error ejecutando receta: {error}'
    finally:
        if process is not None:
            if process.poll() is None:
                _terminate(process)
            if reader is not None:
                reader.join(timeout=2)
            if process.stdout is not None:
                try:
                    process.stdout.close()
                except Exception:
                    pass
        _execution_slots.release()
