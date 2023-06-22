from django.contrib import admin

# Register your models here.
from .models import Board, User, Grades, Application


admin.site.register(User)
admin.site.register(Grades)
admin.site.register(Application)