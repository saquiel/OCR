#! /usr/bin/env python3
# coding = utf-8


# Project3 OCR

# perform data manipulation in pandas in order to answer project3 questions


import pandas as pd
import numpy as np
import os



def CsvToPandas (path_to_csv, input_col):
    ''' load csv to a pandas data frame:
        input:  path to csv file
                column to extract
        output: pandas data frame'''
    try:
        output_df = pd.read_csv(path_to_csv, usecols=input_col)
    except FileNotFoundError:
        return print("file not found, input the path to the csv file")
    return output_df


df_population = CsvToPandas("python/oc_data_analyst/project3/data/fr_population.csv", ["Zone", "Valeur"])
df_sous_alim = CsvToPandas("python/oc_data_analyst/project3/data/fr_sousalimentation.csv", ["Zone", "Année", "Valeur"])
df_animaux = CsvToPandas("python/oc_data_analyst/project3/data/fr_animaux.csv", ["Zone", "Élément", "Produit", "Valeur"])
df_cereales = CsvToPandas("python/oc_data_analyst/project3/data/fr_céréales.csv", ["Produit"])
df_vegetaux = CsvToPandas("python/oc_data_analyst/project3/data/fr_vegetaux.csv", ["Zone", "Élément", "Produit", "Valeur"])
df_list_vegetaux = CsvToPandas("python/oc_data_analyst/project3/data/fr_vegetaux.csv", ["Produit"])

# le parse des fichiers est réalisé en tête de script afin de facilité, si nécessaire, 
# une optimisation (via concurency: lib threading)




# Preparation dataframe disponibilité: df_dispo
# concatenation of animaux and vegetaux
df_dispo = pd.concat([df_animaux, df_vegetaux], ignore_index=True)

# clear useless data
index_delete = df_dispo[df_dispo["Élément"].isin(["Variation de stock"])].index
df_dispo.drop(index_delete, inplace=True)
# unstack Element into dispo Kcal + Dispo prot
df_dispo = df_dispo.pivot_table(index=["Zone", "Produit"], columns="Élément", values="Valeur")

# merge table animaux and population on Zone
df_population.rename(columns={'Valeur':'Population'}, inplace=True) # avoid double column name
df_dispo.reset_index(level=["Zone", "Produit"], inplace=True) # reset index to avoid data killed by merge
df_dispo = pd.merge(df_dispo, df_population, on="Zone", how="left")


# clean value & optimization

# fill no value = 0
df_dispo.fillna(0, inplace=True)

# dispo total (Kton) => Kg
df_dispo["Nourriture"]=df_dispo["Nourriture"].apply(lambda x: x*1000000).astype(int)
df_dispo.rename(columns={'Nourriture':'dispo alim (kg/an)'}, inplace=True)

# dispo interieur total (Kton) => Kg
df_dispo["Disponibilité intérieure"]=df_dispo["Disponibilité intérieure"].apply(lambda x: x*1000000).astype(int)
df_dispo.rename(columns={'Disponibilité intérieure':'dispo int (kg/an)'}, inplace=True)

# Autres utilisations (non alimentaire) (Kton) => Kg
df_dispo["Autres utilisations (non alimentaire)"]=df_dispo["Autres utilisations (non alimentaire)"].apply(lambda x: x*1000000).astype(int)
df_dispo.rename(columns={'Autres utilisations (non alimentaire)':'autre utilisation (kg/an)'}, inplace=True)

# pertes (Kton) => Kg
df_dispo["Pertes"]=df_dispo["Pertes"].apply(lambda x: x*1000000).astype(int)
df_dispo.rename(columns={'Pertes':'Pertes (kg/an)'}, inplace=True)

# Aliments pour animaux (Kton) => Kg
df_dispo["Aliments pour animaux"]=df_dispo["Aliments pour animaux"].apply(lambda x: x*1000000).astype(int)
df_dispo.rename(columns={'Aliments pour animaux':'alim animal (kg/an)'}, inplace=True)

# population to integer *1000
df_dispo["Population"]=df_dispo["Population"].apply(lambda x: x*1000).astype(int)

# dispo (Kcal/jour) => (kcal/an)    *360
df_dispo["Disponibilité alimentaire (Kcal/personne/jour)"]=df_dispo["Disponibilité alimentaire (Kcal/personne/jour)"].apply(lambda x: x*360).astype(int)
df_dispo.rename(columns={'Disponibilité alimentaire (Kcal/personne/jour)':'Dispo alim (Kcal/pers/an)'}, inplace=True)

