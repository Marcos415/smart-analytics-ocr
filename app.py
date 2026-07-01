import streamlit as st
import easyocr
import numpy as np
from PIL import Image
from fpdf import FPDF
import pandas as pd
from pypdf import PdfReader
import altair as alt

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
            self.cell(0, 10, f"Página {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(31, 78, 121)
    pdf.cell(0, 8, "Informações Estruturadas do Documento", ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)

    texto_ocr = st.session_state.get("texto_extraido", "")
    if texto_ocr:
        linhas = texto_ocr.split('\n')
        pdf.set_font("Arial", "B", 10)
        pdf.set_fill_color(240, 243, 246)
        pdf.cell(60, 8, " Campo Identificado", border=1, fill=True)
        pdf.cell(120, 8, " Conteúdo Extraído", border=1, fill=True, ln=True)
        
        pdf.set_font("Arial", "", 9)
        for linha in linhas:
            if ":" in linha:
                parts = linha.split(":", 1)
                pdf.set_font("Arial", "B", 9)
                pdf.cell(60, 7, f" {parts[0].strip()}", border=1)
                pdf.set_font("Arial", "", 9)
                pdf.cell(120, 7, f" {parts[1].strip()}", border=1, ln=True)
    else:
        pdf.cell(0, 8, "Nenhum dado extraído encontrado.", ln=True)
        
    return bytes(pdf.output())

# --- INTERFACE MASTER ---
st.title("📊 Smart Analytics & Document OCR Dashboard")

tab1, tab2, tab3 = st.tabs(["📊 Análise de Dados", "🔍 Extrator OCR (Documentos)", "📝 Gerador de Relatórios"])

# ==========================================
# ABA 1: ANÁLISE DE DADOS (BI DINÂMICO NATIVO)
# ==========================================
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
            
            st.subheader("🎯 Painel de Controle de Tomada de Decisão")
            
            if 'Data' in df.columns and 'Total_Venda' in df.columns:
                c1, c2 = st.columns(2)
                with c1:
                    visao_tempo = st.selectbox(
                        "Escolha o período de análise:",
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
                
                df_grafico = df.groupby(eixo_tempo)[metrica_analise].sum().reset_index()
                
                st.write("📊 **Clique direto em uma barra** para filtrar o painel inteiro. **Clique no fundo branco** do gráfico para limpar o filtro:")
                
                # Engenharia do gráfico interativo com Altair
                selecao_clique = alt.selection_point(fields=[eixo_tempo], name="Selecione")
                
                grafico_altair = alt.Chart(df_grafico).mark_bar(color="#1f4e79").encode(
                    x=alt.X(f'{eixo_tempo}:N', title=visao_tempo, sort=alt.EncodingSortField(field=eixo_tempo, order='ascending')),
                    y=alt.Y(f'{metrica_analise}:Q', title=metrica_analise),
                    opacity=alt.condition(selecao_clique, alt.value(1.0), alt.value(0.35)),
                    tooltip=[eixo_tempo, metrica_analise]
                ).add_params(
                    selecao_clique
                ).properties(
                    width='container',
                    height=350
                )
                
                res_altair = st.altair_chart(grafico_altair, use_container_width=True, on_select="rerun")
                
                # Base padrão: Tudo selecionado
                df_final_exibicao = df.copy()
                valor_clicado = None
                
                # Mapeamento do clique dinâmico (Altair para Pandas)
                if res_altair and "selection" in res_altair and "Selecione" in res_altair["selection"]:
                    dados_selecionados = res_altair["selection"]["Selecione"]
                    
                    if isinstance(dados_selecionados, dict) and eixo_tempo in dados_selecionados:
                        lista_valores = dados_selecionados[eixo_tempo]
                        if lista_valores and len(lista_valores) > 0:
                            valor_clicado = lista_valores[0]
                            
                    elif isinstance(dados_selecionados, list) and len(dados_selecionados) > 0:
                        primeiro_ponto = dados_selecionados[0]
                        if isinstance(primeiro_ponto, dict) and eixo_tempo in primeiro_ponto:
                            valor_clicado = primeiro_ponto[eixo_tempo]
                
                if valor_clicado is not None:
                    df_final_exibicao = df[df[eixo_tempo] == valor_clicado]
                    st.info(f"⚡ Painel filtrado exclusivamente por: **{valor_clicado}**")
                else:
                    st.info("🌐 Exibindo Totais Consolidados (Ano Completo)")
                
                # Métricas Reativas ao Clique
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Investimento Consolidado", f"R$ {df_final_exibicao['Total_Venda'].sum():,.2f}")
                col_m2.metric("Média do Período", f"R$ {df_final_exibicao['Total_Venda'].mean():,.2f}")
                col_m3.metric("Volume de Itens Alocados", f"{int(df_final_exibicao['Quantidade'].sum())} un")
                
                st.write("### 📋 Detalhamento dos Registros")
                st.dataframe(df_final_exibicao.head(20))
                
            else:
                st.warning("⚠️ Certifique-se de que sua planilha possui as colunas 'Data' e 'Total_Venda'.")
                
        except Exception as e:
            st.error(f"Erro ao processar a planilha: {e}")

# ==========================================
# ABA 2: EXTRATOR OCR DINÂMICO CORRIGIDO (SEM ERROS)
# ==========================================
with tab2:
    st.header("🔍 Extrator Avançado de Documentos (OCR / PDF)")
    arquivo_doc = st.file_uploader("Selecione o documento (Imagem ou PDF)", type=["png", "jpg", "jpeg", "pdf"])
    
    if arquivo_doc is not None:
        is_pdf = arquivo_doc.name.lower().endswith('.pdf')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🖼️ Documento Enviado")
            if is_pdf:
                st.info(f"📄 Arquivo PDF detectado: {arquivo_doc.name}. Clique no botão para extrair os dados estruturados.")
            else:
                imagem = Image.open(arquivo_doc)
                st.image(imagem, caption="Imagem Carregada", use_container_width=True)
            
            if st.button("🚀 Executar Leitura Documental Completa", type="primary"):
                with st.spinner("Processando conteúdo e mapeando metadados..."):
                    texto_cru = ""
                    linhas_originais = []
                    
                    if is_pdf:
                        try:
                            leitor_pdf = PdfReader(arquivo_doc)
                            paginas_texto = [pagina.extract_text() for pagina in leitor_pdf.pages if pagina.extract_text()]
                            texto_cru = "\n".join(paginas_texto)
                            linhas_originais = texto_cru.split('\n')
                        except Exception as pdf_err:
                            st.error(f"Erro ao ler as camadas de texto do PDF: {pdf_err}")
                    else:
                        reader = easyocr.Reader(['pt', 'en'])
                        img_np = np.array(imagem)
                        resultado = reader.readtext(img_np, detail=0)
                        texto_cru = "\n".join(resultado)
                        linhas_originais = resultado
                    
                    # Normalização estrutural de strings
                    linhas_maiusculas = [l.upper().strip() for l in linhas_originais if l.strip()]
                    text_completo_upper = "\n".join(linhas_maiusculas)
                    
                    # Definição dos buffers de metadados padrão
                    fornecedor = "Não identificado claramente (Ajuste ao lado)"
                    destinatario = "Não identificado claramente (Ajuste ao lado)"
                    num_nota = "Não localizado"
                    data_emissao = "Não localizada"
                    cnpj_detectado = "Não localizado"
                    
                    # 1. Identificação direta por padrões conhecidos (Camada rápida)
                    if "NORLESS" in text_completo_upper:
                        fornecedor = "NORLESS COMERCIAL LTDA"
                    if "SERRA VERDE" in text_completo_upper:
                        destinatario = "AGROINDUSTRIAL SERRA VERDE LTDA"
                        
                    # 2. Varredura posicional inteligente e blindada contra estouro de índice
                    for idx, linha in enumerate(linhas_maiusculas):
                        if "CNPJ" in linha or "C.N.P.J" in linha:
                            cnpj_detectado = linhas_originais[idx].strip()
                        
                        # Captura contextual do Fornecedor (De Quem)
                        if fornecedor.startswith("Não identificado"):
                            if "EMITENTE" in linha or "FORNECEDOR" in linha or "RAZAO SOCIAL" in linha:
                                if idx + 1 < len(linhas_originais):
                                    fornecedor = linhas_originais[idx + 1].strip()
                                    
                        # Captura contextual do Destinatário (Para Quem)
                        if destinatario.startswith("Não identificado"):
                            if "DESTINATARIO" in linha or "CLIENTE" in linha or "REMETENTE" in linha:
                                if idx + 1 < len(linhas_originais):
                                    destinatario = linhas_originais[idx + 1].strip()
                                    
                        # Captura limpa do Identificador numérico da nota
                        if "NUMERO" in linha or "NF-E" in linha or "NOTA" in linha or "Nº" in linha:
                            num_filtrado = ''.join(c for c in linha if c.isdigit() or c in ['.', '-'])
                            if num_filtrado:
                                num_nota = num_filtrado
                        
                        # Captura de marcos temporais
                        if "EMISSAO" in linha or "DATA" in linha:
                            if "/" in linha:
                                data_emissao = linhas_originais[idx].strip()

                    # Montagem do layout de exibição na caixa de texto do painel
                    linhas_formatadas = [
                        "=== INFORMAÇÕES ESTRUTURADAS DA NOTA ===",
                        f"Fornecedor (De Quem): {fornecedor}",
                        f"Destinatario (Para Quem): {destinatario}",
                        f"Numero da Nota: {num_nota}",
                        f"Data de Emissao: {data_emissao}",
                        f"Dados de Registro: {cnpj_detectado}",
                        "\n=== TEXTO COMPLETO RECONHECIDO NO SCAN ==="
                    ]
                    
                    # Consolida todas as linhas lidas abaixo para fácil recuperação pelo usuário
                    for l_orig in linhas_originais:
                        if len(l_orig.strip()) > 1:
                            linhas_formatadas.append(f"Detectado: {l_orig.strip()}")
                                
                    st.session_state["texto_extraido"] = "\n".join(linhas_formatadas)
                    st.success("Análise documental concluída!")
                    st.rerun()
                    
        with col2:
            st.subheader("📝 Metadados Estruturados & Ajuste Manual")
            if st.session_state["texto_extraido"]:
                st.session_state["texto_extraido"] = st.text_area(
                    "Informações da Nota (Campos editáveis antes de gerar o PDF):", 
                    value=st.session_state["texto_extraido"], 
                    height=450
                )
            else:
                st.info("Os dados extraídos da fatura/nota aparecerão estruturados aqui após a execução do scanner.")

# ==========================================
# ABA 3: EMISSÃO DE DOCUMENTOS OFICIAIS
# ==========================================
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