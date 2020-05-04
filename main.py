''' Application Bokeh M1 MAS.

Application de Visualisation de données:
    Pierre LEPAGNOL
    21910091

Pour lancer l'application :
    ``bokeh serve --show main.py`` 

Accessible dans un navigateur depuis :
    http://localhost:5006/main

'''

from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

import pandas as pd
import re 
from collections import defaultdict

from bokeh.layouts import layout, column, row 
from bokeh.models import ColumnDataSource, HoverTool, FuncTickFormatter,TableColumn, Slider,Select, Paragraph
from bokeh.plotting import figure
from bokeh.models.widgets import Panel,DataTable
from bokeh.tile_providers import Vendors, get_provider
from bokeh.transform import factor_cmap
from data_manipulation import ImportData,LongLat_to_EN,wgs84_to_web_mercator


################################################
## Tab1 : Mariages à Rennes
################################################
TITLE_TAB1='Mariages à Rennes'
donnees_mariage=ImportData('./data/mariages-a-rennes.json')
donnees_mariage=donnees_mariage.sort_values(by='annee')
####################
# Pyramide des ages
####################

# Initialisation
dfpyra=donnees_mariage.copy()
gender_Transform=dfpyra.filter(regex=("epoux_*")).apply(lambda x: -x,axis=0)
dfpyra.update(gender_Transform)

def NbMarAges(df,annee):
    """"

    Parameters
    ----------
    df : DataFrame Pandas
        DataFrame des Mariages.
    annee : str
        Annee à séléctionner.

    Returns
    -------
    ages : DataFrame Pandas
        DataFrame Servant pour le ColumnDataSource.
    """
    ages=df[df.annee==annee]
    ages=ages.filter(regex=("epou_*"))
    ages=ages.transpose() 
    ages.columns=['Value']
    ages['AgeGrp']=[12.5,12.5,35,35,55,55,82.5,82.5]
    ages['sexe']=ages.apply(lambda x: 'Femme' if x['Value']>0 else 'Homme',axis=1)
    ages['height']=[25,25,20,20,20,20,35,35]
    
    return ages

anneemin=dfpyra.annee.min()
anneemax=dfpyra.annee.max()
title=f'Pyramide des ages de {anneemin}'
dfMar=NbMarAges(dfpyra,anneemin)

ages = ColumnDataSource(data=dict(AgeGrp=dfMar['AgeGrp'], Height=dfMar['height'], Sexe=dfMar['sexe'], Value=dfMar['Value']))
# Définition de la figure
pyramid = figure(plot_height=350, toolbar_location=None,name='pyramid',
                 title=title,x_axis_label="Nombre de personnes",y_axis_label="Tranche d\'Âge")

pyramid.hbar(y="AgeGrp", height='Height',right='Value',legend_field="Sexe",
             source=ages,line_width=0, 
             fill_color=factor_cmap('Sexe',palette=["#3498db", "#FF6DAA"],
                                           factors=["Homme","Femme"]))

pyramid.ygrid.grid_line_color = None
pyramid.xaxis.formatter = FuncTickFormatter(code="""return (Math.abs(tick)) +" " """)

# Définition Widget & Callback
sliderAnnee = Slider(start=int(anneemin), end=int(anneemax), value=int(anneemin), step=1, title="Annee")
def updateDate(attrname, old, new):
    dfMar=NbMarAges(dfpyra,str(new))
    title=f'Pyramide des ages de {new}'
    ages.data=dict(AgeGrp=dfMar['AgeGrp'],Height=dfMar['height'], Sexe=dfMar['sexe'], Value=dfMar['Value'])
    pyramid.title.text=title
    
sliderAnnee.on_change('value',updateDate)

####################
# Line Plot
####################
# Initialisation
TITLE_LINE ='fghj'
dataLine=donnees_mariage.filter(regex=("(epou*)"))
sourceLine=ColumnDataSource(data={'x':donnees_mariage['annee'],'y':dataLine['epoux_moins_25']})

