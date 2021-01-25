#! /usr/bin/env python3
# coding = utf-8

# Project 4 OCR
# Data cleaning
# 

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