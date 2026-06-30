def generar_pdf_bytes():
    from fpdf import FPDF
    
    class PDF(FPDF):
        def header(self):
            # Topo estilizado - Identidade Visual
            self.set_fill_color(31, 78, 121) # Azul Corporativo Escuro
            self.rect(0, 0, 210, 35, 'F')
            
            self.set_font("Arial", "B", 18)
            self.set_text_color(255, 255, 255)
            self.cell(0, 10, "SMART ANALYTICS & DOCUMENT OCR", ln=True, align="C")
            
            self.set_font("Arial", "I", 10)
            self.cell(0, 5, "Relatorio Estruturado de Extracao Digital", ln=True, align="C")
            self.ln(12)

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- METADADOS DO DOCUMENTO ---
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(40, 6, "Emitido por:", ln=False)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Marcos - TI Infraestrutura", ln=True)
    
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 6, "Data de Processamento:", ln=False)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "30/06/2026", ln=True)
    pdf.ln(6)
    
    # --- SEÇÃO 1: RESUMO ---
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(31, 78, 121)
    pdf.cell(0, 8, "1. Resumo Executivo", ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)
    
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 6, "Os dados abaixo foram consolidados automaticamente atraves do motor de visao computacional (OCR). O algoritmo realizou o escaneamento matricial da imagem enviada, tratando as distorcoes e segmentando as principais informacoes estruturais do documento fiscal.")
    pdf.ln(6)

    # --- SEÇÃO 2: DADOS ESTRUTURADOS DA NOTA ---
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(31, 78, 121)
    pdf.cell(0, 8, "2. Informacoes Estruturadas (Layout Padrao)", ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)

    # Captura o texto atual que está na session_state do Streamlit
    texto_ocr = st.session_state.get("texto_extraido", "")
    
    if texto_ocr:
        linhas = texto_ocr.split('\n')
        
        # Criando uma tabela para organizar o layout parecido com uma NF
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(240, 243, 246) # Fundo cinza claro para o cabeçalho da tabela
        pdf.set_text_color(31, 78, 121)
        
        # Colunas da Tabela
        pdf.cell(50, 8, " Campo Identificado", border=1, fill=True)
        pdf.cell(130, 8, " Conteudo Extraido", border=1, fill=True, ln=True)
        
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(0, 0, 0)
        
        for linha in linhas:
            if ":" in linha:
                campo, valor = linha.split(":", 1)
                campo_limpo = campo.replace("===", "").strip()
                valor_limpo = valor.strip()
                
                if campo_limpo and valor_limpo:
                    # Desenha a linha da tabela de forma organizada
                    pdf.set_font("Arial", "B", 9)
                    pdf.cell(50, 7, f" {campo_limpo}", border=1)
                    pdf.set_font("Arial", "", 9)
                    pdf.cell(130, 7, f" {valor_limpo}", border=1, ln=True)
    else:
        pdf.set_font("Arial", "I", 10)
        pdf.set_text_color(150, 0, 0)
        pdf.cell(0, 8, "Nenhum documento processado ou extraido na aba de OCR.", ln=True)
        
    return bytes(pdf.output())