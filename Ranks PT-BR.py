from multiprocessing import Process, Manager, Value
from os.path import exists as file_exists
from datetime import datetime, timedelta
from threading import Thread
from ctypes import c_char_p
from time import sleep
from lxml import html

import tkinter.ttk as ttk
import tkinter as tk
import xlsxwriter
import webbrowser 
import pyperclip 
import requests
import fasttext
import json
import sys
import os

# Porque todas essas funções tão aqui ao invés de dentro da classe? Porque o Tkinter
# entra em choque com multiprocessing e essa foi a solução mais preguiçosa que achei.
def thread_rank_geral(clans, nome_clan, barra_progresso, cancelar_operacao, clans_pt_br):
    min = 0
    while min < len(clans) and cancelar_operacao.value == 0:
        dados = html.fromstring(requests.get(clans[min][1]).content)
        clan_xp = dados.xpath('.//td[@class="clan_left"]/text()')

        barra_progresso.value +=  1

        if len(clan_xp) > 0:
            clans_pt_br.append([clans[min][0], clan_xp[4]])
            nome_clan.value = '"' + clans[min][0] + '" analisado...'

        min +=  1

def thread_rank_mes_atual(clans, nome_clan, barra_progresso, cancelar_operacao, clans_pt_br):
    min = 0
    while min < len(clans) and cancelar_operacao.value == 0:
        dados = html.fromstring(requests.get(clans[min][1]).content)
        clan_xp = [tag.text_content() for tag in dados.xpath('.//table[@class = "regular"]//tr')]
        clan_rank = [tag.text_content() for tag in dados.xpath('.//td[@class = "clan_td clan_td_stat_rank"]')]

        barra_progresso.value +=  1

        if len(clan_xp) > 0:
            for i in range(len(clan_xp)):
                if 'Month' in clan_xp[i]:
                    # 'clan_xp[i]' vem no formato "Month" + "123" + "1,234,567,890" (tudo junto, numa só string), mas só a terceira parte que é interessante.
                    # 'clan_xp' tem 5 elementos e 'clan_rank' tem 4, e por isso tem que ser 'clan_rank[i-1]', pra sincronizar os dois.
                    clans_pt_br.append([clans[min][0], clan_xp[i].replace('Month', "").replace(clan_rank[i-1], "", 1)])
                    nome_clan.value = '"' + clans[min][0] + '" analisado...'

        min +=  1

def thread_rank_mes_pass(clans, nome_clan, barra_progresso, cancelar_operacao, clans_pt_br):
    min = 0
    while min < len(clans) and cancelar_operacao.value == 0:
        dados = html.fromstring(requests.get(clans[min][1] + '/xp-tracker?skill=2&criteria_set1=last_month').content)
        xp_total = dados.xpath('.//table[@class="regular"]//b/text()')
        primeiro_lugar_nome = dados.xpath('.//td[@class="clan_td clan_rsn2"]//a/text()')
        primeiro_lugar_xp = dados.xpath('.//td[@class="clan_td clan_xpgain_trk"]/text()')

        barra_progresso.value +=  1

        if len(xp_total) > 0:                   
            clans_pt_br.append([clans[min][0], xp_total[1], primeiro_lugar_nome[0], primeiro_lugar_xp[0]])
            nome_clan.value = '"' + clans[min][0] + '" analisado...'

        min +=  1

def thread_rank_dxp(clans, nome_clan, barra_progresso, cancelar_operacao, clans_pt_br):
    min = 0
    while min < len(clans) and cancelar_operacao.value == 0:
        dados = html.fromstring(requests.get(clans[min][1]).content)
        clan_xp = [tag.text_content() for tag in dados.xpath('.//table[@class = "regular"]//tr')]
        clan_rank = [tag.text_content() for tag in dados.xpath('.//td[@class = "clan_td clan_td_stat_rank"]')]

        barra_progresso.value +=  1

        if len(clan_xp) > 0:
            for i in range(len(clan_xp)):
                if 'DXP Weekend' in clan_xp[i]:
                    # 'clan_xp[i]' vem no formato "DXP Weekend" + "123" + "1,234,567,890" (tudo junto, numa só string), mas só a terceira parte que é interessante.
                    # 'clan_xp' tem 5 elementos e 'clan_rank' tem 4, e por isso tem que ser 'clan_rank[i-1]', pra sincronizar os dois.
                    clans_pt_br.append([clans[min][0], clan_xp[i].replace('DXP Weekend', "").replace(clan_rank[i-1], "", 1)])
                    nome_clan.value = '"' + clans[min][0] + '" analisado...'

        min +=  1

def thread_runeclan(clans_pt_br, nome_clan, barra_progresso, cancelar_operacao, min, max):
    fasttext.FastText.eprint = lambda x: None
    model = fasttext.load_model('lid.176.ftz')
    
    while min <= max and cancelar_operacao.value == 0:
        dados = html.fromstring(requests.get('https://www.runeclan.com/clans/page/' + str(min)).content)
        clans_nomes = list(dict.fromkeys(dados.xpath('.//td[@class = "clans_name"]//a/text()')))
        clans_links = list(dict.fromkeys(dados.xpath('.//td[@class = "clans_name"]//a/@href')))
        clans_motto = [tag.text_content() for tag in dados.xpath('.//span[@class = "clans_motto"]')]

        clans = []
        for nome, link, motto in zip(clans_nomes, clans_links, clans_motto):
            clans.append([nome, 'https://www.runeclan.com' + link, motto.replace("\"", "")])

        for clan in clans:
            barra_progresso.value +=  1
            resultado_motto = model.predict(clan[2], k = 1)           
        
            if resultado_motto[0] == ('__label__pt',):
                clans_pt_br.append([clan[0], clan[1]])
                nome_clan.value = '"' + clan[0] + '" identificado...'

        min +=  1

