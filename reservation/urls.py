from django.urls import include, path
from django.contrib.auth import views as auth_views

from . import views
from .views import SignupView, LoginView
from .forms import PrettyAuthenticationForm

app_name="reservations"

event_patterns = [
    path("apply/", views.ApplyView.as_view(), name="apply"),
    path("apply/<int:event_id>", views.ApplyView.as_view(), name="applyForm"),
    path("", views.event, name="event"),
    path("detail/<int:pk>", views.EventDetailView.as_view(), name="eventDetail"),
    path("create/", views.create, name="eventCreate"),
    path("update/<int:pk>", views.update, name="eventUpdate"),
    path("delete/<int:pk>", views.delete, name="eventDelete"),
    path("apply/detail/<int:apply_id>/", views.applyDetail, name="applyDetail"),
]
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
    path("calendar/", views.calendar, name="calendar"),
    
    path("applyList/", views.applyList, name="applyList"),
    path("event/", include(event_patterns)),
    
]


