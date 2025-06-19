import os
import time
import pandas as pd
from geopy.geocoders import Nominatim
from shapely.geometry import Point


stations = [
    (209, "IJmond"),
    (210, "Valkenburg Zh"),
    (215, "Voorschoten"),
    (225, "IJmuiden"),
    (235, "De Kooy"),
    (240, "Schiphol"),
    (242, "Vlieland"),
    (248, "Wijdenes"),
    (249, "Berkhout"),
    (251, "Hoorn Terschelling"),
    (257, "Wijk aan Zee"),
    (258, "Houtribdijk"),
    (260, "De Bilt"),
    (267, "Stavoren"),
    (269, "Lelystad"),
    (270, "Leeuwarden"),
    (273, "Marknesse"),
    (275, "Deelen"),
    (277, "Lauwersoog"),
    (278, "Heino"),
    (279, "Hoogeveen"),
    (280, "Eelde"),
    (283, "Hupsel"),
    (285, "Huibertgat"),
    (286, "Nieuw Beerta"),
    (290, "Twenthe"),
    (308, "Cadzand"),
    (310, "Vlissingen"),
    (311, "Hoofdplaat"),
    (312, "Oosterschelde"),
    (313, "Vlakte van De Raan"),
    (315, "Hansweert"),
    (316, "Schaar"),
    (319, "Westdorpe"),
    (323, "Wilhelminadorp"),
    (324, "Stavenisse"),
    (330, "Hoek van Holland"),
    (331, "Tholen"),
    (340, "Woensdrecht"),
    (343, "Rotterdam Geulhaven"),
    (344, "Rotterdam"),
    (348, "Cabauw Mast"),
    (350, "Gilze-Rijen"),
    (356, "Herwijnen"),
    (370, "Eindhoven"),
    (375, "Volkel"),
    (377, "Ell"),
    (380, "Maastricht"),
    (391, "Arcen"),
    (392, "Horst")
]

geolocator = Nominatim(user_agent="knmi_station_locator")
station_data = []

for code, name in stations:
    try:
        location = geolocator.geocode(f"{name}, Netherlands", timeout=10)
        if location:
            station_data.append({
                "station_id": code,
                "station_name": name,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "geometry": Point(location.longitude, location.latitude)
            })
        else:
            station_data.append({
                "station_id": code,
                "station_name": name,
                "latitude": None,
                "longitude": None,
                "geometry": None
            })
    except Exception as e:
        station_data.append({
            "station_id": code,
            "station_name": name,
            "latitude": None,
            "longitude": None,
            "geometry": None
        })
    time.sleep(1)


type_of_data = "meteorological_stations_locations.csv"
current_dir = os.getcwd()
csv_path = os.path.join(current_dir, 'data/clean/environment', type_of_data)

df = pd.DataFrame(station_data)
df.to_csv(csv_path, index=False)
