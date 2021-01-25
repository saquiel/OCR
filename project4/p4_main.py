#! /usr/bin/env python3
# coding = utf-8

# Project 4 OCR
# 
# data investigation

# data visualization use only Matplotlib in order to 
# improve my basic visualization skill.

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly
import pingouin as pg


# auto room for the figures
plt.rcParams.update({'figure.autolayout': True})


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


def save_png(target_path, file_format=".png"):
    ''' save all figures instanced by pyplot in path target
        input:  path to saved file (optional) 
                file format (optional)
        output: image file saved in target path'''
    for i in plt.get_fignums():
        plt.figure(i).savefig( target_path + str(i) + file_format)
    print(f"{i} figures saved ")
    return 0


def sampling (input_df, period):
    ''' downsampling time series data by month
        input:  DF time series
                sampling period "m", 
        output: DF sampled by month'''
    output_df = input_df.resample(period, closed="right").sum()
    output_df.reset_index(inplace=True)
    return output_df


def by_categ(input_df, column_to_group):
    ''' helper function that avoid repetition
        split DF by categ + group
        input:  DF
        outpud: 3 df series (one per categ)'''
    df_tmp = input_df[input_df["categ"] == 0]
    arr_zero = df_tmp.groupby(input_df[column_to_group])["price"].sum()

    df_tmp = input_df[input_df["categ"] == 1]
    arr_one = df_tmp.groupby(input_df[column_to_group])["price"].sum()

    df_tmp = input_df[input_df["categ"] == 2]
    arr_two = df_tmp.groupby(input_df[column_to_group])["price"].sum()

    return arr_zero, arr_one, arr_two


def regression_line (input_df, x_value, y_value, deg=1):
    '''build the lineare regression model of 2 variables
        input:  DataFrame and it 2 columns name
                degres of the regression line (optional)
        output: regression line
                R² value'''
    # compute regression line
    reg_coef, stats = poly.polyfit(x=input_df[x_value], y=input_df[y_value], deg=deg, full=True)
    # regression coef R²
    r2 = round(stats[0][0], 0)
    # build the linear regression line
    # reverse the coefficients to fit np.poly1d() expectation
    reg_coef = reg_coef[::-1]
    line_reg = np.poly1d(reg_coef)
    return line_reg, r2


# parse csv
df_customers = CsvToPandas("python/oc_data_analyst/project4/raw_data/customers.csv", ["client_id", "sex", "birth"])
df_products = CsvToPandas("python/oc_data_analyst/project4/raw_data/products.csv", ["id_prod", "price", "categ"])
df_transactions = CsvToPandas("python/oc_data_analyst/project4/raw_data/transactions.csv", ["id_prod", "date", "session_id", "client_id"])


# clean data

# kill test entries
index_delete = df_customers[df_customers["client_id"].isin(["ct_0", "ct_1"])].index
df_customers.drop(index_delete, inplace=True)

index_delete  = df_products[df_products["id_prod"].isin(["T_0"])].index
df_products.drop(index_delete, inplace=True)

index_delete  = df_transactions[df_transactions["id_prod"].isin(["T_0"])].index
df_transactions.drop(index_delete, inplace=True)

# format date
df_transactions["date"] = pd.to_datetime(df_transactions["date"], format="%Y-%m-%d %H:%M:%S.%f")

# product float => int
df_products["categ"] = df_products["categ"].astype(int)

#  age = 2021 - birth
df_customers["age"] = df_customers["birth"].apply(lambda x: 2022 - x).astype(int)
df_customers.drop(columns="birth", inplace=True)

# build DF with:
# transaction date, client_id, age, gender, categ, session_id
df_sales= df_transactions.copy()
df_sales = pd.merge(df_sales, df_customers, on="client_id", how="left")
df_sales = pd.merge(df_sales, df_products, on="id_prod", how="left")

# drop sales without linked product
na_value = df_sales[df_sales.isna().any(1)]
print(f"{len(na_value.index)} lines with no existing product will be ignored")
df_sales.dropna(inplace=True)
na_value = df_sales[df_sales.isna().any(1)]
print(f"{len(na_value.index)} lines with no existing product left")

# categ => int
df_sales["categ"] = df_sales["categ"].astype(int)


