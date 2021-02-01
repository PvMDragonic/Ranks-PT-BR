from lxml import html
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

    def _processarDados(self):
        try:
            listaClans = open("clans.txt", "r")

            # Tem que ser com .splitlines() pra não ficar o "\n" no final da string da URL.
            linhas = listaClans.read().splitlines()
            listaClans.close()

            print("Coletando informações...\n")

            for x in range(len(linhas)):
                try:
                    pagina = requests.get(linhas[x])
                    dados = html.fromstring(pagina.content)

                    # Buscam no código-fonte HTML da página as informações do nome do clan e do XP.
                    nome = dados.xpath('//td[@class="clan_left"]//div[@class="clan_name"]/text()')
                    info = dados.xpath('//td[@class="clan_left"]/text()')

                    # 'info' é uma array com várias informações, mas só o elemento da posição 4 que é o XP total.
                    clan = [nome[0], self._transformar(info[4])] 
                    
                    self.total.append(clan)

                    print(clan)
                except:
                    print(f"Houve um erro na leitura da URL '{linhas[x]}', e portanto ela foi ignorada.")
        except:
            x = input("Arquivo 'clans.txt' não encontrado.\n\nPressione 'Enter' para continuar.")
        
    def gerarRanks(self):
        self._processarDados()

        print("\n\nGerando arquivo...")

        # Ordena os valores da array 'total' com base nos XP de cada clan.
        self.total = sorted(self.total, key=lambda x: x[1], reverse=True) 

        # Pega a data no momento da execução.
        hoje = time.strftime("%d-%m-%Y %H-%M-%S")

        with open(os.path.expanduser(f"~/Desktop/{self.nomeArquivo} {hoje}.txt"), "w") as f:
            for i in range(len(self.total)):
                f.write(f"{i + 1}º: {self.total[i][0]} — {self.total[i][1]:,}\n")
        f.close()

        x = input(f"\nArquivo '{self.nomeArquivo} {hoje}.txt' salvo na Área de Trabalho.\nPrecione 'Enter' para continuar.")

class RanksMensal(RanksTotais):
    def __init__(self):
        self.total = []
        self.nomeArquivo = "Rank mensal"

        # Usei isso aqui só pra não ter que copiar e colar (denovo) o mesmo método só pra mudar um único número.
        self.posicao = 3

    def _transformar(self, lst):
        # Transforma em lista, pra poder manipular.
        lst = list(lst)

        # Retira as vírgulas que vem na string.
        lst = self._virgulas(lst)

        # Junta de novo e retorna.
        lst = "".join(lst)
        return float(lst)

    def _processarDados(self):
        try:
            listaClans = open("clans.txt", "r")

            # Tem que ser com .splitlines() pra não ficar o "\n" no final da string da URL.
            linhas = listaClans.read().splitlines()
            listaClans.close()

            print("Coletando informações...\n")

            for x in range(len(linhas)):
                try:
                    pagina = requests.get(linhas[x])
                    dados = html.fromstring(pagina.content)

                    # Buscam no código-fonte HTML da página as informações do nome do clan e do XP.
                    nome = dados.xpath('//td[@class="clan_left"]//div[@class="clan_name"]/text()')
                    info = dados.xpath('//td[@class="clan_left"]//td[@class="clan_td clan_td_stat_xpgain"]/text()')

                    # 'info' vem em formato de array puxando um bando de coisa junto. 
                    # Só o da posição da variável 'self.posicao' que é o dado correto.
                    clan = [nome[0], self._transformar(info[self.posicao])] 
                    
                    self.total.append(clan)

                    print(clan)
                except:
                    print(f"Houve um erro na leitura da URL '{linhas[x]}', e portanto ela foi ignorada.")
        except:
            x = input("Arquivo 'clans.txt' não encontrado.\n\nPressione 'Enter' para continuar.")

class RanksDXP(RanksMensal):
    def __init__(self):
        self.total = []
        self.nomeArquivo = "Rank DXP"
        self.posicao = 4

def limparTelaMuitoFoda():
    for i in range(30):
        print("")

while True:
    limparTelaMuitoFoda()
    print('============= DIGITE PARA SELECIONAR =============')
    print(' "1" — Gerar rank geral dos clãs PT-BR;')
    print(' "2" — Gerar rank mensal dos clãs PT-BR;')
    print(' "3" — Gerar rank do último DXP dos clãs PT-BR.')

    try:
        x = int(input())

        if x == 1:
            limparTelaMuitoFoda()
            ranks = RanksTotais()
            ranks.gerarRanks()
        elif x == 2:
            limparTelaMuitoFoda()
            ranks = RanksMensal()
            ranks.gerarRanks()
        elif x == 3:
            limparTelaMuitoFoda()
            ranks = RanksDXP()
            ranks.gerarRanks()
        else:
            y = input("\n>> Você não digiou uma opção válida. Precione 'Enter' para continuar.\n")
    except:
        y = input("\n>> Você não digiou uma opção válida. Precione 'Enter' para continuar.\n")