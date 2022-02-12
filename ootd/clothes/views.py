from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Clothes
import datetime
from django.db.models import Q
import random
import folium
import pandas as pd
import requests
from bs4 import BeautifulSoup 

# Create your views here.

def upload(request):
    try :
        login = request.session["login"] # 세션정보. 로그인 정보
    except :
        login = "" # 세션에 로그인 정보가 없는 경우, login변수에 빈 문자열 저장
    if login != "" : # 로그인 된 경우
        if login == 'admin' :
            if request.method != 'POST' :
                return render(request, 'clothes/upload.html')
            else : 
                context = {}
                if request.POST['c_pic'] == "":
                    context = {"msg":"사진은 필수입니다!", "url":"../upload/"}
                    return render(request, 'alert.html', context)
                else :
                    clothes = Clothes(gender=request.POST['gender'],\
                                    age=request.POST['age'],\
                                    temp=request.POST['temp'],\
                                    kind=request.POST['kind'],\
                                    state=request.POST['state'],\
                                    c_pic=request.POST['c_pic'])
                    clothes.save() # clothes 객체를 통해서 데이터베이스에 insert됨
                    return HttpResponseRedirect("../list/")
        else : # 다른 사용자의 정보를 조회
            context = {"msg":"관리자만 접근가능합니다.", "url":"../../../member/main/"}
            return render(request, 'alert.html', context)
    else : # 로그아웃 상태
        context = {"msg":"로그인 하세요!", "url":"../../../member/login/"}
        return render(request, 'alert.html', context)

def list(request):
    # 로그인 정보 조회
    try :
        login = request.session["login"] # 세션정보. 로그인 정보
    except :
        login = "" # 세션에 로그인 정보가 없는 경우, login변수에 빈 문자열 저장
    if login != "" : # 로그인 된 경우
        if login == 'admin' : # 관리자인 경우만(관리자로 로그인: 정상상태)
            clothes = Clothes.objects.all()
            return render(request, 'clothes/list.html', {"clist":clothes})
        else : # 관리자가 아닌 경우 = 다른 사용자인 경우
            context = {"msg":"관리자만 조회가능합니다.", "url":"../../../member/main/"}
            return render(request, 'alert.html', context)
    else : # 로그아웃 상태
        context = {"msg":"로그인 하세요!", "url":"../../../member/login/"}
        return render(request, 'alert.html', context)  
    
def update(request, c_id):
    try :
        login = request.session["login"] # 세션정보. 로그인 정보
    except :
        login = "" # 세션에 로그인 정보가 없는 경우, login변수에 빈 문자열 저장
    if login != "" : # 로그인 된 경우
        if login == 'admin' : # 관리자인 경우만
            return update_rtn(request, c_id)
        else : # 관리자가 아닌 경우 = 다른 사용자인 경우
            context = {"msg":"관리자만 접근가능합니다.", "url":"../../../member/main/"}
            return render(request, 'alert.html', context)
    else : # 로그아웃 상태
        context = {"msg":"로그인 하세요!", "url":"../../../member/login/"}
        return render(request, 'alert.html', context)  
   
def update_rtn(request, c_id) :
    if request.method != 'POST' :
        clothes = Clothes.objects.get(c_id=c_id)
        return render(request, 'clothes/update.html', {"clo":clothes})
    else : # POST
        clothes = Clothes.objects.get(c_id=c_id)
        clothes = Clothes(c_id=request.POST['c_id'], gender=request.POST['gender'], age=request.POST['age'], temp=request.POST['temp'],\
                          kind=request.POST['kind'], state=request.POST['state'], c_pic=request.POST['c_pic'])
        clothes.save() # 기본키가 존재하면 update (insert가 아니라!)
        return HttpResponseRedirect("../../list/") # url 정보 복원

def delete(request, c_id):
    try :
        login = request.session["login"] # 세션정보. 로그인 정보
    except :
        login = "" 
    if login != "" : # 로그인 된 경우
        if login == 'admin' : # 관리자인 경우만
            return delete_rtn(request, c_id)
        else : # 관리자가 아닌 경우 = 다른 사용자인 경우
            context = {"msg":"관리자만 접근가능합니다.", "url":"../../../member/main/"}
            return render(request, 'alert.html', context)
    else : # 로그아웃 상태
        context = {"msg":"로그인 하세요!", "url":"../../../member/login/"}
        return render(request, 'alert.html', context) 

def delete_rtn(request, c_id):
    if request.method != 'POST' :
        clothes = Clothes.objects.get(c_id=c_id)
        return render(request, 'clothes/delete.html', {"clo":clothes})
    else : # POST 방식인 경우
        clothes = Clothes.objects.get(c_id=c_id) 
        clothes.delete()
        context = {"msg":"아이템이 삭제되었습니다!", "url":"../../list/"}
        return render(request, 'alert.html', context)

