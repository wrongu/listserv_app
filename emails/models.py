from django.db import models

# Create your models here.
class Listserv(models.Model):
	listserv_address = models.CharField(max_length=64)
	short_name = models.CharField(max_length = 16)

class Sender(models.Model):
	name = models.CharField(max_length=32)
	email = models.CharField(max_length=32)
	total_sent = models.IntegerField()

class Message(models.Model):
	sender = models.ForeignKey('Sender')
	listserv = models.ForeignKey('Listserv')
	title = models.TextField()
	content = models.TextField()
	length = models.IntegerField()
	time = models.DateTimeField()
	thread = models.BigIntegerField() # gmail threads are 64-bit numbers. So are django's BigIntegerFields