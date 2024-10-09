import pandas as pd
import streamlit as st

from utils.update_sheet import SheetConnector


def main():
    st.title('NBA TEAM ADVANCED STAT')
    st.markdown('''
    - 해당 주차 스케줄표입니다.
    - 참고: [URL](https://hashtagbasketball.com/advanced-nba-schedule-grid)
    ''')
    num_games = SheetConnector('SCHEDULE').get_sheet()
    num_games = num_games[num_games['Team'] != 'Team']
    st.dataframe(num_games, width=2000, height=1000)


if __name__ == '__main__':
    main()