# TODO 1/ turnover evolution
df_turnover = df_sales.groupby(df_sales["date"])["price"].sum().to_frame()
df_turnover = sampling(df_turnover, period="m")

# format x axis (date)
xdates= df_turnover['date'].dt.strftime('%Y-%m')
yvalues = df_turnover['price']

fig, ax = plt.subplots()
ax.bar(xdates, yvalues, label="CA par mois")
ax.set_title("CA mensuel 2021-2022")
ax.set_ylabel("CA (euros)")
ax.legend()
# 45° rotation
ax.xaxis.set_tick_params(rotation=45)


# TODO 2/ sales evolution by gender
df_men = df_sales[df_sales["sex"] == "m"]
df_men = df_men.groupby(df_sales["date"])["price"].sum().to_frame()
df_men = sampling(df_men, period="m")

df_women = df_sales[df_sales["sex"] == "f"]
df_women = df_women.groupby(df_sales["date"])["price"].sum().to_frame()
df_women = sampling(df_women, period="m")

xdates= df_men['date'].dt.strftime('%Y-%m') # x asis with month+year
ymen = df_men['price']
ywomen = df_women["price"]

fig, ax = plt.subplots()
# stack 3 bars
p0 = plt.bar(xdates, ymen, label = "homme")
p1 = plt.bar(xdates, ywomen, bottom=ymen, label = "femme")
# ax.bar(xdates, yvalues)
# 45° rotation on x axis
ax.xaxis.set_tick_params(rotation=45)
ax.set_title("CA mensuel 2021-2022 par genre")
ax.set_ylabel("CA (euros)")
ax.legend(loc="best")


# TODO 3/ sales evolution with categories (0-1-2)

# extract price by categ, grouped by date
df_zero, df_one, df_two = by_categ(df_sales, "date")
df_zero = df_zero.to_frame()
df_one = df_one.to_frame()
df_two = df_two.to_frame()

df_zero = sampling(df_zero, period="m")
df_one = sampling(df_one, period="m")
df_two = sampling(df_two, period="m")

xdates= df_zero['date'].dt.strftime('%Y-%m') # x asis with month+year
yzero = df_zero['price']
yone = df_one["price"]
ytwo = df_two["price"]


fig, ax = plt.subplots()
# stack 3 bars
p0 = plt.bar(xdates, yzero, label = "Categorie 0")
p1 = plt.bar(xdates, yone, bottom=yzero, label = "Categorie 1")
p2 = plt.bar(xdates, ytwo, bottom=yzero+yone, label = "Categorie 2")
# ax.bar(xdates, yvalues)
# 45° rotation on x axis
ax.xaxis.set_tick_params(rotation=45)
ax.set_title("CA mensuel 2021-2022 par catégories")
ax.set_ylabel("CA (euros)")
ax.legend(loc="best")


# TODO 4/ november 2021 sales by day by categories

# select november 2021 data
df_november = df_sales[(df_sales['date'] > '2021-10-1') & (df_sales['date'] <= '2021-10-31')]

# split DF by categories
df_zero_nov, df_one_nov, df_two_nov = by_categ(df_november, "date")
df_zero_nov = df_zero_nov.to_frame()
df_one_nov = df_one_nov.to_frame()
df_two_nov = df_two_nov.to_frame()
# sample by day
df_zero_nov = sampling(df_zero_nov, period="D")
df_one_nov = sampling(df_one_nov, period="D")
df_two_nov = sampling(df_two_nov, period="D")

xdates= df_zero_nov['date'].dt.strftime('%d') # x axis with day
yzero = df_zero_nov['price']
yone = df_one_nov["price"]
ytwo = df_two_nov["price"]

fig, ax = plt.subplots()
# stack 3 bars
p0 = plt.bar(xdates, yzero, label = "Categorie 0")
p1 = plt.bar(xdates, yone, bottom=yzero, label = "Categorie 1")
p2 = plt.bar(xdates, ytwo, bottom=yzero+yone, label = "Categorie 2")
# ax.bar(xdates, yvalues)
# 45° rotation on x axis
ax.xaxis.set_tick_params(rotation=45)
ax.set_title("CA novembre 2021 par catégories")
ax.set_ylabel("CA (euros)")
ax.legend(loc="best")


