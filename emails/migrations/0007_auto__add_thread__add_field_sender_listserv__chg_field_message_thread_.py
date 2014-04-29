# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Message', fields ['gm_id']
        db.delete_unique(u'emails_message', ['gm_id'])

        # Adding model 'Thread'
        db.create_table(u'emails_thread', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('thread_id', self.gf('django.db.models.fields.BigIntegerField')()),
            ('start_message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='thread_start', to=orm['emails.Message'])),
            ('end_message', self.gf('django.db.models.fields.related.ForeignKey')(related_name='thread_end', to=orm['emails.Message'])),
            ('length', self.gf('django.db.models.fields.IntegerField')()),
            ('participants', self.gf('django.db.models.fields.IntegerField')()),
            ('score', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal(u'emails', ['Thread'])

        # Adding field 'Sender.listserv'
        db.add_column(u'emails_sender', 'listserv',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['emails.Listserv']),
                      keep_default=False)


        # Renaming column for 'Message.thread' to match new field type.
        db.rename_column(u'emails_message', 'thread', 'thread_id')
        # Changing field 'Message.thread'
        db.alter_column(u'emails_message', 'thread_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['emails.Thread']))
        # Adding index on 'Message', fields ['thread']
        db.create_index(u'emails_message', ['thread_id'])


    def backwards(self, orm):
        # Removing index on 'Message', fields ['thread']
        db.delete_index(u'emails_message', ['thread_id'])

        # Deleting model 'Thread'
        db.delete_table(u'emails_thread')

        # Deleting field 'Sender.listserv'
        db.delete_column(u'emails_sender', 'listserv_id')


        # Renaming column for 'Message.thread' to match new field type.
        db.rename_column(u'emails_message', 'thread_id', 'thread')
        # Changing field 'Message.thread'
        db.alter_column(u'emails_message', 'thread', self.gf('django.db.models.fields.BigIntegerField')())
        # Adding unique constraint on 'Message', fields ['gm_id']
        db.create_unique(u'emails_message', ['gm_id'])


    models = {
        u'emails.listserv': {
            'Meta': {'object_name': 'Listserv'},
            'folder': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listserv_address': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        u'emails.message': {
            'Meta': {'unique_together': "(('sender', 'time'),)", 'object_name': 'Message'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'gm_id': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {}),
            'listserv': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['emails.Listserv']"}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['emails.Sender']"}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['emails.Thread']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        u'emails.sender': {
            'Meta': {'object_name': 'Sender'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listserv': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['emails.Listserv']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'total_sent': ('django.db.models.fields.IntegerField', [], {})
        },
        u'emails.thread': {
            'Meta': {'object_name': 'Thread'},
            'end_message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thread_end'", 'to': u"orm['emails.Message']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.IntegerField', [], {}),
            'participants': ('django.db.models.fields.IntegerField', [], {}),
            'score': ('django.db.models.fields.FloatField', [], {}),
            'start_message': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'thread_start'", 'to': u"orm['emails.Message']"}),
            'thread_id': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['emails']