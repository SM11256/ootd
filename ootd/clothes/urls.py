# -*- coding: utf-8 -*-
"""
Created on Sun Jan 23 18:17:25 2022

@author: GaYoung
"""
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.list, name='list'), # cldthes/list/ 요청
    path('c_pic/', views.c_pic, name='c_pic'), # clothes/c_pic/ 요청
    path('upload/', views.upload, name='upload'), # clothes/upload/ 요청
    path('update/<str:c_id>/', views.update, name='update'), # clothes/update/아이디값/ 요청 
    path('delete/<str:c_id>/', views.delete, name='delete'), # clothes/delete/아이디값/ 요청 
    path('result/', views.result, name='result'),
    path('festival/<str:season>/', views.festival, name='festival'),
]

