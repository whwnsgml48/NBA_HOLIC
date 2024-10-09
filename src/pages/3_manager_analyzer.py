import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import zscore

from utils.update_sheet import SheetConnector


def get_num_games():
    num_games = SheetConnector('SCHEDULE').get_sheet()[['Team', 'Games']].dropna(how='any')
    num_games = num_games[num_games['Team'] != 'Team']
    team_map = pd.DataFrame(
        {'Team': ['Atlanta Hawks', 'Boston Celtics', 'Brooklyn Nets', 'Charlotte Hornets', 'Chicago Bulls', 'Cleveland Cavaliers',
                  'Dallas Mavericks', 'Denver Nuggets', 'Detroit Pistons', 'Golden State Warriors', 'Houston Rockets', 'Indiana Pacers',
                  'Los Angeles Clippers', 'Los Angeles Lakers', 'Memphis Grizzlies', 'Miami Heat', 'Milwaukee Bucks', 'Minnesota Timberwolves',
                  'New Orleans Pelicans', 'New York Knicks', 'Oklahoma City Thunder', 'Orlando Magic', 'Philadelphia 76ers', 'Phoenix Suns',
                  'Portland Trail Blazers', 'Sacramento Kings', 'San Antonio Spurs', 'Toronto Raptors', 'Utah Jazz', 'Washington Wizards'],
         'Team_code': ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
         }
    )

    num_games = num_games.set_index('Team').join(team_map.set_index('Team'), how='inner', on='Team')

    return num_games[['Games', 'Team_code']]


def get_managers():
    team_roaster = SheetConnector('ROASTER').get_sheet().dropna(how='any')
    return team_roaster.drop_duplicates(subset=['MANAGER']).MANAGER.to_list()


def get_df():
    roaster = SheetConnector('ROASTER').get_sheet().dropna(how='any')
    roaster.MANAGER = roaster.MANAGER.astype('string')
    roaster.PLAYER = roaster.PLAYER.astype('string')

    fantasy_stat = SheetConnector('FANTASY STATS').get_sheet()
    fantasy_stat.Player = fantasy_stat.Player.astype('string')
    fantasy_stat.Pos = fantasy_stat.Pos.astype('string')
    fantasy_stat.Team = fantasy_stat.Team.astype('string')
    fantasy_stat.TOV = -fantasy_stat.TOV
    roaster['Player'] = roaster['PLAYER']
    roaster = roaster[['Player', 'MANAGER']]
    df = roaster.join(fantasy_stat.set_index('Player'), how='left', on='Player')
    return df


def plot_radial(df, manager):
    print(df)
    df = df.apply(zscore)
    if len(manager) > 0:
        df = df.loc[manager]
    fig = px.line_polar(df.melt(ignore_index=False).reset_index(),
                        r='value', theta='variable', color='MANAGER',
                        line_close=True,
                        color_discrete_sequence=px.colors.qualitative.G10)
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.title('MANAGER ANALYZER')
    st.markdown('''
    - 매니저별 강/약점 스탯을 체크합니다.
    ''')
    st.divider()
    df = get_df()
    reflect_games = st.toggle('Reflection of number of games')
    if reflect_games:
        num_games = get_num_games()
        df = df.merge(num_games, how='inner', left_on='Team', right_on='Team_code')
        df['3PTS'] = df['3PTS'] * df.Games
        df['3PTS'] = df['3PTS'].astype('float64')
        df.PTS = df.PTS * df.Games.astype('float64')
        df.REB = df.REB * df.Games.astype('float64')
        df.AST = df.AST * df.Games.astype('float64')
        df.STL = df.STL * df.Games.astype('float64')
        df.BLK = df.BLK * df.Games.astype('float64')
        df.TOV = df.TOV * df.Games.astype('float64')

    manager = st.multiselect('select manager:',
                             get_managers())
    df_avg = df.groupby('MANAGER').agg({
        'FG%': 'mean',
        '3PTS': 'sum',
        'FT%': 'mean',
        'PTS': 'sum',
        'REB': 'sum',
        'AST': 'sum',
        'STL': 'sum',
        'BLK': 'sum',
        'TOV': 'sum'
    })

    plot_radial(df_avg, manager)
    st.markdown('''
    ''')
    st.dataframe(df_avg, width=1000, height=470)


if __name__ == '__main__':
    main()