# TODO 5/ cart density

df_cart = df_sales.groupby(df_sales["session_id"])["price"].sum().to_frame()
df_cart.reset_index(inplace=True)

mean_price = df_cart["price"].mean().round(decimals=2)

fig, ax = plt.subplots()
fig = df_cart["price"].plot.kde(xlim=[0,200], ylim=[0, 0.04])
fig.annotate(f"mean:{mean_price}", xy=(mean_price, 0.015), 
            xytext=(mean_price, 0.02),
            arrowprops=dict(facecolor="black", headwidth=4, width=1, headlength=4),
            horizontalalignment="left",
            verticalalignment="top")
fig.set_title("Répartition des paniers par montant")
ax.set_xlabel("Montant en euros")


# TODO 6/ top client bar

df_top_client = df_sales.groupby(df_sales["client_id"])["price"].sum().to_frame()
df_top_client = df_top_client.sort_values(by=["price"], ascending=False).head(6)

ratio_top_buyer = int(df_top_client["price"].sum() / df_sales["price"].sum() *100)

xvalues = df_top_client.index
yvalues = df_top_client["price"]

fig,ax = plt.subplots()
ax.bar(xvalues, yvalues, label="Meilleur clients 2021-2022")
ax.set_title("Meilleur clients")
ax.set_ylabel("Total des achats (euros)")

