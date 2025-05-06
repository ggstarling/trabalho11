# -*- coding: utf-8 -*-
"""
Created on Sun May  4 12:23:30 2025

Módulo para processamento dos dados climáticos ERA5.

@author: Gustavo Starling

"""

import xarray as xr
import os
import geopandas as gpd
from shapely.geometry import box

# Carrega os datasets de temperatura e precipitação do ERA5
def load_era5_data(data_dir='data'):
    temp_file = os.path.join(data_dir, 'data_0.nc')
    precip_file = os.path.join(data_dir, 'data_1.nc')

    if os.path.exists(temp_file):
        dados_temp = xr.open_dataset(temp_file)
        print(f"Dataset ERA5 carregado com sucesso: {os.path.basename(temp_file)}")
    else:
        print(f"Erro: Arquivo não encontrado: {temp_file}")
        dados_temp = None

    if os.path.exists(precip_file):
        dados_precip = xr.open_dataset(precip_file)
        print(f"Dataset ERA5 carregado com sucesso: {os.path.basename(precip_file)}")
    else:
        print(f"Erro: Arquivo não encontrado: {precip_file}")
        dados_precip = None

    return dados_temp, dados_precip

# Combina os datasets de temperatura e precipitação
def combine_era5_datasets(dados_temp, dados_precip):
    if dados_temp is None or dados_precip is None:
        print("Erro: Um ou ambos os datasets estão vazios, não é possível combinar.")
        return None

    dados_combinados = xr.merge([dados_temp[['t2m']], dados_precip[['tp']]])
    print("\nDataset ERA5 combinado com sucesso.")
    return dados_combinados

# Carrega a geometria da Região Sul a partir de um shapefile
def load_south_america_shapefile(shapefile_path='data/regiao_sul.shp'):
    try:
        regiao_sul = gpd.read_file(shapefile_path)
        south_america_geometry = regiao_sul.unary_union
        return south_america_geometry
    except FileNotFoundError:
        print(f"Erro: Arquivo de shapefile não encontrado em: {shapefile_path}")
        return None
    except Exception as e:
        print(f"Erro ao carregar o shapefile: {e}")
        return None

# Realiza o recorte espacial dos dados do ERA5 para a área da Região Sul
def spatial_subset(dados_era5, south_america_geometry):
    if dados_era5 is None or south_america_geometry is None:
        print("Erro: Dataset ERA5 ou geometria da Região Sul estão vazios.")
        return None

    try:
        minx, miny, maxx, maxy = south_america_geometry.bounds
        dados_recortados = dados_era5.sel(
            longitude=slice(minx - 0.5, maxx + 0.5),
            latitude=slice(maxy + 0.5, miny - 0.5) # Invertido devido à ordem da latitude
        )
        print("Dados recortados espacialmente para a Região Sul.")
        return dados_recortados
    except Exception as e:
        print(f"Erro ao realizar o recorte espacial: {e}")
        return None

if __name__ == "__main__":
    # Carregamento dos Dados
    dados_temp, dados_precip = load_era5_data()

    # Combinação dos Datasets
    dados_combinados = combine_era5_datasets(dados_temp, dados_precip)

    if dados_combinados:
        # Carregamento do Shapefile da Região Sul
        south_america_geometry = load_south_america_shapefile()

        if south_america_geometry:
            # Recorte Espacial dos Dados
            dados_recortados = spatial_subset(dados_combinados, south_america_geometry)

            if dados_recortados:
                # Calcula médias regionais (apenas para demonstração no __main__)
                temperatura_media_regional = dados_recortados['t2m'].mean(dim=['latitude', 'longitude'])
                precipitacao_media_regional = dados_recortados['tp'].mean(dim=['latitude', 'longitude'])
                print("\nMédias regionais calculadas com sucesso (após recorte).\n")
                print("Temperatura média regional (K):\n", temperatura_media_regional)
                print("\nPrecipitação média regional (m):\n", precipitacao_media_regional)

                # Importação das funções de visualização AQUI
                from visualizacao import (
                    plot_annual_max_temperature_maps,
                    plot_annual_line_graph,
                    plot_annual_boxplot,
                    plot_annual_histogram,
                    plot_annual_scatter
                )