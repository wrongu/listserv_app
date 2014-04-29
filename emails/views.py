from django.shortcuts import render, redirect
from emails.models import Listserv, Message, Sender
from emails.PyHighcharts import Highchart

def __chart_total_sent(listserv, **kwarg_filters):
	series = [[str(sender.name), sender.total_sent] for sender in Sender.objects.filter(**kwarg_filters) if sender.total_sent > 1]
	chart = Highchart()
	chart.title("Total Emails Sent")
	chart.add_data_set(series, series_type="pie", name="")
	return chart.generate()

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