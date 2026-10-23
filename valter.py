import flet as ft
import sqlite3
from datetime import date, datetime
import time
import threading
import winsound

def main(page: ft.Page):
    page.title = "Meu Treino Smart Fit"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 400
    page.window_height = 700
    page.padding = 0
    page.bgcolor = ft.Colors.BLACK

    # --- TEMA E CORES MODERNIZADAS ---
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.DEEP_ORANGE_ACCENT,
            secondary=ft.Colors.CYAN_ACCENT,
            surface=ft.Colors.GREY_900,
        )
    )

    page.appbar = ft.AppBar(
        title=ft.Text("Meus Treinos Smart Fit", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREY_900,
        center_title=True,
    )

    conn = sqlite3.connect('meu_treino_smartfit.db', check_same_thread=False)
    cursor = conn.cursor()

    # Garantir tabelas de histórico e corporal
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Historico_Cargas (
        id_carga INTEGER PRIMARY KEY AUTOINCREMENT,
        data_treino DATE,
        id_treino_exercicio INTEGER,
        numero_serie INTEGER,
        carga_kg REAL,
        concluido BOOLEAN
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Evolucao_Corporal (
        id_medida INTEGER PRIMARY KEY AUTOINCREMENT,
        data_registro DATE,
        peso REAL,
        cintura REAL,
        braco REAL,
        perna REAL,
        peito REAL,
        barriga REAL
    )
    ''')
    conn.commit()

    # Garantir compatibilidade se a tabela antiga já existir sem as colunas novas
    try:
        cursor.execute("ALTER TABLE Evolucao_Corporal ADD COLUMN peito REAL")
        cursor.execute("ALTER TABLE Evolucao_Corporal ADD COLUMN barriga REAL")
        conn.commit()
    except Exception:
        pass

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

    # --- LÓGICA DE SALVAMENTO DE TREINO ---
    def salvar_dados(e, id_te, nome_ex, inputs_series):
        data_hoje = date.today().strftime("%Y-%m-%d")
        
        for serie in inputs_series:
            num_serie = serie['numero']
            carga_str = serie['input_carga'].value
            carga = float(carga_str) if carga_str else 0.0
            feito = serie['checkbox_feito'].value
            
            if feito or carga > 0:
                cursor.execute('''
                    INSERT INTO Historico_Cargas (data_treino, id_treino_exercicio, numero_serie, carga_kg, concluido)
                    VALUES (?, ?, ?, ?, ?)
                ''', (data_hoje, id_te, num_serie, carga, feito))
        
        conn.commit()
        
        snack = ft.SnackBar(ft.Text(f"Cargas salvas para: {nome_ex}!"), bgcolor=ft.Colors.GREEN_700)
        page.overlay.append(snack)
        snack.open = True
        page.update()

    # --- FUNÇÃO DE DESCANSO COM AVISO SONORO ---
    def iniciar_descanso_alarme(e):
        snack = ft.SnackBar(ft.Text("⏳ Cronómetro de 60s iniciado! Foco no descanso."), bgcolor=ft.Colors.DEEP_ORANGE_900)
        page.overlay.append(snack)
        snack.open = True
        page.update()

        def rodar_temporizador():
            time.sleep(60)
            try:
                winsound.Beep(1000, 400)
                time.sleep(0.1)
                winsound.Beep(1000, 400)
            except Exception:
                pass

        threading.Thread(target=rodar_temporizador, daemon=True).start()

    # --- CONSTRUÇÃO DA TELA DE EVOLUÇÃO CORPORAL ---
    def construir_tela_corporal():
        txt_peso = ft.TextField(label="Peso (kg)", width=170, keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.DEEP_ORANGE_ACCENT)
        txt_cintura = ft.TextField(label="Cintura (cm)", width=170, keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.DEEP_ORANGE_ACCENT)
        txt_braco = ft.TextField(label="Braço (cm)", width=170, keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.DEEP_ORANGE_ACCENT)
        txt_perna = ft.TextField(label="Perna (cm)", width=170, keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.DEEP_ORANGE_ACCENT)
        txt_peito = ft.TextField(label="Peito (cm)", width=170, keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.DEEP_ORANGE_ACCENT)
        txt_barriga = ft.TextField(label="Barriga (cm)", width=170, keyboard_type=ft.KeyboardType.NUMBER, border_color=ft.Colors.DEEP_ORANGE_ACCENT)

        lista_historico_corpo = ft.Column()

        def carregar_historico_corpo():
            lista_historico_corpo.controls.clear()
            cursor.execute("SELECT data_registro, peso, cintura, braco, perna, peito, barriga FROM Evolucao_Corporal ORDER BY data_registro DESC")
            registros = cursor.fetchall()
            
            if not registros:
                lista_historico_corpo.controls.append(ft.Text("Nenhuma medida registrada ainda.", color=ft.Colors.GREY_500))
            else:
                for reg in registros:
                    dt, p, cin, bra, per, pei, bar = reg
                    lista_historico_corpo.controls.append(
                        ft.Card(
                            elevation=3,
                            content=ft.Container(
                                bgcolor=ft.Colors.GREY_850,
                                padding=14,
                                border_radius=8,
                                content=ft.Column([
                                    ft.Text(f"📅 Data: {dt}", weight=ft.FontWeight.BOLD, color=ft.Colors.DEEP_ORANGE_ACCENT),
                                    ft.Divider(color=ft.Colors.GREY_800),
                                    ft.Row([
                                        ft.Text(f"Peso: {p} kg"),
                                        ft.Text(f"Cintura: {cin} cm"),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.Row([
                                        ft.Text(f"Braço: {bra} cm"),
                                        ft.Text(f"Perna: {per} cm"),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.Row([
                                        ft.Text(f"Peito: {pei or 0} cm"),
                                        ft.Text(f"Barriga: {bar or 0} cm"),
                                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ])
                            )
                        )
                    )
            page.update()

        def salvar_medidas(e):
            data_hoje = date.today().strftime("%Y-%m-%d")
            p = float(txt_peso.value) if txt_peso.value else 0.0
            cin = float(txt_cintura.value) if txt_cintura.value else 0.0
            bra = float(txt_braco.value) if txt_braco.value else 0.0
            per = float(txt_perna.value) if txt_perna.value else 0.0
            pei = float(txt_peito.value) if txt_peito.value else 0.0
            bar = float(txt_barriga.value) if txt_barriga.value else 0.0

            if p > 0:
                cursor.execute('''
                    INSERT INTO Evolucao_Corporal (data_registro, peso, cintura, braco, perna, peito, barriga)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (data_hoje, p, cin, bra, per, pei, bar))
                conn.commit()

                txt_peso.value = ""
                txt_cintura.value = ""
                txt_braco.value = ""
                txt_perna.value = ""
                txt_peito.value = ""
                txt_barriga.value = ""

                carregar_historico_corpo()
                
                snack = ft.SnackBar(ft.Text("Medidas corporais salvas com sucesso!"), bgcolor=ft.Colors.GREEN_700)
                page.overlay.append(snack)
                snack.open = True
                page.update()

        btn_salvar_corpo = ft.Button(
            content=ft.Row([
                ft.Icon(ft.Icons.SAVE, color=ft.Colors.WHITE, size=18),
                ft.Text("Salvar Medidas da Semana", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.Colors.DEEP_ORANGE_700,
            on_click=salvar_medidas,
            height=45,
            width=250
        )

        carregar_historico_corpo()

        return ft.ListView(
            padding=15,
            expand=True,
            controls=[
                ft.Text("Evolução Corporal", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Acompanhe suas medidas e veja sua transformação física:", color=ft.Colors.GREY_400),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Row([txt_peso, txt_cintura], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([txt_braco, txt_perna], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([txt_peito, txt_barriga], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(content=btn_salvar_corpo, padding=10),
                ft.Divider(color=ft.Colors.GREY_800),
                ft.Text("Histórico de Medidas", weight=ft.FontWeight.BOLD, size=16, color=ft.Colors.DEEP_ORANGE_ACCENT),
                lista_historico_corpo
            ]
        )

    # --- CONSTRUÇÃO DAS TELAS DE TREINO (A, B, C) ---
    def construir_tela_treino(id_treino):
        cursor.execute('''
            SELECT te.id_treino_exercicio, e.nome, e.equipamento, e.zona_academia
            FROM Treino_Exercicios te
            JOIN Exercicios e ON te.id_exercicio = e.id_exercicio
            WHERE te.id_treino = ?
            ORDER BY te.ordem_execucao
        ''', (id_treino,))
        exercicios_banco = cursor.fetchall()

        lista_cartoes = []
        
        if exibir_alerta_rotacao:
            lista_cartoes.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.BLACK),
                            ft.Text("Atenção: Seu treino completou 60 dias! Hora de trocar a seleção de exercícios.", color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD, size=12)
                        ]
                    ),
                    bgcolor=ft.Colors.AMBER_400,
                    padding=12,
                    border_radius=8,
                    margin=10
                )
            )

        lista_cartoes.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DIRECTIONS_RUN, color=ft.Colors.GREEN_ACCENT, size=20),
                    ft.Text("Aquecimento: 5 min de caminhada", color=ft.Colors.GREEN_ACCENT, weight=ft.FontWeight.BOLD)
                ], spacing=8),
                padding=10
            )
        )

        for ex in exercicios_banco:
            id_treino_exercicio, nome_exercicio, equipamento, zona = ex
            
            cursor.execute('''
                SELECT DISTINCT numero_serie, repeticoes_alvo, nota_carga
                FROM Metas_Series
                WHERE id_treino_exercicio = ?
                ORDER BY numero_serie
            ''', (id_treino_exercicio,))
            metas_series = cursor.fetchall()
            
            linhas_visuais_series = []
            inputs_desta_maquina = []

            btn_iniciar_descanso = ft.TextButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.TIMER, color=ft.Colors.CYAN_ACCENT, size=18),
                    ft.Text("Descanso (60s)", color=ft.Colors.CYAN_ACCENT, weight=ft.FontWeight.BOLD)
                ], spacing=4),
                on_click=iniciar_descanso_alarme
            )

            for meta in metas_series:
                num, reps, nota = meta
                
                cursor.execute('''
                    SELECT carga_kg 
                    FROM Historico_Cargas 
                    WHERE id_treino_exercicio = ? AND numero_serie = ?
                    ORDER BY id_carga DESC LIMIT 1
                ''', (id_treino_exercicio, num))
                ultima_carga_row = cursor.fetchone()
                valor_ultima_carga = str(int(ultima_carga_row[0])) if ultima_carga_row and ultima_carga_row[0] > 0 else ""

                input_carga = ft.TextField(
                    value=valor_ultima_carga,
                    label="Carga", 
                    width=80, 
                    height=40, 
                    text_size=14, 
                    keyboard_type=ft.KeyboardType.NUMBER,
                    border_color=ft.Colors.DEEP_ORANGE_ACCENT
                )
                check_feito = ft.Checkbox(label="Feito", value=False, active_color=ft.Colors.DEEP_ORANGE_ACCENT)
                
                inputs_desta_maquina.append({
                    'numero': num,
                    'input_carga': input_carga,
                    'checkbox_feito': check_feito
                })
                
                linha = ft.Row(
                    controls=[
                        ft.Text(f"Série {num}:", weight=ft.FontWeight.BOLD, width=60, color=ft.Colors.WHITE),
                        ft.Text(f"{reps} reps", width=60, color=ft.Colors.GREY_300),
                        input_carga,
                        check_feito
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
                
                linhas_visuais_series.append(linha)
                if nota:
                    linhas_visuais_series.append(ft.Text(f"↳ {nota}", size=12, color=ft.Colors.DEEP_ORANGE_200))

            url_pesquisa_youtube = f"https://www.youtube.com/results?search_query=como+fazer+{nome_exercicio.replace(' ', '+')}"
            btn_video = ft.IconButton(
                icon=ft.Icons.PLAY_CIRCLE_FILL,
                icon_color=ft.Colors.RED_400,
                icon_size=30,
                tooltip="Ver Execução no YouTube",
                url=url_pesquisa_youtube
            )

            cartao = ft.Card(
                elevation=6,
                margin=10,
                content=ft.Container(
                    bgcolor=ft.Colors.GREY_900,
                    padding=15,
                    border_radius=8,
                    content=ft.Column(
                        controls=[
                            ft.Row([
                                ft.ListTile(
                                    leading=ft.Icon(ft.Icons.FITNESS_CENTER, color=ft.Colors.DEEP_ORANGE_ACCENT),
                                    title=ft.Text(nome_exercicio, weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.WHITE),
                                    subtitle=ft.Text(f"{zona} | {equipamento}", color=ft.Colors.GREY_400),
                                    expand=True
                                ),
                                btn_video
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Divider(color=ft.Colors.GREY_800),
                            ft.Column([
                                ft.Text("Estratégia: Pirâmide Invertida", color=ft.Colors.DEEP_ORANGE_ACCENT, italic=True, weight=ft.FontWeight.W_500),
                                ft.Row([
                                    ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=ft.Colors.CYAN_ACCENT),
                                    btn_iniciar_descanso
                                ], alignment=ft.MainAxisAlignment.START, spacing=0)
                            ], spacing=2),
                            ft.Divider(color=ft.Colors.GREY_800),
                            *linhas_visuais_series,
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.SAVE, color=ft.Colors.WHITE, size=18),
                                        ft.Text("Salvar Exercício", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER
                                ),
                                bgcolor=ft.Colors.DEEP_ORANGE_700,
                                padding=12,
                                border_radius=8,
                                ink=True,
                                on_click=lambda e, id_te=id_treino_exercicio, nome=nome_exercicio, inputs=inputs_desta_maquina: salvar_dados(e, id_te, nome, inputs)
                            )
                        ]
                    )
                )
            )
            lista_cartoes.append(cartao)

        return ft.ListView(controls=lista_cartoes, padding=10, expand=True)

    # --- ABA DE EVOLUÇÃO DE CARGAS ---
    def construir_tela_evolucao():
        cursor.execute('''
            SELECT DISTINCT e.id_exercicio, e.nome 
            FROM Exercicios e
            JOIN Treino_Exercicios te ON e.id_exercicio = te.id_exercicio
            JOIN Historico_Cargas hc ON te.id_treino_exercicio = hc.id_treino_exercicio
            ORDER BY e.nome
        ''')
        exercicios_com_historico = cursor.fetchall()

        container_grafico = ft.Column(expand=True)

        def atualizar_grafico(e):
            id_ex_selecionado = dropdown_ex.value
            if not id_ex_selecionado:
                return

            cursor.execute('''
                SELECT hc.data_treino, MAX(hc.carga_kg)
                FROM Historico_Cargas hc
                JOIN Treino_Exercicios te ON hc.id_treino_exercicio = te.id_treino_exercicio
                WHERE te.id_exercicio = ?
                GROUP BY hc.data_treino
                ORDER BY hc.data_treino ASC
            ''', (id_ex_selecionado,))
            registros = cursor.fetchall()

            container_grafico.controls.clear()

            if not registros:
                container_grafico.controls.append(ft.Text("Nenhum histórico registrado para este exercício.", color=ft.Colors.GREY_500))
            else:
                pontos_chart = []
                cargas = [r[1] for r in registros]
                max_carga = max(cargas) if cargas else 100
                
                for idx, (dt_tr, max_cg) in enumerate(registros):
                    percentual = max_cg / (max_carga * 1.2) if max_carga > 0 else 0
                    pontos_chart.append(
                        ft.Container(
                            padding=10,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"Data: {dt_tr}", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ft.Text(f"Carga Máxima: {int(max_cg)} kg", color=ft.Colors.DEEP_ORANGE_ACCENT, weight=ft.FontWeight.BOLD)
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.ProgressBar(value=percentual, color=ft.Colors.DEEP_ORANGE_ACCENT, bgcolor=ft.Colors.GREY_800, height=8)
                            ])
                        )
                    )
                container_grafico.controls.extend(pontos_chart)

            page.update()

        options_dropdown = [ft.dropdown.Option(key=str(ex[0]), text=ex[1]) for ex in exercicios_com_historico]
        
        dropdown_ex = ft.Dropdown(
            label="Selecione o Exercício",
            options=options_dropdown,
            border_color=ft.Colors.DEEP_ORANGE_ACCENT,
            color=ft.Colors.WHITE
        )
        if hasattr(dropdown_ex, "on_change"):
            dropdown_ex.on_change = atualizar_grafico
        elif hasattr(dropdown_ex, "on_select"):
            dropdown_ex.on_select = atualizar_grafico

        return ft.ListView(
            padding=15,
            expand=True,
            controls=[
                ft.Text("Evolução de Cargas", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Acompanhe o aumento da sua carga máxima ao longo do tempo:", color=ft.Colors.GREY_400),
                ft.Divider(color=ft.Colors.GREY_800),
                dropdown_ex,
                ft.Divider(color=ft.Colors.GREY_800),
                container_grafico
            ]
        )

    # --- MONTAGEM DAS ABAS PRINCIPAIS ---
    cursor.execute("SELECT id_treino, nome_treino FROM Treinos")
    treinos_cadastrados = cursor.fetchall()

    lista_tabs = []
    lista_views = []

    for treino in treinos_cadastrados:
        id_treino, nome_treino = treino
        letra = nome_treino.split('-')[0].replace("Treino", "").strip()
        
        lista_tabs.append(ft.Tab(label=f"Treino {letra}"))
        lista_views.append(construir_tela_treino(id_treino))

    # Adicionar abas de Evolução de Cargas e Corpo
    lista_tabs.append(ft.Tab(label="Evolução Cargas"))
    lista_views.append(construir_tela_evolucao())

    lista_tabs.append(ft.Tab(label="Corpo"))
    lista_views.append(construir_tela_corporal())

    menu_tabs = ft.Tabs(
        length=len(lista_tabs),
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.TabBar(tabs=lista_tabs),
                ft.TabBarView(controls=lista_views, expand=True)
            ]
        )
    )

    page.add(menu_tabs)

ft.run(main, view=ft.AppView.WEB_BROWSER, port=8550, host="0.0.0.0")
