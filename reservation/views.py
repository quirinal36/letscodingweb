
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Board, User, Event, Grades, Application, Program
from .forms import BoardForm, SignUpForm, PrettyAuthenticationForm, EventForm, ApplyForm, ProgramForm, ApplicationUpdateForm, ApplicationCancelForm, EventUpdateForm

from django.views.generic import View, CreateView, FormView, DetailView, ListView, UpdateView

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
import json
from django.core import validators
import datetime
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Q

def index(request):
    board_list = Board.objects.order_by("id")
    context = {"board_list": board_list}
    return render(request, "index.html", context)

################# User #################
def logout(request):
    return redirect(reverse_lazy("reservations:index"))

class LoginView(View):
    #redirect_authenticated_user = True
    form_class = PrettyAuthenticationForm
    template_name = 'member/login.html'
    model = User
    
    def get(self, request):
        form = self.form_class()
        
        #message = ''
        return render(request, 
                      self.template_name, 
                      context={
                          'form': form, 
                          'message':messages,
                          'next': request.GET.get('next')})
    def post(self, request):
        #print("Login Post")
        form = self.form_class(request.POST)
        print(list(request.POST.items()))
        
        if form.is_valid():
            print("Login Form Valid")
            cleaned_data = form.clean()
            phone_number = cleaned_data.get("phone_number")
            password = cleaned_data.get('password')
            print(f"phone_number:{phone_number}, password:{password}")
            
            user = authenticate(phone_number=phone_number, password=password)
            #print(user)
            if user is not None:
                login(self.request, user)
                if 'next' in request.POST and request.POST.get('next') != 'None' and len(request.POST.get('next'))>0:
                    print(f"request.POST.get('next'):{request.POST.get('next')}")
                    return redirect(request.POST.get('next'))
                return redirect('reservations:index')
        
        messages.error(self.request, '로그인에 실패하였습니다.', extra_tags='danger')
        context = {'form': form, 'message': messages}
        return render(request, 
                      self.template_name, 
                      context=context)

class SignupView(FormView):
    form_class = SignUpForm
    template_name = 'member/join.html'
    success_url = reverse_lazy('reservations:index')
        
    def post(self, request):
        form = self.form_class(request.POST)
        print(list(request.POST.items()))
        if form.is_valid():
            print("form_valid")
            cleaned_data = form.clean()
            
            form.save()
            #email = form.cleaned_data.get('email')
            #email = form.clean_email()
            #password = form.cleaned_data.get('password1')
            #password = form.clean_password()
            email = cleaned_data.get('email')
            password = cleaned_data.get('password1')
            
            print(f"email:{cleaned_data.get('email')}, password:{cleaned_data.get('password')}")
            user = authenticate(self.request, email=email, password=password)
            print(user)
            if user is not None:
                login(self.request, user)
                return redirect('reservations:index')
        else :
            messages.error(self.request, '회원가입에 실패하였습니다.', extra_tags='danger')
        # user.verify_email()
        context = {'form' : form}
        return render(request, 
                      self.template_name, 
                      context=context)
    
def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key) # 👈 uuid값을 기준으로 Object를 가져와요!
        user.email_verified = True 
        user.email_secret = ""
        user.save()
        # to do: add succes message
    except models.User.DoesNotExist:
        # to do: add error message
        pass
    return redirect(reverse("core:home"))

