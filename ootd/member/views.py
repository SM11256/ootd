from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Member
from django.contrib import auth # 로그아웃
from django.db.models import Q
from konlpy.tag import Kkma
import speech_recognition as sr
import datetime as dt

kkma = Kkma()
word_list=list()
index_list=list()
alnum_list = list()
junk_index_list = list()
junk_list = list()

# member/views.py
# Create your views here.

# record.html 연결, 마이크 녹음 후 문자열로 변환 기능
def record(request) :
    
    if request.method != 'POST' :
        context = {'msg':'음성녹음 시작!','url':'../record/'}
        return render(request, 'confirm.html', context)
    else :
        r = sr.Recognizer()
        with sr.Microphone() as source :
            audio = r.listen(source)
        try :
            mic_to_text = r.recognize_google(audio, language='ko-KR')
        except : 
            context = {"msg":"잘못된 입력입니다. 다시 말씀해주세요.", "url":"../../"}
            return render(request, "alert.html", context)
        print(mic_to_text)
        return processing(request, mic_to_text)
# 변환된 문자열 처리
def processing(request, mic_to_text) :
    if request.method == 'POST' :
        kkma = Kkma()
        print(kkma.nouns(mic_to_text))
        word_list=[]
        index_list=[]
        alnum_list =[]
        junk_index_list =[]
        junk_list =[]
        oplace=""
        month=""
        date=""
        year="2022"
        min_date = dt.datetime(2022, 3, 1)
        max_date = dt.datetime(2022, 4, 30)
        
        for item in kkma.nouns(mic_to_text) :
            word_list.append(item)
    
        i = 1
        for item in word_list :
            if item.isalnum() and not item.isalpha() :
                if item.isalnum() and not item.isnumeric() :
                    print(i, item, "true")
                    index_list.append(i-1)
                    i+=1
                else :
                    print(i, item, "junk")
                    junk_index_list.append(i-1)
                    i+=1
            else :
                print(i, item, "false")
                i+=1
                
        try :
            for item in index_list :
                alnum_list.append(word_list[item])
            for item in junk_index_list :
                junk_list.append(word_list[item])
            for item in junk_list :
                word_list.remove(item)
            for item in alnum_list :
                word_list.remove(item)
        except : 
            context = {"msg":"잘못된 입력입니다. 다시 말씀해주세요.", "url":"../../"}
            return render(request, "alert.html", context)


        place_list = {
            "윤종로 벚꽃길(서울 영등포구 여의도동)":'seoul',
            "해운대 달맞이길(부산 해운대 달맞이길 190":'busan',
            "수성못 (대구 수성구 두산동)":'daegu',
            "한라 수목원 (제주 제주시 수목원길 72)":'jeju',
            "거북선 공원 (전남 여수시 거북선공원2길 10)":'yeosu',
            "전주 덕진 공원 (전북 전주시 덕진구 권삼득로 390 전주덕진공원)":'jeonju',
            "무심천 (충북 청주시 상당구 남일면 신송리)":'cheongju',
            "보문산 (대전 중구 대사동)":'daejeon',
            "인천대공원 (인천 남동구 장수동)":'incheon'}

        for item in alnum_list:
            if item.endswith("년") :
                year = int(item.strip("년"))
            elif item.endswith("월") :
                month = int(item.strip("월"))
            elif item.endswith("일") :
                date = int(item.strip("일"))
        
        for word in word_list :
            for place in place_list :
                if (word != '벚꽃' and word != '공원' and len(word) > 1 and (word in place)) :
                    oplace = place
                    break
        if oplace == "" :
            oplace ="목적지 미설정"
            context = {"msg":"장소 정보 오류입니다. 다시 말씀해주세요.", "url":"../../"}
            return render(request, "alert.html", context)    
  
        if year != '' and (int(year) > 2022 or int(year) < 2022) :
            year = "2022"    
        if month != '' and (int(month) < 10) :
            month = "0"+str(month)
        if date != '' and (int(date) < 10) :
            date= "0"+str(date)    
    
        if month == '' and date == '' :
            odate = '날짜 입력 오류'
            context = {"msg":"날짜 입력 오류입니다. 다시 말씀해주세요.", "url":"../../"}
            return render(request, "alert.html", context)
        else : 
            d = dt.datetime(int(year), int(month), int(date))
            if d < min_date or d > max_date :
                odate = '날짜 입력 오류'
                context = {"msg":"범위 바깥의 날짜입니다. 다시 말씀해주세요.", "url":"../../"}
                return render(request, "alert.html", context)
                

        odate = str(year)+"-"+str(month)+"-"+str(date)
        oplace = place_list.get(oplace)
        try :
           login = request.session["login"]  #세션정보. 로그인 정보 
        except :
           login = ""  #로그인 정보가 없는 경우 login=빈문자열 저장
           
        if login != "" : #로그인 된경우
            member = Member.objects.get(mem_id=login) #id에 해당하는 회원 정보
            return render(request, 'member/result.html', {"odate":odate, "oplace":oplace, "mem":member})
        else :
            member = Member.objects.get(mem_id='admin')
            return render(request, 'member/result.html', {"odate":odate, "oplace":oplace, "mem":member}) 
    
