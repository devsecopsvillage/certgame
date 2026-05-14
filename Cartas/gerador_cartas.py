"""
Script: gerador_cartas.py
Descrição: Gerador de cartas em PDF para o jogo CertGame.
             Processa arquivos JSON de perguntas e gera PDFs com frente e verso lado a lado.
Autor: Gemini CLI
Versão: 2.0
"""

import json
import os
import sys

# Importação de módulos do ReportLab para manipulação de PDFs
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.platypus import Paragraph, Frame
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    print("ERRO: A biblioteca 'reportlab' é necessária.")
    print("Execute: pip install -r requirements.txt")
    sys.exit(1)

def get_card_elements(question, style_n, style_b):
    """
    Organiza os elementos textuais de uma única carta.
    
    Args:
        question (dict): Dicionário contendo enunciado, opções e resposta.
        style_n (ParagraphStyle): Estilo para texto normal.
        style_b (ParagraphStyle): Estilo para texto em negrito (resposta).
        
    Returns:
        list: Lista de objetos Paragraph prontos para renderização.
    """
    story = []
    
    # Adiciona o enunciado (pergunta) sempre em negrito
    enunciado = question['enunciado']
    story.append(Paragraph(f"<b>{enunciado}</b>", style_n))
    
    # Itera sobre as alternativas a, b, c, d...
    for opt_key, opt_val in question['opcoes'].items():
        texto_opcao = f"{opt_key}) {opt_val}"
        
        # Se a chave da opção for a resposta correta, aplica o estilo de negrito
        if opt_key == question['resposta']:
            story.append(Paragraph(texto_opcao, style_b))
        else:
            story.append(Paragraph(texto_opcao, style_n))
            
    return story

