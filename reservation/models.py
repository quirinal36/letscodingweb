import uuid # 👈 "uuid" import
from django.conf import settings  # 👈 "settings.py" import
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.core.mail import send_mail # 👈 "send_mail" import
from django.utils.html import strip_tags # 👈 "strip_tags" import
from django.template.loader import render_to_string # 👈 "render_to_string" import
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.timezone import now
from django.core.validators import RegexValidator

import datetime

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError('Users require an phone_number field')
        #phone = self.phone
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)
    
    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number, password, **extra_fields)
    
class User(AbstractUser):
    # phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
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
    #email = models.EmailField(unique=True)
    object = UserManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    # validators = [phoneNumberRegex]
    phone_number = PhoneNumberField(unique=True, blank=False, verbose_name="전화번호")
    name = models.CharField(max_length=120, default="", blank=True, verbose_name="이름")
    #email_verified = models.BooleanField(default=False)  # 👈 인증여부(True, False)
    #email_secret = models.CharField(max_length=120, default="", blank=True)  # 👈 uuid를 사용하여 난수 임시 저장
    school = models.CharField(max_length=120, default="", blank=True)
    create_date =models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField('last login', blank=True, null=True)
    
    """
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
    """
    def __str__(self):
        return f"(name:{self.name}, phone_number:{self.phone_number}, password:{self.password}, school:{self.school})"
# Create your models here.
class Board(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    contents = models.TextField()
    create_date =models.DateTimeField(auto_now_add=True)

class Program(models.Model):
    title = models.CharField(max_length=100)
    def __str__(self):
        return f"(title:{self.title})"
    
    
class Event(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    #section = models.CharField(max_length=200, default='')
    start_date = models.DateField(verbose_name="시작날짜", auto_now=False, auto_now_add=False)
    finish_date = models.DateField(verbose_name="종료날짜", auto_now=False, auto_now_add=False)
    create_date =models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    period = models.PositiveIntegerField(default= 1)
    num = models.PositiveIntegerField(default= 1) 
    deadline = models.DateTimeField(verbose_name="접수마감", auto_now_add=False, blank=False)
    apply_start = models.DateTimeField(verbose_name="접수시작", auto_now_add=False, blank=False)
    capacity = models.PositiveIntegerField(verbose_name="모집인원", default=1)
    
    def get_fields(self):
        return[(field.verbose_name, field.value_from_object(self)) for field in self.__class__._meta.fields]
    
    def save(self,*args, **kwargs):
        self.period = 0
        day = self.start_date
        while day <= self.finish_date :
            if day.weekday() < 5 :
                self.period += 1
            day = day + datetime.timedelta(days=1)
            #print(f"day in Event save:{day}")
            
        super(Event,self).save(*args, **kwargs)
    def __str__(self):
         return f"(title:{self.title}, program:{self.program})"
     
class Grades(models.Model):
    grade = models.PositiveIntegerField(default = 0)
    tgrade = models.CharField(max_length=200)
    
class Application(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(verbose_name="전화번호",blank=False)
    password = models.CharField(verbose_name="비밀번호",max_length=50)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grades, on_delete=models.CASCADE)
    school = models.CharField(verbose_name="학교",max_length=50)
    students = models.IntegerField(verbose_name="인원",)
    numOfClasses = models.PositiveIntegerField(verbose_name="학급수",default = 1)
    create_date =models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    confirmed = models.BooleanField(default = False)
    canceled = models.BooleanField(default = False)
    
    def __str__(self):
        return f"phone_number:{self.phone_number}, event_id:{self.event.id}, event:{self.event}"
    