# /member/login 화면, 유효성검사, 로그인기능-아이디,비밀번호 정보 확인
def login(request):
    if request.method != 'POST' : 
        return render(request,'member/login.html')
    else :
        inputID = request.POST['mem_id'] # 입력받은 아이디
        inputPW = request.POST['pw'] # 입력받은 비밀번호
               
        try :
            member = Member.objects.get(mem_id= inputID) # member 테이블에 입력받은 아이디가 존재 할 경우
            if member.pw == inputPW: # member 테이블에 저장된 비밀번호와 입력받은 비밀번호가 같다면
                session_id = request.session.session_key
                request.session['login'] = inputID  #session 객체에 로그인 정보 저장
                return HttpResponseRedirect('../../') #redirect 설정
            else : # member테이블에 저장 된 아이디와 비밀번호가 일치 하지 않을 경우
                context = {'msg':'비밀번호를 정확히 입력해 주세요.'}
                return render(request,'member/login.html',context)
        except : # member 테이블에 입력받은 아이디가 존재 하지 않을 경우
                context = {'msg':'아이디를 확인하세요.'}
                return render(request,'member/login.html',context)

# agreement.html연결 
def agreement(request):
    return render(request,'member/agreement.html')

# join.html연결, 회원가입기능, 유효성검사
def join(request):
    if request.method != 'POST' :
        return render(request, 'member/join.html')
    else : 
        context = {}
        try : 
            member = Member.objects.get(mem_id=request.POST['mem_id'])
            if member.mem_id == request.POST['mem_id']: # 중복아이디
                context = {'msg':'이미 존재하는 아이디입니다.'}
                return render(request,'#',context)
        except : 
            if request.POST['mem_id'] == "":
                context['id_error'] = '아이디를 입력하세요!'
            if request.POST['pw'] == "" or len(request.POST['pw']) < 4:
                context['pass_error'] = '비밀번호는 4자리 이상 입력해주세요!'
            if request.POST['pwChck'] !=  request.POST['pw']:
                context['pwChck_error'] = '비밀번호와 비밀번호확인 값이 같지 않습니다!'
            if request.POST['nick'] == "":
                context['name_error'] = '별명은 필수입력입니다!'
            if request.POST['tel'] == "":
                context['tel_error'] = '전화번호는 필수입력입니다!'
            if request.POST['email'] == "":
                context['email_error'] = '이메일은 필수입력입니다!'
            if request.POST['birth'] == "":
                context['birth_error'] = '생년월일은 필수입력입니다!'
            if not context: 
                member = Member(mem_id=request.POST['mem_id'],\
                                pw=request.POST['pw'],\
                                nick=request.POST['nick'],\
                                gender=request.POST['gender'],\
                                tel=request.POST['tel'],\
                                email=request.POST['email'],\
                                picture=request.POST['picture'], \
                                birth=request.POST['birth'])
                member.save() # member 객체를 통해서 데이터베이스에 insert됨
                return HttpResponseRedirect("../login/")
            else :
                return render(request, '.', context)

