import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.request import urlopen


from utils.conf import BR_TO_YFB_STATS_NAME_MAP, ALPHABET, N_PLAYERS_WITH_TOP_MPG
from utils.update_sheet import SheetConnector

def get_date():
    now = datetime.now()
    return now.strftime('%Y-%m-%d')


class BasketballReference:
    def __init__(self):
        self.year = 2024
        self.raw_stat = None
        self.fantasy_stat = None
        self.team_advanced_stat = None
        self.reference_url = "https://www.basketball-reference.com/leagues/NBA_{}_totals.html".format(self.year)
        self.advanced_stat = "https://www.basketball-reference.com/leagues/NBA_{}.html".format(self.year)

    def get_raw_stats(self):
        html = urlopen(self.reference_url)
        soup = BeautifulSoup(html, 'lxml')
        headers = [th.get_text() for th in soup.find_all('tr', limit=2)[0].find_all('th')]
        headers = headers[1:]
        rows = soup.find_all('tr')[1:]
        player_stats = [[td.get_text() for td in rows[i].find_all('td')] for i in range(len(rows))]

        __stats_table = pd.DataFrame(player_stats, columns=headers)
        __stats_table = __stats_table.dropna()

        # Replace player's team with the last team if the player played for more than a team in a season, then drop the duplicated data
        # Note on basketball reference for a player with multiple row , the first row is stats with team "TOT", and the last row is stats with current team
        for name in __stats_table[__stats_table["Player"].duplicated()]["Player"].drop_duplicates():
            num_teams = len(__stats_table[__stats_table["Player"] == name])
            current_team = __stats_table.loc[__stats_table["Player"] == name, "Team"].iloc[num_teams - 1]
            __stats_table.loc[__stats_table["Player"] == name, "Team"] = current_team
        __stats_table.drop_duplicates(subset="Player", inplace=True)

        #__stats_table["Player"] = __stats_table["Player"].apply(lambda x: formalize_name(x))
        __stats_table.set_index("Player", inplace=True)

        # rename table header with Yahoo fantasy basketball stats name, type cast cells to float
        __stats_table = __stats_table.replace("", 0)
        for key, value in BR_TO_YFB_STATS_NAME_MAP.items():
            __stats_table = __stats_table.rename(columns={key: value})
            __stats_table[value] = __stats_table[value].apply(lambda x: float(x))

        # filter players based on MPG
        __stats_table["MPG"] = __stats_table["MIN"] / __stats_table["GP"]
        __stats_table = __stats_table.sort_values(by=['MPG'], ascending=False)
        __stats_table = __stats_table.head(N_PLAYERS_WITH_TOP_MPG)
        # __stats_table = __stats_table.sort_index()
        __stats_table['Player'] = __stats_table.index

        self.raw_stat = __stats_table

    def get_advanced_stat(self):
        html = urlopen(self.advanced_stat)
        soup = BeautifulSoup(html, 'lxml')
        test = soup.find_all(id='all_advanced_team')[0]

        #over_headers = [th.get_text() for th in test.find_all('tr', limit=2)[0].find_all('th')]
        headers = [th.get_text() for th in test.find_all('tr', limit=2)[1].find_all('th')]
        rows = test.find_all('tr')[2:-1]
        team_stats = [[td.get_text() for td in rows[i].find_all('td')] for i in range(len(rows))]

        headers[18] = 'OF-eFG%'
        headers[19] = 'OF-TOV%'
        headers[20] = 'OF-ORB%'
        headers[21] = 'OF-FT/FGA'

        headers[23] = 'DF-eFG%'
        headers[24] = 'DF-TOV%'
        headers[25] = 'DF-ORB%'
        headers[26] = 'DF-FT/FGA'
        headers = headers[1:]

        __team_stat = pd.DataFrame(team_stats, columns=headers)
        self.team_advanced_stat = __team_stat[['Team', 'Age', 'W', 'L', 'PW', 'PL', 'MOV', 'SOS', 'SRS', 'ORtg', 'DRtg', 'NRtg', 'Pace', 'FTr', '3PAr',
        'TS%', 'OF-eFG%', 'OF-TOV%', 'OF-ORB%', 'OF-FT/FGA', 'DF-eFG%', 'DF-TOV%', 'DF-ORB%', 'DF-FT/FGA', 'Arena', 'Attend.', 'Attend./G']]

    def preprocess_stats(self):
        # raw stats to fantasy stats
        fantasy_stat = self.raw_stat
        fantasy_stat['Player'] = fantasy_stat.index
        fantasy_stat['FG%'] = fantasy_stat['FG%'] * 100
        fantasy_stat['3PTS'] = fantasy_stat['3PTM'] / fantasy_stat['GP']
        fantasy_stat['FT%'] = fantasy_stat['FT%'] * 100
        fantasy_stat['PTS'] = fantasy_stat['PTS'] / fantasy_stat['GP']
        fantasy_stat['REB'] = fantasy_stat['REB'] / fantasy_stat['GP']
        fantasy_stat['AST'] = fantasy_stat['AST'] / fantasy_stat['GP']
        fantasy_stat['STL'] = fantasy_stat['ST'] / fantasy_stat['GP']
        fantasy_stat['BLK'] = fantasy_stat['BLK'] / fantasy_stat['GP']
        fantasy_stat['TOV'] = fantasy_stat['TO'] / fantasy_stat['GP']
        self.fantasy_stat = fantasy_stat[['Player', 'FG%', '3PTS', 'FT%', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'Pos', 'Team', 'GP', 'MPG']]

    def cal_custom_stats(self):
        return

    def save_stats(self, is_history=False):
        # save stat to data
        cols = ['Player'] + [i for i in self.raw_stat.columns.tolist() if i not in ('Player', 'STL', 'TOV', '3PTS')]
        SheetConnector('RAW STATS').update_sheet(self.raw_stat[cols])
        SheetConnector('TEAM STATS').update_sheet(self.team_advanced_stat)
        SheetConnector('FANTASY STATS').update_sheet(self.fantasy_stat)
        return

    def run(self):
        self.get_raw_stats()
        self.preprocess_stats()
        self.get_advanced_stat()
        self.save_stats()
        return


if __name__ == '__main__':
    t = BasketballReference()
    t.get_advanced_stat()
