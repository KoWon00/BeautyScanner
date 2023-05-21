from django.urls import path
from .import views

urlpatterns = [
    path('upload_image/', views.upload_image, name='upload_image'),
    path('', views.index, name='index'),
    path('chat/', views.chat, name='chat'),
]
