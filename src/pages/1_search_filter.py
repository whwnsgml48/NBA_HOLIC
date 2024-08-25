import pandas as pd
import streamlit as st
from pandas.api.types import is_categorical_dtype, is_numeric_dtype, is_object_dtype, is_datetime64_any_dtype
import plotly.figure_factory as ff


def show_histogram(df):
    show_dist = st.toggle('show distribution')
    cols = ['GP', 'MPG', 'FG%', '3PTS', 'FT%', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']
    if show_dist:
        col = st.selectbox('select stat', cols, placeholder='select stat')
        fig = ff.create_distplot([df[col].to_list()], group_labels=[f'{col}'])
        return fig


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    modify = st.toggle("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


def main():
    st.title('SEARCH FILTER')
    st.markdown('''
    - 선수 검색 페이지입니다. 
    - 판타지에서 사용하는 스탯 기준으로 선수를 검색 가능합니다.
    ''')

    df = pd.read_csv('./data/fantasy_stat.csv')
    df.Pos = df.Pos.astype('category')
    df.Player = df.Player.astype('string')
    df_manager = pd.read_csv('./data/team_list.csv')
    df_manager['Player'] = df_manager.PLAYER
    df_manager.Player = df_manager.Player.astype('string')

    df = df.join(df_manager[['MANAGER', 'Player']].set_index('Player'), how='left', on='Player')
    df.MANAGER = df.MANAGER.fillna('FA')
    df.MANAGER = df.MANAGER.astype('string')
    df.Tm = df.Tm.astype('string')

    st.divider()
    fig = show_histogram(df)
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(filter_dataframe(df[['MANAGER', 'Player', 'Pos', 'Tm', 'GP', 'MPG', 'FG%', '3PTS', 'FT%', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV']]), width=1000, height=1000)


if __name__ == '__main__':
    main()