# 파일 업로드
# BASE_DIR\file\picture 폴더 생성하기
def c_pic(request):
    if request.method != 'POST' :
        return render(request, 'clothes/pictureform.html')
    else :
        # request.FILES['c_pic'] : 파일의 내용
        fname = request.FILES['c_pic'].name # 파일 이름
        handle_upload(request.FILES['c_pic'])
        return render(request, 'clothes/picture.html', {'fname':fname})

# 파일 저장
def handle_upload(f):
    with open("file/c_pic/" + f.name, 'wb+') as destination:
        for ch in f.chunks():
            destination.write(ch)
            
def result(request):
   if request.method != 'POST' :
       return render(request, 'clothes/result.html')
   else:
       m_date = request.POST['m_date']
       m_place = request.POST['m_place']
       data = pd.read_csv('file/data/' + m_place + '_2022.csv')
       data = data.loc[data['날짜'] == m_date]
       data = data['체감온도(°C)'].values[0]
       temp = 1 if data <= 2 else 3 if data >= 6 else 2
       data = round(data, 2)
       # 회원/비회원
       try :
           login = request.session["login"]  #세션정보. 로그인 정보 
       except :
           login = ""  #로그인 정보가 없는 경우 login=빈문자열 저장
       if login != "" : #회원인 경우
           m_gender = int(request.POST['m_gender'])
           m_birth = request.POST['m_birth']
           today_year = str(datetime.date.today())[0:4]  # Returns 2018-01-15
           mem_year = str(m_birth)[0:4]
           mem_age = int(today_year) - int(mem_year) + 1
           m_age = 1 if mem_age <= 16 else 3 if mem_age >= 40 else 2
           return pick_clothes(request, m_gender, m_age, temp, m_date, m_place, data, 1)
       else : # 비회원인 경우
           return pick_clothes(request, 0, 0, temp, m_date, m_place, data, 0)
   
def pick_clothes(request, m_gender, m_age, temp, m_date, m_place, data, state):
    top_clo = Clothes.objects.filter(Q(gender=m_gender) & Q(age=m_age) & Q(temp=temp) & Q(state=state) & Q(kind=1))
    bottom_clo = Clothes.objects.filter(Q(gender=m_gender) & Q(age=m_age) & Q(temp=temp) & Q(state=state) & Q(kind=2))
    shoes_clo = Clothes.objects.filter(Q(gender=m_gender) & Q(age=m_age) & Q(temp=temp) & Q(state=state) & Q(kind=3))
    top_list = tolist(top_clo)
    bottom_list = tolist(bottom_clo) 
    shoes_list = tolist(shoes_clo)
    lat_longitude = loc_map(m_place)
    f = folium.Figure(width=900, height=675)
    map_ootd = folium.Map(location=lat_longitude[:2], zoom_start=15, width='100%', height='100%', scrollWheelZoom=False, dragging=False).add_to(f)
    folium.CircleMarker(lat_longitude[:2], radius=90, tooltip=lat_longitude[2], fill_color='#FFC0CB', fill_opacity=0.5, color=None).add_to(map_ootd)
    folium.Marker(lat_longitude[:2], popup=lat_longitude[2], icon=folium.Icon(color='pink',icon='heart',icon_color='#FF1493')).add_to(map_ootd)
    maps = map_ootd._repr_html_()
    
    days = m_date
    src1 = "/file/graph/" + m_place + "/" + days[5:7] + "/" + days[5:] + ".png"
    src2 = "/file/graph/" + m_place + "/" + days[5:7] + ".png"
    
    m_date = m_date.replace('-', '.')
    m_place = lat_longitude[2]
    return render(request, 'clothes/result.html', {"bottom":bottom_list[rNum(len(bottom_list))], \
                                                   "top":top_list[rNum(len(top_list))], \
                                                   "shoes":shoes_list[rNum(len(shoes_list))], \
                                                   "m_date":m_date, "m_place":m_place, "data":data, 'days':days[5:], \
                                                   "src1":src1, "src2":src2, "month":days[6:7], "map_ootd":maps})

def tolist(rsBoard): # queryset to list
    rslist = []
    for record in rsBoard:
        lst = str(record.c_pic)
        rslist.append(lst)
    return rslist
        
def rNum(num): # 랜덤숫자 뽑기
    return random.randint(0, num - 1)
    
def loc_map(m_place):
    if m_place == 'seoul':
        return [37.5324, 126.9203, '윤종로벚꽃길']
    elif m_place == 'busan':
        return [35.1576, 129.1813, '해운대 달맞이길']
    elif m_place == 'daegu':
        return [35.8282, 128.6177, '수성못']
    elif m_place == 'jeju':
        return [33.4702, 126.4932, '한라수목원']
    elif m_place == 'yeosu':
        return [34.7616, 127.6669, '거북선공원']
    elif m_place == 'jeonju':
        return [35.8478, 127.1219, '전주덕진공원']
    elif m_place == 'cheongju':
        return [36.5817, 127.5030, '무심천']
    elif m_place == 'daejeon':
        return [36.3025, 127.4216, '보문산']
    elif m_place == 'incheon':
        return [37.4573, 126.7580, '인천대공원']
   
