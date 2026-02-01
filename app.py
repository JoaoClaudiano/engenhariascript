import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
import time
from code_editor import code_editor
import re

# --- CONFIGURAÇÃO DA IA GRATUITA (Hugging Face) ---
HF_TOKEN = "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"
API_URL = "https://api-inference.huggingface.co/models/MistralAI/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def perguntar_ia(prompt_texto):
    payload = {
        "inputs": f"<s>[INST] Você é um professor de engenharia. Analise este código e explique em português de forma simples: {prompt_texto} [/INST]",
        "parameters": {"max_new_tokens": 400, "temperature": 0.5}
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            res = response.json()
            # Tratamento para diferentes formatos de retorno da API
            if isinstance(res, list): return res[0]['generated_text'].split("[/INST]")[-1]
            return res['generated_text'].split("[/INST]")[-1]
        elif response.status_code == 503:
            return "⏳ A IA está aquecendo os motores (modelo carregando). Tente novamente em 10 segundos!"
        else:
            return f"⚠️ Erro na conexão: {response.status_code}"
    except:
        return "❌ Ocorreu uma falha na comunicação com o servidor da IA."

# --- INTERFACE E UX ---
st.set_page_config(page_title="EngenhariaScript Academy", layout="wide", page_icon="🏗️")

# Estilo para melhorar a visualização
st.markdown("<style>.stCodeBlock { background-color: #0e1117; }</style>", unsafe_allow_html=True)

with st.sidebar:
    st.title("🎓 Guia do Aluno")
    missao = st.selectbox("Selecione a Missão:", [
        "1. Estática: Tensão", 
        "2. Elétrica: Lei de Ohm",
        "3. Loops: Carga Progressiva"
    ])
    
    st.divider()
    st.markdown("""
    **📜 Glossário Rápido:**
    - `VARIAVEL`: Cria um dado.
    - `CALCULAR`: Resolve fórmulas.
    - `SE / ENTAO`: Decisões.
    - `EXIBIR`: Mostra no console.
    """)

st.header("🏗️ IDE EngenhariaScript PRO")

# Layout de colunas
col_ed, col_res = st.columns([1.2, 0.8])

# Gerenciamento do código no estado da sessão
if 'codigo' not in st.session_state:
    st.session_state['codigo'] = "// Digite seu código de engenharia aqui\nVARIAVEL força = 1000\nVARIAVEL área = 0.05\nCALCULAR tensão = força / área\nEXIBIR tensão"

with col_ed:
    # Editor com numeração de linhas e indentação
    config_ed = {"showLineNumbers": True, "tabSize": 4}
    res_editor = code_editor(st.session_state['codigo'], lang="python", theme="monokai", options=config_ed)
    
    c1, c2 = st.columns(2)
    executar = c1.button("🚀 Executar Projeto", use_container_width=True)
    ajuda_ia = c2.button("🤖 Tutor IA (Mistral)", use_container_width=True)

with col_res:
    st.subheader("📟 Console & Resultados")
    if executar:
        try:
            # Transpilador Simples
            codigo_pt = res_editor['text']
            traducao = {
                'VARIAVEL ': '', 'CALCULAR ': '', 'SE ': 'if ', ' ENTAO': ':',
                'SENAO': 'else:', 'EXIBIR ': 'saida.append(', 'FIM': '#'
            }
            
            linhas_py = ["import numpy as np", "saida = []"]
            for linha in codigo_pt.split('\n'):
                l = linha.strip()
                if not l or l.startswith("//"): continue
                if "EXIBIR" in l: l += ")"
                for pt, py in traducao.items():
                    l = l.replace(pt, py)
                linhas_py.append(l)
            
            # Execução
            escopo = {"np": np, "pd": pd}
            exec("\n".join(linhas_py), escopo)
            
            if "saida" in escopo:
                for msg in escopo["saida"]:
                    st.success(f"📟 {msg}")
            
            # Exemplo de gráfico automático se o aluno criar vetores x e y
            if "x" in escopo and "y" in escopo:
                st.plotly_chart(px.line(x=escopo['x'], y=escopo['y'], title="Gráfico do Projeto"))
                
        except Exception as e:
            st.error(f"Erro no código: {e}")

if ajuda_ia:
    with st.chat_message("assistant"):
        st.write("Analisando sua lógica de engenharia...")
        feedback = perguntar_ia(res_editor['text'])
        st.write(feedback)
