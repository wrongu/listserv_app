from django.contrib import admin
from models import Listserv, Sender, Message, Thread

# Register your models here.
admin.site.register(Listserv)
admin.site.register(Sender)
admin.site.register(Message)
admin.site.register(Thread)