# dispo_prot (g/jour) => (mg/an)    *360000
df_dispo["Disponibilité de protéines en quantité (g/personne/jour)"]=df_dispo["Disponibilité de protéines en quantité (g/personne/jour)"].apply(lambda x: x*360000).astype(int)
df_dispo.rename(columns={'Disponibilité de protéines en quantité (g/personne/jour)':'Dispo prot (mg/pers/an)'}, inplace=True)

# DF population sous nutrition 
# selection des valeur de 2013
# nettoyage
index_delete = df_sous_alim[~df_sous_alim["Année"].isin(["2012-2014"])].index
df_sous_alim.drop(index_delete, inplace=True)
# population en entier *1000000 (unité humain)
df_sous_alim["Valeur"] =  pd.to_numeric(df_sous_alim["Valeur"], errors='coerce').fillna(0).astype(np.float)
df_sous_alim["Valeur"]=df_sous_alim["Valeur"].apply(lambda x: x*1000000).astype(int)

# création list des vegetaux
df_list_vegetaux = df_list_vegetaux.drop_duplicates()

# TODO question 1 Calculez le nombre total d’humains sur la planète
# drop double from china: China (cont) + Hong-Kong + Macao
df_population = df_population.drop([34,35,36])
nbx_humain = df_population["Population"].sum()*1000
print(f"Q1/ total humain: {nbx_humain}")


# TODO Question 3 : Calculez (pour chaque pays et chaque produit) la disponibilité alimentaire en kcal => (Kcal/pers/an)*Population
df_dispo["Dispo tot (Kcal/an)"] = (df_dispo['Dispo alim (Kcal/pers/an)']*df_dispo['Population']).astype(int)
# Question 3 : Calculez (pour chaque pays et chaque produit) la disponibilité alimentaire de protéines en kg => (mg/pers/an)*Population/1000000
df_dispo["Dispo prot (Kg/an)"] = (df_dispo['Dispo prot (mg/pers/an)']*df_dispo['Population']/1000000)


# TODO Question 4 : calculez pour chaque produit le ratio "énergie/poids" (kcal/kg) => Dispo tot (Kcal/an) / dispo alim (kg)
# note: remove infinite and nan division (=0): replace([np.inf, np.nan], 0)
df_dispo["Energie/poids (kcal/kg)"] = (df_dispo["Dispo tot (Kcal/an)"] / df_dispo["dispo alim (kg/an)"]).replace([np.inf, np.nan], 0).astype(int)
# expected: egg: 1470 kcal/kg

# ***ratio "prot/poids" (Kg/kg) => Dispo tot (Kg/an) / dispo alim (kg)
df_dispo["ratio proteine"] = (df_dispo["Dispo prot (Kg/an)"] / df_dispo["dispo alim (kg/an)"]).replace([np.inf, np.nan], 0).round(4)


# TODO Question 5 : Citez 5 aliments parmi les 20 aliments les plus caloriques, en utilisant le ratio énergie/poids.
# copy the needed columns + kill 0
df_maxcal = df_dispo[["Produit", "Energie/poids (kcal/kg)"]].replace(0, np.NaN).copy()
# calculate the mean (speed up: without sorting)
df_maxcal = df_maxcal.groupby("Produit", sort=False).mean()

print("Q5/ 5 plus hauts produits en ratio kcal/kg:")
print(df_maxcal.nlargest(5, ["Energie/poids (kcal/kg)"]))


# TODO Question 6 : Calculez, pour les produits végétaux uniquement, la disponibilité intérieure mondiale exprimée en kcal.

# keep vegetaux rows
index_delete = df_dispo[~df_dispo["Produit"].isin(df_list_vegetaux["Produit"])].index
df_temp = df_dispo.drop(index_delete)
# total dispo int (Kcal/an) = Dispo int (Kg/an) * Energie (Kcal/kg/an)
tot_energie_vegetal = (df_temp["dispo int (kg/an)"]*df_temp["Energie/poids (kcal/kg)"]).sum()
print(f"Q6/ disponibilité intérieure végétal mondiale {tot_energie_vegetal} kcal")

# total dispo int (Kg/an) = Dispo int (Kg/an) * ratio_prot (prot/kg)
tot_prot_vegetal = (df_temp["dispo int (kg/an)"]*df_temp["ratio proteine"]).sum()
print(f"dispo mondial proteine: {tot_prot_vegetal} Kg")