# 로그아웃 기능
def logout(request) :    
    auth.logout(request) 
    return HttpResponseRedirect("../login/")

# main.html연결, 로그인상태확인
def main(request):
    return render(request, 'member/main.html')

# info.html연결, 가입정보조회기능, 관리자나 본인 외 가입정보조회불가 기능
def info(request,mem_id):  #id : apple 아이디정보
    try:
        login = request.session["login"] #세션정보 : 로그인 정보
    except:
        login = "" #로그인 정보가 없는 경우 login=빈문자열저장
    
    if login !="": #로그인이 된 경우(login != 빈문자열)
        if login == mem_id or login =='admin': #로그인된아이디가 조회하려는 mem_id이거나 admin일 경우
            member = Member.objects.get(mem_id=mem_id) #id에 해당하는 회원 정보
            return render(request, 'member/info.html',{"mem":member})
        else: #다른 사용자 정보조회 할 경우
            context = {"msg":"본인 정보만 조회가능합니다.","url":"../../main"}
            return render(request, 'alert.html', context)
    else: #로그아웃상태
        context = {"msg":"로그인하세요.","url":"../../login"}
        return render(request, 'alert.html', context)


# update.html연결, 로그인상태확인, 본인외 가입정보수정불가 기능
def update(request,mem_id):  
    try :
        login = request.session["login"] #세션정보 : 로그인 정보
    except :
        login = "" #로그인 정보가 없는 경우 login=빈문자열저장
        
    if login !="": #로그인이 된 경우(login != 빈문자열)
        if login == mem_id or login =='admin': #로그인된아이디가 수정하려는 mem_id이거나 admin일 경우
            return update_rtn(request,mem_id)
        else: #다른 사용자 정보조회 할 경우
            context = {"msg": "본인 정보만 수정가능합니다.", "url": "../../info/"+login+"/"}
            return render(request, 'alert.html', context)
    else : #로그아웃상태
        context = {"msg": "로그인 하세요.", "url": "../../login/"}
        return render(request, 'alert.html', context)

# update_rtn연결, 비밀번호검증 후 회원정보수정기능
def update_rtn(request,mem_id) :    
    if request.method != 'POST':
        member = Member.objects.get(mem_id=mem_id) #id에 해당하는 회원 정보
        return render(request, 'member/update.html', {"mem": member})
    else :   #POST 방식인 경우
        member = Member.objects.get(mem_id=mem_id) #id에 해당하는 회원 정보
        if member.pw == request.POST['pw'] :
           member = Member(mem_id=request.POST['mem_id'],
                                pw=request.POST['pw'],\
                                nick=request.POST['nick'],\
                                gender=request.POST['gender'],\
                                tel=request.POST['tel'],\
                                email=request.POST['email'],\
                                picture=request.POST['picture'], \
                                birth=request.POST['birth'])                                 
           member.save() # 기본키가 존재하면 update
           return HttpResponseRedirect("../../info/"+mem_id+"/") 
        else: #다른 사용자 정보조회 할 경우
            context = {"msg": "수정실패 : 비밀번호를 확인하세요.", "url": "../../update/"+mem_id+"/"}
            return render(request, 'alert.html', context)

# pwupdate.html연결, 로그인상태확인, 본인외 비밀번호수정불가 기능
def pwupdate(request,mem_id) :   
    try :
        login = request.session["login"] #세션정보 : 로그인 정보
    except :
        login = "" #로그인 정보가 없는 경우 login=빈문자열저장
        
    if login !="": #로그인이 된 경우(login != 빈문자열)
        if login == mem_id: #로그인된아이디가 조회하려는 mem_id일 경우
            return pwupdate_rtn(request,mem_id)
        else: #다른 사용자 정보조회 할 경우
            context = {"msg": "본인 정보만 수정가능합니다.", "url": "../../info/"+login+"/"}
            return render(request, 'alert.html', context)
    else : #로그아웃상태
        context = {"msg": "로그인 하세요.", "url": "../../login/"}
        return render(request, 'alert.html', context)

