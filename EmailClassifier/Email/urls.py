from django.urls import path
from . import views
from .views import user_logout

urlpatterns = [
    # path('login/', views.user_login, name='login'),
    path('email/', views.index, name='index'),
    path('logout/', views.user_logout, name='logout'),
    path('email-details/<str:subject>/', views.email_details, name='email-details'),
]