# TODO Question 7 : Combien d'humains pourraient être nourris si toute la disponibilité intérieure mondiale de produits végétaux était utilisée pour de la nourriture ?
# besoin humain: 2200Kcal (EFSA)
# nbx humain possible avec dispo Kcal
total_humain = int(tot_energie_vegetal/(2200*365))
print(f"Q7/ total humain avec dispo calorique vegetale: {total_humain} humains")
# besoin humain: 0,8 g de protéines par kilo de poids et par jour (Vidal)
# poid moyen humain: 62Kg (BMC Public Health)
# besoin moyen protéines par personne par jour: 50g=0.05Kg
total_humain = int(tot_prot_vegetal/(0.05*365))
print(f"Q7/ total humain avec dispo proteine vegetale: {total_humain} humains")


# TODO Question 8 : Combien d'humains pourraient être nourris si toute la disponibilité alimentaire en produits végétaux la nourriture végétale destinée aux animaux et les pertes de produits végétaux étaient utilisés pour de la nourriture ?


# total dispo animaux+pertes (Kcal/an) = ( (perte + animal(Kg/an) ) * Energie (Kcal/kg/an)
tot_energie_perte_animal = ((df_temp["alim animal (kg/an)"] + df_temp["Pertes (kg/an)"]) * df_temp["Energie/poids (kcal/kg)"]).sum()
# nbx humain possible avec perte et alim animal (Kcal)
total_humain = tot_energie_perte_animal/(2200*365)

# total dispo animaux+pertes (Kcal/an) = (perte + animal) (Kg/an) * ratio_prot (prot/Kg)
tot_energie_perte_animal = int(((df_temp["alim animal (kg/an)"] + df_temp["Pertes (kg/an)"]) * df_temp["ratio proteine"]).sum())
print(f"Q8/ disponibilité perte+animal {tot_energie_perte_animal} Kg proteine")

total_humain = int(tot_energie_perte_animal/(0.05*365))
print(f"Q8/ total humain avec perte+animal (proteine): {total_humain} humains")


# TODO Question 9 : Combien d'humains pourraient être nourris avec la disponibilité alimentaire mondiale (Kcal) + (proteine)

# total dispo int (Kcal/an) = Dispo int (Kg/an) * Energie (Kcal/kg/an)
tot_energie_dispo_int = (df_dispo["dispo int (kg/an)"]*df_dispo["Energie/poids (kcal/kg)"]).sum()
# total dispo int (Kg/an) = Dispo int (Kg/an) * ratio_prot (prot/kg)
tot_prot_dispo_int = (df_dispo["dispo int (kg/an)"]*df_dispo["ratio proteine"]).sum()
# nbx humain possible disponibilite total (Kcal)
total_humain = int(tot_energie_dispo_int/(2200*365))
print(f"Q9/ total humain avec dispo mondiale: {total_humain} ")
# nbx humain possible avec disponibilite total proteine
total_humain = int(tot_prot_dispo_int/(0.05*365))
print(f"Q9/ total humain avec dispo mondiale: {total_humain} ")


# TODO Question 10 : A partir des données téléchargées qui concernent la sous-nutrition, répondez à cette question : Quelle proportion de la population mondiale est considérée comme étant en sous-nutrition ?
# 2013
prop_ss_nut =  ((df_sous_alim["Valeur"].sum()) / nbx_humain).round(decimals=3)
print(f"Q10/ proportion de la population mondiale en sous-nutrition: {prop_ss_nut}")


# TODO Question 11 : En ne prenant en compte que les céréales destinées à l'alimentation (humaine et animale), quelle proportion (en termes de poids) est destinée à l'alimentation animale ?
# creation de la liste des cereales
df_cereales.drop_duplicates(inplace=True)
index_delete = df_vegetaux[~df_vegetaux["Produit"].isin(df_cereales["Produit"])].index
df_vege_tmp = df_vegetaux.drop(index_delete)

split_vegetaux = df_vege_tmp["Valeur"].groupby(df_vege_tmp["Élément"]).sum()
# proportion alimentaiton animal = alim_animal / (alim_animal + alim_humain)
prop_alim_animal = (split_vegetaux["Aliments pour animaux"]/(split_vegetaux["Aliments pour animaux"] + split_vegetaux["Nourriture"])).round(decimals=3)
print(f"Q11/ proportion alimentation animal/alimentation total: {prop_alim_animal}")


# TODO Question 12 : Donnez les 3 produits qui ont la plus grande valeur pour chacun des 2 ratios
# informations relatives aux pays dans lesquels la FAO recense des personnes en sous-nutrition.
df_sous_alim.drop(df_sous_alim[df_sous_alim["Valeur"] == 0].index, inplace=True)

