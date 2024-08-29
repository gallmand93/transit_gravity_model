import pandas as pd
import toml
import itertools
from math import radians, sin, cos, sqrt, atan2
from typing import TypeVar
PandasDataFrame = TypeVar('pandas.core.frame.DataFrame')

def select_and_rename_cols(
        df: PandasDataFrame,
        cols_to_rename: dict
):
    return df.rename(columns = cols_to_rename)[cols_to_rename.values()]

# Haversine formula to calculate the distance between two points (latitude and longitude)
def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Radius of Earth in kilometers (mean radius)
    R = 6371.0
    distance = R * c
    return distance

config = toml.load("./code/config.toml")

filepaths_config = config["filepaths"]
folder_path = filepaths_config["folder_path"]



places_df = pd.read_csv(
    folder_path + filepaths_config["places_filepath"], 
    encoding='latin-1'
)

places_df["long_place_name"] = places_df["place22nm"] + ", " + places_df["ctyhistnm"]

places_cols = {
    "long_place_name": "place_name",
    "splitind": "split",
    "descnm": "place_type",
    "bua22cd": "bua_code",
    "lat": "lat",
    "long": "long"
}
print(places_df[places_df["place22nm"].str.contains("Bournemouth")])

places_df = select_and_rename_cols(places_df, places_cols)

localities = places_df[places_df["place_type"]=="LOC"]

localities = localities.drop(
    columns = ["split", "place_type", "bua_code"]
)

location_mapper = pd.read_csv(
    folder_path + filepaths_config["mappers_filepath"]
)
location_mapper = dict(
    zip(location_mapper["IPN"], location_mapper["BUA"])
)
print(location_mapper)




# Rename cities using the mapper
localities["place_name"] = localities["place_name"].replace(location_mapper)


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
merged_df = merged_df.drop_duplicates()

city_pairs = list(itertools.combinations(merged_df["place_name"], 2))

# Calculate distances for all pairs
distances = []
for (city1, city2) in city_pairs:
    # Get the coordinates for each city
    lat1, lon1 = merged_df.loc[merged_df['place_name'] == city1, ['lat', 'long']].values[0]
    lat2, lon2 = merged_df.loc[merged_df['place_name'] == city2, ['lat', 'long']].values[0]
        
    # Get the population for each city
    pop1 = merged_df.loc[merged_df['place_name'] == city1, 'population'].values[0]
    pop2 = merged_df.loc[merged_df['place_name'] == city2, 'population'].values[0]

    # Calculate the distance using the Haversine formula
    distance = haversine(lat1, lon1, lat2, lon2)
    distances.append((city1, city2, distance, pop1, pop2))

# Create a new DataFrame with the results
df_distances = pd.DataFrame(distances, columns=['city_1', 'city_2', "distance", "population_1", "population_2"])

df_distances["gravitational_force"] = df_distances["population_1"] * df_distances["population_2"] / (df_distances["distance"])**2

print(df_distances.sort_values(by = "gravitational_force", ascending=False).head(50))