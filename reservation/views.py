from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, FormView
#from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .forms import BoardForm, SignUpForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from .models import Board, User

def index(request):
    board_list = Board.objects.order_by("id")
    context = {"board_list": board_list}
    return render(request, "index.html", context)

################# User #################
def logout(request):
    
    return render(request, "logout.html", None)

class SignupView(FormView):
    form_class = SignUpForm
    template_name = 'signup.html'
    success_url = reverse_lazy('reservations:index')
    model = User

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
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

