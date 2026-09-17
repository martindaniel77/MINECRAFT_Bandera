#!/bin/bash
# ==============================================================================
# MINECRAFT CTF - DVWA STYLE DEPLOYMENT SCRIPT
# Kali Linux Automatización de Despliegue (8. Semestre - Seguridad App)
# ==============================================================================

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

clear
echo -e "${GREEN}"
echo "======================================================================"
echo "    ███╗   ███╗██╗███╗   ██╗███████╗ ██████╗██████╗  █████╗ ███████╗████████╗"
echo "    ████╗ ████║██║████╗  ██║██╔════╝██╔════╝██╔══██╗██╔══██╗██╔════╝╚══██╔══╝"
echo "    ██╔████╔██║██║██╔██╗ ██║█████╗  ██║     ██████╔╝███████║█████╗     ██║   "
echo "    ██║╚██╔╝██║██║██║╚██╗██║██╔══╝  ██║     ██╔══██╗██╔══██║██╔══╝     ██║   "
echo "    ██║ ╚═╝ ██║██║██║ ╚████║███████╗╚██████╗██║  ██║██║  ██║██║        ██║   "
echo "    ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝        ╚═╝   "
echo "                    [ CAPTURE THE FLAG - DVWA STYLE ]                 "
echo "======================================================================"
echo -e "${NC}"

# Detectar si se requiere sudo para docker
SUDO=""
if [ "$EUID" -ne 0 ]; then
    if ! groups | grep -q '\bdocker\b'; then
        SUDO="sudo"
    fi
fi

echo -e "${CYAN}[*] Verificando entorno en Kali Linux...${NC}"

# 1. Verificar e iniciar servicio Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[!] Docker no está instalado. Instalando Docker...${NC}"
    sudo apt update && sudo apt install -y docker.io docker-compose
    sudo systemctl enable docker --now
else
    echo -e "${GREEN}[+] Docker CLI encontrado.${NC}"
fi

if ! systemctl is-active --quiet docker; then
    echo -e "${YELLOW}[*] Iniciando servicio Docker con systemctl...${NC}"
    sudo systemctl start docker
    sleep 2
fi

echo -e "${CYAN}[*] Limpiando contenedores previos si existen...${NC}"
$SUDO docker rm -f minecraft_ctf_dvwa 2>/dev/null || true
$SUDO docker-compose down 2>/dev/null || true

echo -e "${CYAN}[*] Construyendo y levantando la imagen Docker...${NC}"

# Estrategia de despliegue con fallback garantizado
DEPLOYED=false

# Intento 1: docker-compose clásico
if command -v docker-compose &> /dev/null; then
    echo -e "${CYAN}[*] Intentando con docker-compose...${NC}"
    if $SUDO docker-compose up -d --build; then
        DEPLOYED=true
    fi
fi

# Intento 2: docker compose v2 plugin
if [ "$DEPLOYED" = false ]; then
    if $SUDO docker compose version &> /dev/null; then
        echo -e "${CYAN}[*] Intentando con docker compose v2...${NC}"
        if $SUDO docker compose up -d --build; then
            DEPLOYED=true
        fi
    fi
fi

# Intento 3: Docker build y run nativo (100% infalible)
if [ "$DEPLOYED" = false ]; then
    echo -e "${YELLOW}[*] Desplegando directamente con Docker nativo (build + run)...${NC}"
    $SUDO docker build -t minecraft_ctf_dvwa .
    if $SUDO docker run -d --name minecraft_ctf_dvwa --restart unless-stopped -p 8080:8080 minecraft_ctf_dvwa; then
        DEPLOYED=true
    fi
fi

# Esperar inicialización
sleep 3

# Verificar si el contenedor está corriendo
if $SUDO docker ps | grep -q "minecraft_ctf_dvwa"; then
    echo ""
    echo -e "${PURPLE}======================================================================${NC}"
    echo -e "${GREEN}  ¡PLATAFORMA MINECRAFT CTF DESPLEGADA Y CORRIENDO CON ÉXITO!         ${NC}"
    echo -e "${PURPLE}======================================================================${NC}"
    echo -e "${YELLOW}  🌐 URL de Acceso Local : ${CYAN}http://localhost:8080${NC}"
    echo -e "${YELLOW}  🌐 URL en Red (VM)     : ${CYAN}http://$(hostname -I 2>/dev/null | awk '{print $1}'):8080${NC}"
    echo -e "${PURPLE}======================================================================${NC}"
    echo -e "${NC}  Dimensiones disponibles:${NC}"
    echo -e "   1. ${GREEN}Overworld${NC} (Fácil)   : Hierro -> Diamante -> Portal Nether"
    echo -e "   2. ${RED}Nether${NC}    (Medio)   : Oro -> Varas de Blaze -> Ender Pearl"
    echo -e "   3. ${PURPLE}The End${NC}   (Difícil) : Cristales -> Dragón -> Huevo de Dragón"
    echo -e "${PURPLE}======================================================================${NC}"
    echo -e "${CYAN}[i] Ver logs en vivo : ${YELLOW}$SUDO docker logs -f minecraft_ctf_dvwa${NC}"
    echo -e "${CYAN}[i] Detener          : ${YELLOW}$SUDO docker stop minecraft_ctf_dvwa${NC}"
    echo ""
else
    echo -e "${RED}[!] ERROR: El contenedor no pudo iniciar. Mostrando logs para depuración:${NC}"
    $SUDO docker logs minecraft_ctf_dvwa 2>&1
fi
