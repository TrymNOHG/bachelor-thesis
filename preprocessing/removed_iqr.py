import pandas as pd
import preprocess as pp

if __name__ == "__main__":
    df = pd.read_csv("./oslo_3_month_aggregated.csv")

    print("Number of rows before removing outliers:", len(df))

    len_before = len(df)

    df = df.loc[(df['scnt'] == 1) & (df['rcnt'] == 1)]

    df = pp.remove_outliers_IQR(df, 'rtt')

    print("Number of rows after removing outliers:", len(df))

    len_after = len(df)

    percent_removed = ((len_before - len_after) / len_before) * 100
    total_removed = (len_before - len_after)
    print(f"Removed {total_removed} or {percent_removed}%") 
