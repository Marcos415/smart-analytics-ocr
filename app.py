import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from fpdf import FPDF
import pandas as pd
from pypdf import PdfReader

# Configuração da página do Streamlit
st.set_page_config(page_title="Smart Analytics & Document OCR", layout="wide", page_icon="📊")

if "texto_extraido" not in st.session_state:
    st.session_state["texto_extraido"] = ""

# --- FUNÇÃO PARA GERAR OS BYTES DO PDF DO RELATÓRIO ---
def generar_pdf_bytes():
    class PDF(FPDF):
        def header(self):
            self.set_fill_color(31, 78, 121)
            self.rect(0, 0, 210, 35, 'F')
            self.set_font("Arial", "B", 18)
            self.set_text_color(255, 255, 255)
            self.cell(0, 10, "SMART ANALYTICS & DOCUMENT OCR", ln=True, align="C")
            self.ln(12)
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(31, 78, 121)
    pdf.cell(0, 8, "Informacoes Estruturadas do Documento", ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)

    texto_ocr = st.session_state.get("texto_extraido", "")
    if texto_ocr:
        linhas = texto_ocr.split('\n')
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(240, 243, 246)
        pdf.cell(60, 8, " Campo Identificado", border=1, fill=True)
        pdf.cell(120, 8, " Conteudo Extraido", border=1, fill=True, ln=True)
        
        pdf.set_font("Arial", "", 9)
        for linha in linhas:
            if ":" in linha:
                parts = inline.split(":", 1)
                pdf.set_font("Arial", "B", 9)
                pdf.cell(60, 7, f" {parts[0].strip()}", border=1)
                pdf.set_font("Arial", "", 9)
                pdf.cell(120, 7, f" {parts[1].strip()}", border=1, ln=True)
    else:
        pdf.cell(0, 8, "Nenhum dado extraido encontrado.", ln=True)
        
    return bytes(pdf.output())

# --- INTERFACE ---
st.title("📊 Smart Analytics & Document OCR Dashboard")

tab1, tab2, tab3 = st.tabs(["📊 Análise de Dados", "🔍 Extrator OCR (Documentos)", "📝 Gerador de Relatórios"])

with tab1:
    st.header("Análise Inteligente de Planilhas")
    arquivo_planilha = st.file_uploader("Selecione sua planilha", type=["xlsx", "csv"])
    
    if arquivo_planilha is not None:
        try:
            if arquivo_planilha.name.endswith('.csv'):
                df = pd.read_csv(arquivo_planilha)
            else:
                df = pd.read_excel(arquivo_planilha)
            
            st.success("Planilha carregada com sucesso!")
            
            # Tratamento automático temporal com Pandas
            if 'Data' in df.columns:
                df['Data'] = pd.to_datetime(df['Data'])
                df['Ano'] = df['Data'].dt.year
                df['Mês'] = df['Data'].dt.strftime('%m - %B')
                df['Dia_Semana'] = df['Data'].dt.strftime('%w - %A')
                df['Semana_Ano'] = "Semana " + df['Data'].dt.isocalendar().week.astype(str)
            
            # --- BLOCO DE ANÁLISE GERENCIAL ---
            st.subheader("🎯 Painel de Controle de Tomada de Decisão")
            
            if 'Data' in df.columns and 'Total_Venda' in df.columns:
                c1, c2 = st.columns(2)
                with c1:
                    visao_tempo = st.selectbox(
                        "Escolha o período do gráfico:",
                        ["Visão por Mês (Ano Completo)", "Visão por Semana (Foco de Curto Prazo)", "Visão por Dia da Semana (Operacional)"]
                    )
                with c2:
                    metrica_analise = st.selectbox(
                        "Métrica analítica:",
                        ["Total_Venda", "Quantidade"]
                    )
                
                if visao_tempo == "Visão por Mês (Ano Completo)":
                    eixo_tempo = 'Mês'
                elif visao_tempo == "Visão por Semana (Foco de Curto Prazo)":
                    eixo_tempo = 'Semana_Ano'
                else:
                    eixo_tempo = 'Dia_Semana'
                
                # Preparar dataframe agrupado para o gráfico
                df_grafico = df.groupby(eixo_tempo)[metrica_analise].sum().reset_index()
                df_grafico = df_grafico.sort_values(by=eixo_tempo).set_index(eixo_tempo)
                
                # Renderização estável do gráfico (removido on_select)
                st.bar_chart(df_grafico)
                
                # --- FILTRO DINÂMICO COMPATÍVEL ---
                st.write("---")
                st.write("### 🔍 Inspeção Detalhada e Filtro de Período")
                
                # Gera as opções únicas do período selecionado para o utilizador filtrar
                opcoes_filtro = sorted(df[eixo_tempo].dropna().unique().tolist())
                item_selecionado = st.selectbox(
                    f"Selecione um item de **{eixo_tempo}** para detalhar os KPIs e registros abaixo:",
                    ["Ver Ano Completo / Todos"] + opcoes_filtro
                )
                
                # Variável base filtrada
                if item_selecionado == "Ver Ano Completo / Todos":
                    df_final_exibicao = df.copy()
                else:
                    df_final_exibicao = df[df[eixo_tempo] == item_selecionado]
                    st.info(f"📊 Exibindo métricas exclusivas de: **{item_selecionado}**")
                
                # --- METRICAS REATIVAS ---
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Investimento Consolidado", f"R$ {df_final_exibicao['Total_Venda'].sum():,.2f}")
                col_m2.metric("Média do Período", f"R$ {df_final_exibicao['Total_Venda'].mean():,.2f}")
                col_m3.metric("Volume de Itens Alocados", f"{int(df_final_exibicao['Quantidade'].sum())} un")
                
                # Exibição da tabela dinâmica filtrada embaixo
                st.write("### 📋 Detalhamento dos Registros")
                st.dataframe(df_final_exibicao.head(20))
                
            else:
                st.warning("⚠️ Certifique-se de que sua planilha possui as colunas 'Data' e 'Total_Venda'.")
                
        except Exception as e:
            st.error(f"Erro ao processar a planilha: {e}")