# matplotlib.patch.Patch properties
props = dict(boxstyle='round', facecolor='lightblue', alpha=0.5)
textstr = f"Soit {ratio_top_buyer}% des ventes"
ax.text(0.6, 0.6, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
ax.legend()


# TODO 7/ cart box plot

# from Matplotlib doc:
# Works with array because it is more efficient:
# boxplot converts a 2-D array into a list of vectors internally anyway.
arr_cart = df_sales.groupby(df_sales["session_id"])["price"].sum().values
# extract maximum cart value
maximum = arr_cart.max()

fig, ax = plt.subplots()
ax.boxplot(arr_cart)
ax.set_title("Répartition des ventes avec outliers")
# comments
props = dict(boxstyle='round', facecolor='lightblue', alpha=0.5)
textstr = f"Max: {maximum} euros"
ax.text(0.6, 0.95, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
ax.set_ylabel("Montant en euros", rotation=90)


# TODO 8/ cart bot plot by categories

arr_cart_zero, arr_cart_one, arr_cart_two = by_categ(df_sales, "session_id")
# Note from MatPlotLib doc:
# Classes that are 'array-like' such as pandas data objects 
# and np.matrix may or may not work as intended. 
# It is best to convert these to np.array objects prior to plotting.
arr_cart_zero = arr_cart_zero.values
arr_cart_one = arr_cart_one.values
arr_cart_two = arr_cart_two.values

data = [arr_cart_zero, arr_cart_one, arr_cart_two]
# with outliers
fig, ax = plt.subplots()
ax.boxplot(data)
ax.set_title("Distribution des ventes par catégories avec outliers")
ax.set_xticklabels(['cat 0','cat 1','cat 2'])
ax.set_ylabel("Montant en euros", rotation=90)
# without outliers
fig, ax = plt.subplots()
ax.boxplot(data, showfliers=False)
ax.set_title("Distribution des ventes par catégories sans outliers")
ax.set_xticklabels(['cat 0','cat 1','cat 2'])
ax.set_ylabel("Montant en euros", rotation=90)


# TODO 10/ sales by category / pie chart

total_zero = df_sales[df_sales["categ"] == 0]["price"].sum()
total_one = df_sales[df_sales["categ"] == 1]["price"].sum()
total_two = df_sales[df_sales["categ"] == 2]["price"].sum()

fig, ax = plt.subplots()
fig.suptitle("Répartition des ventes par catégories")
ax.pie([total_zero, total_one, total_two], labels=["Categorie 0", "Categorie 1", "Categorie 2"], autopct='%1.1f%%')
ax.axis("equal")


# TODO 11/ total sales by gender pie chart
total_sales_men = df_sales[df_sales["sex"] == "m"]["price"].sum()
total_sales_women = df_sales[df_sales["sex"] == "f"]["price"].sum()
fig, ax = plt.subplots()
fig.suptitle("Répartition des ventes par genre")
ax.pie([total_sales_men, total_sales_women], labels=["Homme", "Femme"], autopct='%1.1f%%', startangle=90)
ax.axis("equal") # Equal aspect ratio ensures that pie is drawn as a circle.


# TODO 12/ sex vs categ pie

df_zero_bysex, df_one_bysex, df_two_bysex = by_categ(df_sales, "sex")
df_zero_bysex = df_zero_bysex.values
df_one_bysex = df_one_bysex.values
df_two_bysex = df_two_bysex.values

df_zero_bysex = df_zero_bysex.reshape(2,1)
df_one_bysex = df_one_bysex.reshape(2,1)
df_two_bysex = df_two_bysex.reshape(2,1)

bycateg = np.hstack([df_zero_bysex, df_one_bysex, df_two_bysex])

fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(12, 4) )
fig.suptitle("Répartition des ventes par catégories par genre")

ax0.pie([bycateg[0,0], bycateg[1,0]], labels=["Homme", "Femme"], autopct='%1.1f%%', startangle=75)
ax0.set_title("Catégorie 0")

ax1.pie([bycateg[0,1], bycateg[1,1]], labels=["Homme", "Femme"], autopct='%1.1f%%', startangle=75)
ax1.set_title("Catégorie 1")

ax2.pie([bycateg[0,2], bycateg[1,2]], labels=["Homme", "Femme"], autopct='%1.1f%%', startangle=75)
ax2.set_title("Catégorie 2")


# TODO 13/ corelation between sex and categ

# df sex in function of categ (value = number of sales)
df_sex_cat = df_sales.pivot_table(index=["sex"], columns="categ", values="price", aggfunc="sum")

# compute ANOVA on categ and sex
aov = pg.anova(data=df_sales, dv="categ", between="sex", detailed=True).round(5)
print("OAV contigeance")
print(aov)
arr_value = df_sex_cat.values

fig, ax = plt.subplots()
ax.imshow(arr_value)

ax.set_xticks(np.arange(3))
ax.set_yticks(np.arange(2))
ax.set_xticklabels(["catégorie 0", "catégorie 1", "catégorie 2"])
ax.set_yticklabels(["Homme", "Femme"])
ax.set_title("tableau de contingeance: genre / catégorie (nbx achat)")
ax.text(-0.4, 0.9, f'P-value: {aov.iloc[0,5]}\nLa relation entre sexe et catégorie\n n’est pas significative')
ax.yaxis.set_tick_params(rotation=45)



# TODO 14/ equity sales vs age Lorenz

# lorenz DF = bucket by X value and sum Y grouped value
df_lorenz= (df_sales["price"].groupby(df_sales["age"]).sum()).to_frame()
# cumulative sum + normalization
df_lorenz = df_lorenz.reindex(index=df_lorenz.index[::-1])

df_lorenz["price"] = df_lorenz["price"].cumsum() / df_lorenz["price"].sum()

# add starting point 0
df_lorenz.iloc[0] = [0]
df_lorenz.reset_index(inplace=True)

xvalue=df_lorenz["age"].values
yvalue=df_lorenz["price"].values

# Gini = relative_mean_absolute_difference / 2
arr_lorenz = df_lorenz.to_numpy()
# Mean absolute difference
mad = np.abs(np.subtract.outer(arr_lorenz, arr_lorenz)).mean()
# Relative Mean Absolute Difference
rmad = mad/np.mean(arr_lorenz)
# Gini coefficient
gini_index = round(0.5 * rmad, 3)
print(f"Valeur de Gini: {gini_index} ")

fig, ax = plt.subplots()
ax.plot(xvalue, yvalue)
# perfect equity line
ax.plot([93,18],[0,1])
# reverse xasis
ax.set_xlim(ax.get_xlim()[::-1])
ax.text(50, 0.2, f"Index de Gini:{gini_index} ")
ax.set_title("Courbe de Lorenz achats par age")
ax.set_xlabel("Age des clients")


# TODO 15/ corelation sales vs age

df_corelation = df_sales.groupby(df_sales["session_id"]).agg({"price":"sum", "age":"first"})
# compute the regression line 
line_reg, r2 = regression_line(df_corelation, "age", "price")
print(f"r² de la régression lineaire: {r2} ")
x=df_corelation["age"]
y1=df_corelation["price"]
y2=line_reg(df_corelation["age"])

fig, ax = plt.subplots()
ax.scatter(x, y1, color="lightgreen", label="Paniers par ages", marker=".")
ax.plot(x, y2, label="Regression linéaire Paniers/ages")
ax.text(60, 400, f'R²: {r2}')
ax.set_ylabel("Total des achats (euros)", rotation=90)
ax.set_xlabel("Age des clients")
plt.legend()


# TODO 16/ corelation sales frequency vs age

# group by cart
df_corelation = df_sales.groupby(df_sales["session_id"]).agg({"price":"sum", "age":"first"})
# group by age
df_corelation = df_corelation.groupby(df_corelation["age"]).agg({"price":"count"})

df_corelation.reset_index(inplace=True)
# build the regression line
line_reg, r2 = regression_line(df_corelation, "age", "price")
print(f"r² de la régression lineaire: {r2} ")

x=df_corelation["age"]
y1=df_corelation["price"]
y2=line_reg(df_corelation["age"])

fig, ax = plt.subplots()
ax.scatter(x, y1, color="lightgreen", label="Nbx paniers par ages", marker=".")
ax.plot(x, y2, label="Regression linéaire Nbx paniers/ages")
ax.text(70, 4000, f'R²: {r2}')
ax.set_ylabel("Fréquence des achats", rotation=90)
ax.set_xlabel("Age des clients")
plt.legend()


# TODO 17/ corelation cart size vs age

# group by cart
df_corelation = df_sales.groupby(df_sales["session_id"]).agg({"price":"count", "age":"first"})
df_corelation.reset_index(inplace=True)

# build the regression line
line_reg, r2 = regression_line(df_corelation, "age", "price")
print(f"r² de la régression lineaire: {r2} ")

x=df_corelation["age"]
y1=df_corelation["price"]
y2=line_reg(df_corelation["age"])

fig, ax = plt.subplots()
ax.scatter(x, y1, color="lightgreen", label="Taille panier par ages", marker=".")
ax.plot(x, y2, label="Regression Taille paniers/ages")
ax.text(70, 12, f'R²: {r2}')
ax.set_ylabel("Article par panier", rotation=90)
ax.set_xlabel("Age des clients")
plt.legend()


# TODO 18/ corelation categories vs age

arr_age_zero = df_sales[df_sales["categ"] == 0]["age"]
arr_age_one = df_sales[df_sales["categ"] == 1]["age"]
arr_age_two = df_sales[df_sales["categ"] == 2]["age"]

data = [arr_age_zero, arr_age_one, arr_age_two]
# ANOVA analysis: test group corelated between them?
aov = pg.anova(data=df_sales, dv="age", between="categ", detailed=True)
print(aov)

# without outliers age by categories without outliers
fig, ax = plt.subplots()
ax.boxplot(data, showfliers=False)
ax.set_title("Distribution des ages par catégories sans outliers")
ax.set_xticklabels(['cat 0','cat 1','cat 2'])
ax.text(2.2, 80, f'η²: {round(aov.iloc[0,6],3)} P-value:{aov.iloc[0,5]} < 0.05\nLa relation entre age et catégorie\nest significative')


# TODO 19 / sales by age bucketed
df_sales_bucket = df_sales.groupby(df_sales["age"])["price"].sum().to_frame()
df_sales_bucket.reset_index(inplace=True)
# create bucket
bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
# bucket label
labels =["9-", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79" , "80-89", "90+"]
# sample DF by age
df_sales_bucket['binned'] = pd.cut(df_sales_bucket['age'], bins,labels=labels)
df_sales_bucket = df_sales_bucket.groupby([df_sales_bucket["binned"]])["price"].sum()

xdates= df_sales_bucket.index
yvalues = df_sales_bucket.values

fig, ax = plt.subplots()
ax.bar(xdates, yvalues, label=labels)
ax.set_title("ventes par groupe d'age")
ax.set_ylabel("ventes (euros)")
# 45° rotation
ax.xaxis.set_tick_params(rotation=45)


save_png(target_path="python/oc_data_analyst/project4/figures/figure")

# plt.show()