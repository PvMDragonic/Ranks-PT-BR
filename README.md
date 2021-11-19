# Ranks PT-BR
O Ranks PT-BR é um programa de desktop feito em Python para gerar listas com ranques por XP dos clãs PT-BR do RuneScape 3.

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