# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Listserv'
        db.create_table(u'emails_listserv', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('listserv_address', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal(u'emails', ['Listserv'])

        # Adding model 'Sender'
        db.create_table(u'emails_sender', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('total_sent', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'emails', ['Sender'])

        # Adding model 'Message'
        db.create_table(u'emails_message', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emails.Sender'])),
            ('listserv', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emails.Listserv'])),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('length', self.gf('django.db.models.fields.IntegerField')()),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
            ('thread', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal(u'emails', ['Message'])


    def backwards(self, orm):
        # Deleting model 'Listserv'
        db.delete_table(u'emails_listserv')

        # Deleting model 'Sender'
        db.delete_table(u'emails_sender')

        # Deleting model 'Message'
        db.delete_table(u'emails_message')


    models = {
        u'emails.listserv': {
            'Meta': {'object_name': 'Listserv'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listserv_address': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'emails.message': {
            'Meta': {'object_name': 'Message'},
            'content': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {}),
            'listserv': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['emails.Listserv']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['emails.Sender']"}),
            'thread': ('django.db.models.fields.BigIntegerField', [], {}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        u'emails.sender': {
            'Meta': {'object_name': 'Sender'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'total_sent': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['emails']