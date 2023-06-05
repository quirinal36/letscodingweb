from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .forms import BoardForm
from django.contrib.auth.decorators import login_required
from .models import Board
# Create your views here.
def index(request):
    context = {"hello": "world"}
    return render(request, "index.html", context)

def logout(request):
    
    return render(request, "logout.html", None)

class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'signup.html'
    #success_url = reverse_lazy('index')
    model = User

    def form_valid(self, form):
        form.save()
        username = self.request.POST['username']
        password = self.request.POST['password1']
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return HttpResponseRedirect(reverse('index'))
    
@login_required(login_url='/reservation/login/')
def register(request):
    if request.method == "GET":
        
        if request.user.is_authenticated:
            username = request.user.username
            
        users = User.objects.all()
        index = 0
        for name in users:
            if username == name.username:
                break
            index += 1
        
        boardForm = BoardForm(initial={'user':users[index]})
        context = {'boardForm':boardForm}
        return render(request, 'boardWrite.html', context)
    
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