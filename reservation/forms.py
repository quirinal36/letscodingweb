from django import forms

from .models import Board, User, Event, Application, Program, Grades
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from phonenumber_field.formfields import PhoneNumberField
from django.forms import ModelChoiceField
from django.core.validators import RegexValidator

class PrettyAuthenticationForm(forms.Form):
    """
    email = forms.EmailField(
        error_messages = {'required':'이메일 주소를 입력해 주세요.'},
        widget=forms.TextInput(attrs={'autofocus':True, 'class':'ipt1'}))
    """
    phone_number = PhoneNumberField(
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
        print(f"phone_number:{phone_number}, password:{password}")
        try:
            user = User.objects.get(phone_number=phone_number) # 필드의 email값이 DB에 존재하는지 확인
            
            if user.check_password(password):
                return self.cleaned_data
            else:
                
                self.add_error("password", forms.ValidationError("비밀번호를 확인해 주세요."))
        except User.DoesNotExist:
            users = User.objects.order_by("id")
            print(users)
            for u in users:
                if phone_number == u.phone_number :
                    print(f"same!! {u.phone_number}")
                    
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
        fields = ('start_date', 'finish_date', 'apply_start', 'deadline', 'capacity')
        
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
            'autocomplete' : 'off',
            'placeholder' : '교육이 시작하는 날'
        })
        self.fields['finish_date'].widget.attrs.update({
            'class': 'datetimepicker-input ipt1',
            'autocomplete' : 'off',
            'placeholder' : '교육이 끝나는 날'
        })
        self.fields['deadline'].widget.attrs.update({
            'class': 'datetimepicker-input ipt1',
            'autocomplete' : 'off',
            'placeholder' : '접수 마감일'
        })
        self.fields['apply_start'].widget.attrs.update({
            'class': 'datetimepicker-input ipt1',
            'autocomplete' : 'off',
            'placeholder' : '접수 시작일'
        })
        self.fields['capacity'].widget.attrs.update({
            'class': 'ipt1',
            'autocomplete' : 'off',
            'placeholder' : '모집 인원을 입력하세요.'
        })
        
class GradeModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.tgrade
    
class ApplyForm(forms.ModelForm):
    
    phone_number = PhoneNumberField(
        label = '전화번호',
        required = True,
        widget=forms.TextInput(attrs={'placeholder':'전화번호를 입력하세요.'}),
        error_messages = {
            'name':{
                "required":"전화번호를 입력해 주세요.",
                "malformed":"전화번호를 다시 확인해 주세요."
            }
        }
    )
    password = forms.CharField(
        label = '비밀번호',
        max_length=50, 
        widget=forms.PasswordInput(attrs={'placeholder':'비밀번호를 입력하세요.'})
    )
    grades = GradeModelChoiceField(
        label = '학년',
        queryset = Grades.objects.all(),
        to_field_name="id",
        required=True,
    )
    school = forms.CharField(
        label = '학교',
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder':'학교이름을 입력하세요.'}),
    )
    students = forms.IntegerField(
        label = '신청 인원',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder':'신청인원을 입력하세요.'}),
    )
    numOfClasses = forms.IntegerField(
        label = '학급수',
        required=True,
        widget=forms.NumberInput(attrs={'placeholder':'신청학급수를 입력하세요.'}),
    )
    class Meta:
        model = Application
        fields = ('school', 'students', 'grades', 'numOfClasses', 'phone_number', 'password')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class_update_fields = ['school', 'students', 'grades', 'numOfClasses', 'phone_number', 'password']
        for field_name in class_update_fields:
            self.fields[field_name].widget.attrs.update({
                'class': 'ipt1'
            })
    def phone_number_valid(self):
        phone_regex = RegexValidator(regex=r'^\+?82?\d{10,11}$')
        try:
            phone_number = self.cleaned_data.get('phone_number')
            print(f"clean phone_number:{phone_number}") 
            phone_regex(phone_number) # return None
        except forms.ValidationError:
            # 존재하지 않는다면, 데이터를 반환시킵니다.
            #self.add_error('phone_number', forms.ValidationError("전화번호를 다시 확인해 주세요.."))
            return None
            
        return self.cleaned_data.get('phone_number')
    
    
        
    def is_valid(self):
        valid = super(ApplyForm, self).is_valid()
        cleaned_phone_number = self.phone_number_valid()
        #grade = cleaned_data.get('grade')
        #students = cleaned_data.get('students')
        #print(f"grade:{grade}, students:{students}")
        if valid and cleaned_phone_number :
            return True
        else:
            return False
    
class ProgramForm(forms.ModelForm):
    
    class Meta:
        model = Program
        fields = "__all__"