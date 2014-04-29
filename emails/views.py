import re
import datetime
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
	chart = Highchart(renderTo="total_sent")
	chart.title("Total Emails Sent")
	chart.add_data_set(series, series_type="pie", name="")
	return {
		"id" : "total_sent",
		"js" : chart.generate()
	}

def __stats_args(listserv, **kwarg_filters):
	args = {
		'title' : listserv.short_name,
		'charts' : []
	}
	args['charts'].append(__chart_total_sent(listserv, **kwarg_filters))
	return args

# Create your views here.
def stats(request, site=''):
	listserv = Listserv.objects.filter(url=site).first()
	if listserv:
		return render(request, "emails/stats.html", __stats_args(listserv))
	else:
		return redirect('/fiuh')