<b>AVISO: Como o RuneClan encerrou suas atividades, o Ranks PT-BR encontra-se defazado e não funciona mais.</b>

# Ranks PT-BR
O Ranks PT-BR é um programa de desktop feito em Python para gerar listas com ranques por XP dos clãs PT-BR do RuneScape 3.

<p align="center">
  <img src="https://i.imgur.com/gI6vu68.png" alt="Ranks PT-BR tela de ranks"/>
</p>

## Funcionamento
O programa funciona atrelado ao RuneClan. Na sua primeira execução, ou então a cada mês, o programa irá varrer o site atrás de Clãs cujo lema esteja em Português e armazenar seus nomes em um json, que serve como referência toda vez que uma lista de ranques é gerada.

## Funcionalidades
- Gerar ranking para classificação geral, mensal, do mês anterior e do Double XP;
- Visualizar os dados diretamente no programa, por meio de uma tabela;
- Opções para salvar os dados coletados em .json, .xlsx e .txt;
- Verificador automático de nova atualização disponível.

## Bugs conhecidos
- A detecção da lingua portuguesa não é perfeita, então alguns falso-positivos e falso-negativos acabam passando;
- A tabela com os resultados era para ser listrada, com o intuito de melhorar a visualização, mas alguma coisa em versões mais recentes do Python e/ou TkInter fazem com que a cor não seja aplicada, mesmo que o código não gere erro;
- A aplicação simplesmente não compila corretamente pelo PyInstaller, impossibilitando usar a Versão 3.0 em diante como executável.

# Galeria
<p align="center">
  <img src="https://i.imgur.com/rsfADr5.png" alt="Ranks PT-BR tela inicial" width="300" height="241"/> <img src="https://i.imgur.com/C2Oz53P.png" alt="Ranks PT-BR tela carregando" width="300" height="241"/> <img src="https://i.imgur.com/Ick0yHO.png" alt="Ranks PT-BR tela salvar arquivos" width="300" height="241"/>
  <img src="https://i.imgur.com/l3zjvl9.png" alt="Ranks PT-BR tela salvar arquivos" width="300" height="241"/>
</p>