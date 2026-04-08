"""ESPNClient class responsible for fetching golf tournament data from the ESPN API."""
import requests
import json

from datetime import datetime
from zoneinfo import ZoneInfo

class ESPNClient:
    BASE_URL = "https://site.api.espn.com/"
    SCOREBOARD_URL = "apis/site/v2/sports/golf/leaderboard"

    @staticmethod
    def _get_status(status: dict) -> str:
        if "hole" in status:
            return status["hole"]
        elif status["type"]["name"] == "STATUS_SCHEDULED":
            return status["detail"][:-3]
        elif status["playoff"]:
            return "Playoff"
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
        golf_dict = {
            "tournament": {
                "name": golf_data["name"],
                "course": golf_data["courses"][0]["name"],
                "location": f'{golf_data["courses"][0]["address"]["city"]}, {golf_data["courses"][0]["address"]["country"]}',
                "cut_score": golf_data["tournament"]["cutScore"],
                "status": golf_data["status"]["type"]["name"]
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
        print(golf_data["competitions"][0]["competitors"][-1])
        return golf_dict


if __name__ == "__main__":
    try:
        data = ESPNClient.get_golf_data()
        with open("golf_data.json", "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"An error occurred: {e}")