################# Board #################
@login_required(login_url='/reservation/login/')
@require_http_methods({"GET", "POST"})
def register(request):
    if request.method == "GET":
        
        if request.user.is_authenticated:
            boardForm = BoardForm(initial={'user':request.user})
            context = {'boardForm':boardForm}
            return render(request, 'boardWrite.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
    
    elif request.method == "POST":
        boardForm = BoardForm(request.POST)

        if boardForm.is_valid():
            board = boardForm.save(commit=False)
            board.user = request.user
            board.save()
            return redirect('/reservation/read/'+str(board.id))
        
def read(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    
    return render(request, "detail.html", {
        "board": board,
        "error_message":"You didn't select a choice."
    })

@login_required(login_url="/reservation/login")
@require_http_methods({"GET", "POST"})
def update(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    if request.method == "GET" :
        board = Board.objects.get(id=board_id)
        boardForm = BoardForm(instance=board, initial={'user':request.user})
        
        context = {'boardForm': boardForm}
        return render(request, 'boardWrite.html', context)
    elif request.method == "POST":
        boardForm = BoardForm(request.POST, instance = board)
        
        if boardForm.is_valid():
            board = boardForm.save(commit=False)
            print(board)
            board.save()
            
        return redirect('/reservation/read/'+str(board.id))
    
@login_required(login_url="/reservation/login")
def delete(request, board_id):
    board = Board.objects.get(id = board_id)
    if request.user != board.user:
        return redirect("/reservation/")
    board.delete()
    return redirect("reservation/")

### 관리자 교육등록및 조회 EVENT ###
@staff_member_required
@login_required(login_url='/reservation/login/')
@require_http_methods({"GET", "POST"})
def create(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            eventForm = EventForm(initial={'user':request.user})
            programs = Program.objects.order_by("id")
            context = {'eventForm':eventForm, "programs":programs}
            return render(request, 'event/create.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
    
    elif request.method == "POST":
        eventForm = EventForm(request.POST)
        print("event create")
        print(list(request.POST.items()))
        
        
        if eventForm.is_valid():
            print("eventForm.is_valid()")
            program = Program.objects.get(id=request.POST['program'])
            event = eventForm.save(commit=False)
            event.program = program
            event.user = request.user
            event.save()
            return redirect('/reservation/event/detail/'+str(event.id))
        
class EventDetailView(DetailView):
    model = Event
    template_name = "event/read.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        #grades = Grades.objects.order_by("id")
        #context['grades'] = grades
        context['event'] = event
        applications = Application.objects.filter(event = event)
        context['applications'] = applications
        print(applications)
        return context
    
class EventManageView(LoginRequiredMixin, ListView):
    model = Event
    template_name = "event/event_manage.html"
    context_object_name = "event_list"
    paginate_by = 5 # 한 페이지에 제한할 Object 수
    paginate_orphans = 0 # 짜투리 처리
    ordering = "-create_date" # 정렬기준
    page_kwarg = "page" # 페이징할 argument
    login_url = reverse_lazy('reservations:login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context['page_obj']
        paginator = page.paginator
        pagelist = paginator.get_elided_page_range(page.number, on_each_side=3, on_ends=0)
        context['pagelist'] = pagelist
        return context
    
    def get_queryset(self):
        return Event.objects.order_by("-id")
    
@login_required(login_url='/reservation/login/')
def readEvent(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    return render(request, "event/read.html", {
        "event": event,
        "error_message":"You didn't select a choice."
    })
    
@staff_member_required
@login_required(login_url="/reservation/login")
def eventDelete(request, pk):
    event = Event.objects.get(id = pk)
    response_data = {}
    if request.user != event.user:
        response_data['result'] = 'error'
        response_data['message'] = '작성자만 글을 삭제할 수 있습니다.'
    else :
        event.delete()
        response_data['result'] = 'success'
        response_data['message'] = '글이 삭제되었습니다.'
    return HttpResponse(json.dumps(response_data), content_type="application/json")

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    context_object_name = 'event'
    form_class = EventUpdateForm
    template_name = 'event/event_update.html'
    login_url = reverse_lazy('reservations:login')
    def get_success_url(self):
        #print("get_success_url")
        return reverse_lazy('reservations:eventDetail', args=(self.object.id,))
    
    def has_permission(self, request):
        #print("has_permission")
        return request.user.is_active and request.user.is_staff
    
    def get_initial(self):
        #print("get_initial")
        initial = super(EventUpdateView, self).get_initial()
        user = self.request.user
        initial['user'] = user
        return initial
        
    def get_object(self):
        #print('get_object')
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        return event
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        programs = Program.objects.order_by("id")
        context['programs'] = programs
        event = get_object_or_404(Event, pk=self.kwargs['pk'])
        context['event'] = event
        return context
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Custom logic before rendering the form
        context = self.get_context_data()
        if context['event'].user != request.user:
            return HttpResponseForbidden("작성자만 글을 수정할 수 있습니다..")
        
        return self.render_to_response(context)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        #print(f"get_form_kwargs:{kwargs}")
        # kwargs['request'] = self.request
        return kwargs
    
    def post(self, request, *args, **kwargs):
        if not self.request.user.is_staff :
            # Only staff users are allowed to perform the POST operation
            return HttpResponseForbidden("로그인을 해 주세요.")
        response_data = {}
        eventForm = self.get_form()
        #print("EventUpdateView POST")
        print(list(request.POST.items()))
        
        if eventForm.is_valid():
            
            #print("EventUpdateView validated")
            event = self.get_object()
            #print("after eventform save")
            print(f"event:{event}")
            event.capacity = request.POST['capacity']
            #event.program = eventForm.clean_data.get('program')
            event.start_date = eventForm.cleaned_data.get('start_date')
            event.finish_date = eventForm.cleaned_data.get('finish_date')
            event.apply_start = eventForm.cleaned_data.get('apply_start')
            event.deadline = eventForm.cleaned_data.get('deadline')
            #event.user = request.user
            #event.save() # <<-- 얘가 있으면 수정도 되면서 복제본이 추가됨
            #event.id = request.POST['id']
            #print(f"event:{event}")
            #Event.objects.filter(pk=event.id).update()
            #event.save()
            
            #response_data['result'] = 'success'
        #else :
            #response_data['result'] = 'fail'
        #return HttpResponse(json.dumps(response_data), content_type="application/json")    
        return super().post(request, *args, **kwargs)
            
    
@staff_member_required
@login_required(login_url="/reservation/login")
@require_http_methods({"GET", "POST"})
def eventUpdate(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == "GET" :
        event = Event.objects.get(id=event_id)
        eventForm = EventForm(instance=event, initial={'user':request.user})
        
        context = {'eventForm': eventForm}
        return render(request, 'event/create.html', context)
    elif request.method == "POST":
        eventForm = EventForm(request.POST, instance = event)
        
        if eventForm.is_valid():
            event = eventForm.save(commit=False)
            
            event.save()
            
        return redirect('/reservation/event/detail/'+str(event.id))
    
class EventListView(ListView):
    model = Event
    template_name = "event/list.html"
    context_object_name = "event_list"
    paginate_by = 5 # 한 페이지에 제한할 Object 수
    paginate_orphans = 0 # 짜투리 처리
    ordering = "-create_date" # 정렬기준
    page_kwarg = "page" # 페이징할 argument
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now() 
        year_list = [i for i in range(now.year-1, now.year+2)]
        month_list = [i for i in range(1, 13)]
        show_list = {0:'전체보기', 1:'접수 중'}
        context['show_list'] = show_list
        page = context['page_obj']
        paginator = page.paginator
        
        context['total'] = paginator.count
        context['num_pages'] = paginator.num_pages
        pagelist = paginator.get_elided_page_range(page.number, on_each_side=3, on_ends=0)
        context['pagelist'] = pagelist        
        context['today_date'] = now         
        year = self.request.GET.get('year', now.year)
        month = self.request.GET.get('month', now.month)
        enabled = self.request.GET.get('enabled', 0)
        if enabled :
            context['enabled'] = int(enabled)
        if year :
            context['cur_year']= int(year)
        if month :            
            context['cur_month']=int(month)
                
        context['year_list']=year_list
        context['month_list']=month_list
        return context
    
    def get_queryset(self):
        now = timezone.now() 
        year = self.request.GET.get('year', now.year)
        month = self.request.GET.get('month', now.month)
        
        month = str(month).zfill(2)
        
        #print(f"month:{month}")
        #print(f"year:{year}")
        selected_date = datetime.datetime.strptime(f"{year}/{month}", '%Y/%m')
        #print(f"selected_date:{selected_date}")
        
        lastDayOfMonth = selected_date + relativedelta(months=1)
        #print(f"Last date of month:{lastDayOfMonth}")
        enabled = self.request.GET.get('enabled', '0')
        #print(f"enabled:{enabled}")
        #print(f"enabled:{type(enabled)}")
        if int(enabled) == 0:
            
            queryset = Event.objects.filter(
                (
                    (Q(start_date__lt=lastDayOfMonth)&Q(start_date__gte=selected_date))
                    |
                    (Q(finish_date__lt=lastDayOfMonth)&Q(finish_date__gte=selected_date))
                )
            ).order_by("-id")
            #print(str(queryset.query))
            return queryset
        else:
            
            queryset = Event.objects.filter(
                (
                    (Q(start_date__lt=lastDayOfMonth)&Q(start_date__gte=selected_date))
                    |
                    (Q(finish_date__lt=lastDayOfMonth)&Q(finish_date__gte=selected_date))
                )
                & 
                    (Q(apply_start__lt=now) & Q(deadline__gt=now+ timedelta(days=1))
                )
            ).order_by("-id")
            #print(str(queryset.query))
            return queryset        
    
    def get(self, request, *args,**kwargs):
        
        return super().get(request, *args,**kwargs)
def event(request):
    event_list = Event.objects.order_by("id")
    context = {"event_list": event_list}
    return render(request, "event/list.html", context)

def eventDetail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    return render(request, "event/detail.html", {
        "event": event,
        "error_message":"You didn't select a choice."
    })
    
### APPLY ###
def calendar(request):
    return render(request, "program/calendar.html", None)

class ApplyListView(ListView):
    model = Application
    template_name = "program/apply-list.html"
    context_object_name = "apply_list"
    paginate_by = 5 # 한 페이지에 제한할 Object 수
    paginate_orphans = 0 # 짜투리 처리
    ordering = "-create_date" # 정렬기준
    page_kwarg = "page" # 페이징할 argument
    
    
    def get_context_data(self, **kwargs):
        context = super(ApplyListView, self).get_context_data(**kwargs)
        page = context['page_obj']
        paginator = page.paginator
        pagelist = paginator.get_elided_page_range(page.number, on_each_side=3, on_ends=0)
        context['pagelist'] = pagelist
        context['form'] = ApplyForm()
        
        return context
    
    def get_queryset(self):
        return Application.objects.order_by("-id")
    
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        if "phone_number" in request.GET :
            phone_param = request.GET["phone_number"]
            phone_param = self.format_phone_number(phone_param)
            # print(f"phone_param:{phone_param}")
            self.object_list = Application.objects.filter(phone_number__icontains = phone_param).order_by("-id")
        
        context = self.get_context_data()
        return self.render_to_response(context)
    def format_phone_number(self, input_string):
        if len(input_string) == 10:
            # Assuming the input string has the format "0101111222"
            area_code = input_string[:3]
            first_part = input_string[3:6]
            second_part = input_string[6:]
            formatted_number = f"{area_code}-{first_part}-{second_part}"
            return formatted_number
        elif len(input_string) == 11:
            # Assuming the input string has the format "01011112222"
            #country_code = input_string[:2]
            area_code = input_string[:3]
            first_part = input_string[3:7]
            second_part = input_string[7:]
            formatted_number = f"{area_code}-{first_part}-{second_part}"
            return formatted_number
        else:
            return input_string
        
# @login_required(login_url="/reservation/login")
def applyList(request):
    my_apply_list = Application.objects.order_by("-id")
    if "phone_number" in request.GET :
        phone_param = request.GET["phone_number"]
        my_apply_list = Application.objects.filter(phone_number__icontains =phone_param)
    
    for apply in my_apply_list:
        print(f"phone_number:{apply.phone_number}")
        
    context = {"list": my_apply_list}
    return render(request, "program/apply-list.html", context)

# @login_required(login_url="/reservation/login")
def applyFormView(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    grades = Grades.objects.order_by("id")
    applyForm = ApplyForm(initial={'user':request.user})
    
    return render(request, "program/apply.html", {
        'form': applyForm,
        "event": event,
        "error_message":"You didn't select a choice.",
        "user": request.user,
        "grades":grades
    })

# @login_required(login_url='/reservation/login/')
class ApplyView(CreateView):
    model = Application
    form_class = ApplyForm
    template_name = 'program/apply.html'
    success_url = reverse_lazy('reservations:applyList')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        event = get_object_or_404(Event, pk=self.kwargs['event_id'])
        grades = Grades.objects.order_by("id")
        context['grades'] = grades
        context['event'] = event
        
        return context
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        
        return super(ApplyView, self).get(request, *args, **kwargs)
        
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        
        print(list(request.POST.items()))
        if form.is_valid():
            print("form is valid")
            application = form.save(commit=False)
            print("form saved")
            
            event_id = request.POST['event_id']
            event = Event.objects.get(id=event_id)
            application.event = event
            grade_id = request.POST['grades']
            grade = Grades.objects.get(id=grade_id)
            application.grade = grade
            
            phone_number = application.phone_number
            print(f"phone_number:{phone_number}")
            
            application.save()
            return HttpResponseRedirect(reverse_lazy('reservations:applyList'))
        messages.error(self.request, '교육신청에 실패하였습니다.', extra_tags='danger')
        context = {
            'event': Event.objects.get(id=request.POST['event_id']),
            'form': form, 
            'message': messages
            }
        return render(request, self.template_name, context)
    #super(ApplyView, self).get(request, *args, **kwargs)
            
    """
    def form_valid(self, form):
        if request.method == 'POST':
            applyForm = ApplyForm(request.POST)
            print('applyForm post')
            print(list(request.POST.items()))
            if applyForm.is_valid():
                apply = applyForm.save(commit=False)
                apply.user = request.user
                apply.save()
                return redirect('event/apply/detail/'+str(apply.id))
            else :
                print('applyForm invalid')
        """
def applicationConfirm(request, pk):
    response_data = {}
    application = get_object_or_404(Application, pk=pk)
    if application.confirmed :
        application.confirmed = 0
    else :
        application.confirmed = 1
    #print(f"application.save():{application.save()}")
    response_data['result'] = 'success'
    
    return HttpResponse(json.dumps(response_data), content_type="application/json")

class ApplicationUpdateView(UpdateView):
    model = Application
    form_class = ApplicationUpdateForm
    template_name = "program/update.html"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        application = get_object_or_404(Application, pk=self.kwargs['pk'])
        event = application.event
        
        #event = get_object_or_404(Event, pk=self.kwargs['event_id'])
        grades = Grades.objects.order_by("id")
        context['grades'] = grades
        context['event'] = event
        
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        #print(f"get_form_kwargs:{kwargs}")
        # kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy("reservations:applyList")
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        originApplication = Application.objects.get(pk=self.kwargs['pk'])
        if form.is_valid():
            password = form.cleaned_data.get('password')
            print(f"password:{password} / originApplication.password:{originApplication.password}")
            if password == originApplication.password:
                #messages.success(request, '수정이 완료되었습니다.')
                
                return super().post(request, *args, **kwargs)
            else:
                messages.error(self.request, '비밀번호가 틀렸습니다. 다시 입력해 주세요.', extra_tags='danger')
            print(form.errors)
            print(form.non_field_errors())
            context = {
                    'form': form, 
                    }
            context['grades'] = Grades.objects.order_by("id")
            context['event'] = Event.objects.get(pk=originApplication.event.id)
            return render(request, self.template_name, context)
    
def applyDetail(request, apply_id):
    application = get_object_or_404(Application, pk=apply_id)
    return render(request, "program/read.html", {
        "application": application,
        "error_message":"You didn't select a choice."
    })
    
class ApplicationCancelView(UpdateView):
    model = Application
    form_class = ApplicationCancelForm
    template_name = "program/cancel.html"
    success_url = reverse_lazy("reservations:applyList")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        application = get_object_or_404(Application, pk=self.kwargs['pk'])
        #event = application.event
        
        context['application'] = application
        #context['event'] = event
        
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        #print(f"get_form_kwargs:{kwargs}")
        # kwargs['request'] = self.request
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy("reservations:applyList")
    
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        originApplication = Application.objects.get(pk=self.kwargs['pk'])
        print(f"originApplication:{originApplication}")
        if form.is_valid() :
            password = form.cleaned_data.get('password')
            if password == originApplication.password:
                
                originApplication.canceled = True
                
                # messages.success(request, '취소가 완료되었습니다.')
                return super().post(request, *args, **kwargs)
            else:
                messages.error(self.request, '비밀번호가 틀렸습니다. 다시 입력해 주세요.', extra_tags='danger')        
            context = {
                    'form': form, 
                    }
            #context['grades'] = Grades.objects.order_by("id")
            context['application'] = originApplication
            return render(request, self.template_name, context)

### Program ###    
class ProgramListView(ListView):
    model = Program
    context_object_name = 'program_list'
    template_name='program/list.html'


class ProgramCreateView(CreateView):
    model = Program
    template_name = "program/create.html"
    form_class = ProgramForm

    def get_success_url(self):
        return reverse_lazy("reservations:program")
    

class ProgramUpdateView(UpdateView):
    model = Program
    form_class = ProgramForm
    template_name = "program/create.html"
    
    def get_success_url(self):
        return reverse_lazy("reservations:program")

