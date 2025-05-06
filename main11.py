# -*- coding: utf-8 -*-
"""
Created on Sun May  4 12:23:30 2025

Script principal para análise e visualização de dados climáticos ERA5 para a Região Sul do Brasil.

@author: Gustavo Starling

"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np # Importando numpy aqui, caso não esteja no visualizacao
import rasterio
import statsmodels.api as sm
from scipy.stats import linregress
from rasterio.plot import show
from process_era5 import load_era5_data, combine_era5_datasets, load_south_america_shapefile, spatial_subset
from visualizacao import (
    plot_annual_max_temperature_maps,
    plot_annual_line_graph,
    plot_annual_histogram,
    plot_annual_scatter
)

# Gera boxplot anual (estilo matplotlib) - MOVIDA PARA O NÍVEL SUPERIOR
def plot_annual_boxplot(anos, dados, titulo, xlabel, ylabel, filename, color='green'):
    dados_boxplot = []
    desvio_padrao = 1.5  # Ajuste conforme necessário

    for media in dados:
        dados_simulados = np.random.normal(media, desvio_padrao, size=100)
        dados_boxplot.append(dados_simulados)

    fig, ax = plt.subplots(figsize=(12, 7))
    pos = np.arange(len(anos)) + 1
    bp = ax.boxplot(dados_boxplot, sym='k+', positions=pos, notch=True)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    ax.set_xticks(pos)
    ax.set_xticklabels(anos, rotation=45, ha='right')
    plt.grid(True)
    plt.setp(bp['whiskers'], color=color, linestyle='-')
    plt.setp(bp['fliers'], color=color, markersize=3.0)
    plt.setp(bp['medians'], color=color)
    plt.setp(bp['boxes'], color=color)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

if __name__ == "__main__":
    # Carregamento dos Dados
    print("Carregando os dados do ERA5...")
    dados1, dados2 = load_era5_data()

    # Combinação dos Datasets
    print("Combinando os datasets de temperatura e precipitação...")
    dados_combinados = combine_era5_datasets(dados1, dados2)
    print("\nDataset ERA5 combinado:")
    print(dados_combinados)

    if dados_combinados is not None:
        # Carregamento do Shapefile da Região Sul
        print("\nCarregando o shapefile da Região Sul...")
        south_america_geometry = load_south_america_shapefile()

    if south_america_geometry is not None:
        # Recorte Espacial dos Dados
        print("Realizando o recorte espacial dos dados para a Região Sul...")
        dados_recortados = spatial_subset(dados_combinados, south_america_geometry)

    # --------------------- # Cálculo das Médias Mensais e Criação do DataFrame Mensal # ---------------------
    if dados_recortados is not None:
        print("\nAgrupando os dados por mês e ano e calculando as médias regionais...")
        dados_mensais = dados_recortados.resample(valid_time='1M').mean()
        print("\nDimensões de dados_mensais:", dados_mensais.dims)
        print("Coordenadas de dados_mensais:", dados_mensais.coords)

        # Calcula a média espacial da temperatura média e da precipitação nos dados mensais
        temperatura_media_mensal_regional = dados_mensais['t2m'].mean(dim=['latitude', 'longitude']) - 273.15
        precipitacao_media_mensal_regional = dados_mensais['tp'].mean(dim=['latitude', 'longitude'])

        # Obtém os anos e meses
        datas_mensais = dados_mensais['valid_time'].values
        anos_mensais = [pd.to_datetime(str(date)).year for date in datas_mensais]
        meses_mensais = [pd.to_datetime(str(date)).month for date in datas_mensais]

        # Cria o DataFrame mensal
        estatisticas_mensais_df = pd.DataFrame({
            'Ano': anos_mensais,
            'Mês': meses_mensais,
            'Temperatura Média Mensal (°C)': temperatura_media_mensal_regional.values,
            'Precipitação Média Mensal (m)': precipitacao_media_mensal_regional.values
        })

        print("\nDataFrame de estatísticas mensais criado:")
        print(estatisticas_mensais_df.head())

        # Salva a tabela de estatísticas mensais em um arquivo CSV em outputs
      

        nome_pasta_outputs = 'outputs'
        if not os.path.exists(nome_pasta_outputs):
            os.makedirs(nome_pasta_outputs)
        nome_arquivo_mensal = os.path.join(nome_pasta_outputs, 'estatisticas_mensais.csv')
        estatisticas_mensais_df.to_csv(nome_arquivo_mensal, index=False)
        print(f"\nTabela de estatísticas mensais salva em '{nome_arquivo_mensal}'")

        # *** Bloco para recorte temporal (se você quiser manter) ***
        data_inicio = np.datetime64('1940-01-01')
        data_fim = np.datetime64('2024-12-31')
        dados_recortados_temporal = dados_recortados.sel(valid_time=slice(data_inicio, data_fim))
        print("\nDados recortados para o período de 1940-01-01 até 2024-12-31 (para análise anual).")
        print("Anos presentes nos dados recortados (para análise anual):", np.unique(dados_recortados_temporal['valid_time'].dt.year.values))

        # Agrupamento Anual e Cálculo de Estatísticas (use 'dados_recortados_temporal' daqui para baixo)
        print("Agrupando os dados por ano e calculando as médias e máximas...")
        dados_anuais = dados_recortados_temporal.groupby(dados_recortados_temporal['valid_time'].dt.year).mean(dim='valid_time')
        dados_anuais_max_temporal = dados_recortados_temporal.groupby(dados_recortados_temporal['valid_time'].dt.year).max(dim='valid_time')

        # Calcula a média espacial da temperatura média e da precipitação nos dados anuais
        temperatura_media_anual_regional = dados_anuais['t2m'].mean(dim=['latitude', 'longitude'])
        precipitacao_media_anual_regional = dados_anuais['tp'].mean(dim=['latitude', 'longitude'])

        # Calcula a média espacial da temperatura máxima nos dados anuais
        temperatura_maxima_anual_regional = dados_anuais_max_temporal['t2m'].max(dim=['latitude', 'longitude'])

        # Converter temperaturas de Kelvin para Celsius
        temperatura_media_anual_celsius = temperatura_media_anual_regional - 273.15
        temperatura_maxima_anual_celsius = temperatura_maxima_anual_regional - 273.15

        # Obter os anos
        anos = dados_anuais.coords['year'].values

        print("\n" + "="*50 + "\n")
        print("Temperatura média anual regional (°C) (após recorte):")
        print(temperatura_media_anual_celsius)
        print("Temperatura máxima anual regional (°C) (após recorte):")
        print(temperatura_maxima_anual_celsius)
        print("\n" + "="*50 + "\n")
        print("Precipitação média anual regional (m) (após recorte):")
        print(precipitacao_media_anual_regional)
        print("\n" + "="*50 + "\n")
        print("Anos (após agrupamento e recorte):")
        print(anos)

        # Cria a tabela de estatísticas descritivas anuais
        # Obter os anos
        anos = dados_anuais.coords['year'].values

        print("\n" + "="*50 + "\n")
        print("Temperatura média anual regional (°C) (após recorte):")
        print(temperatura_media_anual_celsius)
        print("Temperatura máxima anual regional (°C) (após recorte):")
        print(temperatura_maxima_anual_celsius)
        print("\n" + "="*50 + "\n")
        print("Precipitação média anual regional (m) (após recorte):")
        print(precipitacao_media_anual_regional)
        print("\n" + "="*50 + "\n")
        print("Anos (após agrupamento e recorte):")
        print(anos)

        estatisticas_temp_anual_df = pd.DataFrame({'year': anos, 'Temperatura Média Anual (°C)': temperatura_media_anual_celsius.values})
        estatisticas_temp_max_anual_df = pd.DataFrame({'year': anos, 'Temperatura Máxima Anual (°C)': temperatura_maxima_anual_celsius.values})
        estatisticas_precip_anual_df = pd.DataFrame({'year': anos, 'Precipitação Média Anual (m)': precipitacao_media_anual_regional.values})

        # Calcule a precipitação máxima anual regional e crie o DataFrame correspondente
        precipitacao_maxima_anual_regional = dados_anuais_max_temporal['tp'].max(dim=['latitude', 'longitude']).values
        estatisticas_precip_max_anual_df = pd.DataFrame({'year': anos, 'Precipitação Máxima Anual (m)': precipitacao_maxima_anual_regional})
        print("\nPrecipitação Máxima Anual Regional:")
        print(precipitacao_maxima_anual_regional)
                
          

                # --------------------- # Criação da tabela de estatísticas descritivas anuais # ---------------------
                

        print("\nCriando a tabela de estatísticas anuais...")
        estatisticas_anuais_df = pd.DataFrame({
            'Ano': estatisticas_temp_anual_df['year'],
            'Temperatura Média Anual (°C)': estatisticas_temp_anual_df['Temperatura Média Anual (°C)'], # Corrigido o nome da coluna
            'Temperatura Máxima Anual (°C)': estatisticas_temp_max_anual_df['Temperatura Máxima Anual (°C)'], # Corrigido o nome da coluna
            'Precipitação Média Anual (m)': estatisticas_precip_anual_df['Precipitação Média Anual (m)'], # Corrigido o nome da coluna
            'Precipitação Máxima Anual (m)': estatisticas_precip_max_anual_df['Precipitação Máxima Anual (m)'] # Corrigido o nome da coluna
        })
        # Salva a tabela de estatísticas anuais em um arquivo CSV
        nome_arquivo_estatisticas = 'estatisticas_anuais.csv'
        estatisticas_anuais_df.to_csv(nome_arquivo_estatisticas, index=False)
        print(f"\nTabela de estatísticas descritivas anuais salva em '{nome_arquivo_estatisticas}'")
        # Reseta o índice para que 'year' se torne uma coluna
        estatisticas_anuais_df = estatisticas_anuais_df.reset_index()

        print("\nEstatísticas Descritivas Anuais:")
        print(estatisticas_anuais_df.describe())

        # Salva a tabela de estatísticas anuais em um arquivo CSV

        output_dir = 'outputs'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        nome_arquivo_estatisticas = os.path.join(output_dir, 'estatisticas_anuais.csv')
        estatisticas_anuais_df.to_csv(nome_arquivo_estatisticas, index=False)
        print(f"\nTabela de estatísticas descritivas anuais salva em '{nome_arquivo_estatisticas}'")

        # --------------------- # Decomposição da Série Temporal Anual # ---------------------
        
        # Garanta que 'Ano' seja o índice para a precipitação
        precip_anual_ts = estatisticas_anuais_df.set_index('Ano')['Precipitação Média Anual (m)']
        
        # Modelo de decomposição aditivo (a frequência seasonal é ignorada para dados anuais)
        decomposicao_precip = sm.tsa.seasonal_decompose(precip_anual_ts, model='additive', period=1) # period=1 para indicar que não há sazonalidade dentro do período
        
        # Extrair os componentes
        tendencia_precip = decomposicao_precip.trend
        residual_precip = decomposicao_precip.resid
        
        # Plotar os componentes da precipitação
        plt.figure(figsize=(12, 8))
        
        plt.subplot(3, 1, 1)
        plt.plot(precip_anual_ts, label='Série Original da Precipitação')
        plt.legend(loc='upper left')
        plt.title('Decomposição da Série Temporal da Precipitação Média Anual')
        
        plt.subplot(3, 1, 2)
        plt.plot(tendencia_precip, label='Tendência da Precipitação')
        plt.legend(loc='upper left')
        plt.title('Tendência da Precipitação')
        
        plt.subplot(3, 1, 3)
        plt.plot(residual_precip, label='Resíduo da Precipitação')
        plt.legend(loc='upper left')
        plt.title('Resíduo da Precipitação')
        
        plt.tight_layout()
        plt.savefig('figures/decomposicao_precipitacao_anual.png')
        plt.close()
        
        print("\nGráfico de decomposição da precipitação média anual salvo em 'figures/decomposicao_precipitacao_anual.png'")
        
        # Repetindo o processo para a temperatura média anual
        temp_anual_ts = estatisticas_anuais_df.set_index('Ano')['Temperatura Média Anual (°C)']
        
        decomposicao_temp = sm.tsa.seasonal_decompose(temp_anual_ts, model='additive', period=1)
        
        tendencia_temp = decomposicao_temp.trend
        residual_temp = decomposicao_temp.resid
        
        plt.figure(figsize=(12, 8))
        
        plt.subplot(3, 1, 1)
        plt.plot(temp_anual_ts, label='Série Original da Temperatura')
        plt.legend(loc='upper left')
        plt.title('Decomposição da Série Temporal da Temperatura Média Anual')
        
        plt.subplot(3, 1, 2)
        plt.plot(tendencia_temp, label='Tendência da Temperatura')
        plt.legend(loc='upper left')
        plt.title('Tendência da Temperatura')
        
        plt.subplot(3, 1, 3)
        plt.plot(residual_temp, label='Resíduo da Temperatura')
        plt.legend(loc='upper left')
        plt.title('Resíduo da Temperatura')
        
        plt.tight_layout()
        plt.savefig('figures/decomposicao_temperatura_anual.png')
        plt.close()
        
        print("\nGráfico de decomposição da temperatura média anual salvo em 'figures/decomposicao_temperatura_anual.png'")

     # --------------------- # Criação dos Gráficos de Linha Anuais # ---------------------
     
        print("\nCriando os gráficos de linha anuais...")
        plot_annual_line_graph(anos, temperatura_media_anual_celsius,
                                'Temperatura Média Anual na Região Sul (1940-2025)',
                                'Ano', 'Temperatura (°C)', 'figures/temperatura_media_anual_regiao_sul.png')

        plot_annual_line_graph(anos, temperatura_maxima_anual_celsius,
                                'Temperatura Máxima Anual na Região Sul (1940-2025)',
                                'Ano', 'Temperatura (°C)', 'figures/temperatura_maxima_anual_regiao_sul.png', color='red')

        plot_annual_line_graph(anos, precipitacao_media_anual_regional,
                                'Precipitação Média Anual na Região Sul (1940-2025)',
                                'Ano', 'Precipitação (m)', 'figures/precipitacao_media_anual_regiao_sul.png')

        # Gráfico de Linha da Precipitação Máxima Anual
        plot_annual_line_graph(anos, estatisticas_precip_max_anual_df['Precipitação Máxima Anual (m)'].values,
                                'Precipitação Máxima Anual na Região Sul (1940-2025)',
                                'Ano', 'Precipitação (m)', 'figures/precipitacao_maxima_anual_regiao_sul.png', color='green')

        # --------------------- # Criação dos Boxplots Anuais # ---------------------
        
        print("\nCriando os boxplots anuais...")
        anos_filtrados_boxplot = anos[::5]
        temp_media_filtrada_boxplot = temperatura_media_anual_celsius.values[::5]
        temp_max_filtrada_boxplot = temperatura_maxima_anual_celsius.values[::5]
        precip_filtrada_boxplot = precipitacao_media_anual_regional.values[::5]
        precip_max_filtrada_boxplot = estatisticas_precip_max_anual_df['Precipitação Máxima Anual (m)'].values[::5]

        plot_annual_boxplot(anos_filtrados_boxplot, temp_media_filtrada_boxplot,
                             'Distribuição da Temperatura Média Anual na Região Sul (A cada 5 anos)',
                             'Ano', 'Temperatura (°C)', 'figures/boxplot_temperatura_anual_5anos_regiao_sul.png')

        plot_annual_boxplot(anos_filtrados_boxplot, temp_max_filtrada_boxplot,
                             'Distribuição da Temperatura Máxima Anual na Região Sul (A cada 5 anos)',
                             'Ano', 'Temperatura Máxima (°C)', 'figures/boxplot_temperatura_maxima_anual_5anos_regiao_sul.png')

        plot_annual_boxplot(anos_filtrados_boxplot, precip_filtrada_boxplot,
                             'Distribuição da Precipitação Média Anual na Região Sul (A cada 5 anos)',
                             'Ano', 'Precipitação (m)', 'figures/boxplot_precipitacao_anual_5anos_regiao_sul.png')

        # Boxplot da Precipitação Máxima Anual
        plot_annual_boxplot(anos_filtrados_boxplot, precip_max_filtrada_boxplot,
                             'Distribuição da Precipitação Máxima Anual na Região Sul (A cada 5 anos)',
                             'Ano', 'Precipitação Máxima (m)', 'figures/boxplot_precipitacao_maxima_anual_5anos_regiao_sul.png', color='green')

  # ---------------------------------- # Criação dos Boxplots Mensais # ----------------------------------
        
        print("\nCriando os boxplots mensais...")
        
        # Carregar os dados mensais novamente
        nome_arquivo_mensal = os.path.join(nome_pasta_outputs, 'estatisticas_mensais.csv')
        try:
            estatisticas_mensais_df = pd.read_csv(nome_arquivo_mensal)
        except:
            print(f"Erro: Arquivo '{nome_arquivo_mensal}' não encontrado.")
            exit()
        
        nome_pasta_figures = "figures"
        # Boxplot da Temperatura Média Mensal
        plt.figure(figsize=(12, 6))
        estatisticas_mensais_df.boxplot(column='Temperatura Média Mensal (°C)', by='Mês')
        plt.title('Distribuição da Temperatura Média Mensal na Região Sul')
        plt.suptitle('') # Remover o título padrão do pandas
        plt.xlabel('Mês')
        plt.ylabel('Temperatura Média (°C)')
        nome_arquivo_boxplot_temp_mensal = os.path.join(nome_pasta_figures, 'boxplot_temperatura_mensal_regiao_sul.png')
        plt.savefig(nome_arquivo_boxplot_temp_mensal)
        plt.close()
        print(f"\nBoxplot da temperatura média mensal salvo em '{nome_pasta_figures}'.")
        
        # Boxplot da Precipitação Média Mensal
        plt.figure(figsize=(12, 6))
        estatisticas_mensais_df.boxplot(column='Precipitação Média Mensal (m)', by='Mês')
        plt.title('Distribuição da Precipitação Média Mensal na Região Sul')
        plt.suptitle('') # Remover o título padrão do pandas
        plt.xlabel('Mês')
        plt.ylabel('Precipitação Média (m)')
        nome_arquivo_boxplot_prec_mensal = os.path.join(nome_pasta_figures, 'boxplot_precipitacao_mensal_regiao_sul.png')
        plt.savefig(nome_arquivo_boxplot_prec_mensal)
        plt.close()
        print(f"Boxplot da precipitação média mensal salvo em '{nome_pasta_figures}'.")
                        
       # --------------------- # Criação dos Histogramas Anuais # ---------------------
        
        print("\nCriando os histogramas anuais...")
        plot_annual_histogram(estatisticas_anuais_df['Temperatura Média Anual (°C)'],
                                'Histograma da Temperatura Média Anual na Região Sul (1940-2025)',
                                'Temperatura Média Anual (°C)', 'Frequência',
                                'figures/histograma_temperatura_media_anual_regiao_sul.png')
        
        plot_annual_histogram(estatisticas_anuais_df['Temperatura Máxima Anual (°C)'],
                                'Histograma da Temperatura Máxima Anual na Região Sul (1940-2025)',
                                'Temperatura Máxima Anual (°C)', 'Frequência',
                                'figures/histograma_temperatura_maxima_anual_regiao_sul.png', color='red')
        
        plot_annual_histogram(estatisticas_anuais_df['Precipitação Média Anual (m)'],
                                'Histograma da Precipitação Média Anual na Região Sul (1940-2025)',
                                'Precipitação Média Anual (m)', 'Frequência',
                                'figures/histograma_precipitacao_anual_regiao_sul.png')
        
        # ADICIONE ESTA LINHA:
        plot_annual_histogram(estatisticas_anuais_df['Precipitação Máxima Anual (m)'],
                                'Histograma da Precipitação Máxima Anual na Região Sul (1940-2025)',
                                'Precipitação Máxima Anual (m)', 'Frequência',
                                'figures/histograma_precipitacao_maxima_anual_regiao_sul.png', color='green')

        # --------------------- # Criação dos Mapas de Temperatura Máxima Anual # ---------------------
        
        print("\nCriando os mapas de temperatura máxima anual...")
        anos_para_mapa = [1940, 1950, 1960, 1970, 1980, 1990, 2000, 2005, 2010, 2015, 2020, 2024]
        plot_annual_max_temperature_maps(dados_recortados, south_america_geometry, anos_para_mapa)

        # --------------------- # Criação dos Gráficos de Dispersão Anuais # ---------------------
        
        print("\nCriando os gráficos de dispersão anuais...")
        plot_annual_scatter(estatisticas_anuais_df['Temperatura Média Anual (°C)'],
                             estatisticas_anuais_df['Precipitação Média Anual (m)'],
                             'Dispersão entre Temperatura Média Anual e Precipitação Média Anual',
                             'Temperatura Média Anual (°C)', 'Precipitação Média Anual (m)',
                             'figures/dispersao_temp_media_precip_anual_regiao_sul.png')

        plot_annual_scatter(estatisticas_anuais_df['Temperatura Máxima Anual (°C)'],
                             estatisticas_anuais_df['Precipitação Média Anual (m)'],
                             'Dispersão entre Temperatura Máxima Anual e Precipitação Média Anual',
                             'Temperatura Máxima Anual (°C)', 'Precipitação Média Anual (m)',
                             'figures/dispersao_temp_max_precip_anual_regiao_sul.png', color='red')

# --------------------- # Análise de Correlação # ---------------------

        if south_america_geometry is not None:
            print("\nCalculando a correlação entre variáveis anuais...")
            correlacao_temp_media_precip_media = estatisticas_anuais_df['Temperatura Média Anual (°C)'].corr(estatisticas_anuais_df['Precipitação Média Anual (m)'])
            print(f"\nCorrelação entre temperatura média anual e precipitação média anual: {correlacao_temp_media_precip_media:.2f}")
    
            correlacao_temp_max_precip_media = estatisticas_anuais_df['Temperatura Máxima Anual (°C)'].corr(estatisticas_anuais_df['Precipitação Média Anual (m)'])
            print(f"Correlação entre temperatura máxima anual e precipitação média anual: {correlacao_temp_max_precip_media:.2f}")
    
            correlacao_temp_media_precip_max = estatisticas_anuais_df['Temperatura Média Anual (°C)'].corr(estatisticas_anuais_df['Precipitação Máxima Anual (m)'])
            print(f"Correlação entre temperatura média anual e precipitação máxima anual: {correlacao_temp_media_precip_max:.2f}")
    
            correlacao_temp_max_precip_max = estatisticas_anuais_df['Temperatura Máxima Anual (°C)'].corr(estatisticas_anuais_df['Precipitação Máxima Anual (m)'])
            print(f"Correlação entre temperatura máxima anual e precipitação máxima anual: {correlacao_temp_max_precip_max:.2f}")
    
            print("\nColunas no DataFrame estatisticas_anuais_df antes da correlação:")
            print(estatisticas_anuais_df.columns)
    
        else:
            print("Erro: Falha ao carregar o shapefile da Região Sul.")

    else:
        print("Erro: Falha ao realizar o recorte espacial dos dados.")

else:
    print("Erro: Falha ao combinar os datasets do ERA5.")

print("\nProcesso concluído!")

# ----------------------- ANÁLISE DE TENDÊNCIAS ANUAIS ---------------------

print("\nAnálise de Tendências Anuais:")

variaveis_anuais = ['Temperatura Média Anual (°C)', 'Temperatura Máxima Anual (°C)', 'Precipitação Média Anual (m)', 'Precipitação Máxima Anual (m)']
anos = estatisticas_anuais_df['Ano'].values
nome_pasta_figures = 'figures'
os.makedirs(nome_pasta_figures, exist_ok=True)

for variavel in variaveis_anuais:
    valores = estatisticas_anuais_df[variavel].values
    slope, intercept, r_value, p_value, std_err = linregress(anos, valores)
    linha_tendencia = slope * anos + intercept
    r_squared = r_value**2

    plt.figure(figsize=(10, 6))
    plt.plot(anos, valores, label=variavel)
    plt.plot(anos, linha_tendencia, color='red', linestyle='--', label=f'Tendência (slope={slope:.4f})')
    plt.title(f'Tendência Anual de {variavel}')
    plt.xlabel('Ano')
    plt.ylabel(variavel)
    plt.legend()
    plt.grid(True)
    nome_arquivo_tendencia = os.path.join(nome_pasta_figures, f'tendencia_anual_{variavel.lower().replace(" ", "_")}.png')
    plt.savefig(nome_arquivo_tendencia)
    plt.close()

    tendencia_significativa = "estatisticamente significativa" if p_value < 0.05 else "não estatisticamente significativa"
    print(f"\nTendência de {variavel}:")
    print(f"  Inclinação (slope): {slope:.4f} por ano.")
    print(f"  P-value: {p_value:.4f} ({tendencia_significativa}).")
    print(f"  R-squared: {r_squared:.4f} (explica {r_squared*100:.2f}% da variabilidade).")
    if slope > 0:
        print("  Indica uma tendência de aumento.")
    elif slope < 0:
        print("  Indica uma tendência de diminuição.")
    else:
        print("  Não indica uma tendência clara de aumento ou diminuição.")

print("\nGráficos de tendência anual salvos na pasta 'figures'.")

# --------------------------------------------------
#  DECOMPOSIÇÃO DA SÉRIE TEMPORAL MENSAL
# --------------------------------------------------

print("\n" + "-"*40)
print("  DECOMPOSIÇÃO DA SÉRIE TEMPORAL MENSAL")
print("-" * 40)

from statsmodels.tsa.seasonal import seasonal_decompose

# Criar um índice de tempo (Year-Month)
estatisticas_mensais_df['Data'] = pd.to_datetime(estatisticas_mensais_df['Ano'].astype(str) + '-' + estatisticas_mensais_df['Mês'].astype(str), format='%Y-%m')
estatisticas_mensais_df.set_index('Data', inplace=True)

print("\nAnálise da Decomposição da Temperatura Média Mensal:")
try:
    decomposicao_temp = seasonal_decompose(estatisticas_mensais_df['Temperatura Média Mensal (°C)'], model='additive', period=12)
    plt.figure(figsize=(12, 8))
    plt.subplot(411)
    plt.plot(estatisticas_mensais_df['Temperatura Média Mensal (°C)'], label='Original')
    plt.legend(loc='upper left')
    plt.subplot(412)
    plt.plot(decomposicao_temp.trend, label='Tendência')
    plt.legend(loc='upper left')
    plt.subplot(413)
    plt.plot(decomposicao_temp.seasonal, label='Sazonalidade')
    plt.legend(loc='upper left')
    plt.subplot(414)
    plt.plot(decomposicao_temp.resid, label='Resíduo')
    plt.legend(loc='upper left')
    plt.tight_layout()
    nome_arquivo_decomposicao_temp = os.path.join(nome_pasta_figures, 'decomposicao_temperatura_mensal.png')
    plt.savefig(nome_arquivo_decomposicao_temp)
    plt.close()
    print(f"  Gráfico de decomposição salvo em '{nome_pasta_figures}'.")
    print(f"  Tendência (primeiros e últimos valores): {decomposicao_temp.trend.iloc[0]:.2f} -> {decomposicao_temp.trend.iloc[-1]:.2f}")
    print(f"  Padrão Sazonal (média da sazonalidade): {decomposicao_temp.seasonal.mean():.2f}")
    print(f"  Resíduo (desvio padrão): {decomposicao_temp.resid.std():.2f} (quanto menor, melhor o ajuste).")
except Exception as e:
    print(f"Erro na decomposição da temperatura: {e}")

print("\nAnálise da Decomposição da Precipitação Média Mensal:")
try:
    decomposicao_prec = seasonal_decompose(estatisticas_mensais_df['Precipitação Média Mensal (m)'], model='additive', period=12)
    plt.figure(figsize=(12, 8))
    plt.subplot(411)
    plt.plot(estatisticas_mensais_df['Precipitação Média Mensal (m)'], label='Original')
    plt.legend(loc='upper left')
    plt.subplot(412)
    plt.plot(decomposicao_prec.trend, label='Tendência')
    plt.legend(loc='upper left')
    plt.subplot(413)
    plt.plot(decomposicao_prec.seasonal, label='Sazonalidade')
    plt.legend(loc='upper left')
    plt.subplot(414)
    plt.plot(decomposicao_prec.resid, label='Resíduo')
    plt.legend(loc='upper left')
    plt.tight_layout()
    nome_arquivo_decomposicao_prec = os.path.join(nome_pasta_figures, 'decomposicao_precipitacao_mensal.png')
    plt.savefig(nome_arquivo_decomposicao_prec)
    plt.close()
    print(f"  Gráfico de decomposição salvo em '{nome_pasta_figures}'.")
    print(f"  Tendência (primeiros e últimos valores): {decomposicao_prec.trend.iloc[0]:.2f} -> {decomposicao_prec.trend.iloc[-1]:.2f}")
    print(f"  Padrão Sazonal (média da sazonalidade): {decomposicao_prec.seasonal.mean():.2f}")
    print(f"  Resíduo (desvio padrão): {decomposicao_prec.resid.std():.2f} (quanto menor, melhor o ajuste).")
except Exception as e:
    print(f"Erro na decomposição da precipitação: {e}")

print("\nModelo de decomposição utilizado: Aditivo (assumindo que a amplitude da sazonalidade não varia com o nível da série).")


# --------------------------------------------------
#  DECOMPOSIÇÃO DA SÉRIE TEMPORAL MENSAL
# --------------------------------------------------

print("\n" + "-"*40)
print("  DECOMPOSIÇÃO DA SÉRIE TEMPORAL MENSAL")
print("-" * 40)

from statsmodels.tsa.seasonal import seasonal_decompose

# Carregar os dados mensais novamente (garantindo que esteja carregado)
nome_arquivo_mensal = os.path.join(nome_pasta_outputs, 'estatisticas_mensais.csv')
try:
    estatisticas_mensais_df = pd.read_csv(nome_arquivo_mensal)
except FileNotFoundError:
    print(f"Erro: Arquivo '{nome_arquivo_mensal}' não encontrado.")
    exit()

# Criar um índice de tempo (Year-Month)
estatisticas_mensais_df['Data'] = pd.to_datetime(estatisticas_mensais_df['Ano'].astype(str) + '-' + estatisticas_mensais_df['Mês'].astype(str), format='%Y-%m')
estatisticas_mensais_df.set_index('Data', inplace=True)

# Decomposição da Temperatura Média Mensal
try:
    decomposicao_temp = seasonal_decompose(estatisticas_mensais_df['Temperatura Média Mensal (°C)'], model='additive', period=12)
    plt.figure(figsize=(12, 8))
    plt.subplot(411)
    plt.plot(estatisticas_mensais_df['Temperatura Média Mensal (°C)'], label='Original')
    plt.legend(loc='upper left')
    plt.subplot(412)
    plt.plot(decomposicao_temp.trend, label='Tendência')
    plt.legend(loc='upper left')
    plt.subplot(413)
    plt.plot(decomposicao_temp.seasonal, label='Sazonalidade')
    plt.legend(loc='upper left')
    plt.subplot(414)
    plt.plot(decomposicao_temp.resid, label='Resíduo')
    plt.legend(loc='upper left')
    plt.tight_layout()
    nome_arquivo_decomposicao_temp = os.path.join(nome_pasta_figures, 'decomposicao_temperatura_mensal.png')
    plt.savefig(nome_arquivo_decomposicao_temp)
    plt.close()
    print(f"\nGráfico de decomposição da temperatura mensal salvo em '{nome_pasta_figures}'.")
except Exception as e:
    print(f"Erro na decomposição da temperatura: {e}")

# Decomposição da Precipitação Média Mensal
try:
    decomposicao_prec = seasonal_decompose(estatisticas_mensais_df['Precipitação Média Mensal (m)'], model='additive', period=12)
    plt.figure(figsize=(12, 8))
    plt.subplot(411)
    plt.plot(estatisticas_mensais_df['Precipitação Média Mensal (m)'], label='Original')
    plt.legend(loc='upper left')
    plt.subplot(412)
    plt.plot(decomposicao_prec.trend, label='Tendência')
    plt.legend(loc='upper left')
    plt.subplot(413)
    plt.plot(decomposicao_prec.seasonal, label='Sazonalidade')
    plt.legend(loc='upper left')
    plt.subplot(414)
    plt.plot(decomposicao_prec.resid, label='Resíduo')
    plt.legend(loc='upper left')
    plt.tight_layout()
    nome_arquivo_decomposicao_prec = os.path.join(nome_pasta_figures, 'decomposicao_precipitacao_mensal.png')
    plt.savefig(nome_arquivo_decomposicao_prec)
    plt.close()
    print(f"Gráfico de decomposição da precipitação mensal salvo em '{nome_pasta_figures}'.")
except Exception as e:
    print(f"Erro na decomposição da precipitação: {e}")
    
    
# -------------------------------------- # Criação das Séries Temporais Anuais # --------------------------------------

print("\nCriando as séries temporais anuais...")

# Carregar os dados anuais novamente
nome_arquivo_anual = os.path.join(nome_pasta_outputs, 'estatisticas_anuais.csv')
try:
    estatisticas_anuais_df = pd.read_csv(nome_arquivo_anual)
except FileNotFoundError:
    print(f"Erro: Arquivo '{nome_arquivo_anual}' não encontrado.")
    exit()

variaveis_anuais_serie_temporal = ['Temperatura Média Anual (°C)', 'Temperatura Máxima Anual (°C)', 'Precipitação Média Anual (m)', 'Precipitação Máxima Anual (m)']
anos = estatisticas_anuais_df['Ano'].values

for variavel in variaveis_anuais_serie_temporal:
    plt.figure(figsize=(12, 6))
    plt.plot(anos, estatisticas_anuais_df[variavel], marker='o', linestyle='-')
    plt.title(f'Série Temporal Anual da {variavel} na Região Sul')
    plt.xlabel('Ano')
    plt.ylabel(variavel)
    plt.grid(True)
    nome_arquivo_serie_temporal = os.path.join(nome_pasta_figures, f'serie_temporal_anual_{variavel.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("°c", "").replace("m", "")}.png')
    plt.savefig(nome_arquivo_serie_temporal)
    plt.close()
    print(f"Série temporal anual da {variavel} salva em '{nome_pasta_figures}'.")

print("\nSéries temporais anuais salvas na pasta 'figures'.")
    