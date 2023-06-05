from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import SignupView

app_name="reservations"

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name='login.html'), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name="logout"),
    path("regist/", views.register, name="regist"),
    path("read/<int:board_id>/", views.read, name="read"),
    path("update/<int:board_id>/", views.update, name="update"),
    path("delete/<int:board_id>/", views.delete, name="delete"),
]