# Définition de la figure
lineplot = figure(tools="wheel_zoom,box_zoom,reset",
                  title='Evolution du nombre d\'epoux de moins 25 ans',
                  x_axis_label='Nombre de personnes',y_axis_label="Années")
lineplot.line(x='x', y='y', source=sourceLine,line_width=1.5,line_alpha=1.0,color='#95a5a6',line_dash='dotted')
lineplot.circle(x='x', y='y', source=sourceLine,line_width=3,line_alpha=1.0,color='#95a5a6')

# Définition Widget & Callback

selector = Select(title="Choisir une variable", value="epoux_moins_25", options=list(dataLine.keys()))
def update_var(attrname, old, new):
    titlevar=new.replace('x_m','x de m').replace('e_m','e de m').replace('5','5 ans').replace('_', ' ')
    lineplot.title.text =f'Evolutions du nombre d\'{titlevar}'
    sourceLine.data['y']=dataLine[new]
    
selector.on_change('value', update_var)

####################
# MultiLine Plot
####################
# Initialisation

DataMP=donnees_mariage.filter(regex=("(hom|fem_hom|fem)")).fillna(0)
DataMariage = defaultdict(list)

for name in DataMP:
    DataMariage["Annee"].append(donnees_mariage.annee)
    DataMariage["Nombre"].append(DataMP[name])
    DataMariage['Legende'].append(name)
DataMariage['color'] = ["#95a5a6", "#3498db", "#FF6DAA"]
sourceMP = ColumnDataSource(DataMariage)
MPlot= figure(plot_height=400,tools="wheel_zoom,box_zoom,reset")
MPlot.multi_line(xs='Annee', ys='Nombre', legend="Legende",
                 line_width=3,line_color='color',
                 line_alpha=1.0,source=sourceMP)




################################################
## Tab2 : Résultat Election Municipale
################################################
def Datable(df):
    '''
    Création de la DataTable
    
    Parameters
    ----------
    df : DataFrame
        DataFrame à transformer en DataTable.
        
    Returns
    -------
    MyDatable : DataTable
        DataTable à afficher.

    '''
    sourceDatable=ColumnDataSource(df)
    MyDatableCol=[TableColumn(field=elem, title=elem.upper()) for elem in df.keys()]
    MyDatable=DataTable(source=sourceDatable,columns=MyDatableCol,height=280)
    return MyDatable


def formating(df_rw):
    mydf=df_rw.apply(lambda x: [(x[f'pourcentage_{i}'],x[f'candidat_{i}']) for i in range(1,10)],axis=1,result_type='expand')
    mydf=mydf.transpose()
    mydf=pd.DataFrame(mydf[115].tolist(), index=mydf.index)  
    mydf.columns=['Pourcentage','Candidat']
    return mydf

#Initialisation des variables Statiques
TITLE_TAB='Résultat Election Municipale'

# Importation des données
data_raw=ImportData('./data/resultats_m20.json')

data_li=data_raw.loc[data_raw['niveau_detail']=='li',]
data_bu=data_raw.loc[data_raw['niveau_detail']=='bu',]
data_li[['ypoint','xpoint']]=pd.DataFrame(data_li['geo_point_2d'].values.tolist(), index= data_li.index)

df=wgs84_to_web_mercator(data_li, lon='xpoint', lat='ypoint')

counts=data_bu.groupby('nom_lieu').size().reset_index(name='counts')
data_li= pd.merge(data_li,counts, on='nom_lieu')

nbvoix=data_li.filter(regex=("nb_voix_*"))
nbvoix.columns =[re.sub('nb_voix','candidat',string) for string in nbvoix.columns.values.tolist()]
nbvoix=nbvoix.transpose()
candidats=data_li.filter(regex=("candidat_*")).iloc[0].reset_index()

winner_df=pd.DataFrame(nbvoix.idxmax())
winner_df.columns=['index']

candidats1=winner_df.merge(candidats,on='index',how='left')

data_li['winner']=candidats1[0]

df = pd.DataFrame({'x': data_li['x'], 'y':data_li['y'],
                   'coordx':data_li['xpoint'], 'coordy':data_li['ypoint'],
                   'nomlieu':data_li['nom_lieu'], 'nb_bureau':data_li['counts'],
                   'vainqueur':data_li['winner'],'adresse_lieu':data_li['adresse_lieu']})

