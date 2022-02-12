# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 20:02:50 2022

@author: SMKIM
"""

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('agreement/', views.agreement, name='agreement'),
    path('join/', views.join, name='join'),
    path('picture/', views.picture, name='picture'), # member/picture/ 요청
    path('main/', views.main,name='main'),
    path('logout/', views.logout,name='logout'), 
    path('info/<str:mem_id>/', views.info, name='info'), # /member/info/apple/ #mem_id : apple 
    path('update/<str:mem_id>/', views.update, name='update'), # /member/update/apple/ #가입정보수정
    path('pwupdate/<str:mem_id>/', views.pwupdate, name='pwupdate'), # /member/pwupdate/apple/ #비밀번호수정
    path('delete/<str:mem_id>/', views.delete, name='delete'), # /member/delete/apple/ #회원탈퇴
    path('list/', views.list,name='list'), # /member/list/ #관리자 회원관리
    path('admindelete/<str:mem_id>/', views.admindelete, name='admindelete'), # /member/admindelete/apple/ #관리자 회원강제탈퇴
    path('result/', views.result, name='result'),
    path('idsearch/', views.idsearch, name='idsearch'),
    path('pwsearch/', views.pwsearch, name='pwsearch'),
    path('record/', views.record, name='record'),
]
