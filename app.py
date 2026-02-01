import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
from code_editor import code_editor
import re

# --- CONFIGURAÇÃO DA IA ---
API_KEY = "AIzaSyBcxiv2H-nxOTsVfHabQYRsbTlRoK7UKWo" 
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Erro na Configuração da IA: {e}")
    model = None

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="EngenhariaScript Academy", layout="wide", page_icon="🎓")

# --- BANCO DE MISSÕES ---
MISSÕES = [
    {
        "id": 1,
        "titulo": "1. Estática: Cálculo de Carga",
        "objetivo": "Calcule a tensão normal (Tensão = Força / Área).",
        "enunciado": "Use VARIAVEL f = 5000 e a = 0.02. Calcule 'tensao' e exiba.",
        "exemplo": "VARIAVEL f = 5000\nVARIAVEL a = 0.02\nCALCULAR tensao = f / a\nEXIBIR f'A tensão calculada é {tensao} Pa'",
        "validação": lambda escopo: escopo.get("tensao") == 250000
    },
    {
        "id": 2,
        "titulo": "2. Lógica: Segurança de Barragem",
        "objetivo": "Verificar nível de alerta usando SE/ENTAO.",
        "enunciado": "Se nivel > 80, EXIBIR 'ALERTA'. Caso contrário, 'NORMAL'.",
        "exemplo": "VARIAVEL nivel = 85\nSE nivel > 80 ENTAO\n    EXIBIR 'ALERTA MÁXIMO'\nSENAO\n    EXIBIR 'NÍVEL SEGURO'\nFIM",
        "validação": lambda escopo: "saida_texto" in escopo
    }
]

# --- MOTOR DE TRADUÇÃO ---
def transpilador(codigo_pt):
    traducao = {
        'VARIAVEL ': '', 'CALCULAR ': '', 'SE ': 'if ', ' ENTAO': ':',
        'SENAO': 'else:', 'PARA ': 'for ', ' DE ': ' in range(',
        ' ATE ': ', ', ' FACA': '):', 'EXIBIR ': 'saida_texto.append(',
        'FIM': '#', 'sen': 'np.sin', 'cos': 'np.cos', 'raiz': 'np.sqrt'
    }
    linhas_py = ["import numpy as np", "saida_texto = []"]
    for linha in codigo_pt.split('\n'):
        l = linha.strip()
        if not l or l.startswith("//"): continue
        if "EXIBIR" in l: l += ")"
        for pt, py in traducao.items():
            l = l.replace(pt, py)
        linhas_py.append(l)
    return "\n".join(linhas_py)

# --- INTERFACE SIDEBAR ---
with st.sidebar:
    st.title("🎓 Central do Aluno")
    aba_missao, aba_ajuda = st.tabs(["🎯 Missões", "📖 Glossário"])
    
    with aba_missao:
        st.write("### Trilha de Aprendizado")
        idx = st.selectbox("Selecione a Missão:", range(len(MISSÕES)), format_func=lambda i: MISSÕES[i]["titulo"])
        missao = MISSÕES[idx]
        st.info(f"**Objetivo:** {missao['objetivo']}")
        st.write(missao['enunciado'])
        
        if st.button("🪄 Autopreencher Exemplo"):
            st.session_state['codigo_atual'] = missao['exemplo']
            st.rerun()

    with aba_ajuda:
        st.markdown("""
        **Comandos Rápidos:**
        - `VARIAVEL x = 10`
        - `CALCULAR y = x * 2`
        - `SE x > 5 ENTAO ... SENAO ... FIM`
        - `PARA i DE 1 ATE 10 FACA ... FIM`
        - `EXIBIR "Mensagem"`
        """)

# --- CORPO PRINCIPAL ---
st.header("🏗️ IDE EngenhariaScript v3.0")

if 'codigo_atual' not in st.session_state:
    st.session_state['codigo_atual'] = "// Bem-vindo! Escolha uma missão ao lado.\n"

col_code, col_res = st.columns([1.2, 0.8])

with col_code:
    # Editor com autopreenchimento dinâmico
    response = code_editor(st.session_state['codigo_atual'], lang="python", theme="monokai", options={"showLineNumbers": True})
    
    c1, c2 = st.columns(2)
    with c1:
        executar = st.button("🚀 Executar Projeto", use_container_width=True)
    with c2:
        ajuda_ia = st.button("🤖 Pedir Ajuda ao Tutor IA", use_container_width=True)

with col_res:
    st.subheader("📟 Console & Gráficos")
    if executar:
        try:
            py_code = transpilador(response['text'])
            escopo = {"np": np, "pd": pd, "st": st}
            exec(py_code, escopo)
            
            # 1. Saída de Texto
            if "saida_texto" in escopo:
                for msg in escopo["saida_texto"]:
                    st.code(msg, language="text")
            
            # 2. Validação de Missão
            if missao["validação"](escopo):
                st.balloons()
                st.success("✅ Missão Concluída com Sucesso!")
            
            # 3. Gráficos Automáticos
            # Se o aluno definir vetores 'x' e 'y', o gráfico aparece
            if "x" in escopo and "y" in escopo:
                df = pd.DataFrame({'x': escopo['x'], 'y': escopo['y']})
                fig = px.line(df, x='x', y='y', title="Gráfico de Engenharia (Interativo)")
                fig.update_traces(line_color='#00ff00')
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Erro na execução: {e}")

# --- TUTOR IA ---
if ajuda_ia and model:
    with st.expander("🧠 Tutor Inteligente Gemini", expanded=True):
        with st.spinner("Analisando sua lógica de engenharia..."):
            prompt = f"""
            Você é um professor de engenharia. Analise este código em português:
            {response['text']}
            O aluno está tentando resolver: {missao['objetivo']}.
            Se houver erros de cálculo ou lógica, explique de forma pedagógica.
            Se estiver correto, sugira um próximo passo desafiador.
            """
            ia_res = model.generate_content(prompt)
            st.markdown(ia_res.text)

