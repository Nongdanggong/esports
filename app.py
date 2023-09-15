import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import requests
from io import BytesIO
from bs4 import BeautifulSoup as bs
import json
import os

# 이미지 로드
def img_load(url, width):
    response = requests.get(url)
    if response.status_code == 200:  # HTTP 상태 코드 200은 요청이 성공했음을 나타냅니다.
        image = Image.open(BytesIO(response.content))
        st.image(image, width=width)

df = pd.read_csv('one_champ_2.csv', encoding='euc-kr')
df_champ_list = df.columns

# fow 장인랭킹
URL = 'https://fow.kr/champranking#86,30,cmd,p,S13B'

rq = requests.get(URL)
soup = bs(rq.content, 'html.parser')

# 챔피언 number 가져오기
champ_one = soup.find_all('li', 'champ_one')

champ_cno = []
champ_name = []

for i in champ_one:
    champ_cno.append(i['cno'])
    champ_name.append(i['tipsy'])
    if i['cno'] == '120':
        break



# 제목
st.title(':blue[장인.GG]')
st.write('장인.GG는 fow.kr 기준 챔프별 :rainbow[**장인들의 데이터**]를 반영합니다. ')

#### LP 상승률
st.divider()

st.header('7일간 LP 상승률 TOP5 챔피언 :sunglasses:')

st.write('이번주 *꿀챔프*는?  ' )
# st.subheader('LP 상승률 TOP5')

# 대상 디렉토리 지정
target_directory = "json"

# 디렉토리의 모든 파일과 폴더 리스트 가져오기
all_files_and_dirs = os.listdir(target_directory)

# 파일만 필터링하여 리스트 만들기
files_only = [f for f in all_files_and_dirs if os.path.isfile(os.path.join(target_directory, f))]

# C1, G1, M1, // D1, D2, D3, D4, E1, E2, E3, E4, P1, P2, P3, P4
score_adj = { 'S4' : -800, 'S3' : -700, 'S2' : -600, 'S1' : -500,
            'G4' : -400, 'G3' : -300, 'G2' : -200, 'G1' : -100, 'P4' : 0, 'P3' : 100, 'P2' : 200, 'P1' : 300, 'E4' : 400, 'E3' : 500, 'E2' : 600,
             'E1' : 700, 'D4' : 800, 'D3' : 900, 'D2' : 1000, 'D1' : 1100, 'M1' : 1200, 'G1' : 1200, 'C1' : 1200}

diff = []
chart_data = {}

# 파일 리스트 출력
for file in files_only:
    print(file)
    # 7일간의 정보 저장
    name = file.split('.')[0]
    chart_data[name] = [0, 0, 0, 0, 0, 0, 0, 0]

    with open('json/' + file, 'r') as json_file:
        champ_json = json.load(json_file)
        # 장인 별로
        for idx in champ_json.keys():
            print(idx)
            for t, v in enumerate(champ_json[idx]['tier_score'][:-1]):
                # 오류로 크롤링 실패
                if v == "":
                    break

                tier, score = v.split(' - ')
                score = int(score)
                score += score_adj[tier]

                n_tier, n_score = champ_json[idx]['tier_score'][t+1].split(' - ')
                n_score = int(n_score)
                n_score += score_adj[n_tier]

                chart_data[name][t] += n_score - score

        # 장인 수 만큼 나눠주기
        if len(champ_json.keys()) != 0:
            chart_data[name] = [x / len(champ_json.keys()) for x in chart_data[name]]

        diff.append(sum(chart_data[name]))

print(diff)
print(chart_data)

sorted_items = sorted(chart_data.items(), key=lambda diff: diff[1], reverse=True)
diff.sort(reverse=True)

# 상위 3개의 항목만 선택하여 새로운 딕셔너리 생성
top_n_items = dict(sorted_items[:5])
diff = diff[:5]

print(top_n_items)

chart_data = pd.DataFrame(
    top_n_items,    
    columns=top_n_items.keys(),
)

st.line_chart(chart_data)

col1, col2, col3 = st.columns([2.5, 0.1, 1.5])
with col1:
    st.dataframe(chart_data)
with col2:
    pass
with col3:
    for idx, v in enumerate(top_n_items.keys()):
        st.write(str(idx+1) + '위: :blue[**' + v + '**] | ' + str(int(diff[idx])) + 'LP 상승')







st.divider()



#####################


st.header('챔프별 상대법 :magic_wand:')
st.write('장인들은 *카운터*를 상대로 어떤 빌드를 사용할까?' )

# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

if "option_1" not in st.session_state: st.session_state.option_1 = '가렌'
if "option_2" not in st.session_state: st.session_state.option_2 = '가렌'
if "option_2" not in st.session_state: st.session_state.option_3 = '가렌'

if "update_1" not in st.session_state: st.session_state.update_1 = True
if "update_2" not in st.session_state: st.session_state.update_2 = True

col1, col2, col3 = st.columns([2, 1, 2])
with col1 :
  # column 1 에 담을 내용
  # 가운데정렬
    st.session_state.option_1 = st.selectbox(
        "**:red[상대 챔피언]** 선택",
        tuple(df_champ_list),
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        key='champ_1',
        on_change=lambda: (setattr(st.session_state, 'update_1', True), setattr(st.session_state, 'update_2', False))

    )
    champ_1_url = 'https://z.fow.kr/champ/' + str(champ_cno[champ_name.index(st.session_state.option_1)]) + '_64.png'

    img_load(champ_1_url, 100)
    
with col2 :
    st.markdown(
    """
    <style>
        .centered {
            display: flex;
            justify-content: center;
            align-items: center;
            text-align: center;
            height: 30vh;
        }
    </style>
    <h1 class="centered">
        vs
    </h1>
    """, 
    unsafe_allow_html=True
    
)
with col3 :
    st.session_state.option_2 = st.selectbox(
        "**:blue[내 챔피언]** 선택",
        tuple(df_champ_list),
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        key='champ_2',
        on_change=lambda: (setattr(st.session_state, 'update_1', True), setattr(st.session_state, 'update_2', False))

    )
    
    champ_2_url = 'https://z.fow.kr/champ/' + str(champ_cno[champ_name.index(st.session_state.option_2)]) + '_64.png'

    img_load(champ_2_url, 100)

    
# 챔피언 json 파일로드
# JSON 파일 불러오기
with open('json/' + st.session_state.option_2 + '.json', 'r') as json_file:
    champ_2_json = json.load(json_file)
    # print(champ_2_json.keys())

# 세번째 컨텐츠 이용중일 때 로딩하지 않음
if st.session_state.update_1 == True:
    for i in champ_2_json.keys():
        # 첫번째 챔피언과 맞라인일 때
        for k, v in champ_2_json[i]['matchs'].items():
            if v['enemy']['opposite'] == st.session_state.option_1:
                # print(i, st.session_state.option_1, v)
                # print(v)
                # 장인 이름
                st.subheader(i)
                # 스펠
                st.write('스펠')
                col1, col2, col3 = st.columns([1, 1, 7])
                with col1:
                    img_load(v['spell']['img'][0], 75)
                with col2:
                    img_load(v['spell']['img'][1], 75)
                # 룬 
                st.write('룬')
                col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
                with col1:
                    img_load( 'https:' + v['rune']['key']['img'][1], 100)
                with col2:
                    img_load( 'https:' + v['rune']['key']['img'][2], 75)
                with col3:
                    img_load( 'https:' + v['rune']['key']['img'][3], 75)
                with col4:
                    img_load( 'https:' + v['rune']['key']['img'][4], 75)
                with col5:
                    img_load( 'https:' + v['rune']['second']['img'][1], 75)
                with col6:
                    img_load( 'https:' + v['rune']['second']['img'][2], 75)
                # 아이템
                st.write('아이템')
                col1, col2, col3, col4 = st.columns([1, 1, 1, 4])
                with col1:
                    if len(v['item']['img']) > 0:
                        img_load(v['item']['img'][0], 75)
                with col2:
                    if len(v['item']['img']) > 1:
                        img_load(v['item']['img'][1], 75)
                with col3:
                    if len(v['item']['img']) > 2:
                        img_load(v['item']['img'][2], 75)
                
                col1, col2, col3, col4 = st.columns([1, 1, 1, 4])
                with col1:
                    if len(v['item']['img']) > 3:
                        img_load(v['item']['img'][3], 75)
                with col2:
                    if len(v['item']['img']) > 4:
                        img_load(v['item']['img'][4], 75)
                with col3:
                    if len(v['item']['img']) > 5:
                        img_load(v['item']['img'][5], 75)
                
                st.divider()

                # 한 장인당 한 빌드만
                break

st.divider()

#################

st.header('장인 레시피 :dancer:')
st.write('한번 잡숴봐! 장인들의 :rainbow[독특한] 플레이' )