def generate_cards():
    """
    Coordena o fluxo principal de geração dos baralhos em PDF.
    """
    
    # 1. Carregamento de Configurações
    config_path = 'config.json'
    if not os.path.exists(config_path):
        print(f"ERRO: Arquivo de configuração '{config_path}' não encontrado.")
        return

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 2. Configurações Físicas da Carta
    # Converte décimos de milímetro para pontos (unidade padrão do PDF)
    # Cast explícito para float para suportar qualquer formato numérico no JSON
    card_width = (float(config['size']['width']) / 10.0) * mm
    card_height = (float(config['size']['height']) / 10.0) * mm

    # 3. Cálculo de Escala de Margens
    # Obtém as dimensões em pixels da imagem de fundo para mapear as margens corretamente
    img_w_px, img_h_px = 965.0, 1282.0 # Fallback como float
    bg_front_path = config['background']['background_card']
    
    if os.path.exists(bg_front_path):
        try:
            from PIL import Image
            with Image.open(bg_front_path) as img:
                w, h = img.size
                img_w_px, img_h_px = float(w), float(h)
        except Exception as e:
            print(f"AVISO: Falha ao ler dimensões da imagem de fundo: {e}")
            
    # Proporção entre o tamanho físico da carta e os pixels da imagem original
    ratio_x = card_width / img_w_px
    ratio_y = card_height / img_h_px

    # Converte as margens de pixels (do config.json) para pontos do PDF
    # Tratando todos os valores como float
    m_top = float(config['font']['margen_top']) * ratio_y
    m_down = float(config['font']['margen_down']) * ratio_y
    m_left = float(config['font']['margen_left']) * ratio_x
    m_right = float(config['font']['margen_right']) * ratio_x

    # 4. Configuração de Tipografia
    font_family = config['font']['name']
    # Garante que o tamanho da fonte seja tratado como ponto flutuante
    font_base_size = float(config['font']['size'])
    text_color = HexColor("#000000") # Texto sempre preto para humanos
    
    # Mapeia alinhamento de texto
    alignment_map = {"left": 0, "center": 1, "right": 2, "justify": 4}
    selected_alignment = alignment_map.get(config['font'].get('alignment', 'left'), 0)
    
    # Tenta registrar a fonte Consolas ou usa Helvetica como fallback
    registered_font = "Helvetica"
    registered_font_bold = "Helvetica-Bold"
    
    font_paths = [
        (font_family, "C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/consolab.ttf"),
        ("Courier", None, None) 
    ]
    
    for f_name, f_path, f_path_b in font_paths:
        if f_path and os.path.exists(f_path):
            try:
                pdfmetrics.registerFont(TTFont(f_name, f_path))
                pdfmetrics.registerFont(TTFont(f"{f_name}-Bold", f_path_b))
                # Registra mapeamento para que as tags <b> funcionem
                from reportlab.lib.fonts import addMapping
                addMapping(f_name, 0, 0, f_name)       # Normal
                addMapping(f_name, 1, 0, f"{f_name}-Bold") # Bold
                registered_font = f_name
                registered_font_bold = f"{f_name}-Bold"
                break
            except:
                continue
        elif f_name == "Courier":
            registered_font = "Courier"
            registered_font_bold = "Courier-Bold"
            break

    # 5. Processamento dos Grupos de Perguntas
    if not os.path.exists('PDFs'):
        os.makedirs('PDFs')

    gerar_verso = config.get('gerar_verso', True)

    for group_id, json_path in config['questions'].items():
        if not os.path.exists(json_path):
            print(f"AVISO: Arquivo {json_path} ignorado (não encontrado).")
            continue
            
        output_file = f"PDFs/{group_id}.pdf"
        print(f"Processando Baralho: {output_file}...")
        
        # Define a largura do PDF baseado na configuração de verso
        canvas_width = card_width * 2 if gerar_verso else card_width
        pdf_canvas = canvas.Canvas(output_file, pagesize=(canvas_width, card_height))
        
        with open(json_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
            
        bg_back_key = f"background_{group_id.replace('_', '')}"
        bg_back_path = config['background'].get(bg_back_key)

        for q in questions:
            # --- RENDERIZAÇÃO DA FRENTE (Esquerda) ---
            # O fundo da frente (background_card) é mantido sempre, conforme solicitado.
            if os.path.exists(bg_front_path):
                pdf_canvas.drawImage(bg_front_path, 0, 0, width=card_width, height=card_height)
            else:
                print(f"AVISO: Fundo da frente não encontrado: {bg_front_path}")
            
            # O retângulo que mantém o texto agora é transparente (fill=0)
            pdf_canvas.setFillColorRGB(1, 1, 1) 
            rect_x, rect_y = float(m_left), float(m_down)
            rect_w = float(card_width - m_left - m_right)
            rect_h = float(card_height - m_top - m_down)
            pdf_canvas.rect(rect_x, rect_y, rect_w, rect_h, fill=0, stroke=0)

            # Define área útil de texto com padding interno reduzido
            padding = 5.0
            f_x, f_y = rect_x + padding, rect_y + padding
            f_w, f_h = rect_w - (2 * padding), rect_h - (2 * padding)
            
            # Estilos de parágrafo baseados no config.json
            style_n = ParagraphStyle(
                'CardNormal', 
                fontName=registered_font, 
                fontSize=font_base_size,
                textColor=text_color, 
                leading=font_base_size * 1.5, # Espaçamento entre linhas proporcional
                alignment=selected_alignment,
                spaceAfter=font_base_size * 0.5 
            )
            style_b = ParagraphStyle('CardBold', parent=style_n, fontName=registered_font_bold)
            
            story = get_card_elements(q, style_n, style_b)
            
            # Frame de fluxo de texto
            text_frame = Frame(f_x, f_y, f_w, f_h, showBoundary=0)
            text_frame.addFromList(story, pdf_canvas)
            
            # --- RENDERIZAÇÃO DO VERSO (Direita) ---
            # A geração do verso é controlada pela propriedade 'gerar_verso' no config.json.
            if gerar_verso and bg_back_path and os.path.exists(bg_back_path):
                pdf_canvas.drawImage(bg_back_path, card_width, 0, width=card_width, height=card_height)
            
            pdf_canvas.showPage()
            
        pdf_canvas.save()
        print(f"Sucesso: {output_file} gerado.")

if __name__ == "__main__":
    generate_cards()
