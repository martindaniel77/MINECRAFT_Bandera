FROM python:3.11-slim

# Instalar herramientas básicas del sistema para el entorno CTF
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    curl \
    net-tools \
    procps \
    libimage-exiftool-perl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crear directorios de secretos y desafíos en el sistema de archivos del contenedor
RUN mkdir -p /secret /var/www/honeypot /root

# Configuración de las banderas del sistema en el contenedor
RUN echo "FLAG{MINECRAFT_IRON_INGOT_C3S4R_X0R_M1N3D}" > /secret/iron_ingot.txt && \
    echo "FLAG{MINECRAFT_DIAMOND_SQL1_Y58_UNLOCKED}" > /secret/diamond_vault.txt && \
    echo "FLAG{MINECRAFT_NETHER_PORTAL_METADATA_IGNITED}" > /secret/portal_key.txt && \
    echo "FLAG{MINECRAFT_PIGLIN_XSS_GOLD_BARTERED}" > /secret/gold_ingot.txt && \
    echo "FLAG{MINECRAFT_BLAZE_ROD_WEBSHELL_RCE}" > /secret/blaze_rod.txt && \
    echo "FLAG{MINECRAFT_ENDER_PEARL_PRIV_ESCALATION}" > /secret/ender_pearl.txt && \
    echo "FLAG{MINECRAFT_END_CRYSTALS_CVE_SHATTERED}" > /secret/end_crystals.txt && \
    echo "FLAG{MINECRAFT_ENDER_DRAGON_SLAIN_COMMAND_INJECTION}" > /secret/dragon_slain.txt && \
    echo "FLAG{MINECRAFT_FINAL_DRAGON_EGG_VICTORY_GG}" > /root/real_dragon_egg.txt && \
    echo "FLAG{HONEYPOT_TRAP_NICE_TRY_LOOK_IN_ROOT}" > /var/www/honeypot/fake_egg.txt

# Asignar permisos
RUN chmod 644 /secret/*.txt && \
    chmod 644 /var/www/honeypot/fake_egg.txt && \
    chmod 644 /root/real_dragon_egg.txt

# Copiar código de la aplicación
COPY app/ /app/

# Crear carpeta de subidas para el reto de File Upload
RUN mkdir -p /app/static/uploads && chmod 777 /app/static/uploads

# Exponer el puerto principal de la plataforma
EXPOSE 8080

ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]
