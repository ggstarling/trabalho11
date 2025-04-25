@author: Gustavo Starling

# Análise climática da região sul do Brasil com dados WorldClim

Este projeto tem como objetivo analisar dados climáticos históricos da Região Sul do Brasil, utilizando a base de dados WorldClim. Serão geradas estatísticas descritivas e visualizações como mapas, histogramas e boxplots para entender melhor os padrões de temperatura na região.

**Dados:**

- Base de dados: WorldClim (versão 2.1)
- Variável climática: Temperatura Máxima (média de 1970-2000)
- Resolução espacial: 2.5 minutos (~25 km²)

**Estrutura do Projeto:**

trabalho01/
├── data/          # Contém os arquivos .tif do WorldClim e o shapefile da Região Sul.
├── outputs/       # Armazena as figuras geradas e quaisquer arquivos de saída (ex: CSVs, se você criar).
├── dataAnalysis.py  # Script Python para carregar os dados e calcular estatísticas básicas.
├── dataFigures.py   # Script Python para gerar as visualizações (mapas, histogramas, boxplots).
├── main.py          # Script Python principal para executar as análises e gerar as figuras.
└── README.md        # Este arquivo, com informações sobre o projeto.

**Resultados Esperados:**

Ao executar o script `main.py`, serão geradas diversas figuras (mapas de temperatura, histogramas, boxplots por mês) que serão salvas na pasta `outputs/`. Além disso, tabelas com estatísticas básicas serão impressas no console ou salvas em arquivos.
=======
# trabalho01
Projeto para análise de dados climáticos da Região Sul do Brasil utilizando a base WorldClim.
>>>>>>> 758b2618c66765c1ac3efb97d36517f355df324a
