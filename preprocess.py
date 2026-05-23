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
    # Determine seller and buyer for directed edges
    df["seller"] = np.where(df["direction"] == "in", df["club_2"], df["club_1"])
    df["buyer"] = np.where(df["direction"] == "in", df["club_1"], df["club_2"])
    
    # Drop duplicates to prevent double-counting if both clubs reported the transfer
    df_unique = df.drop_duplicates(subset=["player_name", "seller", "buyer"])

    # Group by seller and buyer to get the frequency of transfers
    counts = df_unique.groupby(["seller", "buyer"]).size().reset_index(name="count")
    
    # Rename for output compatibility
    counts = counts.rename(columns={"seller": "club_1", "buyer": "club_2"})

    # Reorder columns nicely
    counts = counts[["club_1", "club_2", "count"]]

    return counts

def main():
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir / "data" / "premier-league.csv"

    df = transformData(pd.read_csv(csv_path))

    counts_df = count_names(df)

    df.to_csv("premier-league-processed.csv", index=False)
    counts_df.to_csv("club_weights.csv", index=False)



if __name__ == "__main__":
    main()