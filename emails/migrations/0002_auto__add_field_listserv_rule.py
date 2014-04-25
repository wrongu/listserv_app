# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Listserv.rule'
        db.add_column(u'emails_listserv', 'rule',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Listserv.rule'
        db.delete_column(u'emails_listserv', 'rule')


    models = {
        u'emails.listserv': {
            'Meta': {'object_name': 'Listserv'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listserv_address': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'rule': ('django.db.models.fields.TextField', [], {}),
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