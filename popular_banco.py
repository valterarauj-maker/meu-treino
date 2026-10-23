import sqlite3

conn = sqlite3.connect('meu_treino_smartfit.db')
cursor = conn.cursor()

# Inserir Exercícios Básicos
exercicios = [
    ("Supino Reto", "Halteres / Barra", "Peito"),
    ("Supino Inclinado", "Halteres", "Peito"),
    ("Tríceps Corda", "Polia", "Braços"),
    ("Puxada Alta", "Polia", "Costas"),
    ("Remada Baixa", "Polia", "Costas"),
    ("Rosca Direta", "Halteres", "Braços"),
    ("Leg Press 45º", "Máquina", "Pernas"),
    ("Cadeira Extensora", "Máquina", "Pernas"),
    ("Cadeira Flexora", "Máquina", "Pernas")
]

for ex in exercicios:
    cursor.execute("INSERT OR IGNORE INTO Exercicios (nome, equipamento, zona_academia) VALUES (?, ?, ?)", ex)

# Associar ao Treino A (id_treino = 1)
treino_a = [
    (1, 1, 1), # Supino Reto
    (1, 2, 2), # Supino Inclinado
    (1, 3, 3)  # Tríceps Corda
]

for t in treino_a:
    cursor.execute("INSERT OR IGNORE INTO Treino_Exercicios (id_treino, id_exercicio, ordem_execucao) VALUES (?, ?, ?)", t)

# Inserir metas de séries para o primeiro exercício do Treino A (ex: Supino Reto)
cursor.execute("INSERT OR IGNORE INTO Metas_Series (id_treino_exercicio, numero_serie, repeticoes_alvo, nota_carga) VALUES (1, 1, '12', 'Aquecimento')")
cursor.execute("INSERT OR IGNORE INTO Metas_Series (id_treino_exercicio, numero_serie, repeticoes_alvo, nota_carga) VALUES (1, 2, '10', 'Moderado')")
cursor.execute("INSERT OR IGNORE INTO Metas_Series (id_treino_exercicio, numero_serie, repeticoes_alvo, nota_carga) VALUES (1, 3, '8', 'Pesado')")

conn.commit()
conn.close()
print("Base de dados populada com sucesso!")
