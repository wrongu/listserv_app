from django.contrib import admin
from models import Listserv, Sender, Message

# Register your models here.
admin.site.register(Listserv)
admin.site.register(Sender)
admin.site.register(Message)