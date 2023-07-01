from django import forms

from .models import Board, User, Event, Application, Program
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from phonenumber_field.formfields import PhoneNumberField

class PrettyAuthenticationForm(forms.Form):
    """
    email = forms.EmailField(
        error_messages = {'required':'이메일 주소를 입력해 주세요.'},
        widget=forms.TextInput(attrs={'autofocus':True, 'class':'ipt1'}))
    """
    phone_number = PhoneNumberField(
        region="KR",
        error_messages = {'required':'전화번호를 입력해 주세요.'},
        widget=forms.TextInput(attrs={'autofocus':True, 'class':'ipt1'})
    )
        
    password = forms.CharField(
        error_messages = {'required':'비밀번호를 입력해 주세요.'},
        widget=forms.PasswordInput(attrs={'class':'ipt1'}))
    """
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        class_update_fields = ['password']
        for field_name in class_update_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'ipt1'
            })
        def is_valid(self):
        
        return True
    """
    
    
    def clean(self):
        phone_number = self.cleaned_data.get("phone_number") # 필드의 입력값 가져오기
        password = self.cleaned_data.get("password")
        
        try:
            user = User.objects.get(phone_number=phone_number) # 필드의 email값이 DB에 존재하는지 확인
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error("password", forms.ValidationError("비밀번호를 확인해 주세요."))
        except User.DoesNotExist:
            # 존재하지 않는다면, 데이터를 반환시킵니다.
            self.add_error('phone_number', forms.ValidationError("존재하지 않는 전화번호입니다."))
    
        
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
            'phone_number',
            'school',
            'password1',
            'password2'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_update_fields = ['name','phone_number','school','password1','password2']
        for field_name in class_update_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'ipt1'
            })
    def clean(self):
        phone_number = self.clean_phone_number()
        password = self.clean_password()
        return self.cleaned_data
        
    # phone_number가 이미 등록되었는지에 대한 validation
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number") # 필드의 입력값 가져오기
        try:
            User.objects.get(phone_number=phone_number) # 필드의 phone_number값이 DB에 존재하는지 확인
            raise forms.ValidationError("이미 가입된 전화번호입니다.")
        except User.DoesNotExist:
            return phone_number  # 존재하지 않는다면, 데이터를 반환시킵니다.
        
     # 두개의 password가 일치한지에 대한 validation
    def clean_password(self):
        password = self.cleaned_data.get("password1") # 필드의 입력값 가져오기
        password1 = self.cleaned_data.get("password2") # 필드의 입력값 가져오기
        if password != password1:
            raise forms.ValidationError("입력한 비밀번호가 비밀번호 확인과 일치하지 않습니다.")
        else:
            return password
    
    # save 매서드로 DB에 저장
    def save(self, *args, **kwargs):
        print("save method")
        user = super().save(commit=False) # Object는 생성하지만, 저장은 하지 않습니다.
        #email = self.cleaned_data.get("email")
        phone_number = self.clean_phone_number()
        #password = self.cleaned_data.get("password1")
        password = self.clean_password()
        
        name = self.cleaned_data.get("name")
        school = self.cleaned_data.get("school")
        
        user.phone_number = phone_number
        user.set_password(password) # set_password는 비밀번호를 해쉬값으로 변환해요!
        user.name = name
        user.school = school
        print(user)
        print("before user save")
        user.save() # 이제 저장해줄께요:)   
        return user 
    
class EventForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.HiddenInput())
    #stay = forms.ChoiceField(choices = Event.STAY_CHOICES)
    #section = forms.CharField()
    
    class Meta:
        model = Event
        fields = ('start_date', 'finish_date', 'apply_start', 'deadline')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"init")
        """
        class_update_fields = ['title']
        for field_name in class_update_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'ipt1'
            })
        """
        self.fields['start_date'].widget.attrs.update({
            'class': 'datetimepicker-input ipt1',
            'autocomplete' : 'off'
        })
        self.fields['finish_date'].widget.attrs.update({
            'class': 'datetimepicker-input ipt1',
            'autocomplete' : 'off'
        })
        self.fields['deadline'].widget.attrs.update({
            'class': 'datetimepicker-input ipt1',
            'autocomplete' : 'off'
        })
        self.fields['apply_start'].widget.attrs.update({
            'class': 'datetimepicker-input ipt1',
            'autocomplete' : 'off'
        })

class ApplyForm(forms.ModelForm):
    phone = PhoneNumberField(region="KR")
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
    
    class Meta:
        model = Application
        fields = ('school', 'grade', 'students', 'numOfClasses', 'phone_number', 'password')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_update_fields = ['school', 'grade', 'students', 'numOfClasses', 'phone_number', 'password']
        for field_name in class_update_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'ipt1'
            })
    
    def is_valid(self):
        #cleaned_data = super().clean()
        #grade = cleaned_data.get('grade')
        #students = cleaned_data.get('students')
        #print(f"grade:{grade}, students:{students}")
        return True
    
class ProgramForm(forms.ModelForm):
    
    class Meta:
        model = Program
        fields = "__all__"