# pwupdate_rtn연결, 기존비밀번호검증 후 비밀번호수정기능
def pwupdate_rtn(request,mem_id) :    
    if request.method != 'POST':
        member = Member.objects.get(mem_id=mem_id) #id에 해당하는 회원 정보
        return render(request, 'member/pwupdate.html', {"mem": member})
    else :   #POST 방식인 경우
        member = Member.objects.get(mem_id=mem_id) #id에 해당하는 회원 정보
        if member.pw == request.POST['pw'] :
            member.pw = request.POST['chgpass']
            member.save() #기존내용+변경비밀번호 db에 저장
            context = {"msg": "비밀번호 수정이 완료 되었습니다.",\
                       "url": "../../info/" + mem_id + "/"}
            return render(request, 'alert.html', context)
        else :
           context = {"msg": "수정실패 : 비밀번호를 확인하세요.", "url": "../../pwupdate/"+mem_id+"/"}
           return render(request, 'alert.html', context)


# delete.html연결, 로그인상태확인, 본인외 회원탈퇴불가 기능
def delete(request,mem_id) :   
    try :
        login = request.session["login"] #세션정보 : 로그인 정보
    except :
        login = "" #로그인 정보가 없는 경우 login=빈문자열저장
        
    if login !="": #로그인이 된 경우(login != 빈문자열)
        if login == mem_id : #로그인된아이디가 조회하려는 mem_id일 경우
            if login != 'admin':
                return delete_rtn(request,mem_id)
            else: # 관리자 로그인 일 경우
                context = {"msg": "관리자는 탈퇴 할 수 없습니다.", "url": "../../info/"+login+"/"}
                return render(request, 'alert.html', context)
        else: #다른 사용자 정보조회 할 경우
            context = {"msg": "본인만 탈퇴 가능합니다.", "url": "../../info/"+login+"/"}
            return render(request, 'alert.html', context)
    else : #로그아웃상태
        context = {"msg": "로그인 하세요.", "url": "../../login/"}
        return render(request, 'alert.html', context)

# delete_rtn연결, 비밀번호검증 후 회원탈퇴기능
def delete_rtn(request,mem_id) :    
    if request.method != 'POST':
        member = Member.objects.get(mem_id=mem_id) #id에 해당하는 회원 정보
        return render(request, 'member/delete.html', {"mem": member})
    else :   #POST 방식인 경우
        member = Member.objects.get(mem_id=mem_id) #id에 해당하는 회원 정보
        if member.pw == request.POST['pw'] :
            member.delete() #member에 해당하는 내용 delete
            auth.logout(request) #로그아웃
            context = {"msg": "회원님 탈퇴처리가 완료 되었습니다.", "url": "../../login/"}
            return render(request, 'alert.html', context)
        else: #다른 사용자 정보조회 할 경우
            context = {"msg": "탈퇴실패 : 비밀번호를 확인하세요.", "url": "../../info/"+mem_id+"/"}
            return render(request, 'alert.html', context)

# list.html연결, 모든 회원정보 조회, 관리자외 조회불가 기능
def list(request) :
    try :
        login = request.session["login"] #세션정보 : 로그인 정보
    except :
        login = "" #로그인 정보가 없는 경우 login=빈문자열저장
        
    if login !="": #로그인이 된 경우(login != 빈문자열)
        if login == 'admin': #관리자 로그인 일 경우
            member = Member.objects.all()
            return render(request, 'member/list.html', {"mlist": member})
        else: #관리자 로그인이 아닐 경우
            context = {"msg": "관리자만 조회 가능 합니다.", "url": "../../"}
            return render(request, 'alert.html', context)
    else: #로그아웃상태
        context = {"msg": "로그인 하세요.", "url": "../login/"}
        return render(request, 'alert.html', context)        
              
