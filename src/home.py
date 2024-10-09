import datetime
import streamlit as st
import pandas as pd
from streamlit_modal import Modal

from utils.update_data import BasketballReference
from utils.update_sheet import SheetConnector

modal = Modal(key='Demo Key', title='UPDATE DATA')
st.set_page_config(layout='wide')
updated_at = None
conn = SheetConnector("updated_at")


def get_date():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')


def update_update_date(conn):
    conn.update_sheet(pd.DataFrame({
        'updated_at': [get_date()]
    }))
    return


def get_latest_update_date(conn):
    latest_updated_time = conn.get_sheet()
    latest_updated_time = latest_updated_time['updated_at'].dropna().tail(1)
    return latest_updated_time.values[0]


def main():

    global conn
    updated_at = get_latest_update_date(conn)
    st.subheader('NBA FANTASY LEAGUE')
    st.title('NBAHOLIC')
    st.markdown(f'''
    - NBA 판타지 리그 참가자를 위해 제작한 페이지입니다. 
    - 추가하고 싶은 기능, 버그 발견시 연락 부탁드립니다.
    
    
    📈 스탯 업데이트 날짜: {updated_at} ([url](https://www.basketball-reference.com/leagues/NBA_2025_totals.html))
    ''')
    st.divider()
    st.markdown('''
    **페이지 설명**
    1) search filter: 선수 검색 페이지
    2) roaster management: 로스터 관리 페이지
    3) manager analyzer: 매니저 전력 분석 페이지
    4) **(WIP)** score lab: 커스텀 지표 개발 페이지
    ''')


def sidebar():
    global conn
    sideb = st.sidebar
    refresh_btn = sideb.button('UPDATE STAT')
    if refresh_btn:
        with modal.container():
            with st.spinner('Wait for it ..'):
                stat_updator = BasketballReference()
                stat_updator.run()
                update_update_date(conn)
                #updated_at = get_update_date()
            st.success('updated!!')


if __name__ == '__main__':
    main()
    sidebar()
