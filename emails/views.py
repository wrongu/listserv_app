import re
import datetime
import pytz
from math import log, exp
from django.shortcuts import render, redirect
from emails.models import Listserv, Message, Sender
from emails.PyHighcharts import Highchart

def __string_escape(string):
	return re.escape(str(string))

def __chart_total_sent(listserv, limit=30, **kwarg_filters):
	senders = Sender.objects.filter(**kwarg_filters).order_by('total_sent')
	series = [[__string_escape(sender.name), sender.total_sent] for sender in senders if sender.total_sent > 1]
	# sort by total sent: ['name', 4] => 4
	series.sort(key=lambda point: point[1], reverse=True) 
	# remove all the extras. just too many.
	series = series[:limit]
	series.append(['Everybody Else', sum([int(point[1]) for point in series[limit:]])])
	chart = Highchart(renderTo="total_sent")
	chart.title("Total Emails Sent")
	chart.add_data_set(series, series_type="pie", name="Emails")
	return {
		"id" : "total_sent",
		"js" : chart.generate(),
		"title" : "Total Emails Sent",
		"description" : "Y'all send a lot of emails to %s..." % listserv.short_name
	}

__decay_factor = -7.614368693763378e-06	# chosen such that 99% decay is reached at exactly 1 week
										# (1 - exp(a*x))	where a=__decay_factor
def __thread_score(thread_id, **kwarg_filters):
	## GATHER PARTS ##
	thread_qs = Message.objects.filter(thread=thread_id, **kwarg_filters).order_by('time')
	num_messages = len(thread_qs)   # this hits the database. full query.
	thread_start = thread_qs.first() # here, the queryset is not reevaluated since
	thread_end = thread_qs.last()    #  by the laziness and DRY principles, it only needed to be hit once
	thread_duration = thread_end.time - thread_start.time
	participants = len(thread_qs.values('sender').distinct())
	## COMPUTE SCORE ##
	thread_score = (1 - exp(thread_duration.total_seconds() * __decay_factor)) * log(participants * num_messages)
	return thread_score, thread_start, thread_end

__epoch = datetime.datetime(year=1970, month=1, day=1, tzinfo=pytz.UTC)
__tk_cache = (__epoch, None) # (datetime, value) cache. only updated when new messages arrive.
def __chart_trend_killers(listserv, limit=24, **kwarg_filters):
	global __tk_cache
	updated, serieses = __tk_cache
	if Message.objects.latest('time').time > updated:
		# needs update!
		tupdate = pytz.UTC.localize(datetime.datetime.utcnow())
		threads = Message.objects.filter(listserv=listserv, **kwarg_filters).values_list("thread", flat=True).distinct()
		scores = {} # map sender to score
		for thread in threads:
			# update total score for the last sender in this thread
			score, starter, ender = __thread_score(thread)
			scores[ender.sender] = scores.get(ender.sender, 0) + score
		data = scores.items() # list tupes of (name, score)
		# data is easier to read if sorted
		data.sort(key=lambda point: point[1], reverse=True)
		# only keep top 'limit' scores
		data = data[:limit]
		# construct series
		serieses = [{'name' : __string_escape(sender.name), 'series_type' : 'column', 'data' :  [score]} for sender, score in data]
		__tk_cache = (tupdate, serieses)
	chart = Highchart(renderTo="trend_killers")
	chart.title("Trend Killers")
	for s in serieses:
		chart.add_data_set(**s)
	return {
		"id" : "trend_killers",
		"js" : chart.generate(),
		"title" : "Trend killers",
		"description" : "Each email thread is scored based on duration, number of messages, and number of participants. Points are awarded to whomever got in the last word."
	}

__ts_cache = (__epoch, None) # (datetime, value) cache. only updated when new messages arrive.
def __chart_trend_setters(listserv, limit=24, **kwarg_filters):
	global __ts_cache
	updated, serieses = __ts_cache
	if Message.objects.latest('time').time > updated:
		# needs update!
		tupdate = pytz.UTC.localize(datetime.datetime.utcnow())
		threads = Message.objects.filter(listserv=listserv, **kwarg_filters).values_list("thread", flat=True).distinct()
		scores = {} # map sender to score
		for thread in threads:
			# update total score for the last sender in this thread
			score, starter, ender = __thread_score(thread)
			scores[starter.sender] = scores.get(starter.sender, 0) + score
		data = scores.items() # list tupes of (name, score)
		# data is easier to read if sorted
		data.sort(key=lambda point: point[1], reverse=True)
		# only keep top 'limit' scores
		data = data[:limit]
		# construct series
		serieses = [{'name' : __string_escape(sender.name), 'series_type' : 'column', 'data' :  [score]} for sender, score in data]
		__ts_cache = (tupdate, serieses)
	else:
		print "ts cache success!"
	chart = Highchart(renderTo="trend_setters")
	chart.title("Trend Setters")
	for s in serieses:
		chart.add_data_set(**s)
	return {
		"id" : "trend_setters",
		"js" : chart.generate(),
		"title" : "Trend Setters",
		"description" : "Each email thread is scored based on duration, number of messages, and number of participants. Points are awarded to whomever got the thead started."
	}

def __stats_args(listserv, **kwarg_filters):
	args = {
		'title' : listserv.short_name,
		'charts' : [],
		'startdate' : Message.earliest().strftime("%b %d, %Y")
	}
	args['charts'].append(__chart_total_sent(listserv, **kwarg_filters))
	args['charts'].append(__chart_trend_setters(listserv, **kwarg_filters))
	args['charts'].append(__chart_trend_killers(listserv, **kwarg_filters))
	return args

# Create your views here.
def stats(request, site=''):
	listserv = Listserv.objects.filter(url=site).first()
	if listserv:
		return render(request, "emails/stats.html", __stats_args(listserv))
	else:
		return redirect('/fiuh')