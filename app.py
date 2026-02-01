import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
from code_editor import code_editor
import re

# --- CONFIGURAÇÃO DA IA (GEMINI) ---
# Dica: No Streamlit Cloud, use st.secrets para esconder sua chave
API_KEY = "SUA_CHAVE_AQUI" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="EngenhariaScript Ultimate", layout="wide", page_icon="🎓")

# --- TRADUTOR ROBUSTO ---
def tradutor_pro(codigo_pt, inputs):
    dicionario = {
        'VARIAVEL ': '', 'CALCULAR ': '', 'SE ': 'if ', ' ENTAO': ':',
        'SENAO': 'else:', 'PARA ': 'for ', ' DE ': ' in range(',
        ' ATE ': ', ', ' FACA': '):', 'EXIBIR': 'st.write', 'FIM': '#',
        'sen': 'np.sin', 'cos': 'np.cos', 'raiz': 'np.sqrt'
    }
    
    linhas_py = ["import numpy as np", "import pandas as pd"]
    
    for linha in codigo_pt.split('\n'):
        l = linha.strip()
        if not l or l.startswith("//"): continue
        
        # Tratamento de ENTRADA
        if "ENTRADA" in l:
            match = re.search(r'VARIAVEL\s+(\w+)\s+=\s+ENTRADA', l)
            if match:
                var_nome = match.group(1)
                l = f"{var_nome} = {inputs.get(var_nome, 0.0)}"
        
        for pt, py in dicionario.items():
            l = l.replace(pt, py)
        linhas_py.append(l)
    
    return "\n".join(linhas_py)

# --- INTERFACE ---
st.title("🏗️ EngenhariaScript Ultimate Edition")
st.markdown("---")

with st.sidebar:
    st.header("🎮 Painel de Controle")
    st.write("Configure as entradas do comando `ENTRADA`:")
    # Aqui os alunos definem os valores que o código vai usar
    val1 = st.number_input("Entrada: valor1", value=10.0)
    val2 = st.number_input("Entrada: valor2", value=5.0)
    entradas = {"valor1": val1, "valor2": val2}
    
    st.divider()
    st.write("🤖 **Tutor IA**")
    ajuda_ia = st.button("✨ Analisar meu Código com IA")

col_ed, col_res = st.columns([1.1, 0.9])

with col_ed:
    st.subheader("📝 Editor de Código")
    codigo_init = """// Exemplo de Cálculo com IA e Entrada
VARIAVEL valor1 = ENTRADA("valor1")
VARIAVEL valor2 = ENTRADA("valor2")

CALCULAR resultado = valor1 * valor2

SE resultado > 100 ENTAO
    EXIBIR f"Resultado {resultado} é ALTO"
SENAO
    EXIBIR f"Resultado {resultado} é BAIXO"
FIM

// Gráfico Interativo
VARIAVEL x = np.linspace(0, 10, 20)
VARIAVEL y = x * valor1
"""
    # Editor com numeração de linha e indentação
    ed_response = code_editor(codigo_init, lang="python", theme="monokai", height=[20, 30])

with col_res:
    st.subheader("📊 Resultados e Análise")
    if st.button("🚀 Rodar Projeto", use_container_width=True):
        try:
            py_code = tradutor_pro(ed_response['text'], entradas)
            escopo = {"st": st, "np": np, "pd": pd}
            exec(py_code, escopo)
            
            if "x" in escopo and "y" in escopo:
                fig = px.line(x=escopo['x'], y=escopo['y'], title="Gráfico de Engenharia (Exportável)")
                st.plotly_chart(fig)
        except Exception as e:
            st.error(f"Erro no código: {e}")

# --- LÓGICA DO TUTOR IA ---
if ajuda_ia:
    st.toast("IA analisando seu código...", icon="🧠")
    prompt = f"""
    Você é um professor de engenharia. Analise este código escrito em uma linguagem simplificada em português:
    {ed_response['text']}
    
    Explique:
    1. O que a lógica está fazendo.
    2. Se há algum erro conceitual de engenharia.
    3. Como o aluno pode melhorar.
    Seja breve, motivador e técnico.
    """
    try:
        response = model.generate_content(prompt)
        st.markdown(f"### 🤖 Feedback do Tutor IA\n{response.text}")
    except Exception as e:
        st.warning("IA indisponível. Verifique sua Chave de API.")

