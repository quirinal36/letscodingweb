
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Board, User, Event, Grades, Application, Program
from .forms import BoardForm, SignUpForm, PrettyAuthenticationForm, EventForm, ApplyForm, ProgramForm

from django.views.generic import View, CreateView, FormView, DetailView, ListView, UpdateView

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
import json

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
                if 'next' in request.POST and request.POST.get('next') != 'None':
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
        grades = Grades.objects.order_by("id")
        context['grades'] = grades
        context['event'] = event
        
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
    form_class = EventForm
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
    
    def post(self, request, *args, **kwargs):
        if not self.request.user.is_staff :
            # Only staff users are allowed to perform the POST operation
            return HttpResponseForbidden("로그인을 해 주세요.")
        
        eventForm = EventForm(request.POST)
        #print("EventUpdateView POST")
        if eventForm.is_valid():
            #print("EventUpdateView validated")
            event = eventForm.save(commit=False)
            #print("after eventform save")
            #print(event.user)
            event.user = request.user
            #event.save() <<-- 얘가 있으면 수정도 되면서 복제본이 추가됨
            print(event.user)
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
    
class EventListView(ListView)    :
    model = Event
    template_name = "event/list.html"
    context_object_name = "event_list"
    paginate_by = 5 # 한 페이지에 제한할 Object 수
    paginate_orphans = 0 # 짜투리 처리
    ordering = "-create_date" # 정렬기준
    page_kwarg = "page" # 페이징할 argument
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context['page_obj']
        paginator = page.paginator
        pagelist = paginator.get_elided_page_range(page.number, on_each_side=3, on_ends=0)
        context['pagelist'] = pagelist
        return context
    
    def get_queryset(self):
        return Event.objects.order_by("-id")
    
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

# @login_required(login_url="/reservation/login")
def applyList(request):
    my_apply_list = Application.objects.filter(user_id = request.user).order_by("-id")
    #print(f"list length : {len(my_apply_list)}")
    
    #context = {"list": my_apply_list}
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
            application = Application()
            application.user = request.user
            event_id = request.POST['event_id']
            event = Event.objects.get(id=event_id)
            application.event = event
            grade_id = request.POST['grade_id']
            grade = Grades.objects.get(id=grade_id)
            application.grade = grade
            students = request.POST['students']
            application.students = students
            
            application.save()
            return HttpResponseRedirect(reverse_lazy('reservations:applyList'))
        return super(ApplyView, self).get(request, *args, **kwargs)
            
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

def applyDetail(request, apply_id):
    application = get_object_or_404(Application, pk=event_id)
    return render(request, "program/read.html", {
        "application": application,
        "error_message":"You didn't select a choice."
    })
    
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
