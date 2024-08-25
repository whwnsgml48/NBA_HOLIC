import datetime
import streamlit as st
from streamlit_modal import Modal

from utils.update_data import BasketballReference

modal = Modal(key='Demo Key', title='UPDATE DATA')

updated_at = None


def get_date():
    now = datetime.datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S')


def set_update_date():
    f = open('./update_time.txt', 'w')
    f.write(f'{get_date()}')
    f.close()
    return


def get_update_date():
    f = open('./update_time.txt', 'r')
    line = f.readline()
    f.close()
    return line


def main():
    global updated_at
    updated_at = get_update_date()
    st.set_page_config(layout='wide')
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
    global updated_at
    sideb = st.sidebar
    refresh_btn = sideb.button('UPDATE STAT')
    if refresh_btn:
        with modal.container():
            with st.spinner('Wait for it ..'):
                stat_updator = BasketballReference()
                stat_updator.run()
                set_update_date()
                updated_at = get_update_date()
            st.success('updated!!')


if __name__ == '__main__':
    main()
    sidebar()
