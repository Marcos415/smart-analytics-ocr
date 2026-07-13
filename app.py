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

# Inicializa as variáveis no session_state para evitar conflitos de renderização
if "texto_extraido" not in st.session_state:
    st.session_state["texto_extraido"] = ""

# --- FUNÇÃO PARA GERAR OS BYTES DO PDF DO RELATÓRIO (CORRIGIDA CONTRA ACENTOS) ---
def generar_pdf_bytes():
    class PDF(FPDF):
        def header(self):
            self.set_fill_color(31, 78, 121)
            self.rect(0, 0, 210, 35, 'F')
            self.set_font("Helvetica", "B", 16)
            self.set_text_color(255, 255, 255)
            self.cell(0, 10, "SMART ANALYTICS & DOCUMENT OCR", ln=True, align="C")
            self.ln(12)
        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Pagina {self.page_no()}", align="C")

    pdf = PDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(31, 78, 121)
    pdf.cell(0, 8, "Informacoes Estruturadas do Documento", ln=True)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(4)

    texto_ocr = st.session_state.get("texto_extraido", "")
    if texto_ocr:
        linhas = texto_ocr.split('\n')
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_fill_color(240, 243, 246)
        pdf.cell(60, 8, " Campo Identificado", border=1, fill=True)
        pdf.cell(120, 8, " Conteudo Extraido", border=1, fill=True, ln=True)
        
        pdf.set_font("Helvetica", "", 9)
        for linha in linhas:
            if ":" in linha:
                parts = linha.split(":", 1)
                
                # Tratamento estrito contra FPDFUnicodeEncodingException (Acentuação)
                campo = parts[0].strip().encode('latin-1', 'ignore').decode('latin-1')
                conteudo = parts[1].strip().encode('latin-1', 'ignore').decode('latin-1')
                
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(60, 7, f" {campo}", border=1)
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(120, 7, f" {conteudo}", border=1, ln=True)
    else:
        pdf.cell(0, 8, "Nenhum dado extraido encontrado.", ln=True)
        
    return bytes(pdf.output())

# --- INTERFACE MASTER ---
st.title("📊 Smart Analytics & Document OCR Dashboard")

tab1, tab2, tab3 = st.tabs(["📊 Análise de Dados", "🔍 Extrator OCR (Documentos)", "📝 Gerador de Relatórios"])

