from django.db import models

# Create your models here.
# python manage.py makemigrations
# python manage.py migrate

class Clothes(models.Model):
    c_id = models.AutoField(primary_key=True) # id
    gender = models.IntegerField(default=0) # 성별(0:무관, 1:남자, 2:여자)
    age = models.IntegerField(default=0) # 나이(0:무관, 1:청소년, 2:청년, 3:중장년)
    temp = models.IntegerField(default=0) # 온도(1:~2, 2:3~5, 3:6~)
    kind = models.IntegerField(default=0) # 종류(0:무관, 1:상의, 2:하의, 3:신발)
    state = models.IntegerField(default=0) # 상태(0:로그아웃, 1:로그인)
    c_pic = models.CharField(max_length=200) # 옷 사진
    
    def __str__(self):
        return self.c_id+":"+self.gender+":"+self.age+":"+self.temp+":"+self.kind