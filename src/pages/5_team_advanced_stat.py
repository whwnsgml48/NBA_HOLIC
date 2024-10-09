import pandas as pd
import streamlit as st

from utils.update_sheet import SheetConnector


def main():
    st.title('NBA TEAM ADVANCED STAT')
    st.markdown('''
    - 팀관련 스탯 페이지입니다.
    - 참고: [URL](https://www.basketball-reference.com/leagues/NBA_2024_totals.html)
    ''')
    team_stat = SheetConnector('TEAM STATS').get_sheet().dropna(how='all')#pd.read_csv('./data/team_advanced_stat.csv')
    st.dataframe(team_stat, width=2000, height=1000)


if __name__ == '__main__':
    main()
