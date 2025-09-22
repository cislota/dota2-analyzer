#api client

import requests

OPENDOTA_API = "https://api.opendota.com/api"

def get_recent_matches(account_id: int, count: int = 20):
    #Последние матчи игрока
    #account_id: ID игрока
    #count: количество матчей (max. 20)
    #return: список матчей в формате JSON
    
    url = f"{OPENDOTA_API}/players/{account_id}/recentMatches"
    response = requests.get(url, params={"limit": count})
    response.raise_for_status()
    return response.json()

#test connection 

if __name__ == "__main__":

    try:
        test_id = 1149785629  #тест id 
        data = get_recent_matches(test_id, count=3)
        print("Пример данных:")
        for match in data:
            print(match.keys())  #ключи, чтобы понять структуру
            print(f"Match ID: {match['match_id']}, Hero ID: {match['hero_id']}, Duration: {match['duration']}s")
    except Exception as e:
        print(f"Не удалось получить данные: {e}")