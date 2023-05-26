from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# Create your views here.
def index(request):
    template = loader.get_template("index.html")
    context = {"hello": "world"}
    return render(request, "index.html", context)

def logout(request):
    template = loader.get_template("index.html")
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
