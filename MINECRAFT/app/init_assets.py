import os
import base64
import codecs
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'img')
DOCS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'docs')

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

IRON_FLAG = "FLAG{MINECRAFT_IRON_INGOT_C3S4R_X0R_M1N3D}"
PORTAL_FLAG = "FLAG{MINECRAFT_NETHER_PORTAL_METADATA_IGNITED}"


def rot13_base64(flag):
    return base64.b64encode(codecs.encode(flag, 'rot_13').encode()).decode('utf-8')


# 1. Crear Mapa de la Cueva con Esteganografía (Metadatos EXIF / Comentarios)
def create_stego_map():
    img_path = os.path.join(ASSETS_DIR, 'mapa_cueva.png')
    
    # Crear una imagen pixel-art estilo mapa de Minecraft (256x256)
    img = Image.new('RGB', (256, 256), color=(40, 30, 20))
    draw = ImageDraw.Draw(img)
    
    # Dibujar cuadrícula y cueva simulada
    for x in range(0, 256, 16):
        draw.line([(x, 0), (x, 256)], fill=(50, 40, 30), width=1)
    for y in range(0, 256, 16):
        draw.line([(0, y), (256, y)], fill=(50, 40, 30), width=1)
        
    # Dibujar vetas de mineral de hierro (color arena/óxido)
    draw.rectangle([80, 80, 112, 112], fill=(138, 120, 100), outline=(80, 70, 60))
    draw.rectangle([140, 160, 180, 190], fill=(138, 120, 100), outline=(80, 70, 60))
    draw.rectangle([16, 200, 48, 230], fill=(180, 140, 110), outline=(100, 80, 60)) # Veta de Hierro
    
    # Dibujar antorchas (puntos amarillos)
    draw.point((85, 85), fill=(255, 200, 0))
    draw.point((145, 165), fill=(255, 200, 0))

    # El mensaje secreto se calcula desde la flag canónica: Base64(ROT-13(flag)).
    # Así el dato cifrado nunca puede desincronizarse del flag real.
    stego_comment = (
        "PIXEL_METADATA_SECTION_STEVE_MINING_LOGS:\n"
        "Coordenadas cifradas con Cifrado Cesar (Rot-13) + Base64:\n"
        f"SECRETO_B64: {rot13_base64(IRON_FLAG)}\n"
        "Pista: Decodifica Base64 y luego aplica ROT-13 (Cifrado Cesar de 13 posiciones) para obtener la flag de Hierro."
    )
    
    # Guardar imagen con metadatos PngInfo
    target_info = PngInfo()
    target_info.add_text("Author", "Steve_Miner_Expert")
    target_info.add_text("Description", "Mapa topografico de la cueva en Y=16")
    target_info.add_text("Comment", stego_comment)

    img.save(img_path, "PNG", pnginfo=target_info)
    print(f"[+] Mapa con esteganografía generado en: {img_path}")

# 2. Crear archivo de planos del portal (Metadatos FOCA / ExifTool)
def create_portal_blueprints():
    doc_path = os.path.join(DOCS_DIR, 'planos_portal_nether.txt')
    content = (
        "===============================================================\n"
        " DOCUMENTO OFICIAL: PLANOS DE CONSTRUCCION DEL PORTAL AL NETHER \n"
        "===============================================================\n"
        "AUTOR: Steve_Maestro_Arquitecto\n"
        "FECHA_CREACION: 2026-08-22\n"
        "HERRAMIENTA_DE_DISENO: FOCA_Metadata_Analyzer_v3.4\n"
        "PROYECTO: Obsidian_Gateway_Activation\n"
        "\n"
        "INSTRUCCIONES DE ENSAMBLAJE:\n"
        "1. Colocar 10 bloques de Obsidiana en marco 4x5 (esquinas opcionales).\n"
        "2. Aplicar chispa con pedernal y acero en la base inferior.\n"
        "\n"
        "[METADATA_HEADER_INTERNAL]\n"
        "X-Portal-Security-Hash: 8f4a1c9b2e6d5a7f\n"
        f"X-Obsidian-Ignition-Key: {PORTAL_FLAG}\n"
        "X-Target-Dimension: NETHER_DIMENSION_ID_02\n"
        "===============================================================\n"
    )
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[+] Planos del portal generados en: {doc_path}")

