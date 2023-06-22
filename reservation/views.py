
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Board, User, Event, Grades, Application
from .forms import BoardForm, SignUpForm, PrettyAuthenticationForm, EventForm, ApplyForm

from django.views.generic import View, CreateView, FormView

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator

def index(request):
    board_list = Board.objects.order_by("id")
    context = {"board_list": board_list}
    return render(request, "index.html", context)

################# User #################
def logout(request):
    return render(request, "logout.html", None)

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
                      context={'form': form, 'message':messages})
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
        
            if user is not None:
                login(self.request, user)
                return redirect('reservations:index')
        message = 'Login failed!'
        return render(request, 
                      self.template_name, 
                      context={'form': form, 'message':messages})

class SignupView(FormView):
    form_class = SignUpForm
    template_name = 'member/join.html'
    success_url = reverse_lazy('reservations:index')
    
    def form_valid(self, form):
        print("form_valid")
        form.save()
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        print(f"email:{email}, password:{password}")
        user = authenticate(self.request, username=email, password=password)
        print(user)
        if user is not None:
            login(self.request, user)
        # user.verify_email()
        return super().form_valid(form)
    
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
            context = {'eventForm':eventForm}
            return render(request, 'event/create.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
    
    elif request.method == "POST":
        eventForm = EventForm(request.POST)

        if eventForm.is_valid():
            event = eventForm.save(commit=False)
            event.user = request.user
            event.save()
            return redirect('/reservation/event/detail/'+str(event.id))
        
@login_required(login_url='/reservation/login/')
def readEvent(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    return render(request, "event/read.html", {
        "event": event,
        "error_message":"You didn't select a choice."
    })
@staff_member_required
@login_required(login_url="/reservation/login")
def eventDelete(request, event_id):
    event = Event.objects.get(id = event_id)
    if request.user != event.user:
        return redirect("/reservation/")
    event.delete()
    return redirect("reservation/")
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
    print(f"list length : {len(my_apply_list)}")
    
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
class ApplyView(LoginRequiredMixin, CreateView):
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
            
    
    def form_valid(self, form):
        
        """
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