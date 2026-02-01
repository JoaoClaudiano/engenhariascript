import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai
from code_editor import code_editor
import re

# --- CONFIGURAÇÃO DA IA ---
# Substitua pela sua chave ou use st.secrets["GEMINI_KEY"] no Streamlit Cloud
API_KEY = "SUA_CHAVE_AQUI" 
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')
except:
    model = None

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="EngenhariaScript Academy", layout="wide", page_icon="🎓")

# --- BANCO DE MISSÕES (O CURRÍCULO) ---
MISSÕES = [
    {
        "id": 1,
        "titulo": "1. Fundamentos: Lei de Ohm",
        "objetivo": "Calcule a corrente (I = V / R).",
        "enunciado": "Defina VARIAVEL v = 220 e R = 10. Calcule a corrente e exiba o resultado.",
        "validação": lambda escopo: escopo.get("corrente") == 22,
        "dica": "VARIAVEL v = 220\nVARIAVEL r = 10\nCALCULAR corrente = v / r\nEXIBIR corrente"
    },
    {
        "id": 2,
        "titulo": "2. Lógica: Segurança Térmica",
        "objetivo": "Use SE/ENTAO para verificar temperatura.",
        "enunciado": "Se a temperatura for maior que 100, exiba 'Perigo'. Caso contrário, 'Seguro'.",
        "validação": lambda escopo: "saida_texto" in escopo and len(escopo["saida_texto"]) > 0,
        "dica": "VARIAVEL temp = 105\nSE temp > 100 ENTAO\n    EXIBIR 'Perigo'\nFIM"
    },
    {
        "id": 3,
        "titulo": "3. Loops: Análise de Cargas",
        "objetivo": "Use PARA para calcular múltiplas cargas.",
        "enunciado": "Calcule o peso (p = m * 9.8) para massas de 1 a 5 kg usando um laço.",
        "validação": lambda escopo: "peso" in escopo,
        "dica": "PARA m DE 1 ATE 6 FACA\n    CALCULAR peso = m * 9.8\nFIM"
    }
]

# --- MOTOR DE TRADUÇÃO ---
def transpilador(codigo_pt, inputs):
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
        
        # Fecha o parêntese do EXIBIR se necessário
        if "EXIBIR" in l: l += ")"
        
        if "ENTRADA" in l:
            match = re.search(r'VARIAVEL\s+(\w+)\s+=\s+ENTRADA', l)
            if match:
                var_nome = match.group(1)
                l = f"{var_nome} = {inputs.get(var_nome, 0.0)}"
        
        for pt, py in traducao.items():
            l = l.replace(pt, py)
        linhas_py.append(l)
    
    return "\n".join(linhas_py)

# --- INTERFACE SIDEBAR ---
with st.sidebar:
    st.title("🎓 Academia de Engenharia")
    
    aba_missao, aba_ajuda = st.tabs(["🎯 Missões", "📖 Glossário"])
    
    with aba_missao:
        st.write("### Trilha de Aprendizado")
        index_missao = st.selectbox("Escolha sua Missão:", range(len(MISSÕES)), format_func=lambda i: MISSÕES[i]["titulo"])
        missao = MISSÕES[index_missao]
        
        st.info(f"**Objetivo:** {missao['objetivo']}")
        st.write(missao['enunciado'])
        if st.checkbox("Precisa de uma dica?"):
            st.code(missao['dica'])

    with aba_ajuda:
        st.write("### 📖 Guia de Comandos")
        comandos = {
            "VARIAVEL": "Cria um espaço na memória.",
            "CALCULAR": "Executa fórmulas matemáticas.",
            "SE/ENTAO/SENAO": "Toma decisões lógicas.",
            "PARA/DE/ATE/FACA": "Cria ciclos de repetição.",
            "EXIBIR": "Mostra uma mensagem no console.",
            "FIM": "Finaliza um bloco (SE ou PARA)."
        }
        for cmd, desc in comandos.items():
            st.markdown(f"**{cmd}**: {desc}")

# --- CORPO PRINCIPAL ---
st.header("🏗️ IDE EngenhariaScript")

col_code, col_res = st.columns([1.2, 0.8])

with col_code:
    # Opções do editor avançado
    opcoes = {"showLineNumbers": True, "tabSize": 4}
    response = code_editor("// Escreva seu código aqui\n", lang="python", theme="monokai", options=opcoes)
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        executar = st.button("🚀 Rodar e Validar Missão", use_container_width=True)
    with col_btn2:
        ajuda_ia = st.button("🤖 Pedir Ajuda da IA", use_container_width=True)

with col_res:
    st.subheader("📟 Saída do Console")
    if executar:
        try:
            py_code = transpilador(response['text'], {})
            escopo = {"np": np, "pd": pd, "st": st}
            exec(py_code, escopo)
            
            # Mostra logs de EXIBIR
            if "saida_texto" in escopo:
                for msg in escopo["saida_texto"]:
                    st.success(f"📟 {msg}")
            
            # Validação da Missão
            if missao["validação"](escopo):
                st.balloons()
                st.sidebar.success("🎉 Parabéns! Missão Concluída!")
            else:
                st.sidebar.warning("🧐 O código rodou, mas o objetivo da missão ainda não foi alcançado.")
                
            # Gráfico Automático (Se X e Y existirem)
            if "x" in escopo and "y" in escopo:
                fig = px.line(x=escopo['x'], y=escopo['y'], title="Análise Gráfica")
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Erro técnico: {e}")

# --- LÓGICA DO TUTOR IA ---
if ajuda_ia and model:
    with st.expander("🤖 Resposta do Tutor IA", expanded=True):
        st.write("Analisando sua lógica...")
        prompt = f"Como professor de engenharia, analise este código em português e explique se a lógica de '{missao['titulo']}' está correta:\n{response['text']}"
        try:
            ia_res = model.generate_content(prompt)
            st.write(ia_res.text)
        except:
            st.error("Erro ao conectar com a IA. Verifique sua chave API.")