# ==========================================
# ABA 1: ANÁLISE DE DADOS COMPLETA E INTERATIVA (LINHA DO TEMPO POR SEMANAS)
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
            
            # --- DETECÇÃO AUTOMÁTICA E MAPEAMENTO DE COMPATIBILIDADE ---
            if 'Data' in df.columns or 'Total_Venda' in df.columns:
                if 'Parceiro' not in df.columns and 'Produto' in df.columns:
                    df['Parceiro'] = df['Produto']
            elif 'Data de Emissão' in df.columns or 'Valor Nota Fiscal' in df.columns:
                mapeamento_colunas = {
                    'Data de Emissão': 'Data',
                    'Valor Nota Fiscal': 'Total_Venda',
                    'Quantidade Embarcada': 'Quantidade'
                }
                df.rename(columns=mapeamento_colunas, inplace=True)
            
            # --- TRATAMENTO ADAPTATIVO PADRÃO ---
            if 'Total_Venda' in df.columns:
                df['Total_Venda'] = pd.to_numeric(df['Total_Venda'], errors='coerce').fillna(0)
            if 'Quantidade' in df.columns:
                df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce').fillna(0)
            else:
                df['Quantidade'] = 1
                
            if 'Produto' not in df.columns and 'Parceiro' in df.columns:
                df['Produto'] = df['Parceiro']
            
            # --- TRATAMENTO TEMPORAL ULTRA ROBUSTO (MÚLTIPLOS FORMATOS) ---
            if 'Data' in df.columns:
                # Conversão robusta aceitando formatos brasileiros (dia primeiro)
                df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
                df = df.dropna(subset=['Data'])
                
                df['ANO'] = df['Data'].dt.year.astype(str)
                df['Mês'] = df['Data'].dt.strftime('%m - %B')
                df['Dia_Semana'] = df['Data'].dt.strftime('%w - %A')
                
                # CÁLCULO DA SEMANA DENTRO DO MÊS
                df['Semana_do_Mês'] = ((df['Data'].dt.day - 1) // 7) + 1
                df['Semana_do_Mês'] = df['Semana_do_Mês'].astype(str) + "ª Semana"
                
                # --- NOVO: LINHA DO TEMPO CONTÍNUA (Ex: "01 - January | 1ª Semana") ---
                df['Semana_do_Ano'] = df['Mês'] + " | " + df['Semana_do_Mês']
                
            elif 'ANO' in df.columns:
                df['ANO'] = df['ANO'].astype(str)
            
            st.subheader("🎯 Painel de Controle e Destrinchamento Visual")
            
            # --- OPÇÕES DE VISÃO NO SELECTBOX ESTRUTURADAS ---
            opcoes_disponiveis = []
            if 'Mês' in df.columns:
                opcoes_disponiveis.append("Mês")
            if 'Semana_do_Ano' in df.columns: # Adicionando a nova visão contínua!
                opcoes_disponiveis.append("Semana_do_Ano")
            if 'Semana_do_Mês' in df.columns:
                opcoes_disponiveis.append("Semana_do_Mês")
            if 'Dia_Semana' in df.columns:
                opcoes_disponiveis.append("Dia_Semana")
            if 'Parceiro' in df.columns:
                opcoes_disponiveis.append("Parceiro")
            if 'Nº Contrato' in df.columns:
                opcoes_disponiveis.append("Nº Contrato")
            if 'Produto' in df.columns and 'Parceiro' in df.columns: 
                opcoes_disponiveis.append("Produto")
            if 'ESTADO' in df.columns:
                opcoes_disponiveis.append("ESTADO")
            if 'ANO' in df.columns:
                opcoes_disponiveis.append("ANO")
                
            c1, c2 = st.columns(2)
            with c1:
                visao_analitica = st.selectbox(
                    "Destrinchar o gráfico principal por:",
                    opcoes_disponiveis,
                    index=1 if "Semana_do_Ano" in opcoes_disponiveis else 0 # Já foca na Semana do Ano como padrão se existir!
                )
            with c2:
                metrica_analise = st.selectbox(
                    "Métrica analítica do gráfico:",
                    ["Total_Venda", "Quantidade"]
                )
            
            eixo_x_dinamico = visao_analitica
            df_grafico = df.groupby(eixo_x_dinamico)[metrica_analise].sum().reset_index()
            
            # --- LISTAS DE ORDENAÇÃO CRONOLÓGICA ---
            lista_meses_ordenada = [
                "01 - January", "02 - February", "03 - March", "04 - April", 
                "05 - May", "06 - June", "07 - July", "08 - August", 
                "09 - September", "10 - October", "11 - November", "12 - December"
            ]
            lista_semanas_ordenada = ["1ª Semana", "2ª Semana", "3ª Semana", "4ª Semana", "5ª Semana"]
            
            # --- CONSTRUÇÃO DO GRÁFICO ---
            selecao_clique = alt.selection_point(fields=[eixo_x_dinamico], name="Selecione")
            titulo_eixo_y = "Valor Total (R$)" if metrica_analise == "Total_Venda" else "Volume Operacional / Qtd"
            
            if eixo_x_dinamico == "Mês":
                config_eixo_x = alt.X('Mês:N', title="Meses do Ano", sort=lista_meses_ordenada)
            elif eixo_x_dinamico == "Semana_do_Mês":
                config_eixo_x = alt.X('Semana_do_Mês:N', title="Período Mensal", sort=lista_semanas_ordenada)
            elif eixo_x_dinamico == "Semana_do_Ano":
                # Como começa com "01 - January", a ordenação alfabética natural (ascending) ordena perfeitamente de Jan a Dez!
                config_eixo_x = alt.X('Semana_do_Ano:N', title="Linha do Tempo (Semanas do Ano)", sort='ascending')
            else:
                ordenacao_eixo = 'ascending' if eixo_x_dinamico in ["ANO", "Dia_Semana"] else '-y'
                config_eixo_x = alt.X(f'{eixo_x_dinamico}:N', title=f"Visualização por {visao_analitica}", sort=ordenacao_eixo)

            grafico_altair = alt.Chart(df_grafico).mark_bar(color="#1f4e79").encode(
                x=config_eixo_x,
                y=alt.Y(f'{metrica_analise}:Q', title=titulo_eixo_y),
                opacity=alt.condition(selecao_clique, alt.value(1.0), alt.value(0.35)),
                tooltip=[eixo_x_dinamico, metrica_analise]
            ).add_params(
                selecao_clique
            ).properties(
                width='container',
                height=350
            )
            
            res_altair = st.altair_chart(grafico_altair, use_container_width=True, on_select="rerun")
            
            # --- MOTOR DE DETECÇÃO DO FILTRO POR CLIQUE ---
            df_final_exibicao = df.copy()
            valor_clicado = None
            
            if res_altair and "selection" in res_altair and "Selecione" in res_altair["selection"]:
                dados_selecionados = res_altair["selection"]["Selecione"]
                
                if isinstance(dados_selecionados, list) and len(dados_selecionados) > 0:
                    ponto = dados_selecionados[0]
                    if isinstance(ponto, dict) and eixo_x_dinamico in ponto:
                        valor_clicado = ponto[eixo_x_dinamico]
                elif isinstance(dados_selecionados, dict):
                    if "value" in dados_selecionados and isinstance(dados_selecionados["value"], list) and len(dados_selecionados["value"]) > 0:
                        valor_clicado = dados_selecionados["value"][0]
                    elif eixo_x_dinamico in dados_selecionados:
                        val = dados_selecionados[eixo_x_dinamico]
                        if isinstance(val, list) and len(val) > 0:
                            valor_clicado = val[0]
                        else:
                            valor_clicado = val
            
            if valor_clicado is not None:
                df_final_exibicao = df[df[eixo_x_dinamico].astype(str) == str(valor_clicado)]
                st.info(f"⚡ Painel filtrado exclusivamente por {visao_analitica}: **{valor_clicado}**")
            else:
                st.info("🌐 Exibindo Totais Consolidados (Clique em uma barra para filtrar / Clique fora para limpar)")
            
            # --- CÁLCULO DINÂMICO DOS CARDS ---
            campo_top_card = "Parceiro" if "Nº Contrato" in df.columns else "Produto"
            nome_destaque = "Nenhum"
            if campo_top_card in df_final_exibicao.columns and not df_final_exibicao.empty:
                nome_destaque = str(df_final_exibicao.groupby(campo_top_card)['Total_Venda'].sum().idxmax())
                
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Valor Total Acumulado", f"R$ {df_final_exibicao['Total_Venda'].sum():,.2f}")
            col_m2.metric("Média dos Registros", f"R$ {df_final_exibicao['Total_Venda'].mean():,.2f}")
            col_m3.metric("Volume/Qtd Total", f"{df_final_exibicao['Quantidade'].sum():,.0f} un")
            col_m4.metric(f"🏆 Líder ({campo_top_card})", f"{nome_destaque}")
            
            # --- GRÁFICO DE RANKING SECUNDÁRIO ---
            if 'Produto' in df_final_exibicao.columns:
                titulo_ranking = "📦 Itens/Produtos movimentados no escopo" if "Nº Contrato" in df.columns else "📈 Desempenho por Categoria de Produto"
                st.write(f"### {titulo_ranking}")
                
                df_prod_rank = df_final_exibicao.groupby('Produto')[['Quantidade', 'Total_Venda']].sum().reset_index()
                
                grafico_produtos = alt.Chart(df_prod_rank).mark_bar(color="#2e75b6").encode(
                    x=alt.X(f'{metrica_analise}:Q', title=f"Total de {metrica_analise}"),
                    y=alt.Y('Produto:N', title="Item", sort='-x'),
                    tooltip=['Produto', 'Quantidade', 'Total_Venda']
                ).properties(
                    width='container',
                    height=220
                )
                st.altair_chart(grafico_produtos, use_container_width=True)
            
            # --- DETALHAMENTO EM TABELA ---
            st.write("### 📋 Relação Estruturada dos Dados")
            colunas_possiveis = ['ANO', 'Mês', 'Semana_do_Mês', 'Semana_do_Ano', 'Nº Contrato', 'Parceiro', 'Nota Fiscal', 'Data', 'Total_Venda', 'Quantidade', 'ESTADO', 'Produto', 'Tipo']
            colunas_exibicao = [c for c in colunas_possiveis if c in df_final_exibicao.columns]
            
            st.dataframe(df_final_exibicao[colunas_exibicao].head(50), use_container_width=True)
            
        except Exception as e:
            st.error(f"Erro ao processar a planilha: {e}")

# ==========================================
# ABA 2: EXTRATOR OCR (CORRIGIDO E SEGURO)
# ==========================================
with tab2:
    st.header("🔍 Extrator Avançado de Documentos (OCR / PDF)")
    arquivo_doc = st.file_uploader("Selecione o documento (Imagem ou PDF)", type=["png", "jpg", "jpeg", "pdf"], key="uploader_ocr_unico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🖼️ Documento Enviado")
        if arquivo_doc is not None:
            is_pdf = arquivo_doc.name.lower().endswith('.pdf')
            if is_pdf:
                st.info(f"📄 Arquivo PDF detectado: {arquivo_doc.name}.")
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
                            st.error(f"Erro ao ler PDF: {pdf_err}")
                    else:
                        try:
                            reader = easyocr.Reader(['pt', 'en'])
                            img_np = np.array(imagem)
                            resultado = reader.readtext(img_np, detail=0)
                            texto_cru = "\n".join(resultado)
                            linhas_originais = resultado
                        except Exception as ocr_err:
                            st.error(f"Erro no EasyOCR: {ocr_err}")
                    
                    if linhas_originais:
                        linhas_maiusculas = [l.upper().strip() for l in linhas_originais if l.strip()]
                        text_completo_upper = "\n".join(linhas_maiusculas)
                        
                        fornecedor = "Não identificado claramente (Ajuste ao lado)"
                        destinatario = "Não identificado claramente (Ajuste ao lado)"
                        num_nota = "Não localizado"
                        data_emissao = "Não localizada"
                        cnpj_detectado = "Não localizado"
                        
                        if "NORLESS" in text_completo_upper:
                            fornecedor = "NORLESS COMERCIAL LTDA"
                        if "SERRA VERDE" in text_completo_upper:
                            destinatario = "AGROINDUSTRIAL SERRA VERDE LTDA"
                            
                        for idx, linha in enumerate(linhas_maiusculas):
                            if "CNPJ" in linha or "C.N.P.J" in linha:
                                cnpj_detectado = linhas_originais[idx].strip()
                            
                            if fornecedor.startswith("Não identificado") and ("EMITENTE" in linha or "FORNECEDOR" in linha or "RAZAO" in linha):
                                if idx + 1 < len(linhas_originais):
                                    fornecedor = linhas_originais[idx + 1].strip()
                                        
                            if destinatario.startswith("Não identificado") and ("DESTINATARIO" in linha or "CLIENTE" in linha or "REMETENTE" in linha):
                                if idx + 1 < len(linhas_originais):
                                    destinatario = linhas_originais[idx + 1].strip()
                                        
                            if "NUMERO" in linha or "NF-E" in linha or "NOTA" in linha or "Nº" in linha:
                                num_filtrado = ''.join(c for c in linha if c.isdigit() or c in ['.', '-'])
                                if num_filtrado:
                                    num_nota = num_filtrado
                            
                            if "EMISSAO" in linha or "DATA" in linha:
                                if "/" in linha:
                                    data_emissao = linhas_originais[idx].strip()

                        linhas_formatadas = [
                            "=== INFORMAÇÕES ESTRUTURADAS DA NOTA ===",
                            f"Fornecedor (De Quem): {fornecedor}",
                            f"Destinatario (Para Quem): {destinatario}",
                            f"Numero da Nota: {num_nota}",
                            f"Data de Emissao: {data_emissao}",
                            f"Dados de Registro: {cnpj_detectado}",
                            "\n=== TEXTO COMPLETO RECONHECIDO NO SCAN ==="
                        ]
                        
                        for l_orig in linhas_originais:
                            if len(l_orig.strip()) > 1:
                                linhas_formatadas.append(f"Detectado: {l_orig.strip()}")
                                    
                        conteudo_final = "\n".join(linhas_formatadas)
                        st.session_state["texto_extraido"] = conteudo_final
                        st.success("Análise documental concluída!")
                        st.rerun()
                    else:
                        st.warning("⚠️ O documento foi carregado, mas nenhum texto legível foi extraído.")
        else:
            st.info("Aguardando upload de documento...")

    with col2:
        st.subheader("📝 Metadados Estruturados & Ajuste Manual")
        st.text_area(
            "Informações da Nota (Campos editáveis antes de gerar o PDF):", 
            key="texto_extraido", 
            height=500
        )

# ==========================================
# ABA 3: EMISSÃO DE DOCUMENTOS
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