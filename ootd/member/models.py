from django.db import models

# Create your models here.
# python manage.py makemigrations
# python manage.py migrate

class Member(models.Model):
    mem_id = models.CharField(max_length=20, primary_key=True) # id
    nick = models.CharField(max_length=20) # nick
    pw = models.CharField(max_length=20) # 비밀번호
    email = models.CharField(max_length=100) # 이메일
    tel = models.CharField(max_length=20) # 전화번호
    gender = models.IntegerField(default=0) # 성별
    birth = models.DateField() # 생년월일
    picture = models.CharField(max_length=200) # 회원 사진
    
    def __str__(self):
        return self.mem_id+":"+self.nick+":"+self.pw
    