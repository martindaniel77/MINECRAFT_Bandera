import re
import threading
import time
import requests

PIGLIN_SECRET_TOKEN = "FLAG{MINECRAFT_PIGLIN_XSS_GOLD_BARTERED}"
LEAK_PATH = "/nether/gold/leak"

class PiglinGuardBot:
    """
    Simulación del Piglin Guard / Tesorero del Bastión.
    Revisa las ofertas de tradeo enviadas por los jugadores con su cookie de sesión privilegiada.

    No hay motor de navegador en la imagen, así que el script inyectado no llega a
    ejecutarse por sí solo. El bot inspecciona las ofertas almacenadas y, si encuentra
    una referencia al endpoint receptor, reproduce la exfiltración que el navegador
    ejecutaría: envía sus propias cookies privilegiadas a ese endpoint.
    """
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self._visit_in_progress = False
        self._visit_lock = threading.Lock()
        # Última oferta ya revisada: evita re-atacar ofertas antiguas.
        self._last_seen_offer_id = 0

    def trigger_visit(self):
        """Ejecuta una visita del bot en un hilo separado para no bloquear la petición"""
        with self._visit_lock:
            if self._visit_in_progress:
                return
            self._visit_in_progress = True

        thread = threading.Thread(target=self._simulate_admin_check)
        thread.daemon = True
        thread.start()

    def record_capture(self, leaked_data, offer_id=None):
        """
        Registra un token capturado. Lo invoca /nether/gold/leak al validar la cookie.
        Se guarda en SQLite porque gunicorn corre varios workers en procesos
        separados: una lista en memoria solo sería visible en un worker.
        """
        if not leaked_data:
            return
        try:
            from database import get_db_connection
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT id FROM stolen_tokens WHERE captured_data = ?',
                (leaked_data,)
            )
            if cur.fetchone() is None:
                cur.execute(
                    'INSERT INTO stolen_tokens (offer_id, captured_data) VALUES (?, ?)',
                    (offer_id, leaked_data)
                )
                conn.commit()
            conn.close()
        except Exception:
            pass

    def get_captured_tokens(self):
        try:
            from database import get_db_connection
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT captured_data FROM stolen_tokens ORDER BY id DESC')
            rows = [r[0] for r in cur.fetchall()]
            conn.close()
            return rows
        except Exception:
            return []

    def _simulate_admin_check(self):
        try:
            time.sleep(1) # Simula el tiempo que tarda el Piglin en revisar la oferta
            cookies = {
                'piglin_session_role': 'piglin_treasurer',
                'piglin_gold_vault_token': PIGLIN_SECRET_TOKEN,
                'bastion_access': 'GRANTED_LEVEL_5'
            }
            headers = {
                'User-Agent': 'PiglinGuardBot/1.0 (Nether-Bastion-Automated-Auditor)'
            }
            resp = requests.get(f"{self.base_url}/nether/gold/offers",
                                cookies=cookies, headers=headers, timeout=3)
            self._execute_stored_payload(resp.text, cookies)
        except Exception as e:
            # Ignorar si el servidor está iniciando
            pass
        finally:
            with self._visit_lock:
                self._visit_in_progress = False

    def _execute_stored_payload(self, page_html, cookies):
        """
        Reproduce la ejecución del XSS almacenado. Solo se procesan las ofertas
        nuevas (id mayor al último revisado) y, si una contiene una referencia al
        endpoint receptor, se envía la cookie real del bot a ese endpoint usando el
        mismo parámetro que usó el atacante.
        """
        offers = re.findall(
            r'data-offer-id="(\d+)"(.*?)(?=data-offer-id="|\Z)',
            page_html, re.DOTALL)

        new_offers = [(int(oid), block) for oid, block in offers
                      if int(oid) > self._last_seen_offer_id]
        if not new_offers:
            return

        self._last_seen_offer_id = max(oid for oid, _ in new_offers)

        for _, block in new_offers:
            if LEAK_PATH not in block:
                continue

            # Descubre con qué parámetro el atacante envía los datos (c, cookie, data...).
            param = "cookie"
            match = re.search(re.escape(LEAK_PATH) + r"[^\"'\s]*?[?&]([A-Za-z_][A-Za-z0-9_]*)=", block)
            if match:
                param = match.group(1)

            stolen = "; ".join(f"{k}={v}" for k, v in cookies.items())
            try:
                requests.get(f"{self.base_url}{LEAK_PATH}",
                             params={param: stolen},
                             headers={'User-Agent': 'PiglinGuardBot/1.0'},
                             timeout=3)
            except Exception:
                pass
            return

bot_instance = PiglinGuardBot()
