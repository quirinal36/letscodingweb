from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, FormView
from django.contrib.auth import authenticate, login
from .forms import BoardForm, SignUpForm, PrettyAuthenticationForm, EventForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods, require_POST
from .models import Board, User, Event
from django.views.generic import View

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

class SignupView(View):
    form_class = SignUpForm
    template_name = 'member/join.html'
    success_url = reverse_lazy('reservations:index')
    model = User

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name,
                        context={'form':form, 'message':messages})
    def post(self, request):
        form = self.form_class()
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
        return render(request, self.template_name,
                        context={'form':form, 'message':messages})
    """
    def form_valid(self, form):
        print("form_valid")
        form.save()
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        print(f"email:{email}, password:{password}")
        user = authenticate(self.request, username=email, password=password)
        print(user)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)
    """
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


    
def calendar(request):
    return render(request, "program/calendar.html", None)

# @login_required(login_url="/reservation/login")
def applyList(request):
    board_list = Board.objects.order_by("id")
    context = {"board_list": board_list}
    return render(request, "program/apply-list.html", context)


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
    print(event)
    return render(request, "event/detail.html", {
        "event": event,
        "error_message":"You didn't select a choice."
    })