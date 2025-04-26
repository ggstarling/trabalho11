# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 17:36:59 2025

@author: Gustavo Starling
"""

import rasterio
import xarray as xr
import rioxarray
import geopandas as gpd
import numpy as np
import pandas as pd

def carregar_dados_clima(caminho_arquivo):
    """Carrega um arquivo .tif raster usando xarray."""
    try:
        ds = xr.open_dataset(caminho_arquivo, engine="rasterio")
        return ds
    except Exception as e:
        print(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return None

def carregar_shapefile(caminho_shapefile):
    """Carrega um arquivo shapefile usando geopandas."""
    try:
        gdf = gpd.read_file(caminho_shapefile)
        return gdf
    except Exception as e:
        print(f"Erro ao carregar o shapefile {caminho_shapefile}: {e}")
        return None

def recortar_por_shapefile(dados_raster, shapefile):
    """Recorta os dados raster para a extensão de um shapefile."""
    try:
        dados_recortados = dados_raster.rio.clip(shapefile.geometry, shapefile.crs)
        return dados_recortados
    except Exception as e:
        print(f"Erro ao recortar os dados: {e}")
        return None

def calcular_estatisticas(dados_recortados):
    """Calcula estatísticas básicas (média, min, max) de um DataArray xarray."""
    if dados_recortados is not None:
        # Tenta obter o nome da primeira variável de dados no Dataset
        nome_variavel = list(dados_recortados.data_vars)[0]
        data_array = dados_recortados[nome_variavel]

        media = data_array.mean().compute().item()
        minimo = data_array.min().compute().item()
        maximo = data_array.max().compute().item()
        return {"media": media, "minimo": minimo, "maximo": maximo}
    else:
        return None