# -*- coding: utf-8 -*-
"""
Generador de Documentación en Formato Word (.docx)
Normas APA 7ma Edición
Proyecto: Plataforma Minecraft CTF (Estilo DVWA)
Seguridad en la Nube / Seguridad de Aplicaciones
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_document():
    doc = Document()

    # ---------------------------------------------------------
    # Configuración de Página según Normas APA 7ma Edición
    # Márgenes: 2.54 cm (1 pulgada) en los 4 lados
    # ---------------------------------------------------------
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = False

    # ---------------------------------------------------------
    # Paleta y Estilos Base: Times New Roman 12, Negro (#000000)
    # ---------------------------------------------------------
    BLACK = RGBColor(0, 0, 0)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = BLACK
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_before = Pt(0)
    normal_style.paragraph_format.space_after = Pt(6)

    # ---------------------------------------------------------
    # Funciones Auxiliares de Formato APA 7
    # ---------------------------------------------------------
    def add_p(text, indent=True, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=6):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        if indent:
            p.paragraph_format.first_line_indent = Inches(0.5)
        else:
            p.paragraph_format.first_line_indent = Inches(0.0)

        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = BLACK
        run.bold = bold
        run.italic = italic
        return p

    def add_h1(text):
        """Nivel 1 APA 7: Centrado, Negrilla, Mayúsculas y Minúsculas"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.first_line_indent = Inches(0.0)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = BLACK
        run.bold = True
        return p

    def add_h2(text):
        """Nivel 2 APA 7: Alineado a la izquierda, Negrilla, Mayúsculas y Minúsculas"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.first_line_indent = Inches(0.0)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = BLACK
        run.bold = True
        return p

    def add_h3(text):
        """Nivel 3 APA 7: Alineado a la izquierda, Negrilla y Cursiva"""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.first_line_indent = Inches(0.0)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = BLACK
        run.bold = True
        run.italic = True
        return p

    def add_code_block(code_text):
        """Bloque de código estilizado con recuadro y tipografía monoespaciada"""
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)

        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(r'<w:shd {} w:fill="F5F5F5"/>'.format(nsdecls('w')))
        borders = parse_xml(
            r'<w:tcBorders {}><w:top w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
            r'<w:left w:val="single" w:sz="12" w:space="0" w:color="333333"/>'
            r'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
            r'<w:right w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/></w:tcBorders>'.format(nsdecls('w'))
        )
        tcPr.append(shd)
        tcPr.append(borders)

        cp = cell.paragraphs[0]
        cp.paragraph_format.space_before = Pt(4)
        cp.paragraph_format.space_after = Pt(4)
        cp.paragraph_format.line_spacing = 1.0
        cp.paragraph_format.first_line_indent = Inches(0.0)
        crun = cp.add_run(code_text)
        crun.font.name = 'Consolas'
        crun.font.size = Pt(9.5)
        crun.font.color.rgb = BLACK

        # Espacio posterior a la tabla
        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_before = Pt(0)
        p_space.paragraph_format.space_after = Pt(4)
        p_space.paragraph_format.line_spacing = 1.0

    def add_figure_placeholder(fig_num, title, description, note):
        """Elemento de Figura según APA 7 con recuadro para captura de pantalla"""
        # Etiqueta de la figura (Negrilla)
        p_fig = doc.add_paragraph()
        p_fig.paragraph_format.space_before = Pt(10)
        p_fig.paragraph_format.space_after = Pt(2)
        p_fig.paragraph_format.line_spacing = 1.5
        p_fig.paragraph_format.first_line_indent = Inches(0.0)
        r_fig = p_fig.add_run(f"Figura {fig_num}")
        r_fig.font.name = 'Times New Roman'
        r_fig.font.size = Pt(12)
        r_fig.font.color.rgb = BLACK
        r_fig.bold = True

        # Título de la figura (Cursiva)
        p_title = doc.add_paragraph()
        p_title.paragraph_format.space_before = Pt(0)
        p_title.paragraph_format.space_after = Pt(6)
        p_title.paragraph_format.line_spacing = 1.5
        p_title.paragraph_format.first_line_indent = Inches(0.0)
        r_title = p_title.add_run(title)
        r_title.font.name = 'Times New Roman'
        r_title.font.size = Pt(12)
        r_title.font.color.rgb = BLACK
        r_title.italic = True

        # Recuadro placeholder para la captura de pantalla
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)

        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(r'<w:shd {} w:fill="FAFAFA"/>'.format(nsdecls('w')))
        borders = parse_xml(
            r'<w:tcBorders {}><w:top w:val="dashed" w:sz="6" w:space="0" w:color="888888"/>'
            r'<w:left w:val="dashed" w:sz="6" w:space="0" w:color="888888"/>'
            r'<w:bottom w:val="dashed" w:sz="6" w:space="0" w:color="888888"/>'
            r'<w:right w:val="dashed" w:sz="6" w:space="0" w:color="888888"/></w:tcBorders>'.format(nsdecls('w'))
        )
        tcPr.append(shd)
        tcPr.append(borders)

        cp = cell.paragraphs[0]
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_before = Pt(28)
        cp.paragraph_format.space_after = Pt(28)
        cp.paragraph_format.first_line_indent = Inches(0.0)

        r_box_title = cp.add_run(f"[ESPACIO RESERVADO PARA PANTALLAZO - FIGURA {fig_num}]\n")
        r_box_title.font.name = 'Times New Roman'
        r_box_title.font.size = Pt(11)
        r_box_title.font.color.rgb = BLACK
        r_box_title.bold = True

        r_box_desc = cp.add_run(description + "\n(Pegar o insertar la imagen aquí)")
        r_box_desc.font.name = 'Times New Roman'
        r_box_desc.font.size = Pt(10)
        r_box_desc.font.color.rgb = BLACK
        r_box_desc.italic = True

        # Nota de la figura
        p_note = doc.add_paragraph()
        p_note.paragraph_format.space_before = Pt(6)
        p_note.paragraph_format.space_after = Pt(12)
        p_note.paragraph_format.line_spacing = 1.5
        p_note.paragraph_format.first_line_indent = Inches(0.0)

        r_note_lbl = p_note.add_run("Nota. ")
        r_note_lbl.font.name = 'Times New Roman'
        r_note_lbl.font.size = Pt(10)
        r_note_lbl.font.color.rgb = BLACK
        r_note_lbl.italic = True

        r_note_txt = p_note.add_run(note)
        r_note_txt.font.name = 'Times New Roman'
        r_note_txt.font.size = Pt(10)
        r_note_txt.font.color.rgb = BLACK

    def add_apa_table(table_num, title, headers, data_rows, note=None):
        """Crea una tabla con formato estricto APA 7 (bordes horizontales, sin verticales)"""
        # Etiqueta de la tabla (Negrilla)
        p_num = doc.add_paragraph()
        p_num.paragraph_format.space_before = Pt(10)
        p_num.paragraph_format.space_after = Pt(2)
        p_num.paragraph_format.line_spacing = 1.5
        p_num.paragraph_format.first_line_indent = Inches(0.0)
        r_num = p_num.add_run(f"Tabla {table_num}")
        r_num.font.name = 'Times New Roman'
        r_num.font.size = Pt(12)
        r_num.font.color.rgb = BLACK
        r_num.bold = True

        # Título de la tabla (Cursiva)
        p_title = doc.add_paragraph()
        p_title.paragraph_format.space_before = Pt(0)
        p_title.paragraph_format.space_after = Pt(6)
        p_title.paragraph_format.line_spacing = 1.5
        p_title.paragraph_format.first_line_indent = Inches(0.0)
        r_title = p_title.add_run(title)
        r_title.font.name = 'Times New Roman'
        r_title.font.size = Pt(12)
        r_title.font.color.rgb = BLACK
        r_title.italic = True

        # Tabla
        table = doc.add_table(rows=len(data_rows) + 1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True

        # Estilizar Cabecera
        for col_idx, header_text in enumerate(headers):
            cell = table.cell(0, col_idx)
            tcPr = cell._tc.get_or_add_tcPr()
            # Borde superior y borde inferior en cabecera según APA
            borders = parse_xml(
                r'<w:tcBorders {}><w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
                r'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
                r'<w:left w:val="none"/><w:right w:val="none"/></w:tcBorders>'.format(nsdecls('w'))
            )
            tcPr.append(borders)
            cp = cell.paragraphs[0]
            cp.paragraph_format.space_before = Pt(4)
            cp.paragraph_format.space_after = Pt(4)
            cp.paragraph_format.line_spacing = 1.15
            cp.paragraph_format.first_line_indent = Inches(0.0)
            crun = cp.add_run(header_text)
            crun.font.name = 'Times New Roman'
            crun.font.size = Pt(10.5)
            crun.font.color.rgb = BLACK
            crun.bold = True

        # Estilizar Filas de Datos
        for row_idx, row_data in enumerate(data_rows):
            is_last_row = (row_idx == len(data_rows) - 1)
            for col_idx, cell_value in enumerate(row_data):
                cell = table.cell(row_idx + 1, col_idx)
                tcPr = cell._tc.get_or_add_tcPr()
                if is_last_row:
                    borders = parse_xml(
                        r'<w:tcBorders {}><w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
                        r'<w:top w:val="none"/><w:left w:val="none"/><w:right w:val="none"/></w:tcBorders>'.format(nsdecls('w'))
                    )
                else:
                    borders = parse_xml(
                        r'<w:tcBorders {}><w:bottom w:val="none"/><w:top w:val="none"/>'
                        r'<w:left w:val="none"/><w:right w:val="none"/></w:tcBorders>'.format(nsdecls('w'))
                    )
                tcPr.append(borders)
                cp = cell.paragraphs[0]
                cp.paragraph_format.space_before = Pt(3)
                cp.paragraph_format.space_after = Pt(3)
                cp.paragraph_format.line_spacing = 1.15
                cp.paragraph_format.first_line_indent = Inches(0.0)
                crun = cp.add_run(str(cell_value))
                crun.font.name = 'Times New Roman'
                crun.font.size = Pt(10)
                crun.font.color.rgb = BLACK

        # Nota de la tabla
        if note:
            p_note = doc.add_paragraph()
            p_note.paragraph_format.space_before = Pt(4)
            p_note.paragraph_format.space_after = Pt(12)
            p_note.paragraph_format.line_spacing = 1.5
            p_note.paragraph_format.first_line_indent = Inches(0.0)

            r_note_lbl = p_note.add_run("Nota. ")
            r_note_lbl.font.name = 'Times New Roman'
            r_note_lbl.font.size = Pt(10)
            r_note_lbl.font.color.rgb = BLACK
            r_note_lbl.italic = True

            r_note_txt = p_note.add_run(note)
            r_note_txt.font.name = 'Times New Roman'
            r_note_txt.font.size = Pt(10)
            r_note_txt.font.color.rgb = BLACK

    def add_reference_apa(authors, year, title, source, url=None):
        """Agrega una referencia en formato APA 7ma edición con sangría francesa (1.27 cm)"""
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)

        r_authors = p.add_run(f"{authors} ({year}). ")
        r_authors.font.name = 'Times New Roman'
        r_authors.font.size = Pt(12)
        r_authors.font.color.rgb = BLACK

        r_title = p.add_run(f"{title}. ")
        r_title.font.name = 'Times New Roman'
        r_title.font.size = Pt(12)
        r_title.font.color.rgb = BLACK
        r_title.italic = True

        r_source = p.add_run(source)
        r_source.font.name = 'Times New Roman'
        r_source.font.size = Pt(12)
        r_source.font.color.rgb = BLACK

        if url:
            r_url = p.add_run(f" {url}")
            r_url.font.name = 'Times New Roman'
            r_url.font.size = Pt(12)
            r_url.font.color.rgb = BLACK

    # =========================================================================
    # 1. PORTADA OFICIAL (NORMAS APA 7MA EDICIÓN - VERSIÓN ESTUDIANTIL/PROFESIONAL)
    # =========================================================================
    p_pre_space = doc.add_paragraph()
    p_pre_space.paragraph_format.space_before = Pt(40)
    p_pre_space.paragraph_format.line_spacing = 1.5

    p_cover_title = doc.add_paragraph()
    p_cover_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cover_title.paragraph_format.line_spacing = 1.5
    p_cover_title.paragraph_format.space_before = Pt(20)
    p_cover_title.paragraph_format.space_after = Pt(24)
    p_cover_title.paragraph_format.first_line_indent = Inches(0.0)
    r_cov_title = p_cover_title.add_run(
        "PLATAFORMA GAMIFICADA DE ENTRENAMIENTO EN CIBERSEGURIDAD Y SEGURIDAD EN LA NUBE:\n"
        "LABORATORIO CTF TIPO DVWA CON TEMÁTICA DE MINECRAFT"
    )
    r_cov_title.font.name = 'Times New Roman'
    r_cov_title.font.size = Pt(14)
    r_cov_title.font.color.rgb = BLACK
    r_cov_title.bold = True

    p_cover_sub = doc.add_paragraph()
    p_cover_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cover_sub.paragraph_format.line_spacing = 1.5
    p_cover_sub.paragraph_format.space_before = Pt(0)
    p_cover_sub.paragraph_format.space_after = Pt(36)
    p_cover_sub.paragraph_format.first_line_indent = Inches(0.0)
    r_cov_sub = p_cover_sub.add_run(
        "Documentación Técnica y Arquitectónica de Despliegue, Infraestructura en Contenedores\n"
        "y Análisis Pedagógico de Vulnerabilidades Web"
    )
    r_cov_sub.font.name = 'Times New Roman'
    r_cov_sub.font.size = Pt(12)
    r_cov_sub.font.color.rgb = BLACK
    r_cov_sub.italic = True

    p_cover_authors = doc.add_paragraph()
    p_cover_authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cover_authors.paragraph_format.line_spacing = 1.5
    p_cover_authors.paragraph_format.space_before = Pt(20)
    p_cover_authors.paragraph_format.space_after = Pt(6)
    p_cover_authors.paragraph_format.first_line_indent = Inches(0.0)
    r_cov_aut_lbl = p_cover_authors.add_run("Desarrolladores y Autores Oficiales del Proyecto:\n")
    r_cov_aut_lbl.font.name = 'Times New Roman'
    r_cov_aut_lbl.font.size = Pt(12)
    r_cov_aut_lbl.font.color.rgb = BLACK
    r_cov_aut_lbl.bold = True
    r_cov_aut_names = p_cover_authors.add_run("Thorfinn777, Martyn777, Sassyjack777\n\nEstudiante / Presentador del Proyecto")
    r_cov_aut_names.font.name = 'Times New Roman'
    r_cov_aut_names.font.size = Pt(12)
    r_cov_aut_names.font.color.rgb = BLACK

    p_cover_inst = doc.add_paragraph()
    p_cover_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cover_inst.paragraph_format.line_spacing = 1.5
    p_cover_inst.paragraph_format.space_before = Pt(30)
    p_cover_inst.paragraph_format.space_after = Pt(0)
    p_cover_inst.paragraph_format.first_line_indent = Inches(0.0)
    r_cov_inst = p_cover_inst.add_run(
        "Facultad de Ingeniería de Sistemas y Computación\n"
        "Área de Énfasis: Seguridad en la Nube / Seguridad de Aplicaciones (9.° Semestre)\n"
        "Docente de Cátedra: Asesor de Seguridad en la Nube\n"
        "Año Académico 2026"
    )
    r_cov_inst.font.name = 'Times New Roman'
    r_cov_inst.font.size = Pt(12)
    r_cov_inst.font.color.rgb = BLACK

    doc.add_page_break()

    # =========================================================================
    # RESUMEN Y PALABRAS CLAVE
    # =========================================================================
    add_h1("Resumen")
    add_p(
        "El presente documento expone la memoria técnica y arquitectónica de la plataforma interactiva de entrenamiento "
        "en ciberseguridad denominada Minecraft CTF Lab. Esta herramienta ha sido concebida bajo la filosofía de las aplicaciones "
        "web deliberadamente vulnerables, semejante al estándar pedagógico de DVWA (Damn Vulnerable Web Application), "
        "integrando un modelo de gamificación integral fundamentado en el universo de Minecraft. La plataforma se encuentra "
        "empaquetada y orquestada mediante contenedores Docker, optimizada minuciosamente para ejecutarse en entornos de "
        "virtualización restringidos (VirtualBox sobre Kali Linux con perfiles de 4 GB de memoria RAM y 2 procesadores virtuales). "
        "El diseño formativo abarca nueve desafíos de seguridad informática categorizados en tres dimensiones progresivas: "
        "Overworld (nivel introductorio), Nether (nivel intermedio) y The End (nivel avanzado y combate final). Dichos desafíos "
        "permiten evaluar competencias clave del estándar OWASP Top 10, tales como inyecciones de código SQL (SQLi), ejecución "
        "remota de comandos (Command Injection), cross-site scripting almacenado (Stored XSS), carga arbitraria de ficheros, "
        "enumeración de Active Directory con PowerView, esteganografía forense y manipulación de parámetros de control de acceso. "
        "Asimismo, se detallan los requisitos de instalación, el script de automatización de despliegue con tolerancia a fallos "
        "y los mecanismos de contención que garantizan la integridad del sistema anfitrión sin revelar las soluciones específicas."
    )

    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.line_spacing = 1.5
    p_kw.paragraph_format.space_before = Pt(6)
    p_kw.paragraph_format.space_after = Pt(12)
    p_kw.paragraph_format.left_indent = Inches(0.5)
    r_kw_lbl = p_kw.add_run("Palabras clave: ")
    r_kw_lbl.font.name = 'Times New Roman'
    r_kw_lbl.font.size = Pt(12)
    r_kw_lbl.font.color.rgb = BLACK
    r_kw_lbl.bold = True
    r_kw_lbl.italic = True

    r_kw_txt = p_kw.add_run(
        "Ciberseguridad, Seguridad en la Nube, Docker, Capture The Flag (CTF), Gamificación, OWASP Top 10, "
        "Inyección SQL, Cross-Site Scripting, Ejecución Remota de Código, VirtualBox."
    )
    r_kw_txt.font.name = 'Times New Roman'
    r_kw_txt.font.size = Pt(12)
    r_kw_txt.font.color.rgb = BLACK

    doc.add_page_break()

    # =========================================================================
    # 1. INTRODUCCIÓN Y JUSTIFICACIÓN
    # =========================================================================
    add_h1("1. Introducción y Justificación")
    add_p(
        "En el contexto actual de la ingeniería de software y la computación en la nube, la seguridad de las aplicaciones web "
        "se ha posicionado como un pilar crítico en la mitigación de vectores de ataque e incidentes de fuga de datos. La rápida "
        "adopción de arquitecturas basadas en microservicios, APIs REST y contenedores exige que los futuros profesionales de "
        "tecnologías de la información no solo comprendan los principios teóricos de la seguridad de la información, sino que cuenten "
        "con habilidades analíticas y de auditoría práctica en entornos realistas y controlados."
    )
    add_p(
        "Tradicionalmente, la enseñanza de la ciberseguridad se ha visto limitada por la complejidad que representa el despliegue "
        "de plataformas de laboratorio en equipos de cómputo personales o máquinas virtuales universitarias. Herramientas formativas "
        "clásicas como DVWA (Damn Vulnerable Web Application), bWAPP o OWASP Juice Shop, aunque sumamente completas, suelen carecer "
        "de una narrativa de juego envolvente o conllevan un consumo desproporcionado de recursos de memoria y procesamiento, "
        "generando bloqueos en hipervisores de virtualización convencionales. Con base en esta problemática, el presente proyecto "
        "introduce el Minecraft CTF Lab, una plataforma interactiva que fusiona la rigurosidad técnica de los estándares internacionales "
        "de seguridad web con la estética inmersiva del videojuego Minecraft."
    )
    add_p(
        "La justificación metodológica de este proyecto se fundamenta en la teoría de la gamificación aplicada al aprendizaje técnico. "
        "Al sustituir los menús genéricos de vulnerabilidades por las dimensiones canónicas de Minecraft (el supramundo u Overworld, "
        "el inframundo o Nether y la dimensión sombría de The End), el estudiante experimenta una curva de progresión natural: "
        "comienza obteniendo materiales primarios (hierro, diamante y obsidiana) a través de retos elementales, continúa comerciando "
        "y forjando objetos en el inframundo mediante ataques de nivel intermedio, y culmina en una batalla contra el dragón del fin mediante "
        "la explotación de fallos avanzados del sistema operativo y la enumeración de Active Directory para localizar recursos compartidos."
    )

    # =========================================================================
    # 2. OBJETIVOS DEL PROYECTO
    # =========================================================================
    add_h1("2. Objetivos del Proyecto")
    add_h2("2.1 Objetivo General")
    add_p(
        "Diseñar, implementar y documentar una plataforma de entrenamiento en ciberseguridad y seguridad en la nube tipo CTF "
        "(Capture The Flag) con temática de Minecraft, empaquetada en contenedores Docker y optimizada para operar de manera eficiente "
        "en entornos de virtualización con recursos limitados, facilitando el aprendizaje práctico de auditoría de aplicaciones web sin "
        "comprometer la estabilidad del sistema anfitrión."
    )
    add_h2("2.2 Objetivos Específicos")
    add_p(
        "a) Construir una arquitectura contenerizada y modular basada en Python 3.11, Flask y Gunicorn, parametrizada para "
        "no exceder 512 MB de memoria RAM y 1.5 procesadores virtuales, permitiendo su ejecución fluida en máquinas virtuales de Kali Linux."
    )
    add_p(
        "b) Desarrollar nueve desafíos de seguridad informática distribuidos en tres fases progresivas (Overworld, Nether y The End), "
        "cubriendo vectores de vulnerabilidad representativos de las categorías OWASP Top 10 (SQL Injection, Stored XSS, OS Command Injection, "
        "Arbitrary File Upload, enumeración de Active Directory con PowerView, esteganografía y control de acceso roto)."
    )
    add_p(
        "c) Implementar un motor de contención y aislamiento (Process Sandbox Runner) con cuotas estrictas de CPU, memoria y descriptores "
        "de ficheros mediante llamadas nativas al kernel (rlimit), mitigando riesgos de denegación de servicio accidental o saturación del host."
    )
    add_p(
        "d) Programar un agente simulado no interactivo (PiglinGuardBot) que reproduzca el comportamiento de un usuario administrativo "
        "con credenciales privilegiadas, permitiendo la explotación y validación de ataques de Cross-Site Scripting Almacenado sin la "
        "sobrecarga de un navegador headless."
    )
    add_p(
        "e) Automatizar el ciclo de vida del despliegue mediante un script de orquestación en Bash (deploy.sh) provisto de detección de "
        "permisos y una estrategia de respaldo en cascada (docker-compose v1, docker compose v2 y Docker nativo)."
    )

    # =========================================================================
    # 3. ALCANCE Y POLÍTICAS DE USO ÉTICO
    # =========================================================================
    add_h1("3. Alcance, Público Objetivo y Políticas de Uso Ético")
    add_h2("3.1 Alcance del Laboratorio")
    add_p(
        "El laboratorio está diseñado para ejecutarse en entornos locales de prueba, específicamente sobre la distribución Kali Linux "
        "alojada en el hipervisor Oracle VM VirtualBox. Su alcance contempla la resolución integral de los desafíos mediante navegadores "
        "web estándar (Mozilla Firefox, Google Chrome) y herramientas de análisis de seguridad ampliamente utilizadas por profesionales "
        "de aseguramiento de la información (Burp Suite Community Edition, cURL, ExifTool y terminal de comandos)."
    )
    add_h2("3.2 Público Objetivo")
    add_p(
        "La plataforma está orientada a estudiantes universitarios de ingeniería de sistemas, ingeniería informática, participantes de "
        "semilleros de investigación en ciberseguridad, analistas de seguridad junior y docentes universitarios que requieran un entorno "
        "didáctico autodesplegable, reproducible y de rápida evaluación práctica."
    )
    add_h2("3.3 Políticas de Uso Ético y Responsabilidad")
    add_p(
        "Las vulnerabilidades modeladas en esta plataforma tienen un propósito estrictamente pedagógico y académico. Todo el código "
        "vulnerable se encuentra encapsulado en el contenedor Docker bajo usuarios no privilegiados. Se prohíbe explícitamente el uso de "
        "las técnicas, patrones o conceptos aquí tratados contra sistemas informáticos externos, redes corporativas o plataformas de "
        "producción sin la debida autorización legal y por escrito."
    )
    add_h2("3.4 Formato Estándar de Banderas (Flags)")
    add_p(
        "Para mantener la rigurosidad y compatibilidad con plataformas de evaluación competitiva, todas las recompensas criptográficas "
        "u objetivos del laboratorio siguen un formato estándar unificado: Flag{...}. El sistema de validación interno de la aplicación web "
        "ha sido diseñado con tolerancia a mayúsculas y minúsculas (FLAG{...} o Flag{...}) para optimizar la experiencia del participante. "
        "A modo de ejemplo ilustrativo, una bandera típica adopta la estructura Flag{MINECRAFT_IRON_INGOT_C3S4R_X0R_M1N3D}."
    )

    # =========================================================================
    # 4. ARQUITECTURA DEL SISTEMA E INFRAESTRUCTURA DE CONTENEDORES
    # =========================================================================
    add_h1("4. Arquitectura del Sistema e Infraestructura de Contenedores")
    add_h2("4.1 Visión General de la Arquitectura")
    add_p(
        "La arquitectura del sistema responde a un esquema de aplicación web desacoplada en tres capas principales: capa de presentación "
        "(HTML5 con estética HUD de Minecraft, hojas de estilo CSS modulares y JavaScript asíncrono vanilla), capa lógica de backend "
        "(microframework Flask ejecutado sobre el servidor de aplicaciones WSGI Gunicorn en Python 3.11) y capa de persistencia "
        "(base de datos embebida SQLite3). Todo el ecosistema opera confinado en un contenedor Docker con una red puente (bridge network) "
        "aislada, exponiendo únicamente el puerto TCP 8080."
    )

    add_apa_table(
        1,
        "Capas y componentes de la arquitectura de Minecraft CTF Lab",
        ["Capa Arquitectónica", "Tecnología Principal", "Función en el Sistema"],
        [
            ["Presentación", "HTML5, CSS3, JS Vanilla", "Renderizado de la interfaz visual HUD, formularios y feedback interactivo."],
            ["Servidor WSGI", "Gunicorn 22.0.0", "Gestor de procesos de alto rendimiento con 2 workers y 2 threads concurrentes."],
            ["Lógica de Negocio", "Flask 3.0.3, Werkzeug", "Enrutamiento web, controladores de desafíos, sesiones y validación de flags."],
            ["Persistencia", "SQLite 3 (Modo WAL)", "Almacenamiento liviano de cofres, ofertas de trueque, tokens y telemetría."],
            ["Simulación de Auditoría", "PiglinGuardBot", "Hilo en background que simula la interacción de un administrador con cookies."],
            ["Ejecución Segura", "Process Sandbox Runner", "Aislamiento de comandos de usuario con cuotas de kernel (rlimit)."],
            ["Contenedorización", "Docker Engine 3.8", "Aislamiento de sistema de archivos, namespaces, cgroups y red bridge."]
        ],
        "Elaboración propia con base en el código fuente del proyecto."
    )

    add_h2("4.2 Contenedorización con Docker y Aislamiento de Red")
    add_p(
        "El empaquetado del sistema se realiza a través de un archivo Dockerfile multicapa que toma como imagen base python:3.11-slim. "
        "Esta variante ligera de Debian minimiza la superficie de ataque al no incluir utilidades innecesarias del sistema operativo. "
        "Dentro del contenedor se crea un usuario de sistema dedicado denominado mcuser (con shell /usr/sbin/nologin), garantizando "
        "que el servidor web opere estrictamente bajo el principio de menor privilegio y no con permisos de superusuario (root)."
    )
    add_p(
        "A nivel de red, el archivo docker-compose.yml define una red personalizada bridge denominada ctf_net. Esta configuración evita "
        "que el contenedor interactúe indiscriminadamente con otros servicios de la máquina anfitriona, limitando la exposición al "
        "mapeo del puerto 8080 en la interfaz loopback o la dirección IP asignada a la máquina virtual."
    )

    add_h2("4.3 Dimensionamiento y Perfil de Optimización para VirtualBox")
    add_p(
        "Uno de los mayores desafíos en laboratorios académicos de seguridad de aplicaciones es el impacto en el rendimiento de los hipervisores. "
        "Cuando un contenedor Docker consume el 100% de la CPU o satura la memoria física, la interfaz gráfica del sistema operativo "
        "anfitrión (como el entorno XFCE o LightDM en Kali Linux) se congela, obligando a reiniciar la máquina virtual y perdiendo el "
        "progreso del participante. Para mitigar este riesgo, la plataforma integra un perfil de afinación exhaustivo:"
    )
    add_p(
        "1. Restricción estricta de CPU: Se parametriza cpus: '1.50' y pids_limit: 128 en la definición del contenedor. Al reservar "
        "al menos 0.5 vCPUs exclusivamente para el anfitrión, Kali Linux mantiene suficiente holgura de cómputo para ejecutar "
        "Firefox, Burp Suite y las herramientas de terminal sin experimentar microbloqueos."
    )
    add_p(
        "2. Límite y reserva de memoria RAM: Se establece un límite máximo de 512 MB (mem_limit: 512m) y una memoria reservada de "
        "128 MB (mem_reservation: 128m). En condiciones de reposo, el microservicio Flask y Gunicorn consumen aproximadamente 80 MB, "
        "dejando más de 3.5 GB libres en una máquina virtual de 4 GB para el software de pentesting del usuario."
    )
    add_p(
        "3. Gunicorn Preload y recolección de memoria (Copy-on-Write): En el comando de arranque del Dockerfile se emplea el modificador "
        "--preload. Esto permite que el proceso maestro importe la aplicación y la comparta en memoria física con los workers hijos mediante "
        "Copy-on-Write (COW). Adicionalmente, los parámetros --max-requests 500 y --max-requests-jitter 50 reinician periódicamente "
        "los workers de manera asíncrona, eliminando cualquier potencial fuga de memoria (memory leak) sin provocar caídas de servicio."
    )
    add_p(
        "4. Base de datos SQLite optimizada para I/O virtual: Los discos virtuales en VirtualBox presentan alta latencia en operaciones "
        "sincrónicas de entrada/salida (fsync). En el módulo database.py se aplican las directivas PRAGMA journal_mode = WAL (Write-Ahead Logging) "
        "y PRAGMA synchronous = NORMAL. Esto permite lecturas y escrituras concurrentes sin bloqueo de cerrojos, almacenando tablas "
        "temporales en RAM (temp_store = MEMORY) y reduciendo el desgaste del disco virtual."
    )

    add_apa_table(
        2,
        "Parámetros de optimización del contenedor para máquinas virtuales",
        ["Parámetro de Configuración", "Valor Asignado", "Objetivo de Rendimiento y Estabilidad"],
        [
            ["Límite de Procesador (cpus)", "1.50 vCPUs", "Garantiza 0.5 núcleos libres para la GUI de Kali y Burp Suite."],
            ["Límite de Memoria (mem_limit)", "512 MB", "Evita que un consumo descontrolado agote la RAM de la VM."],
            ["Reserva de Memoria (mem_reservation)", "128 MB", "Asegura memoria mínima garantizada para el contenedor."],
            ["Límite de Procesos (pids_limit)", "128", "Protección contra ataques locales de saturación (Fork Bombs)."],
            ["Modelo de Workers de Gunicorn", "2 workers, 2 threads", "Alineado con los 2 núcleos de CPU de la máquina virtual."],
            ["Reciclaje de Workers", "500 reqs (+/- 50)", "Mitiga fugas de memoria y fragmentación de montículo."],
            ["Journal SQLite", "WAL (Write-Ahead Logging)", "Elimina contención de I/O y llamadas costosas a fsync en disco."]
        ],
        "Configuración validada en entornos virtuales con Kali Linux 2024/2025."
    )

    add_h2("4.4 Subsistemas Especializados del Laboratorio")
    add_h3("4.4.1 Bot Automatizado de Auditoría (PiglinGuardBot)")
    add_p(
        "Para los retos de Cross-Site Scripting Almacenado (Stored XSS) convencionales, los laboratorios tradicionales requieren levantar "
        "un navegador web en modo desatendido (como Puppeteer o Selenium con Google Chrome headless). Sin embargo, un navegador headless "
        "consume más de 400 MB de memoria RAM por sí solo, haciendo inviable su ejecución en una máquina virtual de bajos recursos. "
        "En este proyecto, se diseñó el módulo bot.py, el cual implementa la clase PiglinGuardBot:"
    )
    add_p(
        "Este agente opera como un hilo demonio (threading.Thread) que se dispara automáticamente cada vez que un participante envía "
        "una oferta de trueque. El bot consulta el tablón de ofertas portando una cookie de sesión con privilegios administrativos "
        "(piglin_session_role=piglin_treasurer y piglin_gold_vault_token). Al detectar patrones de carga útil destinados a canales "
        "de exfiltración, el bot ejecuta la petición HTTP reproduciendo con fidelidad la conducta de una víctima humana, registrando "
        "el resultado en la base de datos SQLite compartida sin consumir recursos gráficos de la máquina virtual."
    )

    add_h3("4.4.2 Ejecutor Aislado con Límites de Kernel (Process Sandbox Runner)")
    add_p(
        "Para los desafíos que involucran ejecución de comandos y subida de archivos ejecutables, la plataforma implementa el módulo "
        "sandbox.py (run_sandboxed). Este subsistema encapsula las llamadas a subprocess.Popen aplicando restricciones estrictas "
        "a través del módulo POSIX resource mediante la función setrlimit:"
    )
    add_p(
        "1. Límite de tiempo de CPU (RLIMIT_CPU): Máximo 2 segundos de CPU por proceso hijo, cancelando de inmediato scripts con bucles infinitos.\n"
        "2. Límite de tamaño de archivo (RLIMIT_FSIZE): Máximo 1 MB, evitando que un script llene el almacenamiento del contenedor.\n"
        "3. Límite de descriptores de fichero (RLIMIT_NOFILE): Máximo 32 archivos simultáneos abiertos.\n"
        "4. Semáforo acotado de concurrencia: Limita a un único proceso hijo en ejecución concurrente mediante BoundedSemaphore(1), "
        "garantizando que solicitudes simultáneas no saturen el microprocesador."
    )

    add_h3("4.4.3 Bootstrapper e Inicializador Dinámico de Activos")
    add_p(
        "Para reducir el tiempo de carga durante la ejecución y evitar cálculos repetitivos en tiempo de ejecución, el proyecto incorpora "
        "el módulo bootstrap.py e init_assets.py. Estos scripts se ejecutan durante la fase de compilación del Dockerfile mediante python "
        "-m compileall y python /app/bootstrap.py, pregenerando la base de datos con sus tablas estructuradas, creando las imágenes "
        "PNG con metadatos esteganográficos mediante la biblioteca Pillow y generando los diez iconos SVG en formato pixel-art."
    )

    # =========================================================================
    # 5. REQUISITOS DEL SISTEMA E INSTALACIONES PREVIAS
    # =========================================================================
    add_h1("5. Requisitos del Sistema e Instalaciones de Software")
    add_p(
        "Para poner en funcionamiento el laboratorio de manera exitosa, es fundamental garantizar la correcta instalación y "
        "configuración de las herramientas requeridas tanto en el sistema operativo anfitrión como en la máquina virtual de auditoría. "
        "A continuación, se detalla el procedimiento de instalación ordenado paso a paso con sus comandos respectivos."
    )

    add_h2("5.1 Requisitos de Hardware del Host e Hipervisor")
    add_p(
        "El hipervisor recomendado es Oracle VM VirtualBox (versión 7.0 o superior) ejecutándose sobre un procesador compatible con "
        "virtualización por hardware (Intel VT-x o AMD-V). La máquina virtual destinada a Kali Linux debe configurarse con los siguientes "
        "parámetros mínimos:"
    )
    add_p(
        "• Memoria Base: 4096 MB (4 GB de RAM).\n"
        "• Procesadores: 2 vCPUs asignadas.\n"
        "• Almacenamiento Dinámico: Mínimo 25 GB de espacio en disco.\n"
        "• Adaptador de Red: Conexión mediante Modo Adaptador Puente (Bridged) o Red NAT con reenvío de puertos.\n"
        "• Aceleración Gráfica: Habilitar aceleración 3D con 128 MB de memoria de vídeo (VRAM)."
    )

    add_h2("5.2 Sistema Operativo Base (Kali Linux)")
    add_p(
        "Se recomienda utilizar la distribución oficial Kali Linux 2024.x o superior en arquitectura x86_64, ya que incorpora de forma "
        "nativa el repositorio de herramientas de seguridad ofensiva requeridas para interactuar con los desafíos del CTF."
    )

    add_h2("5.3 Instalación del Motor Docker y Docker Compose")
    add_p(
        "En la consola de terminal de Kali Linux, se deben actualizar los repositorios e instalar los paquetes oficiales de docker.io "
        "y docker-compose mediante el gestor de paquetes APT. Ejecute las siguientes instrucciones en terminal:"
    )

    add_code_block(
        "# 1. Actualizar la lista de paquetes del sistema operativo\n"
        "sudo apt update\n\n"
        "# 2. Instalar Docker Engine y el plugin Docker Compose\n"
        "sudo apt install -y docker.io docker-compose\n\n"
        "# 3. Habilitar y arrancar el demonio del servicio Docker\n"
        "sudo systemctl enable docker --now\n\n"
        "# 4. Comprobar que el servicio Docker se encuentre en estado activo (running)\n"
        "sudo systemctl status docker --no-pager"
    )

    add_p(
        "Para evitar la necesidad de anteponer el comando sudo en cada instrucción de Docker, es recomendable agregar el usuario "
        "actual al grupo docker del sistema y aplicar los cambios sin reiniciar la sesión:"
    )

    add_code_block(
        "# Agregar el usuario actual (ej. kali) al grupo docker\n"
        "sudo usermod -aG docker $USER\n\n"
        "# Recargar la pertenencia de grupos en la sesión activa\n"
        "newgrp docker"
    )

    add_h2("5.4 Dependencias a Nivel de Sistema Operativo dentro del Contenedor")
    add_p(
        "El contenedor requiere utilidades de red, diagnósticos y análisis forense que se instalan durante la construcción de la imagen. "
        "Dichos paquetes están declarados en el Dockerfile y son aprovisionados mediante apt-get:"
    )
    add_p(
        "• sqlite3: Motor de base de datos relacional para consultas de verificación e inicialización.\n"
        "• curl y net-tools: Herramientas de conectividad de red y resolución de peticiones HTTP.\n"
        "• procps: Utilidades para el monitoreo y gestión de procesos del sistema operativo.\n"
        "• libimage-exiftool-perl: Motor forense de lectura y escritura de metadatos EXIF en formatos de imagen y documentos."
    )

    add_h2("5.5 Instalación de Dependencias de Python (requirements.txt)")
    add_p(
        "La lógica del servidor se apoya en bibliotecas oficiales del lenguaje Python (versión 3.11). Estas librerías se instalan "
        "automáticamente dentro del contenedor a través de pip:"
    )

    add_code_block(
        "Flask==3.0.3        # Microframework web para el enrutamiento y plantillas Jinja2\n"
        "Pillow==10.4.0      # Manipulación de imágenes digitales y metadatos esteganográficos\n"
        "requests==2.32.3    # Cliente HTTP síncrono empleado por el bot interno de auditoría\n"
        "gunicorn==22.0.0    # Servidor de aplicaciones WSGI para producción concurrente\n"
        "Werkzeug==3.0.3    # Conjunto de utilidades de desarrollo web y control seguro de archivos"
    )

    add_h2("5.6 Herramientas de Auditoría Recomendadas en la Máquina Anfitriona")
    add_p(
        "Para interactuar con la plataforma, el participante debe disponer de las herramientas estándar preinstaladas en Kali Linux:"
    )
    add_p(
        "• Mozilla Firefox: Navegador web con herramientas para desarrolladores (F12) para inspeccionar almacenamiento local, cookies y peticiones de red.\n"
        "• Burp Suite Community Edition: Proxy de interceptación para capturar y modificar cabeceras HTTP, cookies y parámetros de entrada.\n"
        "• ExifTool: Utilidad de línea de comandos para inspeccionar metadatos ocultos en archivos multimedia y documentos.\n"
        "• cURL: Herramienta de transferencia de datos con sintaxis URL para enviar peticiones HTTP personalizadas."
    )

    # =========================================================================
    # 6. DESPLIEGUE, PUESTA EN MARCHA Y OPERACIÓN
    # =========================================================================
    add_h1("6. Despliegue, Puesta en Marcha y Operación")
    add_p(
        "La plataforma ofrece un flujo de despliegue completamente automatizado que minimiza los errores de configuración "
        "manual y garantiza una experiencia de usuario inmediata."
    )

    add_h2("6.1 Automatización con el Script deploy.sh")
    add_p(
        "El proyecto incluye un script en Bash denominado deploy.sh que implementa una estrategia de despliegue inteligente "
        "con triple nivel de tolerancia a fallos (fallback). Antes de su primera ejecución en Linux, se recomienda normalizar "
        "los saltos de línea (en caso de haber sido transferido desde Windows) y asignarle permisos de ejecución:"
    )

    add_code_block(
        "# 1. Posicionarse en el directorio del proyecto\n"
        "cd /ruta/hacia/MINECRAFT\n\n"
        "# 2. Eliminar potenciales caracteres de retorno de carro de Windows (\\r)\n"
        "sed -i 's/\\r$//' deploy.sh\n\n"
        "# 3. Otorgar permisos de ejecución al script\n"
        "chmod +x deploy.sh\n\n"
        "# 4. Iniciar el despliegue automatizado\n"
        "./deploy.sh"
    )

    add_p(
        "El flujo de ejecución del script deploy.sh comprende cuatro fases automáticas:\n"
        "1. Detección de privilegios: Valida si el usuario actual pertenece al grupo docker o si se requiere elevar privilegios con sudo.\n"
        "2. Verificación del demonio Docker: Si el servicio Docker no se encuentra activo, lo inicia automáticamente mediante systemctl.\n"
        "3. Limpieza de contenedores huérfanos: Detiene y elimina cualquier contenedor previo con el nombre minecraft_ctf_dvwa para evitar conflictos de puerto.\n"
        "4. Estrategia de construcción en cascada: Intenta levantar el laboratorio mediante docker-compose clásico; si no está disponible, "
        "utiliza el plugin docker compose v2; si ambos fallan, recurre a docker build y docker run nativo con asignación explícita de recursos."
    )

    add_h2("6.2 Despliegue Declarativo con Docker Compose")
    add_p(
        "En caso de preferir una ejecución manual directa mediante Docker Compose, el usuario puede invocar:"
    )

    add_code_block(
        "# Levantar y construir el contenedor en segundo plano (daemon)\n"
        "docker-compose up -d --build\n\n"
        "# O mediante la sintaxis moderna de Compose V2:\n"
        "docker compose up -d --build"
    )

    add_h2("6.3 Verificación de Conectividad y Monitoreo de Registros")
    add_p(
        "Una vez completado el despliegue, la plataforma queda accesible en la siguiente dirección URL desde el navegador de Kali Linux:\n"
        "http://localhost:8080 (o mediante la IP de la máquina virtual http://<IP_DE_LA_VM>:8080 desde el sistema anfitrión).\n"
        "Para monitorear los registros del contenedor en tiempo real o detener la ejecución del servicio, se emplean los siguientes comandos:"
    )

    add_code_block(
        "# Visualizar los registros (logs) del contenedor en vivo\n"
        "docker logs -f minecraft_ctf_dvwa\n\n"
        "# Detener la ejecución del contenedor\n"
        "docker stop minecraft_ctf_dvwa\n\n"
        "# Reiniciar el servicio en caso de ser necesario\n"
        "docker start minecraft_ctf_dvwa"
    )

    # =========================================================================
    # 7. MODELO DE DATOS Y GESTIÓN DEL ESTADO
    # =========================================================================
    add_h1("7. Modelo de Datos y Gestión del Estado de la Aplicación")
    add_p(
        "La persistencia y el seguimiento del progreso del usuario se gestionan mediante una combinación de bases de datos relacionales "
        "embebidas (SQLite3) y el almacenamiento criptográfico de sesiones del lado del cliente mediante Flask Sessions."
    )

    add_h2("7.1 Esquema Relacional de Base de Datos SQLite")
    add_p(
        "El módulo database.py inicializa cuatro tablas relacionales que dan soporte a los desafíos y a la auditoría del laboratorio:"
    )

    add_apa_table(
        3,
        "Estructura relacional de las tablas en la base de datos de Minecraft CTF",
        ["Tabla", "Campos y Tipos", "Descripción y Propósito en el Laboratorio"],
        [
            ["villager_chests", "id (INT PK), chest_name (TEXT), location (TEXT), depth_level (INT), secret_loot (TEXT), is_locked (INT)",
             "Almacena los cofres de la aldea del Overworld. El cofre del herrero contiene la reliquia y posee el campo is_locked=1."],
            ["piglin_trade_offers", "id (INT PK), player_name (TEXT), offered_item (TEXT), note_to_piglin (TEXT), status (TEXT), created_at (TIMESTAMP)",
             "Tablón público de trueques con Piglins en el Nether. La columna note_to_piglin es renderizada sin sanitización."],
            ["end_crystals", "id (INT PK), pillar_id (TEXT), frequency (INT), shield_status (TEXT), health (INT)",
             "Telemetría de los cuatro cristales de curación del Ender Dragón (Alpha, Beta, Gamma, Omega) en la dimensión The End."],
            ["stolen_tokens", "id (INT PK), offer_id (INT), captured_data (TEXT), captured_at (TIMESTAMP)",
             "Registro de auditoría donde el bot PiglinGuardBot almacena las cookies exfiltradas durante las pruebas de Stored XSS."]
        ],
        "Esquema generado de forma automática durante la construcción del contenedor."
    )

    add_h2("7.2 Gestión de Sesión, Inventario y Sistema de Experiencia (XP)")
    add_p(
        "El progreso del estudiante se almacena en la cookie de sesión firmada criptográficamente por Flask (app.secret_key). "
        "Las variables clave administradas en la sesión son:\n"
        "• session['inventory']: Lista de identificadores de las reliquias capturadas ('iron', 'diamond', 'portal', 'gold', 'blaze', 'pearl', 'crystals', 'dragon', 'egg').\n"
        "• session['xp']: Puntuación de experiencia acumulada. Todo jugador inicia con 30 puntos de XP. Cada bandera validada exitosamente "
        "otorga una recompensa de +50 XP.\n"
        "• session['unlocked_hints']: Lista de pistas que el usuario ha desbloqueado utilizando sus puntos de experiencia."
    )

    add_h2("7.3 Mecanismo de Pistas Dinámicas y Deducción de Experiencia")
    add_p(
        "Para fomentar el autoaprendizaje sin frustración, cada desafío incluye una pista contextual que no revela la solución directa, "
        "sino que orienta metodológicamente al estudiante. El desbloqueo de una pista requiere un costo de 20 XP. Si el estudiante no "
        "cuenta con saldo suficiente, la API /api/unlock_hint rechaza la solicitud, motivándolo a resolver primero retos iniciales para "
        "financiar pistas en retos más avanzados."
    )

    # =========================================================================
    # 8. CATÁLOGO Y ANÁLISIS PEDAGÓGICO DE LOS DESAFÍOS DE SEGURIDAD
    # =========================================================================
    add_h1("8. Catálogo y Análisis Pedagógico de los Desafíos de Seguridad")
    add_p(
        "El laboratorio organiza sus nueve desafíos en tres dimensiones progresivas, inspiradas en la línea argumental de Minecraft. "
        "A continuación, se detalla la fundamentación teórica, la vulnerabilidad implementada y el análisis de código de cada reto, "
        "omitiendo deliberadamente los vectores de explotación específicos para preservar el valor evaluativo del laboratorio."
    )

    # DIMENSIÓN 1: OVERWORLD
    add_h2("8.1 Dimensión 1: Overworld (Nivel Básico)")
    add_p(
        "Representa la superficie del mundo. Introduce al participante en conceptos fundamentales de esteganografía forense, "
        "criptografía clásica, inyecciones de base de datos básicas y fuga de metadatos."
    )

    add_h3("8.1.1 Desafío 1 - Lingote de Hierro: Esteganografía en Metadatos PNG y Cifrado Clásico")
    add_p(
        "• Fundamento Teórico: Los formatos de archivo de imagen modernos (como PNG y JPEG) incluyen bloques de metadatos "
        "(tEXt, iTXt, EXIF) destinados a registrar datos del autor, software de edición o marcas de tiempo. La inserción de información "
        "confidencial en estos campos representa un vector habitual de exfiltración o de ocultamiento de datos (esteganografía)."
    )
    add_p(
        "• Implementación en el Laboratorio: El módulo init_assets.py genera el archivo mapa_cueva.png e inserta en la cabecera tEXt "
        "bajo el atributo Comment un texto con el secreto protegido mediante una capa de codificación Base64 y una rotación de "
        "sustitución monoalfabética conocida históricamente como Cifrado César o ROT-13."
    )
    add_p(
        "• Impacto y Mitigación: Publicar archivos multimedia en portales web sin eliminar previamente sus metadatos (stripping) "
        "puede exponer secretos de infraestructura, nombres de usuario internos o coordenadas geográficas. La mitigación consiste en "
        "procesar y desinfectar todas las imágenes antes de su almacenamiento público mediante librerías de stripping de metadatos."
    )

    add_h3("8.1.2 Desafío 2 - Diamante en Capa Y=-58: Inyección SQL (SQLi) Clásica en Consultas no Parametrizadas")
    add_p(
        "• Fundamento Teórico: La inyección de lenguaje de consulta estructurado (SQL Injection) ocurre cuando datos suministrados por "
        "el usuario se concatenan directamente en la cadena de consulta que se envía al motor de base de datos, permitiendo al atacante "
        "alterar la lógica booleana de la sentencia original."
    )
    add_p(
        "• Implementación en el Laboratorio: En la ruta /overworld/diamond/search del archivo app.py, el parámetro de búsqueda chest_query "
        "se introduce directamente mediante interpolación de cadenas de texto (f-strings) en la instrucción SQL: "
        "SELECT * FROM villager_chests WHERE is_locked = 0 AND chest_name LIKE '%{chest_query}%'. Dado que el cofre con los diamantes "
        "posee la restricción is_locked = 1, la consulta normal jamás lo retorna, requiriendo que la inyección rompa la cláusula WHERE."
    )
    add_p(
        "• Impacto y Mitigación: Esta vulnerabilidad permite la lectura no autorizada de tablas completas, evasión de autenticación y "
        "exfiltración de datos confidenciales. La remediación estándar exige el uso mandatario de consultas parametrizadas o declaraciones "
        "preparadas (prepared statements), asegurando que las entradas del usuario sean tratadas como datos literales y no como código ejecutable."
    )

    add_h3("8.1.3 Desafío 3 - Consola de las Cuevas: Enumeración de Rutas y Validación por Allowlist")
    add_p(
        "• Fundamento Teórico: Una consola restringida es un ejemplo de superficie de ataque mínima. Si la aplicación valida los "
        "comandos con una allowlist explícita y resuelve las rutas contra un diccionario en memoria, el atacante no puede invocar "
        "una shell, leer archivos del sistema ni salir del directorio lógico. La debilidad pedagógica reside en la enumeración: "
        "el participante debe descubrir qué rutas y archivos existen antes de leer el secreto."
    )
    add_p(
        "• Implementación en el Laboratorio: El módulo cave_data.py define cinco cuevas (/cueva/hielo, /cueva/estalactitas, "
        "/cueva/luminosa, /cueva/bruja y /cueva/lago-de-lava) con archivos de texto simulados. El endpoint POST "
        "/overworld/cueva/terminal solo acepta ls, cat, help y clear; normaliza las rutas con posixpath.normpath y rechaza "
        "cualquier intento de salir de /cueva. La bandera real se inyecta en tiempo de ejecución en llave_ignicion.txt, "
        "mientras que una tablilla congelada contiene una bandera falsa como señuelo. Los escritos de la bruja aportan una "
        "pista contextual para la actividad del caldero en el Nether."
    )
    add_p(
        "• Impacto y Mitigación: En sistemas reales, una consola de administración mal restringida puede derivar en ejecución "
        "remota de comandos o en lectura arbitraria de archivos. La mitigación consiste en validar por allowlist, no concatenar "
        "entradas en intérpretes de shell, resolver rutas contra un origen canónico y ejecutar el servicio con el mínimo privilegio posible."
    )

    # DIMENSIÓN 2: NETHER
    add_h2("8.2 Dimensión 2: Nether (Nivel Intermedio)")
    add_p(
        "Representa el inframundo del juego. Desafía al participante con ataques a nivel de cliente y servidor que involucran ejecución "
        "de scripts en el contexto del navegador, subida no segura de ficheros y escalamiento de privilegios."
    )

    add_h3("8.2.1 Desafío 4 - Lingote de Oro: Stored XSS y Robo de Sesión en el Bastión")
    add_p(
        "• Fundamento Teórico: El Cross-Site Scripting Almacenado (Stored XSS) se produce cuando una aplicación web guarda datos "
        "proporcionados por el usuario sin sanitizar y posteriormente los renderiza en las páginas vistas por otros usuarios, ejecutando "
        "código JavaScript arbitrario en el navegador de la víctima."
    )
    add_p(
        "• Implementación en el Laboratorio: En la plantilla nether.html, el mensaje de trueque se muestra mediante la directiva "
        "{{ offer.note_to_piglin|safe }}. El filtro |safe desactiva deliberadamente el mecanismo de escape automático de Jinja2. Cuando "
        "el usuario envía una oferta, el bot simulado PiglinGuardBot visita la sección con su cookie de tesorero, enviando dicha sesión "
        "al endpoint de fuga (/nether/gold/leak) si se incluye una instrucción adecuada."
    )
    add_p(
        "• Impacto y Mitigación: Puede conducir a la toma de control de cuentas (Account Takeover), robo de tokens de sesión y suplantación "
        "de identidad. Las medidas preventivas incluyen la sanitización estricta de salida mediante codificación contextual HTML, la "
        "implementación de directivas Content Security Policy (CSP) y el marcado de cookies con el atributo HttpOnly."
    )

    add_h3("8.2.2 Desafío 5 - Varas de Blaze: Carga Arbitraria de Archivos y Ejecución de Recetas (File Upload → RCE)")
    add_p(
        "• Fundamento Teórico: Cuando una aplicación permite a los usuarios subir ficheros al servidor sin validar su extensión, contenido "
        "real o permisos de ejecución, un atacante puede cargar scripts ejecutables (Web Shells) para tomar control del sistema operativo."
    )
    add_p(
        "• Implementación en el Laboratorio: El caldero de pociones (/nether/blaze/upload) recibe archivos de recetas guardándolos en "
        "el directorio static/uploads. Si la receta termina en .py o .sh, se ejecuta automáticamente mediante run_sandboxed y su salida "
        "se muestra al participante en la misma tarjeta; la ruta /nether/blaze/execute/<filename> permanece como mecanismo manual de "
        "reejecución. La pista del desafío remite a la cueva de la bruja del Overworld, que indica el archivo objetivo sin repetir la ruta."
    )
    add_p(
        "• Impacto y Mitigación: Conduce a la ejecución remota de código (RCE). La mitigación requiere aplicar listas blancas de tipos MIME "
        "y extensiones, almacenar los archivos en servidores de objetos independientes (como AWS S3 o MinIO), renombrar los ficheros "
        "con identificadores aleatorios (UUID) y denegar permisos de ejecución en el directorio de almacenamiento."
    )

    add_h3("8.2.3 Desafío 6 - Ojo de Ender: Falla de Control de Acceso y Manipulación de Parámetros (Parameter Tampering)")
    add_p(
        "• Fundamento Teórico: El control de acceso roto (Broken Access Control) se sitúa en el primer lugar del OWASP Top 10. Se manifiesta "
        "cuando las decisiones de autorización se toman confiando en parámetros que el cliente puede alterar a voluntad."
    )
    add_p(
        "• Implementación en el Laboratorio: La ruta /nether/pearl/altar valida el nivel de acceso del usuario leyendo el parámetro "
        "user_role directamente desde los parámetros de la URL (query string) o desde una cookie no firmada, asignando por defecto el "
        "rol guest_traveler y concediendo la reliquia si el rol coincide con perfiles privilegiados como ender_master o bastion_overlord."
    )
    add_p(
        "• Impacto y Mitigación: Permite a usuarios no autorizados asumir privilegios de administración. Se remedia gestionando los roles "
        "de usuario estrictamente del lado del servidor dentro de sesiones autenticadas e inmutables o utilizando tokens JWT firmados "
        "criptográficamente."
    )

    # DIMENSIÓN 3: THE END
    add_h2("8.3 Dimensión 3: The End (Nivel Avanzado - Boss Final)")
    add_p(
        "Constituye la fase culminante del laboratorio. Aborda vectores de compromiso a nivel de servicios del sistema operativo, "
        "inyección de comandos en shell y enumeración de Active Directory con PowerView."
    )

    add_h3("8.3.1 Desafío 7 - Cristales del End: Simulación de Explotación de Servicio / CVE Backdoor")
    add_p(
        "• Fundamento Teórico: A lo largo de la historia de la seguridad informática, diversos incidentes de compromiso de cadena de suministro "
        "(como el backdoor en ProFTPD 1.3.3c o incidentes en servidores IRC) han introducido puertas traseras que se activan al recibir "
        "cadenas de texto específicas en puertos de telemetría."
    )
    add_p(
        "• Implementación en el Laboratorio: La consola de telemetría (/end/crystals/exploit) evalúa el payload enviado por el participante. "
        "Si la entrada contiene patrones de firma correspondientes al backdoor simulado (como identificadores de sobrecarga CVE o secuencias "
        "de escape de comando de control), el sistema simula la detonación de los cuatro cristales y libera la bandera contenida en /secret/end_crystals.txt."
    )
    add_p(
        "• Impacto y Mitigación: Compromiso total de la disponibilidad e integridad del servicio. Requiere auditorías periódicas de código, "
        "análisis estático de seguridad (SAST) y gestión continua de parches de vulnerabilidades conocidas."
    )

    add_h3("8.3.2 Desafío 8 - Derrotar al Ender Dragón: Inyección de Comandos del Sistema Operativo (OS Command Injection)")
    add_p(
        "• Fundamento Teórico: La inyección de comandos ocurre cuando una aplicación ejecuta comandos del sistema operativo concatenando "
        "directamente datos del usuario dentro de un shell de sistema (ej. /bin/sh o bash), permitiendo encadenar órdenes arbitrarias mediante "
        "metacaracteres como punto y coma (;), operadores booleanos (&&, ||) o tuberías (|)."
    )
    add_p(
        "• Implementación en el Laboratorio: En la ruta /end/dragon/damage, el cálculo de trayectoria del disparo se modela mediante la instrucción: "
        "cmd = f\"echo 'Calculando impacto de flecha: potencia {shot_power}'\", la cual se ejecuta con shell=True dentro del subsistema sandboxed. "
        "El participante debe analizar cómo cerrar la instrucción original para forzar la lectura del archivo /secret/dragon_slain.txt."
    )
    add_p(
        "• Impacto y Mitigación: Permite el control total del servidor en el contexto del usuario de ejecución. La mitigación radical exige "
        "evitar invocar shells del sistema operativo, empleando funciones que reciban argumentos como listas estructuradas sin shell=True, "
        "o realizando conversiones estrictas a tipos de datos numéricos (ej. int(shot_power)) antes de cualquier procesamiento."
    )

    add_h3("8.3.3 Desafío 9 - Huevo del Dragón: Enumeración de Active Directory con PowerView")
    add_p(
        "• Fundamento Teórico: PowerView es un conjunto de funciones de PowerShell para enumerar Active Directory. "
        "Permite consultar usuarios, grupos, equipos, sesiones y recursos compartidos sin necesidad de herramientas "
        "administrativas adicionales, lo que lo convierte en una técnica habitual de reconocimiento en auditorías internas. "
        "La información expuesta en descripciones de cuentas de servicio y en shares mal segmentados puede revelar la "
        "ubicación de datos sensibles."
    )
    add_p(
        "• Implementación en el Laboratorio: La ruta /end/powerview/terminal expone una consola simulada que interpreta "
        "comandos como Get-NetDomain, Get-NetUser, Get-NetGroupMember, Find-DomainShare, Get-NetShare, Invoke-UserHunter "
        "y Get-Content contra un dominio ficticio llamado end.local. El motor no invoca PowerShell ni accede al sistema "
        "de archivos: resuelve cada comando contra un diccionario de usuarios, grupos, equipos y shares definido en "
        "end_ad.py. La cuenta de servicio svc_backup describe el share \\\\END-FS01\\vault y el archivo "
        "real_dragon_egg.txt contiene la bandera final."
    )
    add_p(
        "• Impacto y Mitigación: La enumeración de AD facilita el movimiento lateral y la identificación de recursos "
        "críticos. Para mitigarlo se recomienda no incluir rutas internas en las descripciones de cuentas, aplicar "
        "mínimo privilegio y ACLs por grupo en los shares, usar cuentas de servicio administradas (gMSA), segmentar "
        "los servidores de archivos y monitorizar consultas LDAP y accesos SMB anómalos."
    )

    # =========================================================================
    # 9. MECANISMOS DE HARDENING Y SEGURIDAD DEFENSIVA
    # =========================================================================
    add_h1("9. Mecanismos de Hardening y Seguridad Defensiva del Entorno")
    add_p(
        "A pesar de ser un laboratorio deliberadamente vulnerable, la arquitectura implementa rigurosas barreras defensivas "
        "para impedir que las actividades de pentesting afecten la máquina anfitriona o el propio contenedor de forma irreversible:"
    )
    add_p(
        "1. Usuario de sistema sin privilegios (mcuser): En el Dockerfile se crea un usuario de sistema dedicado (RUN useradd --create-home "
        "--shell /usr/sbin/nologin mcuser) y se transfiere la propiedad del código (/app). Cualquier código ejecutado a través de inyecciones "
        "o web shells carece de privilegios de superusuario en el contenedor."
    )
    add_p(
        "2. Consola PowerView sin ejecución real: La ruta /end/powerview/terminal no invoca PowerShell ni accede al sistema de archivos "
        "del contenedor. Los comandos se resuelven contra datos simulados en end_ad.py, por lo que la actividad del reto no amplía la "
        "superficie de ataque ni permite ejecución arbitraria de comandos."
    )
    add_p(
        "3. Límite de carga de ficheros: La configuración app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 limita el tamaño de cualquier "
        "archivo subido a un máximo de 2 MB, devolviendo automáticamente un error HTTP 413 si se intenta saturar el almacenamiento."
    )
    add_p(
        "4. Cabeceras de respuesta personalizadas: La aplicación inyecta en cada respuesta HTTP las cabeceras X-Lab-Developers "
        "(Thorfinn777, Martyn777, Sassyjack777) y X-Lab-Platform, garantizando la trazabilidad y autoría institucional de la plataforma."
    )

    # =========================================================================
    # 10. CONCLUSIONES Y RECOMENDACIONES ACADÉMICAS
    # =========================================================================
    add_h1("10. Conclusiones y Recomendaciones Académicas")
    add_h2("10.1 Conclusiones")
    add_p(
        "1. Se logró con éxito la concepción, desarrollo y parametrización de una plataforma de entrenamiento en ciberseguridad "
        "gamificada, demostrando que la integración de narrativas de juego (Minecraft) con escenarios reales de vulnerabilidad web "
        "incrementa el compromiso del estudiante y favorece una comprensión intuitiva del modelo de progresión de ataques."
    )
    add_p(
        "2. La optimización del contenedor Docker para perfiles de hardware ajustados (1.5 vCPUs y 512 MB de RAM) resuelve un problema "
        "recurrente en las prácticas de laboratorio universitarias, permitiendo ejecutar simultáneamente el entorno vulnerable, el navegador "
        "y suites complejas de auditoría (como Burp Suite) en una única máquina virtual sin degradación de rendimiento."
    )
    add_p(
        "3. El diseño del bot emulador (PiglinGuardBot) y del ejecutor restringido (sandbox.py) evidencia que es posible simular interacciones "
        "administrativas complejas y contener procesos de auditoría mediante técnicas ligeras a nivel de kernel, prescindiendo de infraestructuras "
        "pesadas de virtualización interna."
    )
    add_h2("10.2 Recomendaciones")
    add_p(
        "1. Se recomienda a los docentes y evaluadores utilizar el script deploy.sh como método estándar de despliegue en entornos de "
        "evaluación presencial, asegurándose de que la máquina virtual de Kali Linux cuente con al menos 4 GB de RAM asignados en VirtualBox."
    )
    add_p(
        "2. Para los estudiantes, se aconseja abordar el laboratorio de manera metódica, comenzando por el análisis visual, de metadatos "
        "y de enumeración de rutas del Overworld antes de intentar vulnerabilidades de mayor complejidad en el Nether o The End."
    )
    add_p(
        "3. Se sugiere complementar este laboratorio con la redacción de informes de auditoría profesional (Pentesting Reports), donde el "
        "estudiante deba documentar el impacto en el negocio y la recomendación de código seguro para cada uno de los fallos encontrados."
    )

    # =========================================================================
    # 11. REFERENCIAS BIBLIOGRÁFICAS Y TECNOLÓGICAS (APA 7MA EDICIÓN)
    # =========================================================================
    doc.add_page_break()
    add_h1("Referencias")

    add_reference_apa(
        "Clark, A., & Contributors",
        "2024",
        "Pillow (PIL Fork) Documentation and Image Processing Tools (Version 10.4.0)",
        "Read the Docs",
        "https://pillow.readthedocs.io/"
    )
    add_reference_apa(
        "Docker Inc.",
        "2024",
        "Docker Engine and Docker Compose Technical Documentation",
        "Docker Docs",
        "https://docs.docker.com/"
    )
    add_reference_apa(
        "Gunicorn Development Team",
        "2024",
        "Gunicorn: WSGI HTTP Server for UNIX (Version 22.0.0)",
        "Gunicorn Documentation",
        "https://docs.gunicorn.org/"
    )
    add_reference_apa(
        "Harvey, P.",
        "2024",
        "ExifTool by Phil Harvey: Image Metadata Read and Write Engine (Perl Version)",
        "ExifTool Project",
        "https://exiftool.org/"
    )
    add_reference_apa(
        "Offensive Security",
        "2024",
        "Kali Linux Documentation and Penetration Testing Tools Catalog",
        "OffSec Services Limited",
        "https://www.kali.org/docs/"
    )
    add_reference_apa(
        "Oracle Corporation",
        "2024",
        "Oracle VM VirtualBox: User Manual and Virtualization Optimization",
        "Oracle Help Center",
        "https://www.virtualbox.org/manual/"
    )
    add_reference_apa(
        "OWASP Foundation",
        "2021",
        "OWASP Top 10: The Ten Most Critical Web Application Security Risks",
        "Open Web Application Security Project",
        "https://owasp.org/www-project-top-ten/"
    )
    add_reference_apa(
        "Pallets Projects",
        "2024",
        "Flask: A Python Microframework for Web Development (Version 3.0.3)",
        "Pallets Documentation",
        "https://flask.palletsprojects.com/"
    )
    add_reference_apa(
        "Pallets Projects",
        "2024",
        "Werkzeug: Comprehensive WSGI Web Application Library (Version 3.0.3)",
        "Pallets Documentation",
        "https://werkzeug.palletsprojects.com/"
    )
    add_reference_apa(
        "PortSwigger Ltd.",
        "2024",
        "Web Security Academy: SQL Injection, Cross-Site Scripting, and Command Injection",
        "PortSwigger Web Security Research",
        "https://portswigger.net/web-security"
    )
    add_reference_apa(
        "Python Software Foundation",
        "2024",
        "Python Language Reference and POSIX Resource Management (Version 3.11)",
        "PSF Documentation",
        "https://docs.python.org/3.11/"
    )
    add_reference_apa(
        "SQLite Development Team",
        "2024",
        "SQLite Write-Ahead Logging (WAL) and Performance Tuning Specifications",
        "SQLite Consortium",
        "https://www.sqlite.org/wal.html"
    )

    # =========================================================================
    # 12. ANEXO: ESPACIOS PARA PANTALLAZOS (EVIDENCIA VISUAL DEL PROYECTO)
    # =========================================================================
    doc.add_page_break()
    add_h1("Anexo: Evidencias y Espacios para Capturas de Pantalla")
    add_p(
        "A continuación, se disponen los espacios estructurados en formato formal de figuras bajo normas APA 7ma edición, "
        "destinados a la inserción de las capturas de pantalla de la puesta en marcha, la interfaz visual de cada dimensión "
        "y la interacción con el entorno de pruebas."
    )

    add_figure_placeholder(
        1,
        "Ejecución del script deploy.sh y verificación del contenedor Docker en Kali Linux",
        "Ventana de la terminal de Kali Linux mostrando el banner de bienvenida de Minecraft CTF,\n"
        "la verificación del demonio Docker y el mensaje de confirmación de despliegue exitoso.",
        "Captura de pantalla de la terminal Bash tras ejecutar el comando ./deploy.sh en la máquina virtual."
    )

    add_figure_placeholder(
        2,
        "Pantalla principal del laboratorio (HUD de Minecraft) y selección de dimensiones",
        "Navegador web cargando http://localhost:8080 mostrando la interfaz visual con barras de vida (corazones),\n"
        "nivel de experiencia (XP), inventario de reliquias y accesos al Overworld, Nether y The End.",
        "Vista panorámica del menú de inicio y estado inicial del participante (30 XP, 0/9 reliquias)."
    )

    add_figure_placeholder(
        3,
        "Panel de desafíos del Overworld (Fase 1: Fácil)",
        "Interfaz web de la fase Overworld con las tarjetas de los retos del Lingote de Hierro,\n"
        "el Diamante en capa Y=-58 (buscador de cofres) y la consola restringida de las cuevas.",
        "Formularios de validación de banderas, botón de acceso a la consola y descarga de activos (mapa_cueva.png)."
    )

    add_figure_placeholder(
        4,
        "Panel de desafíos del Nether e interacción con el Bastión (Fase 2: Medio)",
        "Vista de la dimensión del Nether mostrando el formulario de trueque con Piglins,\n"
        "el tablón de ofertas públicas recientes y la consola de auditoría del Piglin Guard.",
        "Evidencia de la interacción en el tablón del Bastión y la recepción de ofertas por parte del bot."
    )

    add_figure_placeholder(
        5,
        "Caldero de recetas y subida de archivos en el Nether",
        "Formulario de subida de archivos de receta (File Upload) en el Nether\n"
        "y área de ejecución controlada en el caldero.",
        "Visualización del selector de ficheros y el resultado devuelto por el caldero."
    )

    add_figure_placeholder(
        6,
        "Panel de The End: Batalla contra el Dragón y telemetría de cristales (Fase 3: Difícil)",
        "Consola de telemetría de combate en The End con el panel de ataque a los Cristales de curación,\n"
        "el cálculo de potencia de disparo contra el Ender Dragón y la terminal PowerView del Huevo.",
        "Interfaz del combate final mostrando los formularios de envío de payloads y la enumeración de Active Directory."
    )

    add_figure_placeholder(
        7,
        "Inspección de peticiones y análisis del laboratorio con herramientas de auditoría",
        "Captura del navegador web con las herramientas de desarrollador abiertas (F12) o Burp Suite\n"
        "inspeccionando cabeceras HTTP (X-Lab-Developers, cookies de sesión o consultas de red).",
        "Demostración del análisis técnico del tráfico HTTP generado entre el cliente y el contenedor Docker."
    )

    add_figure_placeholder(
        8,
        "Pantalla final de victoria tras completar el inventario de 9 reliquias",
        "Vista de la ruta /victory con el trofeo de Minecraft, felicitaciones de los desarrolladores\n"
        "(Thorfinn777, Martyn777, Sassyjack777) y el inventario completo de los 9 ítems.",
        "Confirmación visual de la culminación del laboratorio con las nueve banderas desbloqueadas."
    )

    # ---------------------------------------------------------
    # Guardar Documento Word (.docx)
    # ---------------------------------------------------------
    output_filename = "Documentacion_Minecraft_CTF_Lab_APA7.docx"
    scratch_dir = r"C:\Users\nicol\.gemini\antigravity\brain\cf994e5c-5c3d-45bf-b8a8-2120a9e6d728\scratch"
    os.makedirs(scratch_dir, exist_ok=True)
    scratch_path = os.path.join(scratch_dir, output_filename)
    doc.save(scratch_path)
    print(f"[+] Documento Word generado exitosamente en scratch: {scratch_path}")

if __name__ == '__main__':
    create_document()
