from django.contrib import admin

# Register your models here.
from .models import Board, User, Grades, Application, Event


admin.site.register(User)
admin.site.register(Grades)
admin.site.register(Application)
admin.site.register(Event)