# 3. Generar iconos SVG en pixel art para cada uno de los 9 ítems de Minecraft
def create_svg_icons():
    icons = {
        'iron_ingot.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="64" height="64" shape-rendering="crispEdges">
            <path fill="#2c2c2c" d="M10 6h12v2h2v12h-2v2H10v-2H8V8h2z"/>
            <path fill="#d8d8d8" d="M10 8h10v2h2v8h-2v2H10v-2H8v-8h2z"/>
            <path fill="#ffffff" d="M10 8h8v2h-8zM8 10h2v6H8z"/>
            <path fill="#a0a0a0" d="M18 10h2v8h-2zM10 18h8v2h-8z"/>
            <path fill="#e8e8e8" d="M10 10h8v8h-8z"/>
        </svg>''',
        'diamond.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="64" height="64" shape-rendering="crispEdges">
            <path fill="#1a4c54" d="M12 4h8v2h4v4h2v8h-2v4h-4v4h-8v-4H8v-4H6v-8h2V6h4z"/>
            <path fill="#4dedf4" d="M12 6h8v2h4v4h2v6h-2v4h-4v4h-8v-4H8v-4H6v-6h2V8h4z"/>
            <path fill="#ffffff" d="M12 6h6v2h-6zM8 8h4v2H8zM6 12h2v4H6zM14 10h4v4h-4z"/>
            <path fill="#2bb8c4" d="M18 6h2v2h4v4h2v6h-2v-4h-2v-2h-4zM8 16h2v4h4v4h6v-2h-4v-4H8z"/>
        </svg>''',
        'nether_portal.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="64" height="64" shape-rendering="crispEdges">
            <path fill="#120c1f" d="M4 2h24v28H4z"/>
            <path fill="#7e22ce" d="M10 6h12v20H10z"/>
            <path fill="#a855f7" d="M12 8h8v16h-8z"/>
            <path fill="#c084fc" d="M14 10h4v12h-4zM12 14h8v4h-8z"/>
            <path fill="#ffffff" opacity="0.8" d="M14 12h2v2h-2zM16 18h2v2h-2z"/>
        </svg>''',
        'gold_ingot.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="64" height="64" shape-rendering="crispEdges">
            <path fill="#4a3b00" d="M10 6h12v2h2v12h-2v2H10v-2H8V8h2z"/>
            <path fill="#facc15" d="M10 8h10v2h2v8h-2v2H10v-2H8v-8h2z"/>
            <path fill="#fef08a" d="M10 8h8v2h-8zM8 10h2v6H8z"/>
            <path fill="#ca8a04" d="M18 10h2v8h-2zM10 18h8v2h-8z"/>
            <path fill="#eab308" d="M10 10h8v8h-8z"/>
        </svg>''',
        'blaze_rod.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="64" height="64" shape-rendering="crispEdges">
            <path fill="#78350f" d="M22 4h4v4h-2v2h-2v2h-2v2h-2v2h-2v2h-2v2h-2v2h-2v2H8v4H4v-4h2v-2h2v-2h2v-2h2v-2h2v-2h2v-2h2v-2h2V8h2V4z"/>
            <path fill="#f59e0b" d="M22 6h2v2h-2v2h-2v2h-2v2h-2v2h-2v2h-2v2h-2v2H8v2H6v-2h2v-2h2v-2h2v-2h2v-2h2v-2h2V8h2V6z"/>
            <path fill="#fef08a" d="M22 6h1v1h-1zM18 10h1v1h-1zM14 14h1v1h-1zM10 18h1v1h-1zM6 22h1v1H6z"/>
        </svg>''',
        'ender_pearl.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="64" height="64" shape-rendering="crispEdges">
            <path fill="#042f2e" d="M10 4h12v2h4v4h2v12h-2v4h-4v2H10v-2H6v-4H4V10h2V6h4z"/>
            <path fill="#0d9488" d="M10 6h12v2h4v4h2v8h-2v4h-4v2H10v-2H6v-4H4v-8h2V8h4z"/>
            <path fill="#5eead4" d="M10 8h8v2h4v4h2v4h-2v-2h-2v-4h-4V8h-6z"/>
            <path fill="#ccfbf1" d="M12 10h4v2h2v2h-4v-2h-2z"/>
            <path fill="#115e59" d="M10 18h4v4h8v2h-8v-2H8v-4h2z"/>
        </svg>''',
        'end_crystal.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="64" height="64" shape-rendering="crispEdges">
            <path fill="#3b0764" d="M14 2h4v2h4v4h2v4h2v8h-2v4h-2v4h-4v2h-4v-2h-4v-4H6v-4H4v-8h2V8h2V4h4z"/>
            <path fill="#a855f7" d="M14 4h4v2h4v4h2v4h-2v-2h-2V8h-4V4h-2zM8 12h2v4H8zM22 12h2v4h-2zM12 24h8v2h-8z"/>
            <path fill="#e9d5ff" d="M14 10h4v12h-4zM10 14h12v4H10z"/>
            <path fill="#f43f5e" d="M14 14h4v4h-4z"/>
        </svg>''',
        'ender_dragon.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="64" height="64" shape-rendering="crispEdges">
            <path fill="#09090b" d="M2 10h8v4h12v-4h8v12h-4v4h-8v-4h-4v4H6v-4H2z"/>
            <path fill="#18181b" d="M4 12h6v2h12v-2h6v8h-2v2h-8v-4h-4v4H8v-2H4z"/>
            <path fill="#d946ef" d="M4 14h4v2H4zM24 14h4v2h-4z"/>
            <path fill="#ffffff" d="M5 14h2v1H5zM25 14h2v1h-2z"/>
        </svg>''',
        'dragon_egg.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="64" height="64" shape-rendering="crispEdges">
            <path fill="#030712" d="M12 4h8v2h4v4h2v12h-2v4h-4v2h-8v-2H8v-4H6V10h2V6h4z"/>
            <path fill="#1f1f2e" d="M12 6h8v2h4v4h2v8h-2v4h-4v2h-8v-2H8v-4H6v-8h2V8h4z"/>
            <path fill="#4a044e" d="M12 8h4v2h-4zM8 12h4v2H8zM20 16h4v4h-4zM10 20h4v2h-4z"/>
            <path fill="#c026d3" d="M14 10h2v2h-2zM10 14h2v2h-2zM22 18h2v2h-2z"/>
        </svg>''',
        'heart.svg': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="24" height="24" shape-rendering="crispEdges">
            <path fill="#000" d="M2 1h4v1h4V1h4v1h1v4h-1v2h-1v2h-2v2h-2v2H7v-2H5v-2H3V8H2V6H1V2h1z"/>
            <path fill="#e11d48" d="M2 2h3v1h1v2H2zM10 2h3v1h1v3h-1v1h-1v2h-2v2H7v-2H5V9H4V6h1V5h1V3h4z"/>
            <path fill="#ffffff" d="M2 2h2v2H2z"/>
        </svg>'''
    }
    for name, content in icons.items():
        file_path = os.path.join(ASSETS_DIR, name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
    print(f"[+] {len(icons)} Iconos SVG de Minecraft creados exitosamente.")

if __name__ == '__main__':
    create_stego_map()
    create_portal_blueprints()
    create_svg_icons()
