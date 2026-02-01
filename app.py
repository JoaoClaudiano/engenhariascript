import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from code_editor import code_editor
import re

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="EngenhariaScript IDE", layout="wide")

st.title("👨‍🔬 EngenhariaScript PRO")
st.markdown("### Ambiente de Programação para Engenharia")

# --- LÓGICA DO TRADUTOR (COM IDENTAÇÃO) ---
def compilar_engenharia(codigo_pt):
    traducao = {
        'VARIAVEL ': '',
        'CALCULAR ': '',
        'SE ': 'if ',
        ' ENTAO': ':',
        'SENAO': 'else:',
        'PARA ': 'for ',
        ' DE ': ' in range(',
        ' ATE ': ', ',
        ' FACA': '):',
        'EXIBIR': 'print',
        'FIM': '#',
        'sen': 'np.sin',
        'cos': 'np.cos'
    }
    
    linhas_py = ["import numpy as np", "saida_texto = []"]
    
    for linha in codigo_pt.split('\n'):
        l_traduzida = linha
        for pt, py in traducao.items():
            l_traduzida = l_traduzida.replace(pt, py)
        
        # Redireciona o print para capturarmos na interface
        if "print" in l_traduzida:
            l_traduzida = l_traduzida.replace("print", "saida_texto.append")
            
        linhas_py.append(l_traduzida)
    
    return "\n".join(linhas_py)

# --- INTERFACE ---
col_ed, col_out = st.columns([1.2, 0.8])

with col_ed:
    st.write("📝 **Editor com Contagem de Linhas**")
    
    # Configurações do Editor Visual
    opcoes_editor = {
        "buttons": [{
            "name": "Executar",
            "feather": "Play",
            "primary": True,
            "showInNormalMode": True,
            "callback": "execute"
        }],
        "showLineNumbers": True,
        "tabSize": 4,
    }

    codigo_inicial = """// Exemplo: Cálculo de Fadiga
VARIAVEL limite = 100
PARA i DE 1 ATE 6 FACA
    CALCULAR tensao = i * 20
    SE tensao > limite ENTAO
        EXIBIR f"Falha na iteração {i}: {tensao}MPa"
    SENAO
        EXIBIR f"Seguro: {tensao}MPa"
FIM

// Gerar gráfico automático
VARIAVEL x = np.linspace(0, 10, 100)
VARIAVEL y = sen(x)
"""
    
    # Renderiza o editor avançado
    response = code_editor(codigo_inicial, lang="python", theme="monokai", options=opcoes_editor)

with col_out:
    st.write("📊 **Console e Resultados**")
    
    # O botão de execução agora vem do retorno do componente code_editor
    if response['type'] == "submit" or st.button("Executar Manualmente"):
        codigo_usuario = response['text']
        
        try:
            # 1. Transpilação
            codigo_python = compilar_engenharia(codigo_usuario)
            
            # 2. Execução
            escopo = {}
            exec(codigo_python, escopo)
            
            # 3. Mostrar Logs
            if "saida_texto" in escopo:
                for msg in escopo["saida_texto"]:
                    st.code(msg, language="text")
            
            # 4. Mostrar Gráfico se X e Y existirem
            if "x" in escopo and "y" in escopo:
                fig, ax = plt.subplots(figsize=(6, 3))
                ax.plot(escopo["x"], escopo["y"], lw=2, color='green')
                ax.set_title("Gráfico de Engenharia")
                st.pyplot(fig)
                
            # 5. Tabela de Variáveis
            vars_finais = {k: v for k, v in escopo.items() if k not in ['np', 'saida_texto', '__builtins__', 'x', 'y']}
            if vars_finais:
                st.table(pd.DataFrame(vars_finais.items(), columns=["Variável", "Valor"]))

        except Exception as e:
            st.error(f"Erro na linha: {e}")

