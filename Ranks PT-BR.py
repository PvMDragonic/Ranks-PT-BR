from lxml import html
import requests
import time
import os

total = []

def transformar(lst): #Transforma em float (porque vem como string).
    lst = list(lst)
    del lst[0] #Tem que deletar o primeiro elemento porque vem com um espaço na frente.
    lst = virgulas(lst)
    lst = "".join(lst)
    return float(lst)

def virgulas(lst): #Retira as vírgulas que vem na string.
    continuar = True
    while True:
        for i in range(len(lst)):
            if (lst[i] == ","):
                del lst[i]
                continuar = True
                break
            else:
                continuar = False
        if (continuar == False):
            break
    return lst
try:
    listaClans = open("clans.txt", "r")
    linhas = listaClans.read().splitlines() #Tem que ser assim, com .splitlines(), pra não ficar o "\n" no final da string da URL.
    listaClans.close()
except:
    x = input("Arquivo 'clans.txt' não encontrado.\n\nPressione 'Enter' para encerrar.")
    exit()

print("Coletando informações...\n")
for x in range(len(linhas)):
    try:
        pagina = requests.get(linhas[x])
        dados = html.fromstring(pagina.content)

        #Buscam no código-fonte HTML da página as informações do nome do clan e do XP.
        nome = dados.xpath('//td[@class="clan_left"]//div[@class="clan_name"]/text()')
        info = dados.xpath('//td[@class="clan_left"]/text()')
        clan = [nome[0], transformar(info[4])] #O XP (segundo dado) vem junto de um bando de informação inútil, salvo em uma array, por conta do jeito que o site foi feito.
        
        total.append(clan)
        print(clan)
    except:
        print("A URL '" + linhas[x] + "' é inválida, e por tanto, foi ignorada.")

print("\n\nGerando arquivo...")
total = sorted(total, key=lambda x: x[1], reverse=True) #Ordena os valores da array 'total' com base nos XP de cada clan.
hoje = time.strftime("%d-%m-%Y %H-%M-%S") #Pega a data no momento da execução.

with open(os.path.expanduser("~/Desktop/Ranks " + hoje + ".txt"), "w") as f:
    for i in range(len(total)):
        f.write(total[i][0] + " — {:,}".format(total[i][1]) + "\n")
f.close()

x = input("\nArquivo 'Ranks " + hoje + ".txt' salvo na Área de Trabalho.")