def festival(request, season):
    lation = {'윤종로벚꽃길':[37.5324, 126.9203, 'seoul'], '해운대 달맞이길':[35.1576, 129.1813, 'busan'], \
              '수성못':[35.8282, 128.6177, 'daegu'], '한라수목원':[33.4702, 126.4932, 'jeju'], \
              '거북선공원':[34.7616, 127.6669, 'yeosu'], '전주덕진공원':[35.8478, 127.1219, 'jeonju'],\
              '무심천':[36.5817, 127.5030, 'cheongju'], '보문산':[36.3025, 127.4216, 'daejeon'], \
              '인천대공원':[37.4573, 126.7580, 'incheon']}
    f = folium.Figure(width=1200, height=1400)
    f_name, f_days = "", ""
    if season == 'spring':
        f_name, f_days = "봄 축제", "(3월 - 4월)"
        map_season = folium.Map([36.0053542, 127.7043419], zoom_start=8, width='100%', height='100%', scrollWheelZoom=False, dragging=False).add_to(f)
        for key in lation:
            html = crawling_weather(lation[key][2])
            iframe = folium.IFrame(html, width=250, height=180)
            popup = folium.Popup(iframe)
            folium.Marker(lation[key][:2], popup=popup, \
                          icon=folium.Icon(color='pink',icon='heart',icon_color='#FF1493')).add_to(map_season)
            maps = map_season._repr_html_()
        return render(request, 'clothes/festival.html', {"map_season":maps, "f_name":f_name, "f_days":f_days})
    else :
       context = {"msg":"아직 준비 중 입니다.", "url":"../../../"}
       return render(request, 'alert.html', context)
    
def crawling_weather(place):
    url = "https://www.weather.go.kr/weather/observation/currentweather.jsp"
    html = requests.get(url).text 
    soup = BeautifulSoup(html, "html.parser") 
    table = soup("table", "table_develop3")[0]
    table_rows = table.find_all("tr") 
    table_headers = table_rows[:2] 
    table_data = table_rows[2:] 
    table_data_elements = [x.find_all("td") for x in table_data] 
    data = [] 
    for elem in table_data_elements: 
        if len(elem) > 0: 
            data.append([x.text for x in elem]) 
    df = pd.DataFrame(data) 
    header_text0 = [x.text for x in table_headers[0].find_all("th")] 
    header_text1 = [x.text for x in table_headers[1].find_all("th")] 
    header = [header_text0[0].replace('\r\n\t\t', '')] + header_text1 
    df.columns = header 
    df.set_index('지점', inplace=True)
    df = df.loc[['서울','인천','대구','대전','부산','제주','여수','전주','청주']]
    df.columns = df.columns.str.strip()
    df = df[['현재일기', '현재기온', '체감온도', '습도%']]
    df.rename(index={'서울': 'seoul', '인천':'incheon','대구':'daegu','대전':'daejeon','부산':'busan',\
                     '제주':'jeju','여수':'yeosu','전주':'jeonju','청주':'cheongju'}, inplace=True)
    days = df.loc[place, '현재일기']
    temp = df.loc[place, '현재기온']
    p_temp = df.loc[place, '체감온도']
    humidity = df.loc[place, '습도%']
    html = '''<style>
                @font-face { font-family: 'ONE-Mobile-POP'; 
                src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_2105_2@1.0/ONE-Mobile-POP.woff') format('woff'); 
                font-weight: normal; 
                font-style: normal;}
              </style><body style="font-size: 1.8rem; font-family: 'ONE-Mobile-POP'; color:gray;"><p>'''
    if days == '구름많음':
        html += '⛅ '
    elif days == '구름조금':
        html += '🌤️ '
    elif days == '맑음':
        html += '🌞 '
    elif days.find('눈') != -1:
        html += '⛄ '
    elif days == '흐림':
        html += '☁️ '
    elif days.find('비') != -1:
        html += '🌧️ '
    elif days == '연무' or days == '박무' or days.find('안개') != -1:
        html += '🌫️ '
    else :
        html += '👷‍♂️ '
    html = html + days + "</p><p style='font-size: 1rem; color:Tomato;'>현재기온 " + temp + "°</p><p style='font-size: 1rem;'>체감기온 " \
        + p_temp + "°</p><p style='font-size: 1rem; color:SteelBlue;'>습도 " + humidity + "%</p></body>"
    return html
   
    