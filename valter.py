import streamlit as st
import sqlite3
import os
from datetime import date, datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Meu Treino Smart Fit", 
    page_icon="🏋️‍♂️", 
    layout="centered"
)

# --- ESTILO VISUAL (MODO ESCURO / TONS DE LARANJA) ---
st.markdown("""
<style>
    .stApp {background-color: #000000; color: #ffffff;}
</style>
""", unsafe_allow_html=True)

# --- CONEXÃO E BASE DE DADOS ---
db_path = 'meu_treino_smartfit.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()

# Criar tabelas fundamentais
cursor.execute('''CREATE TABLE IF NOT EXISTS Treinos (
                    id_treino INTEGER PRIMARY KEY AUTOINCREMENT, 
                    nome_treino TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Exercicios (
                    id_exercicio INTEGER PRIMARY KEY AUTOINCREMENT, 
                    nome TEXT, 
                    equipamento TEXT, 
                    zona_academia TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Treino_Exercicios (
                    id_treino_exercicio INTEGER PRIMARY KEY AUTOINCREMENT, 
                    id_treino INTEGER, 
                    id_exercicio INTEGER, 
                    ordem_execucao INTEGER)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Metas_Series (
                    id_meta INTEGER PRIMARY KEY AUTOINCREMENT, 
                    id_treino_exercicio INTEGER, 
                    numero_serie INTEGER, 
                    repeticoes_alvo TEXT, 
                    nota_carga TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Historico_Cargas (
                    id_carga INTEGER PRIMARY KEY AUTOINCREMENT, 
                    data_treino DATE, 
                    id_treino_exercicio INTEGER, 
                    numero_serie INTEGER, 
                    carga_kg REAL, 
                    concluido BOOLEAN)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS Evolucao_Corporal (
                    id_medida INTEGER PRIMARY KEY AUTOINCREMENT, 
                    data_registro DATE, 
                    peso REAL, 
                    cintura REAL, 
                    braco REAL, 
                    perna REAL, 
                    peito REAL, 
                    barriga REAL)''')

# Popular dados iniciais se a tabela de treinos estiver vazia
cursor.execute("SELECT COUNT(*) FROM Treinos")
if cursor.fetchone()[0] == 0:
    cursor.executemany("INSERT OR IGNORE INTO Treinos (id_treino, nome_treino) VALUES (?, ?)", 
                       [(1, "Treino A"), (2, "Treino B"), (3, "Treino C")])

    exercicios = [
        ("Supino Reto", "Halteres / Barra", "Peito"),
        ("Supino Inclinado", "Halteres", "Peito"),
        ("Tríceps Corda", "Polia", "Braços"),
        ("Puxada Alta", "Polia", "Costas"),
        ("Remada Baixa", "Polia", "Costas"),
        ("Rosca Direta", "Halteres", "Braços"),
        ("Leg Press 45º", "Máquina", "Pernas"),
        ("Cadeira Extensora", "Máquina", "Pernas"),
        ("Cadeira Flexora", "Máquina", "Pernas"),
        ("Desenvolvimento", "Halteres", "Ombros"),
        ("Elevação Lateral", "Halteres", "Ombros")
    ]
    cursor.executemany("INSERT OR IGNORE INTO Exercicios (nome, equipamento, zona_academia) VALUES (?, ?, ?)", exercicios)

    # Associações A, B e C
    rel_a = [(1, 1, 1), (1, 2, 2), (1, 3, 3)]
    cursor.executemany("INSERT OR IGNORE INTO Treino_Exercicios (id_treino, id_exercicio, ordem_execucao) VALUES (?, ?, ?)", rel_a)

    rel_b = [(2, 4, 1), (2, 5, 2), (2, 6, 3)]
    cursor.executemany("INSERT OR IGNORE INTO Treino_Exercicios (id_treino, id_exercicio, ordem_execucao) VALUES (?, ?, ?)", rel_b)

    rel_c = [(3, 7, 1), (3, 8, 2), (3, 9, 3), (3, 10, 4), (3, 11, 5)]
    cursor.executemany("INSERT OR IGNORE INTO Treino_Exercicios (id_treino, id_exercicio, ordem_execucao) VALUES (?, ?, ?)", rel_c)

    cursor.execute("SELECT id_treino_exercicio FROM Treino_Exercicios")
    todos_tes = cursor.fetchall()
    for te in todos_tes:
        id_te = te[0]
        metas_padrao = [
            (id_te, 1, '12', 'Aquecimento / Leve'),
            (id_te, 2, '10', 'Moderado'),
            (id_te, 3, '8', 'Pesado')
        ]
        cursor.executemany("INSERT OR IGNORE INTO Metas_Series (id_treino_exercicio, numero_serie, repeticoes_alvo, nota_carga) VALUES (?, ?, ?, ?)", metas_padrao)

