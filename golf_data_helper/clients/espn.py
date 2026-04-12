"""ESPNClient class responsible for fetching golf tournament data from the ESPN API."""
import requests
import json

class ESPNClient:
    BASE_URL = "https://site.api.espn.com/"
    SCOREBOARD_URL = "apis/site/v2/sports/golf/leaderboard"

    @staticmethod
    def _get_status(status: dict) -> str:
        # print(status)
        if status["type"]["name"] == "STATUS_SCHEDULED":
            return status["detail"][:-3]
        elif status["type"]["name"] == "STATUS_FINISH":
            return "F"
        elif status["type"]["name"] == "STATUS_IN_PROGRESS":
            if "hole" in status:
                if status["hole"] == 18:
                    return "F"
                return status["hole"]
        # elif status.get("playoff") is not None:
        #     return "Playoff"
        else:
            return "WD"



    @staticmethod
    def get_golf_data(tournament_id: str = "401811941") -> dict:
        """
        Fetches golf tournament data from the ESPN API for a given tournament ID.
        
        Args:
            tournament_id (str): The ID of the golf tournament to fetch data for.
        
        Returns:
            dict: A dictionary containing tournament details and leaderboard information.
        """
        url = f"{ESPNClient.BASE_URL}{ESPNClient.SCOREBOARD_URL}"
        response = requests.get(url, params={"league": "pga", "event": tournament_id, "limit": "1000"})
        if not response.status_code == 200:
            raise Exception(f"Error fetching data: {response.status_code} - {response.text}")

        golf_data = response.json()["events"][0]
        # print(golf_data["name"])
        # print(golf_data["defendingChampion"])
        golf_dict = {
            "tournament": {
                "name": golf_data["name"],
                "course": golf_data["courses"][0]["name"],
                "location": f'{golf_data["courses"][0]["address"]["city"]}, {golf_data["courses"][0]["address"]["country"]}',
                "cut_score": golf_data["tournament"]["cutScore"],
                "status": golf_data["status"]["type"]["name"],
                # "total_yards": golf_data["courses"][0]["totalYards"],
                # "shots_to_par": golf_data["courses"][0]["shotsToPar"],
                # "defending_champion": golf_data["defendingChampion"]["athlete"]["displayName"] if golf_data["defendingChampion"] else "N/A",
                # "weather": {
                #     "temperature": golf_data["courses"][0]["weather"]["temperature"],
                #     "description": golf_data["courses"][0]["weather"]["displayValue"],
                #     "wind_speed": golf_data["courses"][0]["weather"]["windSpeed"]
                # }
            },
            "leaderboard": [
                {
                    "id": golfer["sortOrder"],
                    "name": golfer["athlete"]["displayName"],
                    "country": golfer["athlete"]["flag"]["alt"],
                    "score": int(golfer["statistics"][0].get("value", 0)),
                    "position": int(golfer["status"]["position"]["id"]),
                    "thru": ESPNClient._get_status(golfer["status"]),
                    "rounds": [
                        {"round": i + 1, "strokes": int(golfer["linescores"][i].get("value", 0)) if i < len(golfer["linescores"]) else 0}
                        for i in range(4)
                    ],
                    "status": golfer["status"]["displayValue"],
                } for golfer in golf_data["competitions"][0]["competitors"]
            ]
        }
        golf_dict["leaderboard"] = sorted(golf_dict["leaderboard"], key=lambda x: x["id"])
        return golf_dict


if __name__ == "__main__":
    try:
        data = ESPNClient.get_golf_data()
        with open("golf_data.json", "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"An error occurred: {e}")