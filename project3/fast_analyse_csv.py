#! /usr/bin/env python3
# coding = utf-8

# load a csv and perform basic analysis
# input: csv file
# output: report.txt with duplicates, NaN, Type, statistic description and outliers

import pandas as pd
import numpy as np
import os


def CsvToPandas (path_to_csv):
    ''' load csv to a pandas data frame:
        input: path to csv file
        output: pandas data frame'''
    try:
        output_df = pd.read_csv(path_to_csv)
    except FileNotFoundError:
        return print("file not found, input the path to the csv file")
    return output_df

def PreAnalyse (input_df, path="python/oc_ data_analyst/project3/report.txt", outlier_range=3):
    ''' return a report with duplicates, NaN, Type, statistic description and outliers
        input: pandas DF
        optional input: path where the report will be saved
        optional input: outlier_range
        output: report in .txt format'''
    # duplicate values
    duplicate = input_df[input_df.duplicated()]
    # NaN values
    null_value = input_df[input_df.isna().any(1)]
    # column types
    column_type = input_df.dtypes
    # DF statistic description
    stat_description = input_df.describe()


    # find outliers
    col_to_process = input_df.describe().columns
    # initialize outliers DF
    outliers = pd.DataFrame()

    for column in col_to_process:

        col_outlier = input_df[column]
        # outlier calculation => |value| > outlier_range * median
        outlier = col_outlier[np.abs(col_outlier) > outlier_range*(col_outlier.median())]
        
        outliers = outliers.append(outlier)
    # clean result
    outliers = outliers.fillna("").swapaxes("index", "columns")


    with open (path, "w") as outfile:
        outfile.write("Basic analyse of the data frame: \n ")

        outfile.write("\n ---Value type by columns--- \n")
        column_type.to_string(outfile)

        outfile.write("\n \n ---Duplicates--- \n")
        duplicate.to_string(outfile)

        outfile.write("\n \n ---NaN values--- \n")
        null_value.to_string(outfile)

        outfile.write("\n \n ---Statistic description--- \n")
        stat_description.to_string(outfile)

        outfile.write("\n \n ---Outliers: ")
        outfile.write(str(outlier_range))
        outfile.write(" times far away from the median--- \n")
        outliers.to_string(outfile)


    return print(f"report located in {path}")



df = CsvToPandas("python/oc_ data_analyst/project3/data/fr_population.csv")


result = PreAnalyse(df)