conn.commit()

# --- ALERTA BIMESTRAL (60 dias) ---
exibir_alerta_rotacao = False
try:
    cursor.execute("SELECT MIN(data_treino) FROM Historico_Cargas")
    row_data = cursor.fetchone()
    if row_data and row_data[0]:
        primeira_data = datetime.strptime(row_data[0], "%Y-%m-%d").date()
        if (date.today() - primeira_data).days >= 60:
            exibir_alerta_rotacao = True
except Exception:
    pass

# --- BARRA LATERAL (MENU) ---
st.sidebar.title("💪 Smart Fit - Valter")
menu = st.sidebar.radio("Escolha a seção:", ["Treino A", "Treino B", "Treino C", "Evolução Cargas", "Evolução Corporal"])

# --- EXIBIÇÃO DOS TREINOS (A, B, C) ---
if menu.startswith("Treino"):
    mapa_ids = {"Treino A": 1, "Treino B": 2, "Treino C": 3}
    id_treino_atual = mapa_ids.get(menu, 1)
    
    st.title(f"🔥 {menu}")
    
    if exibir_alerta_rotacao:
        st.warning("⚠️ Atenção: Seu treino completou 60 dias! Hora de trocar a seleção de exercícios.")
        
    st.markdown("🏃 **Aquecimento:** 5 min de caminhada")
    st.write("---")
    
    cursor.execute('''
        SELECT te.id_treino_exercicio, e.nome, e.equipamento, e.zona_academia 
        FROM Treino_Exercicios te 
        JOIN Exercicios e ON te.id_exercicio = e.id_exercicio 
        WHERE te.id_treino = ? 
        ORDER BY te.ordem_execucao
    ''', (id_treino_atual,))
    
    exercicios = cursor.fetchall()
    
    if not exercicios:
        st.warning("Ainda não há exercícios cadastrados para este treino.")
    else:
        for ex in exercicios:
            id_te, nome_ex, eq, zona = ex
            with st.container():
                st.markdown(f"### 📌 {nome_ex}")
                st.caption(f"{zona} | {eq} | *Estratégia: Pirâmide Invertida*")
                
                cursor.execute("SELECT numero_serie, repeticoes_alvo, nota_carga FROM Metas_Series WHERE id_treino_exercicio = ? ORDER BY numero_serie", (id_te,))
                metas = cursor.fetchall()
                
                inputs_series = []
                for meta in metas:
                    num, reps, nota = meta
                    cursor.execute("SELECT carga_kg FROM Historico_Cargas WHERE id_treino_exercicio = ? AND numero_serie = ? ORDER BY id_carga DESC LIMIT 1", (id_te, num))
                    ultima = cursor.fetchone()
                    val_antiga = float(ultima[0]) if ultima and ultima[0] > 0 else 0.0
                    
                    col1, col2, col3 = st.columns([1, 2, 2])
                    with col1:
                        st.write(f"**Série {num}**")
                    with col2:
                        st.text(f"{reps}\n({nota or 'Normal'})")
                    with col3:
                        carga = st.number_input(f"Carga S{num} ({nome_ex})", min_value=0.0, value=val_antiga, step=1.0, key=f"c_{id_te}_{num}")
                        feito = st.checkbox(f"Feito S{num}", key=f"f_{id_te}_{num}")
                    
                    inputs_series.append({"num": num, "carga": carga, "feito": feito})
                
                if st.button(f"Salvar {nome_ex}", key=f"btn_{id_te}"):
                    data_hoje = date.today().strftime("%Y-%m-%d")
                    for s in inputs_series:
                        if s["feito"] or s["carga"] > 0:
                            cursor.execute("INSERT INTO Historico_Cargas (data_treino, id_treino_exercicio, numero_serie, carga_kg, concluido) VALUES (?, ?, ?, ?, ?)", 
                                           (data_hoje, id_te, s["num"], s["carga"], s["feito"]))
                    conn.commit()
                    st.success(f"Cargas salvas para {nome_ex}!")
                
                st.markdown("---")

