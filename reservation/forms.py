from django import forms
from .models import Board, User
#from django.contrib.auth.models import User


class BoardForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
    class Meta:
        model = Board
        fields = ('title', 'contents')
        
class SignUpForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            'email',
        )
    password = forms.CharField(widget=forms.PasswordInput)
    password1 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
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
        user = super().save(commit=False) # Object는 생성하지만, 저장은 하지 않습니다.
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user.username = email
        user.set_password(password) # set_password는 비밀번호를 해쉬값으로 변환해요!
        user.save() # 이제 저장해줄께요:)    