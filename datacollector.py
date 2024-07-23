import mlbstatsapi
import pandas as pd

mlb = mlbstatsapi.Mlb()

# Function to get all game IDs for the 2023 season
def get_all_game_ids(year):
    schedule = mlb.get_schedule(start_date=f'{year}-04-01', end_date=f'{year}-10-01')
    
    # Extracting game IDs from the schedule object
    game_ids = []
    for date_info in schedule.dates:
        for game in date_info.games:
            game_ids.append(game.gamepk)  # Use the correct attribute for the game ID
    return game_ids

# Function to extract play-by-play data for a given game ID
def get_game_data(game_id):
    playbyplay = mlb.get_game_play_by_play(game_id)
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
                    'Velocity': event.pitchdata.startspeed if event.pitchdata else None,
                    'SpinRate': event.pitchdata.breaks.spinrate if event.pitchdata else None,
                    'ReleasePoint': event.pitchdata.extension if event.pitchdata else None,
                    'Outcome': event.details.description if event.details else None
                })
    return game_data

# Function to save data to a CSV file
def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

# Main script to get data for the 2023 season and save to a CSV file
def main():
    game_ids = get_all_game_ids(2023)
    all_game_data = []

    for game_id in game_ids:
        game_data = get_game_data(game_id)
        all_game_data.extend(game_data)

    #save_to_csv(all_game_data, 'historical_pitch_data_2023.csv')
    print(all_game_data)

if __name__ == "__main__":
    main()