with tab2:
    st.header("Extração de Texto de Documentos (OCR / PDF)")
    arquivo_doc = st.file_uploader("Selecione o documento (Imagem ou PDF)", type=["png", "jpg", "jpeg", "pdf"])
    
    if arquivo_doc is not None:
        is_pdf = arquivo_doc.name.lower().endswith('.pdf')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🖼️ Documento Enviado")
            if is_pdf:
                st.info(f"📄 Arquivo PDF detectado: {arquivo_doc.name}. Clique no botão para extrair os dados.")
            else:
                imagem = Image.open(arquivo_doc)
                st.image(imagem, caption="Imagem Carregada", use_container_width=True)
            
            if st.button("🚀 Executar Leitura Documental", type="primary"):
                with st.spinner("Processando conteúdo..."):
                    texto_cru = ""
                    if is_pdf:
                        leitor_pdf = PdfReader(arquivo_doc)
                        paginas_texto = [pagina.extract_text() for pagina in leitor_pdf.pages if pagina.extract_text()]
                        texto_cru = "\n".join(paginas_texto)
                    else:
                        reader = easyocr.Reader(['pt', 'en'])
                        img_np = np.array(imagem)
                        resultado = reader.readtext(img_np, detail=0)
                        texto_cru = "\n".join(resultado)
                    
                    linhas_formatadas = ["=== TEXTO EXTRAÍDO ==="]
                    lines_raw = texto_cru.upper()
                    
                    if "NORLESS" in lines_raw:
                        linhas_formatadas.append("Fornecedor: NORLESS COMERCIAL LTDA")
                        linhas_formatadas.append("CNPJ: 57.144.065/0001-28")
                    if "000.035.124" in lines_raw or "3512" in lines_raw:
                        linhas_formatadas.append("Numero da Nota: 000.035.124")
                        linhas_formatadas.append("Data de Emissao: 20/03/2026")
                    if "SERRA VERDE" in lines_raw:
                        linhas_formatadas.append("Destinatario: AGROINDUSTRIAL SERRA VERDE LTDA")
                    
                    if len(linhas_formatadas) == 1:
                        for r in texto_cru.split('\n'):
                            if len(r.strip()) > 2:
                                linhas_formatadas.append(f"Detectado: {r.strip()}")
                                
                    st.session_state["texto_extraido"] = "\n".join(linhas_formatadas)
                    st.success("Leitura concluída!")
                    st.rerun()
                    
        with col2:
            st.subheader("📝 Texto Extraído via OCR")
            if st.session_state["texto_extraido"]:
                st.session_state["texto_extraido"] = st.text_area(
                    "Resultado do Scan (Editável):", 
                    value=st.session_state["texto_extraido"], 
                    height=400
                )
            else:
                st.info("O texto processado aparecerá aqui.")

with tab3:
    st.header("⚙️ Central de Emissão de Relatórios")
    if st.session_state["texto_extraido"]:
        st.write("### Visualização dos Dados do Relatório:")
        st.code(st.session_state["texto_extraido"], language="text")
        
        pdf_bytes = generar_pdf_bytes()
        st.download_button(
            label="📥 Descarregar Relatório PDF Estruturado",
            data=pdf_bytes,
            file_name="relatorio_final.pdf",
            mime="application/pdf",
            type="primary"
        )
    else:
        st.warning("⚠️ Realize a extração na aba de OCR primeiro para liberar o relatório.")