from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views import SignupView, LoginView
from .forms import PrettyAuthenticationForm

app_name="reservations"

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", SignupView.as_view(), name="signup"),
    #path("login/", auth_views.LoginView.as_view(template_name='member/login.html'), name="login"),
    path("login/", views.LoginView.as_view(
                        template_name="member/login.html"
        ), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name="logout"),
    path("regist/", views.register, name="regist"),
    path("read/<int:board_id>/", views.read, name="read"),
    path("update/<int:board_id>/", views.update, name="update"),
    path("delete/<int:board_id>/", views.delete, name="delete"),
    path("verify/<str:key>", views.complete_verification, name="complete-verification"), #인증 메일 내 링크가 클릭되면 "complete_verification" 함수가 작동합니다:)
    path("block/", views.block, name="block"),
    path("calendar/", views.calendar, name="calendar"),
    path("applyList/", views.applyList, name="applyList"),
    path("event/", views.event, name="event"),
    path("event/detail/<int:event_id>", views.eventDetail, name="eventDetail"),
    path("event/create/", views.create, name="eventCreate"),
    path("event/update/", views.update, name="eventUpdate"),
    path("event/delete/", views.delete, name="eventDelete"),
]


