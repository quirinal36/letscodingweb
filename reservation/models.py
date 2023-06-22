import uuid # 👈 "uuid" import
from django.conf import settings  # 👈 "settings.py" import
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.mail import send_mail # 👈 "send_mail" import
from django.utils.html import strip_tags # 👈 "strip_tags" import
from django.template.loader import render_to_string # 👈 "render_to_string" import


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users require an email field')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
    
class User(AbstractUser):
    """
    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_OTHER = "other"
    GENDER_CHOICES = (
        (GENDER_MALE, "Male"),
        (GENDER_FEMALE, "Female"),
        (GENDER_OTHER, "Other"),
    )
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=10, null=True, blank=True
    )
    
    birthdate = models.DateField(null=True)
    """
    username = None
    email = models.EmailField(unique=True)
    object = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    name = models.CharField(max_length=120, default="", blank=True)
    email_verified = models.BooleanField(default=False)  # 👈 인증여부(True, False)
    email_secret = models.CharField(max_length=120, default="", blank=True)  # 👈 uuid를 사용하여 난수 임시 저장
    school = models.CharField(max_length=120, default="", blank=True)
    def verify_email(self): # 👈 회원가입 시, email을 인증을 위한 매서드입니다.
        if self.email_verified is False:
            secret = uuid.uuid4().hex[:20] # 👈 random key 생성
            self.email_secret = secret  # 👈 random key를 DB에 저장
            html_message = render_to_string(
                "emails/verify_email.html", {"secret": secret}
            )
            
            send_mail(
                "Verify LetsCoding Account",  # 👈 제목
                strip_tags(html_message),  # 👈 내용
                settings.EMAIL_FROM,  # 👈 발송자
                [self.email],  # 👈 수신자
                fail_silently=False, 
                html_message=html_message,  # 👈 html을 메일로 전송해줍니다.
            )
            self.save() # 👈 저장(save매서드를 통해 필드의 값을 저장합니다.)
        return
    
# Create your models here.
class Board(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    contents = models.TextField()
    create_date =models.DateTimeField(auto_now_add=True)
    
class Event(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stay = models.PositiveIntegerField(default = 0)
    section = models.CharField(max_length=200, default='')
    start_date = models.DateField(auto_now=False, auto_now_add=False)
    finish_date = models.DateField(auto_now=False, auto_now_add=False)
    create_date =models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
        
class Grades(models.Model):
    grade = models.PositiveIntegerField(default = 0)
    tgrade = models.CharField(max_length=200)
    
class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grades, on_delete=models.CASCADE)
    students = models.IntegerField()
    create_date =models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    confirm = models.IntegerField(default = 0)