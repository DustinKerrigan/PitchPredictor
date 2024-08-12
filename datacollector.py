import mlbstatsapi
import pandas as pd
import time
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

mlb = mlbstatsapi.Mlb()

def get_all_game_ids(year):
    schedule = mlb.get_schedule(start_date=f'{year}-04-01', end_date=f'{year}-10-01')
    game_ids = []
    for date_info in schedule.dates:
        for game in date_info.games:
            game_ids.append(game.gamepk)  
    return game_ids

def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

def get_game_data(game_id):
    session = requests_retry_session()
    playbyplay = None
    #retry logic for the MLB API call
    for _ in range(3):
        try:
            playbyplay = mlb.get_game_play_by_play(game_id, session=session)
            break  
        except requests.exceptions.RequestException as e:
            print(f"Request failed for game ID {game_id}, retrying... Error: {e}")
            time.sleep(2)  #give some time before retrying
    if playbyplay is None:
        print(f"Failed to retrieve data for game ID {game_id} after multiple attempts.")
        return []
    game_data = []
    for play in playbyplay.allplays:
        for event in play.playevents:
            if event.ispitch:
                runners_on = ', '.join([runner.movement.end if runner.movement.end else 'Unknown' for runner in play.runners]) if play.runners else 'None'
                game_data.append({
                    'GameID': game_id,
                    'PitcherName': play.matchup.pitcher.fullname,
                    'BatterName': play.matchup.batter.fullname,
                    'Count': f"{event.count.balls}-{event.count.strikes}",
                    'Inning': play.about.halfinning,
                    'Outs': play.count.outs,
                    'RunnersOn': runners_on,
                    'PitchType': event.details.type.description if event.details and event.details.type else None,
                    'Outcome': event.details.description if event.details else None
                })
    return game_data

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def main():
    game_ids = get_all_game_ids(2023)
    all_game_data = []
    for count, game_id in enumerate(game_ids, start=1):
        game_data = get_game_data(game_id)
        all_game_data.extend(game_data) 
        #log progress every 50 games
        if count % 50 == 0:
            print(f"Processed {count} games out of {len(game_ids)}")
            # sleep to prevent hitting the rate limit
            time.sleep(1)
    print("Data collection complete.")
    save_to_csv(all_game_data, 'historical_test_2023.csv')
    print(all_game_data)

if __name__ == "__main__":
    main()