# admindelete.html연결, 관리자외 강제탈퇴 불가
def admindelete(request,mem_id) :   
    try :
        login = request.session["login"] #세션정보 : 로그인 정보
    except :
        login = "" #로그인 정보가 없는 경우 login=빈문자열저장
        
    if login !="": #로그인이 된 경우(login != 빈문자열)
        if login == 'admin' : #로그인된아이디가 조회하려는 admin일 경우
            return admindelete_rtn(request,mem_id)
        else: #다른 사용자 정보조회 할 경우
            context = {"msg": "관리자만 강제탈퇴 가능합니다.", "url": "../../list/"}
            return render(request, 'alert.html', context)
    else : #로그아웃상태
        context = {"msg": "로그인 하세요.", "url": "../../login/"}
        return render(request, 'alert.html', context)

# admindelete_rtn연결, 비밀번호검증 후 회원탈퇴기능
def admindelete_rtn(request,mem_id) :    
    if request.method != 'POST':
        member = Member.objects.get(mem_id=mem_id) #id에 해당하는 회원 정보
        return render(request, 'member/admindelete.html', {"mem": member})
    
    else :   #POST 방식인 경우
        admin = Member.objects.get(mem_id='admin')
        member = Member.objects.get(mem_id=mem_id) #id에 해당하는 회원 정보   
        if member.mem_id == 'admin': #강제탈퇴 대상이 관리자 일 경우
            context = {"msg": "관리자는 강제탈퇴 할 수 없습니다.", "url": "../../list/"}
            return render(request, 'alert.html', context)
        if admin.pw == request.POST['adminpw'] :
            member.delete() #member에 해당하는 내용 delete
            context = {"msg": "강제탈퇴처리가 완료 되었습니다.", "url": "../../list/"}
            return render(request, 'alert.html', context)
        else: #다른 사용자 정보조회 할 경우
            context = {"msg": "탈퇴실패 : 비밀번호를 확인하세요.", "url": "../../list/"}
            return render(request, 'alert.html', context) 
 
# 파일 업로드
# BASE_DIR\file\picture 폴더 생성하기
def picture(request):
    if request.method != 'POST' :
        return render(request, 'member/pictureform.html')
    else :
        # request.FILES['picture'] : 파일의 내용
        fname = request.FILES['picture'].name # 파일 이름
        handle_upload(request.FILES['picture'])
        return render(request, 'member/picture.html', {'fname':fname})

# 파일 저장
def handle_upload(f):
    with open("file/picture/" + f.name, 'wb+') as destination:
        for ch in f.chunks():
            destination.write(ch)


# 검새결과화면
def result(request):
   if request.method != 'POST' :
       return render(request, 'member/result.html')
   else:
       odate = request.POST['ootd-date']
       oplace = request.POST['ootd-place'] #pass 파라미터
       try :
          login = request.session["login"]  #세션정보. 로그인 정보 
       except :
          login = ""  #로그인 정보가 없는 경우 login=빈문자열 저장
       if login != "" : #로그인 된경우
           member = Member.objects.get(mem_id=login) #id에 해당하는 회원 정보
           return render(request, 'member/result.html', {"odate":odate, "oplace":oplace, "mem":member})
       else :
           member = Member.objects.get(mem_id='admin')
           return render(request, 'member/result.html', {"odate":odate, "oplace":oplace, "mem":member})


#아이디, 비밀번호 찾기 - 모달창      
def tolist_id(rsBoard): # queryset to list
    rslist = []
    for record in rsBoard:
        lst = str(record.mem_id)
        rslist.append(lst)
    return rslist

