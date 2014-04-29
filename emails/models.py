from django.db import models
from math import exp, log

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
	listserv = models.ForeignKey('Listserv') # the same person on 2 listservs is, for our purposes, two users

	def __unicode__(self):
		return self.name

class Thread(models.Model):

	DecayFactor = -7.614368693763378e-06 # chosen such that 99% decay is reached at exactly 1 week
	                                     # (1 - exp(a*x))	where a=DecayFactor
	thread_id = models.BigIntegerField(unique=True)
	start_message = models.ForeignKey('Message', related_name='thread_start')
	end_message = models.ForeignKey('Message', related_name='thread_end')
	length = models.IntegerField()
	participants = models.IntegerField()
	score = models.FloatField()

	def __unicode__(self):
		return self.start_message.title

	def update_score(self):
		duration = self.end_message.time - self.start_message.time
		self.score = (1 - exp(duration.total_seconds() * Thread.DecayFactor)) * log(self.participants * self.length)

class Message(models.Model):
	gm_id = models.BigIntegerField(unique=True) # gmail provides us with unique ids. we can use it to avoid double-counting.
	sender = models.ForeignKey('Sender')
	listserv = models.ForeignKey('Listserv')
	title = models.TextField()
	content = models.TextField()
	length = models.IntegerField()
	time = models.DateTimeField()
	thread_id = models.BigIntegerField(db_column='thread') # gmail threads are 64-bit numbers. So are django's BigIntegerFields
	
	def __unicode__(self):
		return u'%s: "%s" <%s>' % (str(self.sender), self.title, self.time.strftime("%m/%d %H:%M"))

	@classmethod
	def latest(cls, l):
		"""Return the datetime object of the most recent message
		"""
		return cls.objects.filter(listserv=l).order_by('-time').first().time

	@classmethod
	def earliest(cls, l):
		"""Return the datetime object of the oldest message
		"""
		return cls.objects.filter(listserv=l).order_by('-time').last().time

	class Meta:
		# avoid duplicate entries by enforcing that no single person can send 2 emails at exactly the same time
		unique_together = (('sender', 'time'),)
