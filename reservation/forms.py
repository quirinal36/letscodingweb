from django import forms
from .models import Board, User, Event
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

class PrettyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        class_update_fields = ['username', 'password']
        for field_name in class_update_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'ipt1'
            })

class BoardForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
    class Meta:
        model = Board
        fields = ('title', 'contents')
        
class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'name',
            'username',
            'school',
        ]
        
        password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
        password2 = forms.CharField(label='Password confirmation', 
                                    widget=forms.PasswordInput,
                                    help_text = 'Enter the same password as above, for verification')
    # email이 이미 등록되었는지에 대한 validation
    def clean_email(self):
        email = self.cleaned_data.get("email") # 필드의 입력값 가져오기
        try:
            User.objects.get(email=email) # 필드의 email값이 DB에 존재하는지 확인
            raise forms.ValidationError("User already exists with that email")
        except User.DoesNotExist:
            return email  # 존재하지 않는다면, 데이터를 반환시킵니다.
        
     # 두개의 password가 일치한지에 대한 validation
    def clean_password1(self):
        password = self.cleaned_data.get("password") # 필드의 입력값 가져오기
        password1 = self.cleaned_data.get("password1") # 필드의 입력값 가져오기
        if password != password1:
            raise forms.ValidationError("Password confirmation does not match")
        else:
            return password
    
    # save 매서드로 DB에 저장
    def save(self):
        print("save method")
        user = super().save(commit=False) # Object는 생성하지만, 저장은 하지 않습니다.
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user.username = email
        user.set_password(password) # set_password는 비밀번호를 해쉬값으로 변환해요!
        user.save() # 이제 저장해줄께요:)    
        
class EventForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
    start_date = forms.DateTimeField(
        input_formats=['%Y/%m/%d'],
        widget = forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input'
        })
    )
    finish_date = forms.DateTimeField(
        input_formats=['%Y/%m/%d'],
        widget = forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input'
        })
    )
    class Meta:
        model = Event
        fields = ('title', 'start_date', 'finish_date')