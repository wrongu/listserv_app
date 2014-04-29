import re
import datetime
import pytz
from math import floor
from django.shortcuts import render, redirect
from emails.models import Listserv, Message, Sender, Thread
from emails.PyHighcharts import Highchart

def __chart_total_sent(listserv, limit=40, **kwarg_filters):
	senders = Sender.objects.filter(listserv=listserv, **kwarg_filters)
	series = [[re.escape(str(sender.name)), sender.total_sent] for sender in senders if sender.total_sent > 1]
	# sort by total sent: ['name', 4] => 4
	series.sort(key=lambda point: point[1], reverse=True) 
	# remove all the extras. just too many.
	all_others = sum([int(point[1]) for point in series[limit:]])
	series = series[:limit]
	chart = Highchart(renderTo="total_sent")
	chart.title("Total Emails Sent")
	chart.add_data_set(series, series_type="pie", name="Emails")
	return {
		"id" : "total_sent",
		"js" : chart.generate(),
		"title" : "Total Emails Sent",
		"description" : "Y'all send a lot of emails to %s... (Everybody else not shown sent a total of %d.)" % (listserv.short_name, all_others)
	}

__epoch = datetime.datetime(year=1970, month=1, day=1, tzinfo=pytz.UTC)

def __chart_thread_killers(listserv, limit=24, **kwarg_filters):
	scores = {}
	for thread in Thread.objects.all():
		s = thread.end_message.sender
		scores[s] = scores.get(s, 0) + thread.score
	data = scores.items() # list of tuples of (name, score)
	# data is easier to read if sorted
	data.sort(key=lambda point: point[1], reverse=True)
	# only keep top 'limit' scores
	data = data[:limit]
	# construct series
	serieses = [{'name' : re.escape(str(sender.name)), 'series_type' : 'column', 'data' :  [score]} for sender, score in data]
	chart = Highchart(renderTo="thread_killers")
	chart.title("Thread Killers")
	for s in serieses:
		chart.add_data_set(**s)
	return {
		"id" : "thread_killers",
		"js" : chart.generate(),
		"title" : "Thread killers",
		"description" : "Same formula, but points are awarded to whomever got in the last word."
	}

def __chart_trend_setters(listserv, limit=24, **kwarg_filters):
	scores = {}
	for thread in Thread.objects.all():
		s = thread.start_message.sender
		scores[s] = scores.get(s, 0) + thread.score
	data = scores.items() # list of tuples of (name, score)
	# data is easier to read if sorted
	data.sort(key=lambda point: point[1], reverse=True)
	# only keep top 'limit' scores
	data = data[:limit]
	# construct series
	serieses = [{'name' : re.escape(str(sender.name)), 'series_type' : 'column', 'data' :  [score]} for sender, score in data]
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

def __threads_info(listserv, **kwarg_filters):
	threads = Thread.objects.filter(start_message__listserv=listserv, **kwarg_filters).order_by('-score')
	ret = []
	print "getting thread info..."
	for th in threads:
		print str(th)
		duration = th.end_message.time - th.start_message.time
		duration_str = "%dd %dh %dm" % (duration.days, floor(duration.seconds / 3600), floor(duration.seconds / 60))
		ret.append({
			'title' : th.start_message.title,
			'score' : th.score,
			'participants' : th.participants,
			'messages' : th.length,
			'duration' : duration_str
			})
	return ret

def __stats_args(listserv, **kwarg_filters):
	args = {
		'title' : listserv.short_name,
		'charts' : [],
		'startdate' : Message.earliest(listserv).strftime("%b %d, %Y"),
		'all_threads' : __threads_info(listserv)
	}
	args['charts'].append(__chart_total_sent(listserv, **kwarg_filters))
	args['charts'].append(__chart_trend_setters(listserv, **kwarg_filters))
	args['charts'].append(__chart_thread_killers(listserv, **kwarg_filters))
	return args

# Create your views here.
def stats(request, site=''):
	listserv = Listserv.objects.filter(url=site).first()
	if listserv:
		return render(request, "emails/stats.html", __stats_args(listserv))
	else:
		return redirect('/fiuh')