# garder les pays avec sous nutrition
index_delete = df_dispo[~df_dispo["Zone"].isin(df_sous_alim["Zone"])].index
df_dispo_ss_al = df_dispo.drop(index_delete)
# Repérez les 15 produits les plus exportés par ce groupe de pays: Exportations - Quantité
top_15 = df_dispo_ss_al["Exportations - Quantité"].groupby(df_dispo_ss_al["Produit"]).sum().nlargest(15)
print(top_15.index)
# sélectionnez les 200 plus grandes importations de ces produits: Importations - Quantité
# INCOMPREHENSIBLE ET INUTILE

# filtrer les 15 produits
index_delete = df_dispo[~df_dispo["Produit"].isin(top_15.index)].index
df_dispo_15 = df_dispo.drop(index_delete)
df_dispo_15.drop(columns=["Dispo alim (Kcal/pers/an)", "Dispo prot (mg/pers/an)","Disponibilité alimentaire en quantité (kg/personne/an)","Disponibilité de matière grasse en quantité (g/personne/jour)", "Population","Dispo tot (Kcal/an)","Dispo prot (Kg/an)","Energie/poids (kcal/kg)","ratio proteine"], inplace =True)
# le ratio entre la quantité destinés aux "Autres utilisations" (Other uses) et la disponibilité intérieure.
df_dispo_15["ratio autre/int"] = (df_dispo_15["autre utilisation (kg/an)"] / df_dispo["dispo int (kg/an)"]).round(decimals=3)
# le ratio entre la quantité destinée à la nourriture animale et la quantité destinée à la nourriture (animale + humaine)
df_dispo_15["ratio animal/animal_humain"] = (df_dispo_15["alim animal (kg/an)"] / (df_dispo_15["alim animal (kg/an)"] + df_dispo_15["dispo alim (kg/an)"])).round(decimals=3)

# Donnez les 3 produits qui on t la plus grande valeur pour chacun des 2 ratios (vous aurez donc 6 produits à citer)
top_3_other = df_dispo_15["ratio autre/int"].groupby(df_dispo_15["Produit"]).max().to_frame()
print("QUESTION 12")
print("Plus grande valeur du ratio autre/int") # probleme avec la norvege + huile de palme 
print(top_3_other["ratio autre/int"].nlargest(3))


top_3_animal = df_dispo_15["ratio animal/animal_humain"].groupby(df_dispo_15["Produit"]).max().to_frame()
print("Plus grande valeur ration animal/total")
print(top_3_animal["ratio animal/animal_humain"].nlargest(3))


# TODO Question 13 : Combien de tonnes de céréales pourraient être libérées si les USA diminuaient leur production de produits animaux de 10% ?
# clear table: keep cereales + USA + aliment_animaux
index_delete = df_vegetaux[(~df_vegetaux["Produit"].isin(df_cereales["Produit"])) | (~df_vegetaux["Zone"].isin(["États-Unis d'Amérique"])) | (~df_vegetaux["Élément"].isin(["Aliments pour animaux"]))].index
df_usa = df_vegetaux.drop(index_delete)
# en millier de tonnes
diminution_10 = int(df_usa["Valeur"].sum()/10)
print(f"Q13/ 10% de la consomation animal de cereal aux usa: {diminution_10} milliers de tonnes")


# TODO Question 14 : En Thaïlande, quelle proportion de manioc est exportée ? Quelle est la proportion de personnes en sous-nutrition?

df_thai_export = df_vegetaux[(df_vegetaux["Zone"]=="Thaïlande") & (df_vegetaux["Produit"]=="Manioc") & (df_vegetaux["Élément"]=="Exportations - Quantité")]
thai_manioc_export = int(df_thai_export.iloc[0]["Valeur"])

df_thai_ss_nut = df_sous_alim[(df_sous_alim["Zone"]=="Thaïlande")]
thai_ss_nut = df_thai_ss_nut.iloc[0]["Valeur"]
print(f"Q14 Thailand: {thai_manioc_export} milliers de tonnes de manioc exportés")
print(f"Q14 Thailand: {thai_ss_nut} personnes en sous nutrition")

# df[(df['Gender']=='Male') & (df['Year']==2014)]
# or
# df.query('Gender=="Male" & Year=="2014" ') => faster for 500K more rows


# return result.csv for testing
df_thai_ss_nut.to_csv('python/oc_data_analyst/project3/result.csv')

