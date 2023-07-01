from django.contrib import admin

# Register your models here.
from . import models


admin.site.register(models.User)
admin.site.register(models.Grades)
admin.site.register(models.Application)
admin.site.register(models.Event)
