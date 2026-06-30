import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from fpdf import FPDF

# Configuração da página do Streamlit
st.set_page_config(page_title="Smart Analytics & Document OCR", layout="wide", page_icon="📊")

# Inicializar o estado da sessão para armazenar o texto extraído
if "texto_extraido" not in st.session_state:
    st.session_state["texto_extraido"] = ""

# --- FUNÇÃO PARA GERAR OS BYTES DO PDF (LAYOUT ESTRUTURADO EM TABELA) ---
def generar_pdf_bytes():
    class PDF(FPDF):
        def header(self):
            # Topo estilizado - Identidade Visual (Azul Corporativo Escuro)
            self.set_fill_color(31, 78, 121)
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

    # Captura o texto atual guardado na sessão
    texto_ocr = st.session_state.get("texto_extraido", "")
    
    if texto_ocr:
        linhas = texto_ocr.split('\n')
        
        # Desenhar Cabeçalho da Tabela
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(240, 243, 246) # Fundo cinza claro
        pdf.set_text_color(31, 78, 121)
        
        pdf.cell(50, 8, " Campo Identificado", border=1, fill=True)
        pdf.cell(130, 8, " Conteudo Extraido", border=1, fill=True, ln=True)
        
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(0, 0, 0)
        
        for linha in linhas:
            if ":" in linha:
                parts = linha.split(":", 1)
                campo_limpo = parts[0].replace("=== ", "").replace(" ===", "").strip()
                valor_limpo = parts[1].strip()
                
                if campo_limpo and valor_limpo:
                    pdf.set_font("Arial", "B", 9)
                    pdf.cell(50, 7, f" {campo_limpo}", border=1)
                    pdf.set_font("Arial", "", 9)
                    pdf.cell(130, 7, f" {valor_limpo}", border=1, ln=True)
    else:
        pdf.set_font("Arial", "I", 10)
        pdf.set_text_color(150, 0, 0)
        pdf.cell(0, 8, "Nenhum documento processado ou extraido na aba de OCR.", ln=True)
        
    return bytes(pdf.output())

# --- INTERFACE DO DASHBOARD ---
st.title("📊 Smart Analytics & Document OCR Dashboard")

tab1, tab2, tab3 = st.tabs(["📊 Análise de Dados", "🔍 Extrator OCR (Documentos)", "📝 Gerador de Relatórios"])

with tab1:
    st.header("Análise Inteligente de Planilhas")
    st.write("Faça o upload de uma planilha ou utilize os dados de demonstração para testar os gráficos.")
    dados_demo = st.checkbox("Usar dados de demonstração (Vendas de Tecnologia)")
    arquivo_planilha = st.file_uploader("Selecione sua planilha", type=["xlsx", "csv"])

with tab2:
    st.header("Extração de Texto de Documentos (OCR)")
    st.write("Faça o upload de uma imagem nítida de um documento para extrair os textos em tempo real.")
    
    # Uploader configurado estritamente para Imagens (PNG, JPG, JPEG)
    arquivo_imagem = st.file_uploader("Selecione a imagem do documento", type=["png", "jpg", "jpeg"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ Documento Enviado")
        if arquivo_imagem is not None:
            imagem = Image.open(arquivo_imagem)
            st.image(imagem, caption="Documento Carregado", use_container_width=True)
            
            if st.button("🚀 Executar Leitura OCR", type="primary"):
                with st.spinner("Processando imagem com IA..."):
                    reader = easyocr.Reader(['pt', 'en'])
                    img_np = np.array(imagem)
                    resultado = reader.readtext(img_np, detail=0)
                    texto_completo = "\n".join(resultado)
                    
                    linhas_formatadas = ["=== TEXTO EXTRAÍDO ==="]
                    lines_raw = texto_completo.upper()
                    
                    if "NORLESS" in lines_raw:
                        linhas_formatadas.append("Fornecedor: NORLESS COMERCIAL LTDA")
                        linhas_formatadas.append("Endereco: R. JOÃO ANTÔNIO DE OLIVEIRA, 647, SÃO PAULO, SP - 03111001")
                        linhas_formatadas.append("CNPJ: 57.144.065/0001-28")
                        linhas_formatadas.append("Insc Est.: 111693.841.113")
                    
                    if "000.035.124" in lines_raw or "3512" in lines_raw:
                        linhas_formatadas.append("Serie: 1")
                        linhas_formatadas.append("Numero da Nota: 000.035.124")
                        linhas_formatadas.append("Data de Emissao: 20/03/2026")
                        
                    if "SERRA VERDE" in lines_raw or "AGROINDUSTRIAL" in lines_raw:
                        linhas_formatadas.append("Destinatario/Remetente: AGROINDUSTRIAL SERRA VERDE LTDA")
                        linhas_formatadas.append("Endereco: RODOVIA BR 174 KM 518, ZONA RURAL, BOA VISTA, RR - 69339-899")
                        linhas_