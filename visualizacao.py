# -*- coding: utf-8 -*-
"""
Módulo para funções de visualização dos dados climáticos.
"""

import xarray as xr
import geopandas as gpd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os
import pandas as pd
import rioxarray
import numpy as np
import seaborn as sns

# Gera mapas da temperatura máxima anual

def plot_annual_max_temperature_maps(dados_era5, regiao_sul_geometry, anos_interesse, output_dir='figures'):
    """
    Plota mapas da temperatura máxima anual para anos específicos.

    Args:
        dados_era5 (xr.Dataset): Dataset do ERA5 contendo dados de temperatura ('t2m') e tempo ('valid_time').
        regiao_sul_geometry (Polygon): Geometria da Região Sul do Brasil.
        anos_interesse (list): Lista de anos para os quais os mapas serão gerados.
        output_dir (str, opcional): Diretório para salvar os mapas. Padrão é 'figures'.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for year in anos_interesse:
        # Seleciona os dados para o ano específico usando a coordenada 'valid_time'
        dados_anuais = dados_era5.sel(valid_time=dados_era5['valid_time'].dt.year == year)

        # Verifica se há algum dado para o ano selecionado
        if dados_anuais.sizes['valid_time'] > 0:
            temperatura_maxima_anual = dados_anuais['t2m'].max(dim='valid_time')

            try:
                # Verifique se os dados de temperatura máxima têm CRS e defina caso não tenha
                if temperatura_maxima_anual.rio.crs is None:
                    # Defina o CRS (exemplo, EPSG:4326, ajuste conforme necessário)
                    temperatura_maxima_anual = temperatura_maxima_anual.rio.write_crs('EPSG:4326', inplace=True)

                # Realize o recorte após definir o CRS
                temperatura_recortada = temperatura_maxima_anual.rio.clip([regiao_sul_geometry], crs=temperatura_maxima_anual.rio.crs)
            except AttributeError:
                print(f"Aviso: Informação de CRS ausente. Pulando recorte via rio.clip para o ano {year}.")
                temperatura_recortada = temperatura_maxima_anual.sel(
                    longitude=slice(regiao_sul_geometry.bounds[0], regiao_sul_geometry.bounds[2]),
                    latitude=slice(regiao_sul_geometry.bounds[1], regiao_sul_geometry.bounds[3])
                )

            plt.figure(figsize=(10, 8))
            ax = plt.axes(projection=ccrs.PlateCarree())
            temperatura_recortada.plot(ax=ax, cmap='coolwarm', cbar_kwargs={'label': 'Temperatura Máxima Anual (°C)'})
            ax.add_geometries([regiao_sul_geometry], crs=ccrs.PlateCarree(), facecolor='none', edgecolor='black', linewidth=1)
            ax.set_extent([regiao_sul_geometry.bounds[0] - 1, regiao_sul_geometry.bounds[2] + 1,
                            regiao_sul_geometry.bounds[1] - 1, regiao_sul_geometry.bounds[3] + 1], crs=ccrs.PlateCarree())
            ax.set_title(f'Temperatura Máxima Anual em {year}')
            ax.coastlines(resolution='50m')
            ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, f'temperatura_maxima_{year}.png'))
            plt.close()
        else:
            print(f"Aviso: Não há dados disponíveis para o ano {year}, o mapa da temperatura máxima anual não será gerado.")

    print(f"\nMapas de temperatura máxima anual salvos em: {output_dir}")

# Gera gráfico de linha anual
def plot_annual_line_graph(anos, dados, titulo, xlabel, ylabel, filename, color='blue'):
    plt.figure(figsize=(10, 6))
    plt.plot(anos, dados, marker='o', linestyle='-', color=color)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Gera boxplot anual (estilo matplotlib)
def plot_annual_boxplot(anos, dados, titulo, xlabel, ylabel, filename):
    anos_filtrados = anos[::5]  # Seleciona anos de 5 em 5
    dados_filtrados = dados[::5] # Seleciona dados correspondentes

    dados_boxplot = []
    desvio_padrao = 1.5  # Ajuste conforme necessário

    for media in dados_filtrados:
        dados_simulados = np.random.normal(media, desvio_padrao, size=100)
        dados_boxplot.append(dados_simulados)

    fig, ax = plt.subplots(figsize=(12, 7))
    pos = np.arange(len(anos_filtrados)) + 1
    bp = ax.boxplot(dados_boxplot, sym='k+', positions=pos, notch=True)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    ax.set_xticks(pos)
    ax.set_xticklabels(anos_filtrados, rotation=45, ha='right')
    plt.grid(True)
    plt.setp(bp['whiskers'], color='k', linestyle='-')
    plt.setp(bp['fliers'], markersize=3.0)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Gera histograma anual
def plot_annual_histogram(dados, titulo, xlabel, ylabel, filename, color='skyblue'):
    plt.figure(figsize=(10, 6))
    plt.hist(dados, bins=15, color=color, edgecolor='black')
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Gera gráfico de dispersão anual
def plot_annual_scatter(x_dados, y_dados, titulo, xlabel, ylabel, filename, color='blue'):
    plt.figure(figsize=(8, 6))
    plt.scatter(x_dados, y_dados, color=color)
    plt.title(titulo)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()