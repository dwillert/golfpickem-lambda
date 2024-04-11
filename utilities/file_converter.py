import json
import csv

def csv_to_json():
    player_list = []
    with open(file="datafiles/golf_picks.csv", mode="r") as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader):
            pick_data =  {
                "id": index + 1,
                "name": row["Name"],
                "tiebreaker": row["Tiebreaker"],
                "score": 0,
                "penalty": 0,
                "golfers": [
                    {
                    "id": 1,
                    "name": row["Golfer 1"]
                    },
                    {
                    "id": 2,
                    "name": row["Golfer 2"]
                    },
                    {
                    "id": 3,
                    "name": row["Golfer 3"]
                    },
                    {
                    "id": 4,
                    "name": row["Golfer 4"]
                    },
                    {
                    "id": 5,
                    "name": row["Golfer 5"]
                    },
                    {
                    "id": 6,
                    "name": row["Golfer 6"]
                    }
                ]
            }
            player_list.append(pick_data)
    f.close()
    with open(file="./datafiles/picks_data.json", mode="w+", encoding="utf-8") as jf:
        json.dump(player_list, jf, indent=4)
    jf.close()

if __name__ == "__main__":
    csv_to_json()
