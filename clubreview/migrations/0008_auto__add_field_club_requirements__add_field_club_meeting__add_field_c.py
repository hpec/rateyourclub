# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Club.requirements'
        db.add_column(u'clubreview_club', 'requirements',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Club.meeting'
        db.add_column(u'clubreview_club', 'meeting',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Club.address'
        db.add_column(u'clubreview_club', 'address',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Club.activity_summary'
        db.add_column(u'clubreview_club', 'activity_summary',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Club.requirements'
        db.delete_column(u'clubreview_club', 'requirements')

        # Deleting field 'Club.meeting'
        db.delete_column(u'clubreview_club', 'meeting')

        # Deleting field 'Club.address'
        db.delete_column(u'clubreview_club', 'address')

        # Deleting field 'Club.activity_summary'
        db.delete_column(u'clubreview_club', 'activity_summary')


    models = {
        u'clubreview.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'clubreview.club': {
            'Meta': {'object_name': 'Club'},
            'SGID': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'activity_summary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'callink_permalink': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clubreview.Category']", 'null': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'default': 'None', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'facebook_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'hit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'meeting': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'requirements': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'review_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clubreview.School']"}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'clubreview.event': {
            'Meta': {'object_name': 'Event'},
            'club': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['clubreview.Club']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'clubreview.review': {
            'Meta': {'object_name': 'Review'},
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clubreview.Club']"}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_posted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['clubreview.Event']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ratings': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'clubreview.school': {
            'Meta': {'object_name': 'School'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['clubreview']