def idsearch(request):
    if request.method != 'POST' :
        return render(request,'member/idsearch.html')
    else :
        try :
            m_email = request.POST['email']
            m_tel = request.POST['tel'] 
            m_birth = request.POST['birth']
            member = Member.objects.filter(Q(email=m_email) & Q(tel=m_tel) & Q(birth=m_birth))
            mem_list = tolist_id(member)
            try :
                m_msg = '회원님의 아이디는 ' + mem_list[0] + '입니다.'
                return render(request, 'member/login.html', {'m_msg':m_msg})
            except :
                context = {'m_msg':'해당 정보의 회원이 없습니다.'}
                return render(request, 'member/login.html', context)
        except :
            context = {"msg": "값을 전부 입력해주세요!", "url": "../login/"}
            return render(request, 'alert.html', context)

def tolist_pw(rsBoard): # queryset to list
    rslist = []
    for record in rsBoard:
        lst = str(record.pw)
        rslist.append(lst)
    return rslist

def pwsearch(request):
    if request.method != 'POST' :
        return render(request,'member/pwsearch.html')
    else :
        try :
            m_id = request.POST['mem_id']
            m_tel = request.POST['tel'] 
            m_email = request.POST['email']
            member = Member.objects.filter(Q(email=m_email) & Q(tel=m_tel) & Q(mem_id=m_id))
            mem_list = tolist_pw(member)
            try :
                m_msg = '회원님의 비밀번호는 ' + mem_list[0] + '입니다.'
                return render(request, 'member/login.html', {'m_msg':m_msg})
            except :
                context = {'m_msg':'해당 정보의 회원이 없습니다.'}
                return render(request, 'member/login.html', context)
        except :
            context = {"msg": "값을 전부 입력해주세요!", "url": "../login/"}
            return render(request, 'alert.html', context)
'''

#아이디, 비밀번호 찾기 
def tolist_id(rsBoard): # queryset to list
    rslist = []
    for record in rsBoard:
        lst = str(record.mem_id)
        rslist.append(lst)
    return rslist

def idsearch(request):
    if request.method != 'POST' :
        return render(request,'member/idsearch.html')
    else :
        try:
            m_email = request.POST['email']
            m_tel = request.POST['tel'] 
            m_birth = request.POST['birth']
            member = Member.objects.filter(Q(email=m_email) & Q(tel=m_tel) & Q(birth=m_birth))
            mem_list = tolist_id(member)
            
            #유효성검사
            if not(m_email and m_tel and m_birth):
                context = {"msg": "값을 전부 입력해주세요!", "url": "."}
                return render(request, 'alert.html', context)
            else:
                try :
                    context = {"msg": '회원님의 아이디는 ' + mem_list[0] + '입니다.'}
                    return render(request, 'alert_close.html', context)
                except :
                    context = {"msg": "해당 정보의 회원이 없습니다.", "url": "."}
                    return render(request, 'alert.html', context)
        except :
            context = {"msg": "값을 전부 입력해주세요!", "url": "."}
            return render(request, 'alert.html', context)


def tolist_pw(rsBoard): # queryset to list
    rslist = []
    for record in rsBoard:
        lst = str(record.pw)
        rslist.append(lst)
    return rslist

def pwsearch(request):
    if request.method != 'POST' :
        return render(request,'member/pwsearch.html')
    else :
        try :
            m_id = request.POST['mem_id']
            m_tel = request.POST['tel'] 
            m_email = request.POST['email']
            member = Member.objects.filter(Q(email=m_email) & Q(tel=m_tel) & Q(mem_id=m_id))
            mem_list = tolist_pw(member)
            
            #유효성검사
            if not(m_id and m_tel and m_email):
                context = {"msg": "값을 전부 입력해주세요!", "url": "."}
                return render(request, 'alert.html', context)
            try :
                context = {"msg": '회원님의 비밀번호는 ' + mem_list[0] + '입니다.'}
                return render(request, 'alert_close.html', context)

            except :
                context = {"msg": "해당 정보의 회원이 없습니다.", "url": "."}
                return render(request, 'alert.html', context)
        except :
            context = {"msg": "값을 전부 입력해주세요!", "url": "."}
            return render(request, 'alert.html', context)
'''

