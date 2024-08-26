import pandas as pd
import toml
from typing import TypeVar
PandasDataFrame = TypeVar('pandas.core.frame.DataFrame')

def select_and_rename_cols(
        df: PandasDataFrame,
        cols_to_rename: dict
):
    return df.rename(columns = cols_to_rename)[cols_to_rename.values()]



config = toml.load("./code/config.toml")

filepaths_config = config["filepaths"]
folder_path = filepaths_config["folder_path"]



places_df = pd.read_csv(
    folder_path + filepaths_config["places_filepath"], 
    encoding='latin-1'
)

places_cols = {
    "place22nm": "place_name",
    "splitind": "split",
    "descnm": "place_type",
    "bua22cd": "bua_code",
    "lat": "lat",
    "long": "long"
}

places_df = select_and_rename_cols(places_df, places_cols)

localities = places_df[places_df["place_type"]=="LOC"]
localities = localities.drop(
    columns = ["split", "place_type", "bua_code"]
)




eng_wal_pop_df = pd.read_csv(
    folder_path + filepaths_config["eng_wal_pop_filepath"]
)

eng_wal_pop_cols = {
    "geography": "place_name",
    "Sex: All persons; measures: Value": "population",
}
eng_wal_pop_df = select_and_rename_cols(eng_wal_pop_df, eng_wal_pop_cols)
eng_wal_pop_df["place_name"] = eng_wal_pop_df["place_name"].str[:-4] 

scot_pop_df = pd.read_csv(
    folder_path + filepaths_config["scot_pop_filepath"],
    header = 2
)
scot_pop_df = scot_pop_df[1:-2]

scot_pop_cols = {
    "Settlement Name": "place_name",
    "All Ages": "population",
}

scot_pop_df = select_and_rename_cols(scot_pop_df, scot_pop_cols)

pop_df = pd.concat([eng_wal_pop_df, scot_pop_df], ignore_index=True, sort=False)


merged_df = localities.merge(pop_df, how="inner")

larger_localities  = merged_df[merged_df["population"]>=5000]

print(larger_localities.sort_values(by = "population", ascending=False).head(25))
