import threading
import time
import requests

PIGLIN_SECRET_TOKEN = "FLAG{MINECRAFT_PIGLIN_XSS_GOLD_BARTERED}"

class PiglinGuardBot:
    """
    Simulación del Piglin Guard / Tesorero del Bastión.
    Revisa las ofertas de tradeo enviadas por los jugadores con su cookie de sesión privilegiada.
    """
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.captured_tokens = []

    def trigger_visit(self):
        """Ejecuta una visita del bot en un hilo separado para no bloquear la petición"""
        thread = threading.Thread(target=self._simulate_admin_check)
        thread.daemon = True
        thread.start()

    def _simulate_admin_check(self):
        time.sleep(1) # Simula el tiempo que tarda el Piglin en revisar la oferta
        try:
            cookies = {
                'piglin_session_role': 'piglin_treasurer',
                'piglin_gold_vault_token': PIGLIN_SECRET_TOKEN,
                'bastion_access': 'GRANTED_LEVEL_5'
            }
            headers = {
                'User-Agent': 'PiglinGuardBot/1.0 (Nether-Bastion-Automated-Auditor)'
            }
            requests.get(f"{self.base_url}/nether/gold/offers", cookies=cookies, headers=headers, timeout=3)
        except Exception as e:
            # Ignorar si el servidor está iniciando
            pass

bot_instance = PiglinGuardBot()
