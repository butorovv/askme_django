from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from app import views

urlpatterns = [
    path('', views.new_questions, name = 'new_questions'),
    path('hot/', views.hot_questions, name = 'hot_questions'),
    path('tag/<str:tag_name>/', views.tag, name = 'tag'),
    path('question/<int:question_id>/', views.question, name = 'question'),
    path('ask/', views.ask, name = 'ask'),
    path('signup/', views.signup, name = 'signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('settings/', views.settings, name='settings'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)