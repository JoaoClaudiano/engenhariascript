import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Configuração de UX da Página
st.set_page_config(page_title="EngenhariaScript IDE", layout="wide", page_icon="🛠️")

# Estilização CSS para deixar a interface limpa
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTextArea textarea { font-family: 'Fira Code', monospace; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛠️ EngenhariaScript")
st.subheader("A linguagem de programação feita para engenheiros brasileiros.")

# Barra lateral com tutorial rápido
with st.sidebar:
    st.header("📖 Guia Rápido")
    st.info("""
    **Comandos:**
    - `VARIAVEL nome = valor`
    - `CALCULAR nome = formula`
    - `ANALISAR condicao`
    - `GRAFICO funcao` (ex: sen(x))
    
    **Exemplo:**
    `VARIAVEL massa = 80`
    `CALCULAR peso = massa * 9.81`
    """)
    st.write("---")
    st.success("Dica: Use `//` para comentários.")

# Layout principal: Editor vs Resultado
col_dir, col_esq = st.columns([1, 1])

with col_dir:
    st.markdown("### 📝 Editor de Projeto")
    codigo_padrao = """// Exemplo: Cálculo de Tensão
VARIAVEL forca = 1500
VARIAVEL area = 0.02
CALCULAR tensao = forca / area

// Verificação de Segurança
ANALISAR tensao < 80000

// Visualização Matemática
GRAFICO sen(x) * e^(-0.1*x)"""
    
    input_usuario = st.text_area("Digite seu código em Português:", value=codigo_padrao, height=400)
    btn_rodar = st.button("🚀 Executar e Analisar", use_container_width=True)

with col_esq:
    st.markdown("### 📊 Relatório Técnico")
    
    if btn_rodar:
        # Contexto de execução (Matemática avançada)
        contexto = {"np": np, "plt": plt, "math": math, "e": math.e, "pi": math.pi}
        linhas = input_usuario.split('\n')
        
        try:
            for linha in linhas:
                linha = linha.strip()
                if not linha or linha.startswith("//"): continue
                
                # Tradutor de Comandos
                if "VARIAVEL" in linha or "CALCULAR" in linha:
                    # Remove palavras-chave e limpa a expressão
                    expr = linha.replace("VARIAVEL", "").replace("CALCULAR", "").strip()
                    exec(expr, contexto, contexto)
                
                elif "ANALISAR" in linha:
                    condicao = linha.replace("ANALISAR", "").strip()
                    resultado = eval(condicao, contexto, contexto)
                    if resultado:
                        st.success(f"✅ CONFORMIDADE: {condicao} (Dentro do limite)")
                    else:
                        st.error(f"❌ ALERTA: {condicao} (Fora do limite técnico)")
                
                elif "GRAFICO" in linha:
                    funcao_str = linha.replace("GRAFICO", "").strip()
                    st.write(f"📈 Gráfico da função: `{funcao_str}`")
                    
                    x = np.linspace(0, 20, 200)
                    # Prepara a função para ser avaliada em vetor
                    safe_dict = {"x": x, "np": np, "sen": np.sin, "cos": np.cos, "tan": np.tan, "e": np.e}
                    y = eval(funcao_str.replace("sen", "np.sin").replace("cos", "np.cos"), {}, safe_dict)
                    
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.plot(x, y, color='#007bff', linewidth=2)
                    ax.grid(True, linestyle='--', alpha=0.7)
                    st.pyplot(fig)

            # Tabela de Variáveis Calculadas
            st.markdown("---")
            st.markdown("#### 📋 Memória de Cálculo")
            itens_invalidos = ['np', 'plt', 'math', 'e', 'pi', '__builtins__', 'safe_dict', 'x', 'y']
            resumo = {k: v for k, v in contexto.items() if k not in itens_invalidos and not hasattr(v, '__call__')}
            if resumo:
                st.table(pd.DataFrame(resumo.items(), columns=["Parâmetro", "Valor"]))
                
        except Exception as e:
            st.error(f"⚠️ Erro na Lógica: {e}")