# --- EVOLUÇÃO CORPORAL ---
elif menu == "Evolução Corporal":
    st.title("📈 Evolução Corporal")
    st.markdown("Registe suas medidas semanais:")
    
    with st.form("form_corpo"):
        col1, col2 = st.columns(2)
        with col1:
            peso = st.number_input("Peso (kg)", min_value=0.0, format="%.1f")
            cintura = st.number_input("Cintura (cm)", min_value=0.0, format="%.1f")
            braco = st.number_input("Braço (cm)", min_value=0.0, format="%.1f")
        with col2:
            perna = st.number_input("Perna (cm)", min_value=0.0, format="%.1f")
            peito = st.number_input("Peito (cm)", min_value=0.0, format="%.1f")
            barriga = st.number_input("Barriga (cm)", min_value=0.0, format="%.1f")
            
        submitted = st.form_submit_button("Salvar Medidas da Semana")
        if submitted and peso > 0:
            data_hoje = date.today().strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO Evolucao_Corporal (data_registro, peso, cintura, braco, perna, peito, barriga) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                           (data_hoje, peso, cintura, braco, perna, peito, barriga))
            conn.commit()
            st.success("Medidas corporais salvas com sucesso!")
            
    st.write("### Histórico de Medidas")
    cursor.execute("SELECT data_registro, peso, cintura, braco, perna, peito, barriga FROM Evolucao_Corporal ORDER BY data_registro DESC")
    registros = cursor.fetchall()
    for reg in registros:
        dt, p, cin, bra, per, pei, bar = reg
        st.info(f"📅 **Data:** {dt} | **Peso:** {p}kg | **Cintura:** {cin}cm | **Braço:** {bra}cm | **Perna:** {per}cm | **Peito:** {pei or 0}cm | **Barriga:** {bar or 0}cm")

# --- EVOLUÇÃO DE CARGAS ---
elif menu == "Evolução Cargas":
    st.title("📊 Evolução de Cargas")
    
    cursor.execute("""
        SELECT DISTINCT e.id_exercicio, e.nome 
        FROM Exercicios e 
        JOIN Treino_Exercicios te ON e.id_exercicio = te.id_exercicio 
        JOIN Historico_Cargas hc ON te.id_treino_exercicio = hc.id_treino_exercicio 
        ORDER BY e.nome
    """)
    exercicios_hist = cursor.fetchall()
    
    if not exercicios_hist:
        st.warning("Ainda não há cargas registradas no histórico.")
    else:
        nomes_exs = {ex[1]: ex[0] for ex in exercicios_hist}
        escolha = st.selectbox("Selecione o Exercício:", list(nomes_exs.keys()))
        
        if escolha:
            id_sel = nomes_exs[escolha]
            cursor.execute("""
                SELECT hc.data_treino, MAX(hc.carga_kg) 
                FROM Historico_Cargas hc 
                JOIN Treino_Exercicios te ON hc.id_treino_exercicio = te.id_treino_exercicio 
                WHERE te.id_exercicio = ? 
                GROUP BY hc.data_treino 
                ORDER BY hc.data_treino ASC
            """, (id_sel,))
            
            dados_graf = cursor.fetchall()
            if dados_graf:
                datas = [d[0] for d in dados_graf]
                cargas = [d[1] for d in dados_graf]
                st.line_chart(dict(zip(datas, cargas)))
