import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import re

# --- CONFIGURAÇÕES DE INTERFACE ---
st.set_page_config(page_title="EngenhariaScript PRO", layout="wide", page_icon="🏗️")

st.markdown("""
    <style>
    .stTextArea textarea { font-family: 'Fira Code', monospace; background-color: #1e1e1e; color: #d4d4d4; }
    .status-box { padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- MOTOR DA LINGUAGEM (O TRANSPILADOR) ---
def transpilar_para_python(codigo_pt):
    # Dicionário de tradução de palavras-chave
    traducoes = {
        r'\bVARIAVEL\b': '',
        r'\bCALCULAR\b': '',
        r'\bSE\b': 'if',
        r'\bENTAO\b': ':',
        r'\bSENAO\b': 'else:',
        r'\bPARA\b': 'for',
        r'\bDE\b': 'in range(',
        r'\bATE\b': ',',
        r'\bFACA\b': '):',
        r'\bEXIBIR\b': 'print',
        r'\bFIM\b': '', # Python usa indentação, então FIM é visual
        r'\bsen\(': 'np.sin(',
        r'\bcos\(': 'np.cos(',
        r'\braiz\(': 'math.sqrt(',
    }
    
    linhas = codigo_pt.split('\n')
    codigo_py = ["import numpy as np", "import math", "resultados_exibidos = []"]
    
    # Substituindo comandos e ajustando o print para o Streamlit
    for linha in linhas:
        if not linha.strip() or linha.strip().startswith("//"): continue
        
        linha_convertida = linha
        for pt, py in traducoes.items():
            linha_convertida = re.sub(pt, py, linha_convertida)
        
        # Captura o que seria impresso para mostrar na interface
        if "print" in linha_convertida:
            linha_convertida = linha_convertida.replace("print", "resultados_exibidos.append")
            
        codigo_py.append(linha_convertida)
    
    return "\n".join(codigo_py)

# --- INTERFACE ---
st.title("🏗️ EngenhariaScript PRO v2.0")
st.caption("A primeira linguagem brasileira focada em introdução à engenharia.")

col_editor, col_visual = st.columns([1.2, 0.8])

with col_editor:
    st.write("### ⌨️ Editor")
    codigo_exemplo = """// Exemplo de Repetição e Condição
VARIAVEL limite = 50
PARA i DE 1 ATE 5 FACA
    CALCULAR forca = i * 15
    SE forca > limite ENTAO
        EXIBIR f"Alerta: Forca {forca} acima do limite!"
    SENAO
        EXIBIR f"Carga {forca} segura."

// Gerar dados para gráfico
VARIAVEL x = np.linspace(0, 10, 100)
VARIAVEL y = sen(x)
GRAFICO x, y"""

    codigo_usuario = st.text_area("Escreva seu código técnico em Português:", value=codigo_exemplo, height=450)
    btn_executar = st.button("🚀 Compilar e Rodar Projeto", use_container_width=True)

with col_visual:
    st.write("### 📟 Console de Saída")
    
    if btn_executar:
        try:
            # 1. Transpilação
            codigo_final = transpilar_para_python(codigo_usuario)
            
            # 2. Execução com captura de contexto
            contexto_global = {"np": np, "math": math}
            exec(codigo_final, contexto_global)
            
            # 3. Exibição de Prints
            if "resultados_exibidos" in contexto_global:
                for res in contexto_global["resultados_exibidos"]:
                    st.code(res, language="text")
            
            # 4. Exibição de Gráficos (se houver x e y no contexto)
            if "x" in contexto_global and "y" in contexto_global:
                st.write("📈 **Análise Gráfica:**")
                fig, ax = plt.subplots()
                ax.plot(contexto_global["x"], contexto_global["y"], color='red')
                ax.grid(True)
                st.pyplot(fig)
                
            # 5. Tabela de Memória
            st.write("📋 **Variáveis em Memória:**")
            vars_limpas = {k: v for k, v in contexto_global.items() if k not in ['np', 'math', '__builtins__', 'resultados_exibidos', 'x', 'y']}
            st.table(pd.DataFrame(vars_limpas.items(), columns=["Parâmetro", "Valor"]))

        except Exception as e:
            st.error(f"❌ Erro de Compilação: {e}")
            st.info("Dica: Verifique se você esqueceu o ENTAO após o SE ou o FACA após o PARA.")

