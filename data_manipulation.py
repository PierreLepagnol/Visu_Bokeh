#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Pierre LEPAGNOL
"""
# Module d'importation des données

   
import pandas as pd
from pyproj import Transformer
import numpy as np

def ImportData(path):
    data=pd.read_json(path)['fields']
    data=pd.DataFrame(list(data))
    return data 

def LongLat_to_EN(long, lat):
    transformer = Transformer.from_crs(4326, 3857,always_xy=True)
    try:
        return transformer.transform(long, lat)
    except:
        return None, None

def wgs84_to_web_mercator(df, lon="x", lat="y"):
    """Converts decimal longitude/latitude to Web Mercator format"""
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df
