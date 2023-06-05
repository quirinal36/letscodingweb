from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Board(models.Model) :
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    contents = models.TextField()
    create_date =models.DateTimeField(auto_now_add=True)