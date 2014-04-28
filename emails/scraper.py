# email scraper based on mailbot

import os, sys
sys.path.append("/home/richard/code/listserv_app")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "listserv_app.settings")

import email
import imapclient
from time import time, sleep
from dateutil.parser import parse as date_parse
import datetime
from emails.models import Listserv, Sender, Message
from email_creds import *

class Gmail(object):

	HOST = gmail_server
	BATCH_SIZE = 64

	def __init__(self, username, password, folder="inbox"):
		self.client = imapclient.IMAPClient(self.HOST, ssl=True)
		self.client.login(username, password)
		self.str = "%s: %s" % (username, folder)
		try:
			self.client.select_folder(folder)
		except Exception:
			print folder, "is not a valid gmail folder for", username
			raise

	def __str__(self):
		return self.str

	def messages(self, unread_only=True, since=None):
		"""A generator function which returns a email objects
		"""
		# two-part transaction. first we get message ids according to a query
		# then we fetch content of those ids

		# Part I: Ids
		filters = []
		if unread_only:
			filters.extend(['Unseen', 'Unflagged'])
		if since:
			filters.append('SINCE "%s"' % (since.strftime("%d-%b-%Y")))
		# query server for ids matching filters
		message_ids = self.client.search(filters)

		# Part II: fetch (both message body RFC822 and thread id X-GM-THRID)
		# because it may be large, get results in batches
		for batch in range(int(len(message_ids) / self.BATCH_SIZE)):
			# compute start- and end-indices of this batch
			start = batch*self.BATCH_SIZE
			end = min(len(message_ids), 1 + (batch+1)*self.BATCH_SIZE)
			# splice out the ids of this batch
			batch_ids = message_ids[start:end]
			print "fetching batch..."
			start = time()
			# request message data for this batch of ids
			response = self.client.fetch(batch_ids, ['RFC822', 'X-GM-THRID', 'X-GM-MSGID'])
			print "fetched in %f seconds" % (time() - start)
			for uid, msg in response.iteritems():
				try:
					msg_obj = email.message_from_string(msg['RFC822'])
					thread = msg['X-GM-THRID']
					msg_id = msg['X-GM-MSGID']
				except Exception:
					continue
				yield (msg_obj, thread, msg_id)

def __get_listserv_address(email_obj):
	dest = email_obj.get('To')
	return Listserv.objects.filter(listserv_address=dest).first()

def __get_sender_name_email(email_obj):
	info = email_obj.get('From')
	# 'From' generally contains "Joe Shmoe <joe.shmoe@example.com>"
	# So, we split on " <" to break name from email
	parts = info.split(" <")
	name = parts[0]
	address = parts[1].split(">")[0]
	return name, address

def __remove_quote_lines(payload):
	lines = payload.split('\r\n')
	return '\n'.join(filter(lambda l: not l.startswith(">"), lines))

def email_to_database(email_obj, thread_id, message_id):
	# check if listserv is ok
	listserv = __get_listserv_address(email_obj)
	if listserv is None:
		return

	# check if message already accounted for
	if Message.objects.filter(gm_id=message_id).first():
		return

	##################
	## SENDER TABLE ##
	##################
	sender_name, sender_email = __get_sender_name_email(email_obj)
	sender = Sender.objects.filter(name=sender_name, email=sender_email).first()
	if not sender:
		# check for email only
		sender = Sender.objects.filter(email=sender_email).first()
		# if found, update name (to longer one)
		if sender:
			if len(sender_name) > len(sender.name):
				print "updating name '%s' to '%s'" % (sender.name, sender_name)
				sender.name = sender_name
		else:
			# must be new! create 'em
			print "creating new sender: %s <%s>" % (sender_name, sender_email)
			sender = Sender(name=sender_name, email=sender_email, total_sent=0)
	# record the new email in sender's total
	sender.total_sent += 1
	# saving gives the sender an id (auto-incremented)
	# so this needs to be done before creating the message instance
	# (if not creating one anew, then this updates the object)
	sender.save()

	###################
	## MESSAGE TABLE ##
	###################
	subject = email_obj.get('Subject') or ""
	content = email_obj.get_payload()
	length = len(__remove_quote_lines(content))
	time = date_parse(email_obj.get('Date'))
	# create and save the new message object
	message = Message(sender=sender, listserv=listserv, title=subject, content=content, length=length, time=time, thread=thread_id, gm_id=message_id)
	message.save()
	print "saved message", message

if __name__ == '__main__':
	INTERVAL_MINS = 5 # same as zapier
	scrapers = [(Gmail(gmail_user, gmail_passwd, l.folder), l) for l in Listserv.objects.all()]

	while True:
		for g, l in scrapers:
			latest = Message.objects.filter(listserv=l).order_by('-time').first()
			if latest:
				latest = latest.time # get the datetime object
			else: # the first-time running it, there is no latest. set to way-back-when.
				latest = datetime.datetime(year=2000, month=01, day=01)
			print "getting emails for", g, "since", latest
			for m in g.messages(unread_only=False, since=latest):
				try:
					email_to_database(*m)
				except KeyboardInterrupt:
					raise # pass it on
				except Exception, e:
					print e
		sleep(INTERVAL_MINS * 60)