source = ColumnDataSource(df)

# Initialisation de la carte
ZOOM=1.001

xrennes,yrennes=LongLat_to_EN(-1.6742900,48.1119800)

p = figure(x_axis_type="mercator", y_axis_type="mercator",
           title="Carte des Elections Municipales - Rennes",
           x_range=(xrennes/ZOOM,xrennes*ZOOM),
           y_range=(yrennes/ZOOM,yrennes*ZOOM),
           x_axis_label='Longitude', y_axis_label='Latitude')

p.add_tile(get_provider(Vendors.CARTODBPOSITRON))

# Initialisation des points de la carte
p.circle(x='x',y='y',source=source,size=10,color=factor_cmap('vainqueur',
                           palette=['#2980b9','#95a5a6','#c0392b',
                                    '#9b59b6','#e74c3c','#273c75',
                                    '#FF6DAA','#2ecc71','#c0392b'],
                           factors=list(candidats[0])))

# Ajout de l'outil : HoverTool // Déplacement sur les points
hover_tool= HoverTool(tooltips=[( 'Nom du Lieu ','@nomlieu'),
                                ('Nombre de Bureau ','@nb_bureau'),
                                ('Adresse du lieu ','@adresse_lieu'),
                                ('Vainqueur ','@vainqueur')])
p.add_tools(hover_tool)

# Ajout de la DataTable Générale
Datable_ville=Datable(formating(data_raw[data_raw['niveau_detail']=='vi']).sort_values(by='Pourcentage',ascending=False))

texteee =Paragraph(text="""Choisir un candidat + une condition + un pourcentage.  
                           Pour faire apparaître seulement les bureaux de votes correspondants.""",height=25)

Explic=Paragraph(text="""""",height=25)
menuCandidat=list(candidats[0])
menuCondi= [">",">=","<","=<","="]   
selectorCand = Select(title="Choisir un candidat", value=menuCandidat[0], options=menuCandidat)
selectorCondi = Select(title='Condition',value=menuCondi[0], options=menuCondi,width=100)

SliderPerc= Slider(start=0, end=100, value=50, step=0.05, title="Pourcentage")

def SelectData(df,SPer,sCand,sCondi):
    cand=list(candidats[candidats[0]==sCand]['index'])[0]
    cand=cand.replace('candidat','pourcentage')
    res=pd.DataFrame()
    if(sCondi=='<'):
        res=data_li[data_li[cand]<SPer] 
    if(sCondi=='>'):
        res=data_li[data_li[cand]>SPer]
    if(sCondi=='<='):
        res=data_li[data_li[cand]<=SPer]
    if(sCondi=='>='):
        res=data_li[data_li[cand]>=SPer]
    if(sCondi=='='):
        res=data_li[data_li[cand]==SPer]
    return res

def updateDate(attrname, old, new):
    Mydata=SelectData(data_li,SliderPerc.value,selectorCand.value,selectorCondi.value)
    source.data={'x': Mydata['x'],'y':Mydata['y'],
             'coordx':Mydata['xpoint'], 'coordy':Mydata['ypoint'],
             'nomlieu':Mydata['nom_lieu'], 'nb_bureau':Mydata['counts'],
             'vainqueur':Mydata['winner'],'adresse_lieu':Mydata['adresse_lieu']}
                  
    
SliderPerc.on_change('value',updateDate)
selectorCand.on_change('value',updateDate)
selectorCondi.on_change('value',updateDate)


tab1 = Panel(child=layout([[MPlot,column(sliderAnnee,pyramid)],column(selector,lineplot)]), title=TITLE_TAB1)
tab2 = Panel(child=layout([[p,[Datable_ville,texteee,row(selectorCand,selectorCondi,SliderPerc)]]]),title=TITLE_TAB)

# Attachement des Tabs à curdoc()
tabs = Tabs(tabs = [tab1, tab2])
curdoc().add_root(tabs)
curdoc().title = "Application Pierre LEPAGNOL"
