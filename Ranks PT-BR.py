from lxml import html
import threading
import requests
import time
import os

class RanksTotais:
    def __init__(self):
        self.total = []
        self.nomeArquivo = "Rank geral"

    def _transformar(self, lst):
        # Transforma em lista, pra poder manipular.
        lst = list(lst)

        # Tem que deletar o primeiro elemento porque vem com um espaço na frente.
        del lst[0]

        # Retira as vírgulas que vem na string.
        lst = self._virgulas(lst)

        # Junta de novo e retorna.
        lst = "".join(lst)
        return float(lst)

    def _virgulas(self, lst): 
        continuar = True

        while True:
            for i in range(len(lst)):
                if (lst[i] == ","):
                    del lst[i]
                    continuar = True

                    # Tem que recomeçar o loop agora que removeu um elemento, senão vai acabar pulando elementos mais pra frente.
                    break
                else:
                    continuar = False

            # Só vai chegar aqui se passar pela lista toda e não encontrar ",".
            if (continuar == False):
                break
        return lst

    def _separarListas(self, lista, quantasListas):
        return (lista[i::quantasListas] for i in range(quantasListas))

    def _pegarDadosURL(self, lista):
        for x in range(len(lista)):
            try:
                pagina = requests.get(lista[x])
                dados = html.fromstring(pagina.content)

                # Buscam no código-fonte HTML da página as informações do nome do clan e do XP.
                nomeClan = dados.xpath('//td[@class="clan_left"]//div[@class="clan_name"]/text()')
                xp = dados.xpath('//td[@class="clan_left"]/text()')

                # 'xp' é uma array com várias informações, mas só o elemento da posição 4 que é o XP total.
                clan = [nomeClan[0], self._transformar(xp[4])] 
                
                self.total.append(clan)

                print(f"Informações de '{clan[0]}' coletadas com sucesso.")
            except:
                print(f"Houve um erro na leitura da URL '{lista[x]}', e portanto ela foi ignorada.")

    def _processarDados(self, arquivo):
        try:
            listaClans = open(arquivo, "r")

            # Tem que ser com .splitlines() pra não ficar o "\n" no final da string da URL.
            linhas = listaClans.read().splitlines()
            listaClans.close()

            # Isso aqui vai separar os links em duas listas, pra serem processadas por dois threads.
            linhas = list(self._separarListas(linhas, 3))
            primeiroGrupo = linhas[0]
            segundoGrupo = linhas[1]
            terceiroGrupo = linhas[2]

            print("Coletando informações...\n")

            # Vai criar 3 threads, que vão coletar os dados.
            thread1 = threading.Thread(target=self._pegarDadosURL,args=(primeiroGrupo,), daemon=True)
            thread2 = threading.Thread(target=self._pegarDadosURL,args=(segundoGrupo,), daemon=True)
            thread3 = threading.Thread(target=self._pegarDadosURL,args=(terceiroGrupo,), daemon=True)
            thread1.start()
            thread2.start()
            thread3.start()

            # O código vai esperar os threads terminarem antes de continuar.
            thread1.join()
            thread2.join()
            thread3.join()   
        except:
            x = input("Arquivo 'clans.txt' não encontrado.\n\nPressione 'Enter' para continuar.")
        
    def _formatoBrasileiro(self, numeros):
        for i in range(len(numeros)):
            # Vai formatar o número separando as casas de milhares por , (porque não achei como fazer com . direto).
            numeros[i][1] = f'{numeros[i][1]:,}'
            # Vai trocar todas as , por .
            numeros[i][1] = str(numeros[i][1].replace(",","."))
            # Vai remover os últimos dois caracteres da string, que são left-overs de quando o dado tava em formato float.
            numeros[i][1] = numeros[i][1][:-2]

        return numeros

    def gerarRanks(self):
        self._processarDados("clans.txt")

        print("\n\nGerando arquivo...")

        # Ordena os valores da array 'total' com base nos XP de cada clan.
        self.total = sorted(self.total, key=lambda x: x[1], reverse=True) 

        # Deixa os dados no padrão numérico brasileiro.
        self.total = self._formatoBrasileiro(self.total)

        # Pega a data no momento da execução.
        hoje = time.strftime("%d-%m-%Y %H-%M-%S")

        # Cria um arquivo na área de trabalho do usuário, e então vai escrevendo linha por linha nele os clas e ranks.
        with open(os.path.expanduser(f"~/Desktop/{self.nomeArquivo} {hoje}.txt"), "w") as f:
            for i in range(len(self.total)):
                f.write(f"{i + 1}º: {self.total[i][0]} — {self.total[i][1]}\n")
        f.close()

        x = input(f"\nArquivo '{self.nomeArquivo} {hoje}.txt' salvo na Área de Trabalho.\nPrecione 'Enter' para continuar.")

