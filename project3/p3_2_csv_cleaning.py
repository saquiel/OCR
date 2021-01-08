#! /usr/bin/env python3
# coding = utf-8

# Project3 OCR

# prepare csv file in order to be loaded in a SQL data base
# input: raw csv file
# output: cleaned csv file (in csv_db folder)

import pandas as pd
import numpy as np
import os


def pk_test (df, column_name):
    '''test if a columns contain only unique value'''
    if df[column_name].is_unique:
        return print(f" {column_name} de {df.name} est unique: PK possible")
    else:
        return print(f" {column_name} de {df.name} n'est  pas unique: PK impossible")


# load data: csv tp df
df_population = pd.read_csv("python/oc_data_analyst/project3/data/fr_population.csv", usecols=["Zone", "Code zone", "Année", "Valeur"])


df_animaux = pd.read_csv("python/oc_data_analyst/project3/data/fr_animaux.csv", usecols=["Zone", "Code zone", "Année", "Produit", "Code Produit", "Élément", "Valeur"])

df_vegetaux = pd.read_csv("python/oc_data_analyst/project3/data/fr_vegetaux.csv", usecols=["Zone", "Code zone", "Année", "Produit", "Code Produit", "Élément", "Valeur"])

df_sous_nutrition = pd.read_csv("python/oc_data_analyst/project3/data/fr_sousalimentation.csv", usecols=["Zone", "Code zone", "Année", "Valeur"])



# TODO 1/ table population
df_population.rename(columns={"Zone": "pays", "Code zone": "code_pays", "Année": "annee", "Valeur": "population"}, inplace=True)
# population to integer *1000
df_population["population"]=df_population["population"].apply(lambda x: x*1000).astype(int)
# df_population["code_pays"]=df_population["code_pays"].astype(int)
# df_population.reset_index(drop=True, inplace=True)
df_population.name = "population"





# TODO 2/ table df_dispo_alim
# add origin columns
df_animaux["origin"] = "animal"
df_vegetaux["origin"] = "vegetal"

# concatenation of animaux and vegetaux
df_dispo = pd.concat([df_animaux, df_vegetaux], ignore_index=True)

# clear useless data
index_delete = df_dispo[~df_dispo["Élément"].isin(["Nourriture", "Disponibilité alimentaire (Kcal/personne/jour)", "Disponibilité de protéines en quantité (g/personne/jour)", "Disponibilité de matière grasse en quantité (g/personne/jour)"])].index
df_dispo_alim = df_dispo.drop(index_delete)

# unstack Element 
df_dispo_alim = df_dispo_alim.pivot_table(index=["Zone", "Code zone", "Année", "Produit", 
                                                "Code Produit", "origin"], columns="Élément", values="Valeur")
df_dispo_alim.reset_index(inplace=True)

df_dispo_alim.rename(columns={"Zone": "pays", "Code zone":"code_pays", "Année": "annee", 
                                "Produit": "produit", "Code Produit": "code_produit", 
                                "Nourriture": "dispo_alim_tonnes", 
                                "Disponibilité alimentaire (Kcal/personne/jour)": "dispo_alim_kcal_p_j", 
                                "Disponibilité de protéines en quantité (g/personne/jour)": "dispo_prot", 
                                "Disponibilité de matière grasse en quantité (g/personne/jour)": "dispo_mat_gr"}, inplace=True) 

# dispo_alim millier tonnes => tonnes : *1000
df_dispo_alim["dispo_alim_tonnes"].fillna(0, inplace=True)
df_dispo_alim["dispo_alim_tonnes"]=df_dispo_alim["dispo_alim_tonnes"].apply(lambda x: x*1000).astype(int)

df_dispo_alim.name = "dispo_alim"


# TODO 3/ table equilibre_prod

index_delete = df_dispo[~df_dispo["Élément"].isin(["Disponibilité intérieure", "Aliments pour animaux", "Semences", "Pertes", "Traitement", "Nourriture", "Autres utilisations (non alimentaire)"])].index
df_equilibre_prod = df_dispo.drop(index_delete)

# unstack Element 
df_equilibre_prod = df_equilibre_prod.pivot_table(index=["Zone", "Code zone", "Année", "Produit", 
                                                "Code Produit"], columns="Élément", values="Valeur")
df_equilibre_prod.reset_index(inplace=True)
df_equilibre_prod.fillna(0, inplace=True)

df_equilibre_prod.rename(columns={"Zone": "pays", "Code zone":"code_pays", "Année": "annee", 
                                "Produit": "produit", "Code Produit": "code_produit", 
                                "Nourriture": "dispo_alim_tonnes", 
                                "Disponibilité intérieure": "dispo_int", 
                                "Aliments pour animaux": "alim_ani", 
                                "Semences": "semences", "Pertes": "pertes",
                                "Traitement": "transfo", "Nourriture": "nourriture", 
                                "Autres utilisations (non alimentaire)": "autres_utilisations"}, inplace=True)

df_equilibre_prod.name = "equilibre_prod"


# TODO 4/ table sous_nutrition

# select year 2013
index_delete = df_sous_nutrition[~df_sous_nutrition["Année"].isin(["2012-2014"])].index
df_sous_nutrition = df_sous_nutrition.drop(index_delete)

# rename columns
df_sous_nutrition.rename(columns={"Zone": "pays", "Code zone":"code_pays", "Année": "annee", 
                                "Valeur": "nb_personnes"}, inplace=True)

# clean value & population to integer *1000000
df_sous_nutrition["nb_personnes"] =  pd.to_numeric(df_sous_nutrition["nb_personnes"], errors='coerce').fillna(0).astype(np.float)
df_sous_nutrition["nb_personnes"]=df_sous_nutrition["nb_personnes"].apply(lambda x: x*1000000).astype(int)

# change annee value "2012-2014" (str) to 2013 INT
df_sous_nutrition["annee"] = 2013
df_sous_nutrition["annee"].astype(int)
df_sous_nutrition.name = "nutrition"



df_population.to_csv('python/oc_data_analyst/project3/csv_db/population.csv', index = False)
df_dispo_alim.to_csv('python/oc_data_analyst/project3/csv_db/dispo_alim.csv', index = False)
df_equilibre_prod.to_csv('python/oc_data_analyst/project3/csv_db/equilibre_prod.csv', index = False)
df_sous_nutrition.to_csv('python/oc_data_analyst/project3/csv_db/sous_nutrition.csv', index = False)