line_url = {'top' : 'https://i.namu.wiki/i/O_2CMyNl09bgyIrZi4NkOOd6XgFor1gL7CGNpVQylYoR99BhzKmsJ4IHEJflS1VKy0pOClKORm3A9tpAlqI_Mw.svg', 'jug' : 'https://i.namu.wiki/i/55_PrrwhffRxaKUXg4P76uYVOPfP3iRLJX2C2FvrgujYgR259-Gb9JTNaM64bDySkpWvw5-0ai6BEZfhkWOevw.svg',
            'mid' : 'https://i.namu.wiki/i/a4YtZ6YnqKKcxV1pQX26JWGcz8bZK7lholTjn3Fkqc8W2gUyyF0MeZ6Le5B_BYo5wgekVhWY2tkCNiJ_bk-Rzw.svg', 'adc' : 'https://i.namu.wiki/i/cGDoagUcrocScakidJnEvkaAN1JYhoaA9TgIMw1yJHvsKz0w6UWhuiwys64bDOfx7djXcAp5GSGnkD9Y4V_G7w.svg',
            'sup' : 'https://i.namu.wiki/i/6bCkOuVHyCnbjvqYRgMaWKCbi16P0WMh6tbhspZ7-Jp0T1ba_3tsncN7094lq3n7worGfgvC1WrS-EGNzch3_Q.svg'}

st.session_state.option_3 = st.selectbox(
    "챔피언 선택",
    tuple(df_champ_list),
    label_visibility=st.session_state.visibility,
    disabled=st.session_state.disabled,
    key='champ_3',
    on_change=lambda: (setattr(st.session_state, 'update_1', False), setattr(st.session_state, 'update_2', True))

)

champ_1_url = 'https://z.fow.kr/champ/' + str(champ_cno[champ_name.index(st.session_state.option_3)]) + '_64.png'

img_load(champ_1_url, 150)

# 챔피언 json 파일로드
# JSON 파일 불러오기
if st.session_state.update_2 == True:
    with open('json/' + st.session_state.option_3 + '.json', 'r') as json_file:
        champ_3_json = json.load(json_file)

        st.subheader('라인')
        line_cnt = {'top' : 0, 'jug' : 0, 'mid' : 0, 'adc' : 0, 'sup' : 0}
        for i in champ_3_json.keys():
            line_cnt[champ_3_json[i]['line']] += 1

        max_key = max(line_cnt, key=lambda k: line_cnt[k])
        for i in champ_3_json.keys():
            if champ_3_json[i]['line'] != max_key:
                link = 'https://fow.kr/find/' + i.replace(' ', '%20')
                st.write(f"{i}  \t\t({link})")
                # img_load(line_url[champ_3_json[i]['line']], 250)
                st.image(line_url[champ_3_json[i]['line']])


        
        # st.divider()    
        # st.subheader('스펠')
        
        

        st.divider()
        st.subheader('룬')
        rune_cnt = {}
        for i in champ_3_json.keys():
            for j in champ_3_json[i]['matchs'].keys():
                if champ_3_json[i]['matchs'][j]['rune']['key']['name'][1] in rune_cnt:
                    rune_cnt[champ_3_json[i]['matchs'][j]['rune']['key']['name'][1]] += 1
                else:
                    rune_cnt[champ_3_json[i]['matchs'][j]['rune']['key']['name'][1]] = 1

        # 모든 value들을 추출하고 정렬
        values = list(rune_cnt.values())
        values.sort()

        # 상위 30%에 해당하는 임계값 찾기
        threshold_index = int(len(values) * 0.7)
        threshold_value = values[threshold_index]

        filtered_dict = {k: v for k, v in rune_cnt.items() if v < threshold_value}

        # print(rune_cnt)
        # print(filtered_dict)

        # max_key = max(line_cnt, key=lambda k: line_cnt[k])
        for i in champ_3_json.keys():
            for j in champ_3_json[i]['matchs'].keys():
                if champ_3_json[i]['matchs'][j]['rune']['key']['name'][1] in filtered_dict:
                    link = 'https://fow.kr/find/' + i.replace(' ', '%20')
                    st.write(f"{i}  \t\t({link})")
                    # img_load(line_url[champ_3_json[i]['line']], 250)
                    img_load('https:' + champ_3_json[i]['matchs'][j]['rune']['key']['img'][1], 250)
                    break
        
        # st.divider()
        # st.subheader('아이템')
