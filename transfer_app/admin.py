from django.contrib import admin
from .models import File, TransferHistory

admin.site.register(File)
admin.site.register(TransferHistory)