def procurar_runeclan(clans_pt_br, nome_clan, barra_progresso, cancelar_operacao, min):
    t1 = Thread(target = thread_runeclan, args = (clans_pt_br, nome_clan, barra_progresso, cancelar_operacao, min, min+83, ))
    t2 = Thread(target = thread_runeclan, args = (clans_pt_br, nome_clan, barra_progresso, cancelar_operacao, min+83+1, min+83*2, ))
    t3 = Thread(target = thread_runeclan, args = (clans_pt_br, nome_clan, barra_progresso, cancelar_operacao, min+83*2+1, min+83*3, ))
    t1.start(); t2.start(); t3.start()
    t1.join(); t2.join(); t3.join()
    sys.exit()

class MenuPrincipal:
    def __init__(self):
        def verificar_update():
            ATUAL = 3.0

            def tela_aviso_outdated():
                frame_aviso = ttk.Frame(self.top)
                frame_aviso.place(relx = 0.015, rely = 0.02, relheight = 0.96, relwidth = 0.97)
                frame_aviso.configure(relief = 'groove')
                frame_aviso.configure(borderwidth = '2')
                frame_aviso.configure(relief = 'groove')

                titulo_aviso = ttk.Label(frame_aviso)
                titulo_aviso.place(relx = 0.18, rely = 0.021, height = 39, width = 400)
                titulo_aviso.configure(font = self.font10)
                titulo_aviso.configure(anchor = 's')
                titulo_aviso.configure(justify = 'center')
                titulo_aviso.configure(text = 'Nova versão disponível')

                texto1_titulo = ttk.Label(frame_aviso)
                texto1_titulo.place(relx = 0.23, rely = 0.3, height = 20, width = 200)
                texto1_titulo.configure(font = self.font12)
                texto1_titulo.configure(anchor = 'ne')
                texto1_titulo.configure(justify = 'right')
                texto1_titulo.configure(text = 'Versão atual:')

                texto1_mensagem = tk.Message(frame_aviso)
                texto1_mensagem.place(relx = 0.54, rely = 0.31, relheight = 0.030, relwidth = 0.045)
                texto1_mensagem.configure(font = self.font11)
                texto1_mensagem.configure(background = '#d9d9d9')
                texto1_mensagem.configure(highlightbackground = '#d9d9d9')
                texto1_mensagem.configure(highlightcolor = 'black')
                texto1_mensagem.configure(anchor = 'center')
                texto1_mensagem.configure(justify = 'center')       
                texto1_mensagem.configure(text = f'{ATUAL}')

                texto2_titulo = ttk.Label(frame_aviso)
                texto2_titulo.place(relx = 0.265, rely = 0.365, height = 20, width = 200)
                texto2_titulo.configure(font = self.font12)
                texto2_titulo.configure(anchor = 'ne')
                texto2_titulo.configure(justify = 'right')
                texto2_titulo.configure(text = 'Versão disponível:')

                texto2_mensagem = tk.Message(frame_aviso)
                texto2_mensagem.place(relx = 0.575, rely = 0.375, relheight = 0.030, relwidth = 0.045)
                texto2_mensagem.configure(font = self.font11)
                texto2_mensagem.configure(background = '#d9d9d9')
                texto2_mensagem.configure(highlightbackground = '#d9d9d9')
                texto2_mensagem.configure(highlightcolor = 'black')
                texto2_mensagem.configure(anchor = 'center')
                texto2_mensagem.configure(justify = 'center')
                texto2_mensagem.configure(text = f'{versao}')

                texto_download = ttk.Label(frame_aviso)
                texto_download.place(relx = 0.36, rely = 0.485, height = 29, width = 200)
                texto_download.configure(font = self.font11)
                texto_download.configure(anchor = 'w')
                texto_download.configure(justify = 'left')
                texto_download.configure(text = 'Download disponível em:')

                botao_download = ttk.Button(frame_aviso, text = 'GitHub', command = lambda: webbrowser.open('https://github.com/PvMDragonic/Ranks-PT-BR/releases', new = 2, autoraise = True))
                botao_download.place(relx = 0.4, rely = 0.55, height = 35, width = 116)

                botao_voltar = ttk.Button(frame_aviso, text = 'Voltar', command = frame_aviso.destroy)
                botao_voltar.place(relx = 0.4, rely = 0.9, height = 35, width = 116)

            dados = html.fromstring(requests.get('https://github.com/PvMDragonic/Ranks-PT-BR/releases').content)
            versao = dados.xpath('.//h1[@class="d-inline mr-3"]//a/text()')       
            versao = float(versao[0].split(" ")[1])

            if versao > ATUAL:
                t = Thread(target = tela_aviso_outdated())
                t.start()
                t.join()

        self.top = tk.Tk()
        
        # Vai ser usado pra guardar os ranks já processados. Tá aqui por motivos de reutilização dos dados.
        self.cc = []

        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        
        self.font9 = '-family {Segoe UI} -size 10'
        self.font10 = '-family {Segoe UI} -size 23 -weight bold'
        self.font11 = '-family {Segoe UI} -size 11'
        self.font12 = '-family {Segoe UI} -size 11 -weight bold'

        self.style = ttk.Style()
        if sys.platform == 'win32':
            self.style.theme_use('winnative')
        self.style.configure('.',background = _bgcolor)
        self.style.configure('.',foreground = _fgcolor)
        self.style.configure('.',font = 'TkDefaultFont')
        self.style.map('.',background = [('selected', _compcolor), ('active',_ana2color)])

        self.top.geometry('664x506+732+149')
        self.top.minsize(120, 1)
        self.top.maxsize(3844, 1061)
        self.top.resizable(1, 1)
        self.top.configure(background = '#d9d9d9')
        self.top.title('Ranks PT-BR v3.0')
        self.top.resizable(False, False)

        self.TFrame1 = ttk.Frame(self.top)
        self.TFrame1.place(relx = 0.015, rely = 0.02, relheight = 0.96, relwidth = 0.97)
        self.TFrame1.configure(relief = 'groove')
        self.TFrame1.configure(borderwidth = '2')
        self.TFrame1.configure(relief = 'groove')
        self.TFrame1.configure(cursor = 'arrow')

        self.titulo = ttk.Label(self.TFrame1)
        self.titulo.place(relx = 0.248, rely = 0.021, height = 39, width = 295)
        self.titulo.configure(font = self.font10)
        self.titulo.configure(anchor = 's')
        self.titulo.configure(justify = 'center')
        self.titulo.configure(text = 'Ranks PT-BR')

        self.label_rank_geral = ttk.Label(self.TFrame1)
        self.label_rank_geral.place(relx = 0.124, rely = 0.247, height = 29, width = 505)
        self.label_rank_geral.configure(font = self.font11)
        self.label_rank_geral.configure(relief = 'flat')
        self.label_rank_geral.configure(anchor = 'w')
        self.label_rank_geral.configure(justify = 'left')
        self.label_rank_geral.configure(text = 'Rank geral — gera uma lista com o rank baseado no EXP total de cada clã.')

        self.label_rank_mes_atual = ttk.Label(self.TFrame1)
        self.label_rank_mes_atual.place(relx = 0.124, rely = 0.35, height = 39, width = 456)
        self.label_rank_mes_atual.configure(font = self.font11)
        self.label_rank_mes_atual.configure(anchor = 'w')
        self.label_rank_mes_atual.configure(justify = 'left')
        self.label_rank_mes_atual.configure(wraplength = '450')
        self.label_rank_mes_atual.configure(text = 'Rank mês atual — gera uma lista com o rank baseado no EXP feito (até o momento) no mês atual.')

        self.label_rank_mes_pass = ttk.Label(self.TFrame1)
        self.label_rank_mes_pass.place(relx = 0.124, rely = 0.473, height = 39, width = 495)
        self.label_rank_mes_pass.configure(font = self.font11)
        self.label_rank_mes_pass.configure(anchor = 'w')
        self.label_rank_mes_pass.configure(justify = 'left')
        self.label_rank_mes_pass.configure(wraplength = '470')
        self.label_rank_mes_pass.configure(text = 'Rank mês passado — gera uma lista com o rank baseado no EXP feito no mês passado.')

        self.label_rank_dxp = ttk.Label(self.TFrame1)
        self.label_rank_dxp.place(relx = 0.124, rely = 0.597, height = 29, width = 475)
        self.label_rank_dxp.configure(font = self.font11)
        self.label_rank_dxp.configure(anchor = 'w')
        self.label_rank_dxp.configure(justify = 'left')
        self.label_rank_dxp.configure(text = 'Rank DXP — gera uma lista com o rank baseado no último/atual DXP.')

        self.botao_rank_geral = ttk.Button(self.TFrame1, command = lambda: self._gerar_rank_clicado(1))
        self.botao_rank_geral.place(relx = 0.14, rely = 0.870, height = 35, width = 110)
        self.botao_rank_geral.configure(takefocus = '')
        self.botao_rank_geral.configure(text = 'Rank geral')
        self.botao_rank_geral.configure(cursor = 'hand2')

        self.botao_rank_mes_atual = ttk.Button(self.TFrame1, command = lambda: self._gerar_rank_clicado(2))
        self.botao_rank_mes_atual.place(relx = 0.326, rely = 0.870, height = 35, width = 110)
        self.botao_rank_mes_atual.configure(takefocus = '')
        self.botao_rank_mes_atual.configure(text = 'Rank mês atual')
        self.botao_rank_mes_atual.configure(cursor = 'hand2')

        self.botao_rank_mes_pass = ttk.Button(self.TFrame1, command = lambda: self._gerar_rank_clicado(3))
        self.botao_rank_mes_pass.place(relx = 0.512, rely = 0.870, height = 35, width = 110)
        self.botao_rank_mes_pass.configure(takefocus = '')
        self.botao_rank_mes_pass.configure(text = 'Rank mês pass.')
        self.botao_rank_mes_pass.configure(cursor = 'hand2')   

        self.botao_rank_dxp = ttk.Button(self.TFrame1, command = lambda: self._gerar_rank_clicado(4))
        self.botao_rank_dxp.place(relx = 0.699, rely = 0.870, height = 35, width = 111)
        self.botao_rank_dxp.configure(takefocus = '')
        self.botao_rank_dxp.configure(text = 'Rank DXP')
        self.botao_rank_dxp.configure(cursor = 'hand2')

        Thread(target = verificar_update()).start()

        self.top.mainloop()  

    def _tela_aviso_outdated(self, dataa, clans, qual_rank, cem_porcento):
        """Exibe uma tela de aviso caso dados tenham mais de 1 mês."""
        self.frame_tela_aviso = ttk.Frame(self.top)
        self.frame_tela_aviso.place(relx = 0.015, rely = 0.02, relheight = 0.96, relwidth = 0.97)
        self.frame_tela_aviso.configure(relief = 'groove')
        self.frame_tela_aviso.configure(borderwidth = '2')
        self.frame_tela_aviso.configure(relief = 'groove')

        titulo_mensagem = ttk.Label(self.frame_tela_aviso)
        titulo_mensagem.place(relx = 0.248, rely = 0.021, height = 39, width = 295)
        titulo_mensagem.configure(background = '#d9d9d9')
        titulo_mensagem.configure(foreground = '#000000')
        titulo_mensagem.configure(font = self.font10)
        titulo_mensagem.configure(anchor = 's')
        titulo_mensagem.configure(justify = 'center')
        titulo_mensagem.configure(text = 'Aviso')

        texto1_mensagem = tk.Message(self.frame_tela_aviso)
        texto1_mensagem.place(relx = 0, rely = 0.225, relheight = 0.292, relwidth = 1)
        texto1_mensagem.configure(background = '#d9d9d9')
        texto1_mensagem.configure(font = self.font11)
        texto1_mensagem.configure(foreground = '#000000')
        texto1_mensagem.configure(highlightbackground = '#d9d9d9')
        texto1_mensagem.configure(highlightcolor = 'black')
        texto1_mensagem.configure(anchor = 'center')
        texto1_mensagem.configure(justify = 'center')
        texto1_mensagem.configure(width = 1000)       
        texto1_mensagem.configure(text = f'Os dados atuais são de {dataa} e podem estar defazados.')

        texto2_mensagem = tk.Message(self.frame_tela_aviso)
        texto2_mensagem.place(relx = 0, rely = 0.500, relheight = 0.250, relwidth = 1)
        texto2_mensagem.configure(background = '#d9d9d9')
        texto2_mensagem.configure(font = self.font11)
        texto2_mensagem.configure(foreground = '#000000')
        texto2_mensagem.configure(highlightbackground = '#d9d9d9')
        texto2_mensagem.configure(highlightcolor = 'black')
        texto2_mensagem.configure(anchor = 'center')
        texto2_mensagem.configure(justify = 'center')
        texto2_mensagem.configure(width = 1000)
        texto2_mensagem.configure(text = 'É recomendado que os dados sejam atualizados,\npara garantirque todos os clãs sejam devidamente processados.')

        def ignorar_clicado():
            self.frame_tela_aviso.destroy()
            self._rankear_clans_pt_br(clans, qual_rank, cem_porcento)

        def atualizar_clicado():
            self.frame_tela_aviso.destroy()
            self.frame_que_uso_pra_tudo.destroy()
            self._selecionar_clans_pt_br(qual_rank)

        def retornar_clicado():
            self.frame_tela_aviso.destroy()
            self.frame_que_uso_pra_tudo.destroy()

        botao_ignorar = ttk.Button(self.frame_tela_aviso, text = 'Ignorar', command = ignorar_clicado)
        botao_ignorar.place(relx = 0.200, rely = 0.870, height = 35, width = 116)

        botao_atualizar = ttk.Button(self.frame_tela_aviso, text = 'Atualizar', command = atualizar_clicado)
        botao_atualizar.place(relx = 0.400, rely = 0.870, height = 35, width = 116)

        botao_retornar = ttk.Button(self.frame_tela_aviso, text = 'Retornar', command = retornar_clicado)
        botao_retornar.place(relx = 0.600, rely = 0.870, height = 35, width = 116)

    def _tela_coletando_dados(self):
        # Porque essa nomenclatura? Porque eu acabo chamando isso aqui de todos os cantos do código,
        # pra reutilizar em vez de ter que destuir e daí recriar. Três érres que chama, né? Bruh.
        self.frame_que_uso_pra_tudo = tk.Frame(self.top)
        self.frame_que_uso_pra_tudo.place(relx = 0.015, rely = 0.02, relheight = 0.96, relwidth = 0.97)
        self.frame_que_uso_pra_tudo.configure(relief = 'groove')
        self.frame_que_uso_pra_tudo.configure(borderwidth = "2")
        self.frame_que_uso_pra_tudo.configure(relief = "groove")
        self.frame_que_uso_pra_tudo.configure(background = "#d9d9d9")

        self.label_titulo_pra_tudo = ttk.Label(self.frame_que_uso_pra_tudo)
        self.label_titulo_pra_tudo.place(relx = 0.095, rely = 0.030, height = 50, width = 500)
        self.label_titulo_pra_tudo.configure(font = self.font10)
        self.label_titulo_pra_tudo.configure(anchor = 's')
        self.label_titulo_pra_tudo.configure(justify = 'center')
        self.label_titulo_pra_tudo.configure(text = '')

        self.label_aviso_pra_tudo = ttk.Label(self.frame_que_uso_pra_tudo)
        self.label_aviso_pra_tudo.place(relx = 0.095, rely = 0.130, height = 30, width = 500)
        self.label_aviso_pra_tudo.configure(font = self.font11)
        self.label_aviso_pra_tudo.configure(anchor = 's')
        self.label_aviso_pra_tudo.configure(justify = 'center')
        self.label_aviso_pra_tudo.configure(text = 'Por favor, aguarde...')
        
        self.barra_progresso = ttk.Progressbar(self.frame_que_uso_pra_tudo, maximum = "9150", length = "9150")
        self.barra_progresso.place(relx = 0.129, rely = 0.722, relwidth = 0.729, relheight = 0.0, height = 22)

        self.label_nome_clan = ttk.Label(self.frame_que_uso_pra_tudo)
        self.label_nome_clan.place(relx = 0.125, rely = 0.68, height = 19, width = 225)
        self.label_nome_clan.configure(font = "TkDefaultFont")
        self.label_nome_clan.configure(anchor = 'w')
        self.label_nome_clan.configure(justify = 'left')

        self.label_down_porcentagem = ttk.Label(self.frame_que_uso_pra_tudo)
        self.label_down_porcentagem.place(relx = 0.805, rely = 0.68, height = 19, width = 35)
        self.label_down_porcentagem.configure(font = "TkDefaultFont")
        self.label_down_porcentagem.configure(anchor = 'e')
        self.label_down_porcentagem.configure(justify = 'left')
        self.label_down_porcentagem.configure(text = '0%')

        def cancelar():
            global cancelar_operacao

            cancelar_operacao.value = 1
            self.frame_que_uso_pra_tudo.destroy()

        botao_cancelar = ttk.Button(self.frame_que_uso_pra_tudo, text = 'Cancelar', command = cancelar)
        botao_cancelar.place(relx = 0.400, rely = 0.885, height = 35, width = 116)        

    def _selecionar_clans_pt_br(self, botao_clicado):
        global parar_progresso
        global cancelar_operacao
        global barra_progresso
        global clans_pt_br
        global nome_clan

        def regra_de_tres(num):
            """Vai devolver uma porcentagem (baseada em 9150, que é o número de páginas na lista de clans do RuneClan * 10) exibindo até 1 casa decimal."""
            return "{:.1f}%".format((num * 100) / 9150)

        def atualizar_texto():
            """Fica atualizando as informações na tela enquanto o programa puxa os clãs pt-br do RuneClan."""       
            while parar_progresso.value == 0:
                self.label_down_porcentagem.configure(text = regra_de_tres(barra_progresso.value))
                self.label_nome_clan.configure(text = nome_clan.value)
                self.barra_progresso['value'] = barra_progresso.value
                sleep(0.1)

            if cancelar_operacao.value == 0:
                # Chegou aqui é porque terminou de coletar os dados.
                self.label_nome_clan.configure(text = 'Clãs coletados com sucesso!')
                self.label_down_porcentagem.configure(text = '100%')
                self.barra_progresso['value'] = '9150'    
                sleep(2)
                
                self._gerar_rank(qual_rank = botao_clicado, json_criado = True)

            sys.exit()

        def thread():
            """Gerencia os processos que coletam os clãs pt-br sem travar o resto do código."""
            global parar_progresso

            p1 = Process(target = procurar_runeclan, args = (clans_pt_br, nome_clan, barra_progresso, cancelar_operacao, 1, ))    
            p2 = Process(target = procurar_runeclan, args = (clans_pt_br, nome_clan, barra_progresso, cancelar_operacao, 251, ))
            p3 = Process(target = procurar_runeclan, args = (clans_pt_br, nome_clan, barra_progresso, cancelar_operacao, 501, ))
            p4 = Process(target = procurar_runeclan, args = (clans_pt_br, nome_clan, barra_progresso, cancelar_operacao, 751, ))
            p1.start(); p2.start(); p3.start(); p4.start()
            p1.join(); p2.join(); p3.join(); p4.join()

            if cancelar_operacao.value == 0:
                with open("clans_pt_br.json", "w") as f:
                    clans_pt_br.insert(0, datetime.now().isoformat())
                    json.dump(list(clans_pt_br), f, indent = 4)
                    f.close()

                parar_progresso.value = 1

            sys.exit()

        # Criando GUI                       
        self._tela_coletando_dados()
        self.label_titulo_pra_tudo.configure(text = "Coletando clãs PT-BR")

        # Reseta os valores antes de começar, caso não seja a primeira vez do usuário passando por ali.
        nome_clan.value = 'Procurando...'
        cancelar_operacao.value = 0
        barra_progresso.value = 0
        parar_progresso.value = 0  
        clans_pt_br[:] = []

        Thread(target = atualizar_texto).start()
        Thread(target = thread).start()

    def _exibir_dados_clans(self, qual_rank):
        """Mostra os dados salvos na lista 'clans_pt_br' em uma planílha, junto de opção pra salvar."""
        global clans_pt_br

        def retornar():
            self.frame_que_uso_pra_tudo.destroy()
            frame_exibir_ranks.destroy()

        def salvar():
            def salvar_arqv(qual):
                if qual == 1:  
                    nome = f'Rank {tipo} {data_rank_criado}.txt'              
                    with open(os.path.expanduser(f"~/Desktop/{nome}"), "w") as f:
                        if qual_rank != 3:
                            for i in range(1, len(self.cc)):
                                f.write(f"{i}º: {self.cc[i][0]}\n    EXP: {self.cc[i][1]}\n\n")                             
                        else:
                            for i in range(1, len(self.cc)):
                                f.write(f"{i}º: {self.cc[i][0]}\n    XP total: {self.cc[i][1]}\n    1º lugar: {self.cc[i][2]}\n    1º lugar XP: {self.cc[i][3]}\n\n")
                        f.close()
                elif qual == 2:
                    nome = f'Rank {tipo} {data_rank_criado}.xlsx' 
                    workbook = xlsxwriter.Workbook(os.path.expanduser(f"~/Desktop/{nome}"))
                    worksheet1 = workbook.add_worksheet()
                    worksheet1.set_column(0, 3, 20)

                    if qual_rank != 3:
                        for i in range(1, len(self.cc)):
                            worksheet1.write(f'A{i}', self.cc[i][0])
                            worksheet1.write(f'B{i}', self.cc[i][1])
                    else:
                        for i in range(1, len(self.cc)):
                            worksheet1.write(f'A{i}', self.cc[i][0])
                            worksheet1.write(f'B{i}', self.cc[i][1])
                            worksheet1.write(f'C{i}', self.cc[i][2])
                            worksheet1.write(f'D{i}', self.cc[i][3])

                    workbook.close()
                else:
                    nome = f'Rank {tipo} {data_rank_criado}.json'
                    with open(os.path.expanduser(f"~/Desktop/{nome}"), "w") as f:
                        del self.cc[0]
                        json.dump(self.cc, f, indent = 4)
                        f.close()

                label_salvar_explicacao.configure(text = f'O arquivo "{nome}"\nfoi salvo na Área de Trabalho com sucesso!')
                botao_txt.destroy()
                botao_sheet.destroy()
                botao_algum_louco_vai_querer_isso.destroy()
                botao_cancelar.configure(text = 'Ok')

            frame_salvar = tk.Frame(self.top)
            frame_salvar.place(relx = 0.015, rely = 0.02, relheight = 0.96, relwidth = 0.97)
            frame_salvar.configure(relief = 'groove')
            frame_salvar.configure(borderwidth = "2")
            frame_salvar.configure(relief = "groove")
            frame_salvar.configure(background = "#d9d9d9")

            label_salvar_explicacao = ttk.Label(frame_salvar)
            label_salvar_explicacao.place(relx = 0.095, rely = 0.35, height = 100, width = 500)
            label_salvar_explicacao.configure(background = '#d9d9d9')
            label_salvar_explicacao.configure(foreground = '#000000')
            label_salvar_explicacao.configure(font = self.font11)
            label_salvar_explicacao.configure(relief = 'flat')
            label_salvar_explicacao.configure(anchor = 's')
            label_salvar_explicacao.configure(justify = 'center')
            label_salvar_explicacao.configure(text = 'Selecione o tipo de arquivo no\nqual os dados serão salvos:')

            titulo_salvar = ttk.Label(frame_salvar)
            titulo_salvar.place(relx = 0.095, rely = 0.0125, height = 50, width = 500)
            titulo_salvar.configure(font = self.font10)
            titulo_salvar.configure(anchor = 'n')
            titulo_salvar.configure(justify = 'center')
            titulo_salvar.configure(text = 'Salvar em arquivo')

            botao_txt = ttk.Button(frame_salvar, text = '.txt', command = lambda: salvar_arqv(1))
            botao_txt.place(relx = 0.290, rely = 0.58, height = 30, width = 80)

            botao_sheet = ttk.Button(frame_salvar, text = '.xlsx', command = lambda: salvar_arqv(2))
            botao_sheet.place(relx = 0.425, rely = 0.58, height = 30, width = 80)

            botao_algum_louco_vai_querer_isso = ttk.Button(frame_salvar, text = '.json', command = lambda: salvar_arqv(3))
            botao_algum_louco_vai_querer_isso.place(relx = 0.560, rely = 0.58, height = 30, width = 80)

            botao_cancelar = ttk.Button(frame_salvar, text = 'Cancelar', command = frame_salvar.destroy)
            botao_cancelar.place(relx = 0.4, rely = 0.9, height = 35, width = 116)

        for child in self.frame_que_uso_pra_tudo.winfo_children():
            child.destroy()

        frame_exibir_ranks = tk.Frame(self.frame_que_uso_pra_tudo)
        frame_exibir_ranks.place(relx = 0.035, rely = 0.13, relheight = 0.7375, relwidth = 0.93)
        frame_exibir_ranks.configure(relief = 'groove')
        frame_exibir_ranks.configure(borderwidth = "2")
        frame_exibir_ranks.configure(relief = "groove")
        frame_exibir_ranks.configure(background = "#d9d9d9")

        botao_retornar = ttk.Button(self.frame_que_uso_pra_tudo, text = 'Retornar', command = retornar)
        botao_retornar.place(relx = 0.4, rely = 0.9, height = 35, width = 116)
        botao_salvar = ttk.Button(self.frame_que_uso_pra_tudo, text = 'Salvar', command = salvar)
        botao_salvar.place(relx = 0.855, rely = 0.025, height = 30, width = 80)
        
        scroll_vertical = ttk.Scrollbar(frame_exibir_ranks)
        scroll_vertical.pack(side = tk.RIGHT, fill = tk.Y)

        tabela = ttk.Treeview(frame_exibir_ranks, yscrollcommand = scroll_vertical.set)
        tabela.pack(expand = True, fill = tk.BOTH)

        scroll_vertical.config(command = tabela.yview)

        tabela.tag_configure('gray', background = '#ccccc0')

        def copiar_menu_popup():
            for item in tabela.selection():
                values = [tabela.item(item, 'text')]
                values.extend(tabela.item(item, 'values'))
                pyperclip.copy("\t".join(values))

        def mostrar_menu_popup(event):
            try:
                popup.selection = tabela.set(tabela.identify_row(event.y))
                popup.post(event.x_root, event.y_root)
            finally:
                popup.grab_release()

        popup = tk.Menu(tabela, tearoff = 0)
        popup.add_command(label = "Copiar", command = copiar_menu_popup)

        tabela.bind("<ButtonRelease-3>", mostrar_menu_popup)

        def copiar_ctrl_c(tree, event):
            for item in tree.selection():
                values = [tree.item(item, 'text')]
                values.extend(tree.item(item, 'values'))
                pyperclip.copy("\t".join(values))

        tabela.bind("<Control-Key-c>", lambda x: copiar_da_tabela(tabela, x))

        tabela['column'] = ('Pos', 'Clã', 'Experiência', 'PrimeiroNome', 'PrimeiroXP')
        tabela.column("#0", width = 0, stretch = tk.NO)
        tabela.column("Pos", anchor = tk.CENTER, width = 35, stretch = tk.NO)
        tabela.column("Clã", anchor = tk.CENTER, width = 134, stretch = tk.NO)
        tabela.column("Experiência", anchor = tk.CENTER, width = 134, stretch = tk.NO)
        tabela.column("PrimeiroNome", anchor = tk.CENTER, width = 134, stretch = tk.NO)
        tabela.column("PrimeiroXP", anchor = tk.CENTER, width = 134, stretch = tk.NO)

        tabela.heading("#0",text = "", anchor = tk.CENTER)
        tabela.heading("Pos", text = "Pos.", anchor = tk.CENTER)
        tabela.heading("Clã", text = "Clã", anchor = tk.CENTER)
        tabela.heading("Experiência", text = "Experiência", anchor = tk.CENTER)
        if qual_rank == 3:
            tabela.heading("PrimeiroNome", text = "1º lugar", anchor = tk.CENTER)
            tabela.heading("PrimeiroXP", text = "1º lugar EXP", anchor = tk.CENTER)

        with open('clans_pt_br.json') as f:
            tam_total = len(json.load(f))
            f.close()

        if self.cc == []:
            if qual_rank != 3:
                for i in range(len(clans_pt_br)):
                    self.cc.append([clans_pt_br[i][0], int(clans_pt_br[i][1].replace(",",""))])
            else:
                for i in range(len(clans_pt_br)):
                    self.cc.append([clans_pt_br[i][0], int(clans_pt_br[i][1].replace(",","")), clans_pt_br[i][2], clans_pt_br[i][3]])
    
            self.cc.sort(key = lambda x: x[1], reverse = True)
            self.cc.insert(0, qual_rank)

        # Salvo em variáveis aqui pra serem reutilizados na hora de salvar em arqv.
        tipo = { 1 : 'geral', 2 : 'mês atual', 3 : 'mês passado', 4 : 'DXP'}.get(qual_rank)
        data_rank_criado = datetime.now().strftime("%d-%m-%Y %H-%M-%S")

        tipo_rank = ttk.Label(self.frame_que_uso_pra_tudo)
        tipo_rank.place(relx = 0.03, rely = 0.01, height = 21, width = 300)
        tipo_rank.configure(font = self.font9)
        tipo_rank.configure(anchor = 'nw')
        tipo_rank.configure(justify = 'right')
        tipo_rank.configure(text = f'Rank {tipo} — {data_rank_criado.replace("-", "/", 2).replace("-", ":")}')

        quant_ignorados = ttk.Label(self.frame_que_uso_pra_tudo)
        quant_ignorados.place(relx = 0.03, rely = 0.045, height = 21, width = 150)
        quant_ignorados.configure(font = self.font9)
        quant_ignorados.configure(anchor = 'nw')
        quant_ignorados.configure(justify = 'right')
        quant_ignorados.configure(text = f'Clãs inativos: {tam_total - len(self.cc)}')

        quant_total = ttk.Label(self.frame_que_uso_pra_tudo)
        quant_total.place(relx = 0.03, rely = 0.08, height = 21, width = 150)
        quant_total.configure(font = self.font9)
        quant_total.configure(anchor = 'nw')
        quant_total.configure(justify = 'right')
        quant_total.configure(text = f'Clãs rankeados: {len(self.cc)}')

        if qual_rank != 3:
            for i in range(1, len(self.cc)):
                if type(self.cc[i][1]) == int:
                    self.cc[i][1] = format(self.cc[i][1],",")
                    self.cc[i][1] = str(self.cc[i][1]).replace(",",".")

                if i % 2 == 0:
                    tabela.insert(parent = '', index = 'end', iid = i, values = (f'{i}º', self.cc[i][0], self.cc[i][1]))
                else:
                    tabela.insert(parent = '', index = 'end', iid = i, tag = ('gray', ), values = (f'{i}º', self.cc[i][0], self.cc[i][1]))
        else:
            for i in range(1, len(self.cc)):
                if type(self.cc[i][1]) == int:
                    self.cc[i][1] = format(self.cc[i][1],",")
                    self.cc[i][1] = str(self.cc[i][1]).replace(",",".")
                    self.cc[i][3] = self.cc[i][1].replace(",",".")

                if i % 2 == 0:
                    tabela.insert(parent = '', index = 'end', iid = i, values = (f'{i}º', self.cc[i][0], self.cc[i][1], self.cc[i][2], self.cc[i][3]))
                else:
                    tabela.insert(parent = '', index = 'end', iid = i, tag = ('gray', ), values = (f'{i}º', self.cc[i][0], self.cc[i][1], self.cc[i][2], self.cc[i][3]))

    def _rankear_clans_pt_br(self, clans, qual_rank, cem_porcento):
        """Coleta os dados individuais de cada clã pt-br para depois gerar uma tabela com os ranques."""
        global parar_progresso
        global cancelar_operacao
        global barra_progresso
        global clans_pt_br
        global nome_clan

        def regra_de_tres(num):
            return "{:.1f}%".format((num * 100) / cem_porcento)

        def atualizar_texto():
            """Fica atualizando as informações na tela enquanto o programa puxa os dados dos clãs pt-br do RuneClan."""       
            while parar_progresso.value == 0:
                self.label_down_porcentagem.configure(text = regra_de_tres(barra_progresso.value))
                self.label_nome_clan.configure(text = nome_clan.value)
                self.barra_progresso['value'] = barra_progresso.value
                sleep(0.1)

            if cancelar_operacao.value == 0:
                # Chegou aqui é porque terminou de coletar os dados.
                self.label_nome_clan.configure(text = 'Rank gerado com sucesso!') 
                self.label_down_porcentagem.configure(text = '100%')
                sleep(3)

                if cancelar_operacao.value == 0:
                    self._exibir_dados_clans(qual_rank)

            sys.exit()

        def coleta_dados():
            """Gerencia os threads que coletam os dados dos clãs pt-br sem travar o resto do código."""
            global parar_progresso

            func = { 1 : thread_rank_geral, 2 : thread_rank_mes_atual, 3 : thread_rank_mes_pass, 4 : thread_rank_dxp }.get(qual_rank)

            t1 = Thread(target = func, args = (clans[0], nome_clan, barra_progresso, cancelar_operacao, clans_pt_br, ))
            t2 = Thread(target = func, args = (clans[1], nome_clan, barra_progresso, cancelar_operacao, clans_pt_br, ))
            t3 = Thread(target = func, args = (clans[2], nome_clan, barra_progresso, cancelar_operacao, clans_pt_br, ))
            t1.start(); t2.start(); t3.start()
            t1.join(); t2.join(); t3.join()

            parar_progresso.value = 1

            sys.exit()

        self.barra_progresso = ttk.Progressbar(self.frame_que_uso_pra_tudo, maximum = cem_porcento, length = cem_porcento)
        self.barra_progresso.place(relx = 0.129, rely = 0.722, relwidth = 0.729, relheight = 0.0, height = 22)
        self.label_nome_clan.configure(text = 'Analisando clãs pt-br...')
        self.label_down_porcentagem.configure(text = '0.0%')
        self.barra_progresso['value'] = 0

        # Reseta os valores antes de começar, caso não seja a primeira vez do usuário passando por ali.
        nome_clan.value = 'Procurando...'
        cancelar_operacao.value = 0
        barra_progresso.value = 0
        parar_progresso.value = 0  
        clans_pt_br[:] = []

        Thread(target = coleta_dados).start()
        Thread(target = atualizar_texto).start()

    def _gerar_rank(self, qual_rank = 0, json_criado = False):
        def escolher_titulo():
            return { 1 : 'rank geral', 2 : 'rank mês atual', 3 : 'rank mês passado', 4 : 'rank Double XP' }.get(qual_rank)

        if json_criado: # Nesse caso eu reutilizo o que já existe, pra não ter que destruir e daí recriar em seguida.       
            self.label_titulo_pra_tudo.configure(text = 'Gerando ' + escolher_titulo())
        else:
            self._tela_coletando_dados()
            self.label_titulo_pra_tudo.configure(text = 'Gerando ' + escolher_titulo())

        if self.cc != [] and self.cc[0] == qual_rank:
            self._exibir_dados_clans(qual_rank)
        else:
            self.cc = []

            with open('clans_pt_br.json') as f:
                clans = json.load(f)
                f.close()

            # Tem que se livrar do primeiro elemento, pra não atrapalhar mais pra frente.
            data_ultima_coleta = datetime.fromisoformat(clans.pop(0))

            if datetime.now() - data_ultima_coleta > timedelta(days = 30):
                self._tela_aviso_outdated(data_ultima_coleta.strftime("%d/%m/%Y"), [clans[i::3] for i in range(3)], qual_rank, len(clans))
            else:         
                self._rankear_clans_pt_br([clans[i::3] for i in range(3)], qual_rank, len(clans))

    # 'qual_botao' se refere aos botões no menu inicial — 1 à 4, da esquerda pra direita.
    def _gerar_rank_clicado(self, qual_botao):
        """Chamado pelos botões no menu inicial do programa.""" 
        if file_exists('clans_pt_br.json'):
            self._gerar_rank(qual_rank = qual_botao)
        else:
            self._selecionar_clans_pt_br(qual_botao)

if __name__ == '__main__':
    clans_pt_br = Manager().list()
    nome_clan = Manager().Value(c_char_p, "")
    barra_progresso = Manager().Value('i', 0)
    cancelar_operacao = Manager().Value('i', 0)
    parar_progresso = Manager().Value('i', 0)

    MenuPrincipal()