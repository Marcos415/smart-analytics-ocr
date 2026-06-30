import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import easyocr  # Motor OCR 100% Python
import numpy as np
from fpdf import FPDF  # Biblioteca para geração de relatórios PDF

# 1. Configuração da página (Deve ser sempre o primeiro comando Streamlit)
st.set_page_config(
    page_title="Smart Analytics & OCR Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Título Principal da Aplicação
st.title("📊 Smart Analytics & Document OCR Dashboard")
st.markdown("---")

# 3. Criação das Abas de Navegação
aba_analytics, aba_ocr, aba_relatorio = st.tabs([
    "📈 Análise de Dados", 
    "🔍 Extrator OCR (Documentos)", 
    "📋 Gerador de Relatórios"
])

# Inicializa variáveis no st.session_state se elas não existirem
if 'texto_ocr' not in st.session_state:
    st.session_state['texto_ocr'] = ""
if 'total_registros_df' not in st.session_state:
    st.session_state['total_registros_df'] = 0

# =====================================================================
# ABA 1: ANÁLISE DE DADOS
# =====================================================================
with aba_analytics:
    st.header("Análise Inteligente de Planilhas")
    st.write("Faça o upload de uma planilha ou utilize os dados de demonstração para testar os gráficos.")
    
    # Upload do arquivo pelo usuário
    arquivo_dados = st.file_uploader("Selecione sua planilha", type=["csv", "xlsx"], key="uploader_dados")
    df = None

    if arquivo_dados is not None:
        try:
            # Detecta extensão e lê o arquivo corretamente
            df = pd.read_csv(arquivo_dados) if arquivo_dados.name.endswith('.csv') else pd.read_excel(arquivo_dados)
            st.success("Arquivo carregado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            
    # Dados de demonstração caso o usuário não queira subir um arquivo agora
    else:
        st.info("💡 Dica: Você pode ativar os dados de demonstração abaixo para ver o painel em ação.")
        if st.checkbox("Usar dados de demonstração (Vendas de Tecnologia)"):
            dados_teste = {
                "Data": pd.date_range(start="2026-01-01", periods=10, freq="D").strftime("%Y-%m-%d"),
                "Produto": ["Notebook Pro", "Monitor 24'", "Teclado Mecânico", "Mouse Sem Fio", "Notebook Pro", "Monitor 24'", "Cadeira Gamer", "Mouse Sem Fio", "Teclado Mecânico", "Notebook Pro"],
                "Categoria": ["Hardware", "Monitores", "Periféricos", "Periféricos", "Hardware", "Monitores", "Móveis", "Periféricos", "Periféricos", "Hardware"],
                "Quantidade": [2, 5, 10, 12, 1, 3, 2, 15, 8, 3],
                "Faturamento (R$)": [12000, 7500, 4500, 3600, 6000, 4500, 5000, 4500, 3600, 18000]
            }
            df = pd.DataFrame(dados_teste)

    # Renderiza os elementos visuais caso haja dados carregados
    if df is not None:
        st.session_state['total_registros_df'] = len(df) # Armazena a quantidade de linhas para o PDF
        
        with st.expander("👀 Visualizar Dados Brutos (Tabela)"):
            st.dataframe(df)
            
        # Filtra colunas automaticamente por tipo
        colunas_texto = df.select_dtypes(include=['object', 'category']).columns.tolist() or df.columns.tolist()
        colunas_numericas = df.select_dtypes(include=['number']).columns.tolist()
        
        st.subheader("💡 Métricas Gerais")
        m1, m2 = st.columns(2)
        m1.metric(label="Total de Registros (Linhas)", value=len(df))
        if colunas_numericas:
            m2.metric(label=f"Soma Total da última coluna numérica ({colunas_numericas[-1]})", value=f"R$ {df[colunas_numericas[-1]].sum():,.2f}")
        
        st.markdown("---")
        st.subheader("📊 Construção Dinâmica de Gráficos")
        c1, c2 = st.columns(2)
        eixo_x = c1.selectbox("Escolha a categoria (Eixo X):", options=colunas_texto)
        eixo_y = c2.selectbox("Escolha o valor métrico (Eixo Y):", options=colunas_numericas) if colunas_numericas else None

        if eixo_y:
            g1, g2 = st.columns(2)
            
            # Gráfico 1: Barras Agrupadas
            df_grouped = df.groupby(eixo_x)[eixo_y].sum().reset_index()
            fig_bar = px.bar(df_grouped, x=eixo_x, y=eixo_y, color=eixo_x, template="plotly_white")
            g1.plotly_chart(fig_bar, use_container_width=True)
            
            # Gráfico 2: Evolução Temporal / Linhas
            fig_line = px.line(df, x=df.columns[0], y=eixo_y, markers=True, template="plotly_white")
            g2.plotly_chart(fig_line, use_container_width=True)

# =====================================================================
# ABA 2: EXTRATOR OCR (EASYOCR)
# =====================================================================
with aba_ocr:
    st.header("Extração de Texto de Documentos (OCR)")
    st.write("Faça o upload de uma imagem nítida de um documento para extrair os textos em tempo real.")
    
    arquivo_imagem = st.file_uploader("Selecione a imagem do documento", type=["jpg", "jpeg", "png"], key="uploader_img")
    
    if arquivo_imagem is not None:
        imagem = Image.open(arquivo_imagem)
        col_img, col_txt = st.columns(2)
        
        with col_img:
            st.subheader("🖼️ Documento Enviado")
            st.image(imagem, use_container_width=True)
            
        with col_txt:
            st.subheader("📝 Texto Extraído via OCR")
            
            if st.button("🚀 Executar Leitura OCR", type="primary"):
                with st.spinner("Inicializando o motor de leitura... (A primeira execução pode demorar alguns segundos)"):
                    try:
                        reader = easyocr.Reader(['pt', 'en'], gpu=False)
                        img_array = np.array(imagem)
                        resultados = reader.readtext(img_array, detail=0)
                        texto_extraido = "\n".join(resultados)
                        
                        st.session_state['texto_ocr'] = texto_extraido if texto_extraido.strip() else "Nenhum texto claro detectado."
                        st.success("Leitura concluída com sucesso!")
                    except Exception as e:
                        st.error(f"Erro no processamento do EasyOCR: {e}")
            
            texto_final = st.text_area("Resultado do Scan (Editável):", value=st.session_state['texto_ocr'], height=300)
            st.session_state['texto_ocr'] = texto_final

# =====================================================================
# ABA 3: GERADOR DE RELATÓRIOS (CORRIGIDO)
# =====================================================================
with aba_relatorio:
    st.header("📋 Exportação de Resultados em PDF")
    st.write("Gere um documento consolidado contendo os dados processados nas abas anteriores.")
    
    titulo_relatorio = st.text_input("Título do Relatório:", "Relatório Consolidado de Operações")
    responsavel = st.text_input("Responsável Técnico:", "Marcos - TI Infraestrutura")
    
    st.markdown("---")
    
    def generar_pdf_bytes():
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho estruturado
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, titulo_relatorio, ln=True, align="C")
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 10, f"Emitido por: {responsavel}", ln=True, align="C")
        pdf.line(10, 30, 200, 30)
        pdf.ln(10)
        
        # Seção 1: Dados Gerenciais da Planilha
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "1. Resumo da Análise de Dados", ln=True)
        pdf.set_font("Helvetica", "", 12)
        total_linhas = st.session_state['total_registros_df']
        
        # LINHA CORRIGIDA ABAIXO (Aspas fechadas corretamente):
        pdf.cell(0, 8, f"Total de registros processados na planilha: {total_linhas}", ln=True)
        pdf.ln(5)
        
        # Seção 2: Histórico/Logs do Processamento OCR
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "2. Conteúdo Extraído via OCR", ln=True)
        pdf.set_font("Helvetica", "", 11)
        
        texto_ocr_limpo = st.session_state['texto_ocr']
        if texto_ocr_limpo:
            texto_formatado = texto_ocr_limpo.encode('latin-1', 'ignore').decode('latin-1')
            pdf.multi_cell(0, 6, texto_formatado)
        else:
            pdf.cell(0, 8, "Nenhum documento processado na aba de OCR.", ln=True)
            
        # O fpdf2 moderno aceita retornar em formato de string de bytes destrutiva se passarmos vazio ou usar output direto
        return bytes(pdf.output())

    # Executa a geração e entrega os bytes estáveis para download
    pdf_output = generar_pdf_bytes()
    
    st.download_button(
        label="📥 Baixar Relatório em PDF",
        data=pdf_output,
        file_name="relatorio_final.pdf",
        mime="application/pdf",
        type="primary"
    )