class RanksMesPassado(RanksTotais):
    def __init__(self):
        self.total = []
        self.nomeArquivo = "Rank mês passado"

    def _transformar(self, lst):
        lst = list(lst)

        lst = self._virgulas(lst)

        lst = "".join(lst)
        return float(lst)

    def _pegarDadosURL(self, lista):
        for x in range(len(lista)):
            try:
                pagina = requests.get(lista[x])
                dados = html.fromstring(pagina.content)

                nomeClan = dados.xpath('//td[@class="clan_left"]//div[@class="clan_name"]/text()')

                xp = dados.xpath('//td[@class="clan_right"]//div[@class="clan_trk_wrap"]//table[@class="regular"]//b/text()')

                primeiroLugar = dados.xpath('//td[@class="clan_right"]//div[@class="clan_trk_wrap"]//table[@class="regular"]//td[@class="clan_td clan_rsn2"]//a/text()')

                clan = [nomeClan[0], self._transformar(xp[1]), primeiroLugar[0]] 
                
                self.total.append(clan)

                print(f"Informações de '{clan[0]}' coletadas com sucesso.")
            except:
                print(f"Houve um erro na leitura da URL '{lista[x]}', e portanto ela foi ignorada.")

    def gerarRanks(self):
        self._processarDados("clans_mensal.txt")

        print("\n\nGerando arquivo...")

        self.total = sorted(self.total, key=lambda x: x[1], reverse=True) 

        self.total = self._formatoBrasileiro(self.total)

        hoje = time.strftime("%d-%m-%Y %H-%M-%S")

        with open(os.path.expanduser(f"~/Desktop/{self.nomeArquivo} {hoje}.txt"), "w") as f:
            for i in range(len(self.total)):
                f.write(f"{i + 1}º: {self.total[i][0]} — {self.total[i][1]} — {self.total[i][2]}\n")
        f.close()

        x = input(f"\nArquivo '{self.nomeArquivo} {hoje}.txt' salvo na Área de Trabalho.\nPrecione 'Enter' para continuar.")

class RanksMesAtual(RanksMesPassado):
    def __init__(self):
        self.total = []
        self.nomeArquivo = "Rank mês atual"

        # Usei isso aqui só pra não ter que copiar e colar (denovo) o mesmo método só pra mudar um único número.
        self.posicao = 3

    def _pegarDadosURL(self, lista):
        for x in range(len(lista)):
            try:
                pagina = requests.get(lista[x])
                dados = html.fromstring(pagina.content)

                nomeClan = dados.xpath('//td[@class="clan_left"]//div[@class="clan_name"]/text()')
                xp = dados.xpath('//td[@class="clan_left"]//td[@class="clan_td clan_td_stat_xpgain"]/text()')

                clan = [nomeClan[0], self._transformar(xp[self.posicao])] 
                
                self.total.append(clan)

                print(f"Informações de '{clan[0]}' coletadas com sucesso.")
            except:
                print(f"Houve um erro na leitura da URL '{lista[x]}', e portanto ela foi ignorada.")

    def gerarRanks(self):
        self._processarDados("clans_mensal.txt")

        print("\n\nGerando arquivo...")

        self.total = sorted(self.total, key=lambda x: x[1], reverse=True) 

        self.total = self._formatoBrasileiro(self.total)

        hoje = time.strftime("%d-%m-%Y %H-%M-%S")

        with open(os.path.expanduser(f"~/Desktop/{self.nomeArquivo} {hoje}.txt"), "w") as f:
            for i in range(len(self.total)):
                f.write(f"{i + 1}º: {self.total[i][0]} — {self.total[i][1]}\n")
        f.close()

        x = input(f"\nArquivo '{self.nomeArquivo} {hoje}.txt' salvo na Área de Trabalho.\nPrecione 'Enter' para continuar.")

class RanksDXP(RanksMesAtual):
    def __init__(self):
        self.total = []
        self.nomeArquivo = "Rank DXP"
        self.posicao = 4

def limparTelaMuitoFoda():
    for i in range(30):
        print("")

while True:
    limparTelaMuitoFoda()
    print('================ DIGITE PARA SELECIONAR ================')
    print(' "1" — Gerar rank geral dos clãs PT-BR (clans.txt);')
    print(' "2" — Gerar rank do mês atual dos clãs PT-BR (clans_mensal.txt);')
    print(' "3" — Gerar rank do último mês dos clãs PT-BR (clans_mensal.txt);')
    print(' "4" — Gerar rank do último DXP dos clãs PT-BR (clans_mensal.txt).')

    try:
        x = int(input())

        if x == 1:
            limparTelaMuitoFoda()
            ranks = RanksTotais()
            ranks.gerarRanks()
        elif x == 2:
            limparTelaMuitoFoda()
            ranks = RanksMesAtual()
            ranks.gerarRanks()
        elif x == 3:
            limparTelaMuitoFoda()
            ranks = RanksMesPassado()
            ranks.gerarRanks()
        elif x == 4:
            limparTelaMuitoFoda()
            ranks = RanksDXP()
            ranks.gerarRanks()
        else:
            y = input("\n>> Você não digiou uma opção válida. Precione 'Enter' para continuar.\n")
    except:
        y = input("\n>> Você não digiou uma opção válida. Precione 'Enter' para continuar.\n")