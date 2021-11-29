from django.contrib import admin
from .models import Client, UniBook2, UniBook, PRTOType, Region

# Register your models here.
admin.site.register(Client)
admin.site.register(UniBook2)
admin.site.register(UniBook)
admin.site.register(PRTOType)
admin.site.register(Region)
