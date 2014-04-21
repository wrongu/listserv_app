from django.shortcuts import render, redirect

__config = {
	'fiuh' : {
		'key' : '0Ar7wwOUxi3Y9dG9XX1ZLejlJdE9VRUJneFM4anhXQlE',
		'title' : 'Fi-Uh'
	},
	'aolocal' : {
		'key' : '0Ar7wwOUxi3Y9dGZNaHlkUnRZR25ySkgzU25JZkVHaHc',
		'title' : 'AO-Local'
	}
}

# Create your views here.
def stats(request, site='fiuh'):
	if site in __config:
		return render(request, "charts/stats.html", __config[site])
	else:
		return redirect('/fiuh')