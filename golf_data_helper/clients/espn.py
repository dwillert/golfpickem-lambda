import requests
import json

class ESPNClient:
    BASE_URL = "https://site.api.espn.com/"
    SCOREBOARD_URL = "apis/site/v2/sports/golf/leaderboard"
    
    @staticmethod
    def get_golf_data(tournament_id="401811940") -> dict:
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
                    "score": int(golfer["statistics"][0]["value"]),
                    "position": int(golfer["status"]["position"]["id"]),
                    "thru": golfer["status"].get("hole", "WD"),
                    "rounds": [
                        {"round": i + 1, "strokes": int(golfer["linescores"][i]["value"]) if i < len(golfer["linescores"]) else 0}
                        for i in range(4)
                    ],
                    "status": golfer["status"]["displayValue"],
                } for golfer in golf_data["competitions"][0]["competitors"]
            ]
        }
        golf_dict["leaderboard"] = sorted(golf_dict["leaderboard"], key=lambda x: x["id"])
        return golf_dict


if __name__ == "__main__":
    espn_client = ESPNClient()
    try:
        data = espn_client.get_golf_data()
        with open("golf_data.json", "w") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"An error occurred: {e}")