# 📊 Smart Analytics & Document OCR Dashboard

[![Streamlit App](https://static.streamlit.io/badge_svg.svg)](https://smart-analytics-ocr-as7b4huezl5wycqyppizes.streamlit.app/)

Um sistema unificado de Inteligência de Negócios (BI) e Visão Computacional desenvolvido em Python. A aplicação resolve uma dor real das empresas: a automação da leitura de documentos fiscais/faturas (dados não estruturados) integrada a um ecossistema de análise de dados dinâmico e tomadas de decisão baseadas em dados.

---

## 🎯 O Problema de Negócio Resolvido
Processos manuais de digitação de notas fiscais e relatórios geram gargalos operacionais, erros de digitação e atrasos na tomada de decisão. Esta solução automatiza o ciclo completo:
1. **Ingestão:** Upload centralizado de arquivos heterogêneos (Excel, CSV, PDFs e Imagens).
2. **Processamento:** Extração inteligente de metadados textuais através de OCR (Optical Character Recognition).
3. **Análise:** Visualização de indicadores financeiros através de gráficos bidirecionais e reativos.
4. **Governança:** Exportação de relatórios gerenciais estruturados em PDF de forma automatizada.

---

## 🚀 Funcionalidades Principais

### 1. 📊 Aba 1: Análise Inteligente de Planilhas
* **Painel Reativo com Altair:** Gráficos interativos onde o clique em uma barra (Mês, Semana ou Dia) filtra instantaneamente todo o restante do dashboard em tempo real utilizando gerenciamento avançado de estado (`st.session_state`).
* **Métricas Consolidadas:** Cálculo dinâmico de Investimento Consolidado, Média do Período e Volume de Itens Alocados.
* **Filtro Granular:** Exibição imediata das top 20 linhas correspondentes ao período selecionado pelo usuário no gráfico.

### 2. 🔍 Aba 2: Extrator Avançado de Documentos (OCR)
* **Visão Computacional de Ponta:** Integração com a biblioteca `EasyOCR` para mapear e digitalizar textos em imagens (JPG, JPEG, PNG).
* **Leitura Nativa de PDFs:** Integração com `PyPDF` para extração direta de fluxos de texto de documentos digitais.
* **Mapeamento de Metadados:** Algoritmos de varredura que identificam e isolam automaticamente campos críticos como *Fornecedor*, *Destinatário*, *Número da Nota*, *Data de Emissão* e *CNPJ*.
* **Ajuste Humano (Human-in-the-loop):** Campo de texto interativo que permite ao usuário revisar e editar os dados extraídos antes da consolidação.

### 3. 📝 Aba 3: Central de Emissão de Relatórios
* **Geração Dinâmica de PDFs:** Conversão do texto estruturado da nota em um documento PDF formal usando a biblioteca `FPDF`.
* **Segurança de Codificação:** Implementação de tratamento estrito de caracteres e decodificação (`latin-1`) para evitar quebras ou falhas com acentuações da língua portuguesa.

---

## 🛠️ Tecnologias e Ferramentas Utilizadas

* **Linguagem:** Python 3.x
* **Interface Web:** Streamlit
* **Visão Computacional / OCR:** EasyOCR & PyTorch
* **Manipulação de Dados:** Pandas & Numpy
* **Visualização de Dados:** Altair (Vega-Lite)
* **Manipulação de Arquivos e PDFs:** PyPDF (PdfReader) & FPDF

---

## 🔧 Como Executar o Projeto Localmente

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/Marcos415/smart-analytics-ocr.git](https://github.com/Marcos415/smart-analytics-ocr.git)
   cd smart-analytics-ocr