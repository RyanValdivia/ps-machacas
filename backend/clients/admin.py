from django.contrib import admin
from .models import Client, Recipe, Optometrist

# Register your models here.
admin.site.register(Client)
admin.site.register(Recipe)
admin.site.register(Optometrist)

