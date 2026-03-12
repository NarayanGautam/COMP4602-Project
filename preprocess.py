import pandas as pd
from pathlib import Path
import numpy as np

def transformData(df: pd.DataFrame) -> pd.DataFrame:
    # dropping irrelevant columns
    df.drop(["age", "position", "fee", "transfer_period", "league_name", "year", "season"], 
            axis=1, inplace=True)

    # rename column
    df.rename(columns={
        "fee_cleaned": "fee", 
        "transfer_movement": "direction", 
        "club_name":"club_1", 
        "club_involved_name":"club_2"
    }, inplace=True)

    # replacing NA with randomized values
    df.replace("NA", np.nan, inplace=True)

    for col in df.columns:
        mask = df[col].isna()
        df.loc[mask, col] = np.round(
            np.random.uniform(1, 80, size=mask.sum()), 2   # 2 decimal places
        )

    return df

def count_names(df: pd.DataFrame) -> pd.DataFrame:
    counts = (
        pd.concat([df["club_1"], df["club_2"]])  # combine both columns
        .value_counts()
        .reset_index()
    )

    counts.columns = ["name", "weight"]

    return counts

def main():
    base_dir = Path(__file__).resolve().parent.parent

    csv_path = base_dir / "comp4602finalproject" / "data" / "premier-league.csv"

    df = transformData(pd.read_csv(csv_path))

    counts_df = count_names(df)

    df.to_csv("premier-league-processed.csv", index=False)
    counts_df.to_csv("club_weights.csv", index=False)



if __name__ == "__main__":
    main()