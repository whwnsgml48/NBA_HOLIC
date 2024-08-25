import streamlit as st
import pandas as pd


def get_managers():
    team_roaster = pd.read_csv('./data/team_list.csv')
    return team_roaster.drop_duplicates(subset=['MANAGER']).MANAGER.to_list()


managers = get_managers()


def get_team_list(manager):
    team_roaster = pd.read_csv('./data/team_list.csv')
    team_roaster = team_roaster[team_roaster['MANAGER'] == manager]
    return team_roaster


def get_player_list():
    player_list = pd.read_csv('./data/fantasy_stat.csv')
    return player_list.Player.to_list()


def add(manager, player):
    roaster_total = pd.read_csv('./data/team_list.csv')
    added = pd.DataFrame([{'MANAGER': manager,
                           'PLAYER': player}])
    _tmp = roaster_total[(roaster_total.MANAGER == manager) & (roaster_total.PLAYER == player)]
    if _tmp.shape[0] > 0:
        st.error(f'{player} is a player already on your roaster.', icon="🚨")
        return
    else:
        roaster_total = pd.concat([roaster_total, added])
        roaster_total.to_csv('./data/team_list.csv', index=False)
        st.success(f'{player} added !', icon='✅')


def drop(manager, player):
    roaster_total = pd.read_csv('./data/team_list.csv')
    _tmp = roaster_total[(roaster_total.MANAGER == manager) & (roaster_total.PLAYER == player)]
    if _tmp.shape[0] == 0:
        st.error(f'{player} is a player not on your roaster.', icon="🚨")
        return
    else:
        roaster_total = roaster_total[~((roaster_total.MANAGER == manager) & (roaster_total.PLAYER == player))]
        roaster_total.to_csv('./data/team_list.csv', index=False)
        st.success(f'{player} dropped !', icon='✅')


def main():
    global managers
    st.title('ROASTER MANAGEMENT')
    st.markdown('''
    - 로스터 관리 페이지입니다. 
    - 원하는 선수를 검색하여 추가하거나 삭제할 수 있습니다.
    ''')
    st.divider()
    manager = st.selectbox('Select manager', managers)

    with st.form('Add/Drop'):
        player = st.selectbox('select player', get_player_list())
        option = st.radio('add or drop:', ['add', 'drop'])
        submit = st.form_submit_button('submit')

    if option == 'add' and submit:
        add(manager, player)
    if option == 'drop' and submit:
        drop(manager, player)
    roaster = get_team_list(manager)
    st.dataframe(roaster)

    return


if __name__ == '__main__':
    main()
