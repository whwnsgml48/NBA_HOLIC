import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import zscore


def get_managers():
    team_roaster = pd.read_csv('./data/team_list.txt')
    return team_roaster.drop_duplicates(subset=['MANAGER']).MANAGER.to_list()


def get_df():
    roaster = pd.read_csv('./data/team_list.txt')
    roaster.MANAGER = roaster.MANAGER.astype('string')
    roaster.PLAYER = roaster.PLAYER.astype('string')

    fantasy_stat = pd.read_csv('./data/fantasy_stat.csv')
    fantasy_stat.Player = fantasy_stat.Player.astype('string')
    fantasy_stat.Pos = fantasy_stat.Pos.astype('string')
    fantasy_stat.Tm = fantasy_stat.Tm.astype('string')
    roaster['Player'] = roaster['PLAYER']
    roaster = roaster[['Player', 'MANAGER']]
    df = roaster.join(fantasy_stat.set_index('Player'), how='left', on='Player')
    return df


def plot_radial(df, manager):
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
    manager = st.multiselect('select manager:',
                             get_managers())
    df_avg = df.groupby('MANAGER').agg({
        'FG%': 'mean',
        '3PTS': 'mean',
        'FT%': 'mean',
        'PTS': 'mean',
        'REB': 'mean',
        'AST': 'mean',
        'STL': 'mean',
        'BLK': 'mean',
        'TOV': 'mean'
    })
    plot_radial(df_avg, manager)
    st.markdown('''
    ''')
    st.dataframe(df_avg, width=1000, height=470)


if __name__ == '__main__':
    main()
