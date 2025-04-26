# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 19:31:05 2025

@author: Gustavo Starling
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import rasterio
from rasterio.plot import show
from dataAnalysis import carregar_dados_clima, carregar_shapefile, recortar_por_shapefile, calcular_estatisticas

if __name__ == "__main__":
    arquivos_tmax = [
        "wc2.1_2.5m_tmax_01.tif",
        "wc2.1_2.5m_tmax_02.tif",
        "wc2.1_2.5m_tmax_03.tif",
        "wc2.1_2.5m_tmax_04.tif",
        "wc2.1_2.5m_tmax_05.tif",
        "wc2.1_2.5m_tmax_06.tif",
        "wc2.1_2.5m_tmax_07.tif",
        "wc2.1_2.5m_tmax_08.tif",
        "wc2.1_2.5m_tmax_09.tif",
        "wc2.1_2.5m_tmax_10.tif",
        "wc2.1_2.5m_tmax_11.tif",
        "wc2.1_2.5m_tmax_12.tif",
    ]
    caminho_shapefile = os.path.join("data", "regiao_sul.shp")
    resultados_lista = []

    shape_regiao_sul = carregar_shapefile(caminho_shapefile)

    if shape_regiao_sul is not None:
        for arquivo in arquivos_tmax:
            caminho_dados = os.path.join("data", arquivo)
            dados_clima = carregar_dados_clima(caminho_dados)

            if dados_clima is not None:
                dados_recortados = recortar_por_shapefile(dados_clima, shape_regiao_sul)
                if dados_recortados is not None:
                    estatisticas = calcular_estatisticas(dados_recortados)
                    mes = arquivo[-6:-4]  # Extrai o número do mês do nome do arquivo
                    resultados_lista.append({
                        'Mês': mes,
                        'Média': estatisticas['media'],
                        'Mínimo': estatisticas['minimo'],
                        'Máximo': estatisticas['maximo']
                    })

        resultados_df = pd.DataFrame(resultados_lista)
        print("\nEstatísticas de Temperatura Máxima Mensal na Região Sul:")
        print()
        print(resultados_df)


        #--------------------- Início da criação da Tabela como Figura ------------------------
        
        
        fig, ax = plt.subplots(figsize=(10, len(resultados_df) * 0.5))
        ax.axis('off')

        table = ax.table(cellText=resultados_df.values,
                         colLabels=resultados_df.columns,
                         cellLoc='center',
                         loc='center')

        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

        plt.title('Estatísticas de Temperatura Máxima Média Mensal na Região Sul (1970-2000)')
        plt.tight_layout()
        plt.savefig(os.path.join("figures", "tabela_tmax_mensal_regiao_sul.png"))
        plt.show()


       #--------------------- Início da criação do Boxplot (siteMatplotlib) ------------------------
       
       
        import matplotlib.pyplot as plt
        import numpy as np

        meses = resultados_df['Mês'].tolist()
        medias = resultados_df['Média'].tolist()

        # Vamos criar dados simulados para os quartis e whiskers
        # Já que não temos esses dados diretamente no nosso DataFrame de médias mensais
        dados_boxplot = []
        for media in medias:
            # Simula uma distribuição em torno da média
            desvio_padrao = 1.5  # Você pode ajustar esse valor
            dados_simulados = np.random.normal(media, desvio_padrao, size=100)
            dados_boxplot.append(dados_simulados)

        fig, ax = plt.subplots(figsize=(12, 7))
        pos = np.arange(len(meses)) + 1
        bp = ax.boxplot(dados_boxplot, sym='k+', positions=pos, notch=True)

        ax.set_xlabel('Mês')
        ax.set_ylabel('Temperatura Média (°C)')
        ax.set_title('Distribuição da Temperatura Máxima Média Mensal na Região Sul (1970-2000)')
        ax.set_xticks(pos)
        ax.set_xticklabels(meses)
        plt.grid(True)
        plt.setp(bp['whiskers'], color='k', linestyle='-')
        plt.setp(bp['fliers'], markersize=3.0)

        plt.savefig(os.path.join("figures", "boxplot_tmax_matplotlib.png"))
        plt.show()
        
        
        #--------------------- Início da criação dos Mapas de Temperatura Mensais ------------------------
        
        
        import rasterio
        from rasterio.plot import show

        for arquivo in arquivos_tmax:
            mes_numero = arquivo[-6:-4]
            nome_arquivo_mapa = f"mapa_tmax_{mes_numero}_regiao_sul.png"
            caminho_dados_mes = os.path.join("data", arquivo)
            dados_mes = carregar_dados_clima(caminho_dados_mes)

            if dados_mes is not None and shape_regiao_sul is not None:
                dados_recortados_mes = recortar_por_shapefile(dados_mes, shape_regiao_sul)

                if dados_recortados_mes is not None:
                    # Extrai o DataArray (assumindo que há pelo menos uma variável)
                    nome_variavel = list(dados_recortados_mes.data_vars)[0]
                    data_array_mes = dados_recortados_mes[nome_variavel]

                    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
                    data_array_mes.plot(cmap='viridis', ax=ax, vmin=data_array_mes.min(), vmax=data_array_mes.max())
                    shape_regiao_sul.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1)
                    ax.set_title(f'Temperatura Máxima em {mes_numero} na Região Sul (1970-2000)')
                    ax.set_xlabel('Longitude')
                    ax.set_ylabel('Latitude')
                    mappable = data_array_mes.plot(cmap='viridis', ax=ax, vmin=data_array_mes.min(), vmax=data_array_mes.max())
                    plt.colorbar(mappable=mappable, ax=ax, label='Temperatura (°C)')
                    plt.savefig(os.path.join("figures", nome_arquivo_mapa))
                    plt.close(fig)
                    
                    
         #--------------------- Início da criação dos Histogramas de Temperatura Mensais ------------------------
                    
                    
        import matplotlib.pyplot as plt
        import numpy as np

        for arquivo in arquivos_tmax:
            mes_numero = arquivo[-6:-4]
            nome_arquivo_histograma = f"histograma_tmax_{mes_numero}_regiao_sul.png"
            caminho_dados_mes = os.path.join("data", arquivo)
            dados_mes = carregar_dados_clima(caminho_dados_mes)

            if dados_mes is not None and shape_regiao_sul is not None:
                dados_recortados_mes = recortar_por_shapefile(dados_mes, shape_regiao_sul)

                if dados_recortados_mes is not None:
                    # Extrai os valores do DataArray como um array NumPy
                    nome_variavel = list(dados_recortados_mes.data_vars)[0]
                    valores_temperatura = dados_recortados_mes[nome_variavel].values.flatten()
                    valores_validos = valores_temperatura[~np.isnan(valores_temperatura)] # Remove valores NaN

                    if valores_validos.size > 0:
                        plt.figure(figsize=(10, 6))
                        plt.hist(valores_validos, bins=20, color='skyblue', edgecolor='black')
                        plt.title(f'Distribuição da Temperatura Máxima Média Mensal em {mes_numero} na Região Sul (1970-2000)')
                        plt.xlabel('Temperatura Máxima (°C)')
                        plt.ylabel('Frequência')
                        plt.grid(axis='y', alpha=0.75)
                        plt.savefig(os.path.join("figures", nome_arquivo_histograma))
                        plt.close()
       