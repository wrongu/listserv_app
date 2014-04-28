from django.db import models

# Create your models here.
class Listserv(models.Model):
	listserv_address = models.CharField(max_length = 64)
	short_name = models.CharField(max_length = 16)
	folder = models.CharField(max_length = 16)
	url = models.CharField(max_length = 16)

	def __unicode__(self):
		return self.short_name

class Sender(models.Model):
	name = models.CharField(max_length = 32)
	email = models.CharField(max_length = 64)
	total_sent = models.IntegerField()

	def __unicode__(self):
		return self.name

class Message(models.Model):
	sender = models.ForeignKey('Sender')
	listserv = models.ForeignKey('Listserv')
	title = models.TextField()
	content = models.TextField()
	length = models.IntegerField()
	time = models.DateTimeField()
	thread = models.BigIntegerField() # gmail threads are 64-bit numbers. So are django's BigIntegerFields
	gm_id = models.BigIntegerField(unique=True) # gmail provides us with unique ids. we can use it to avoid double-counting.
	
	def __unicode__(self):
		return u'%s: "%s" <%s>' % (str(self.sender), self.title, self.time.strftime("%m/%d %H:%M"))

	class Meta:
		# avoid duplicate entries by enforcing that no single person can send 2 emails at exactly the same time
		unique_together = (('sender', 'time'),)