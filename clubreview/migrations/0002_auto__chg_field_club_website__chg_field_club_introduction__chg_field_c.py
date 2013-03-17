# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Club.website'
        db.alter_column('clubreview_club', 'website', self.gf('django.db.models.fields.URLField')(max_length=200, null=True))

        # Changing field 'Club.introduction'
        db.alter_column('clubreview_club', 'introduction', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Club.abbrev'
        db.alter_column('clubreview_club', 'abbrev', self.gf('django.db.models.fields.CharField')(max_length=80, null=True))

        # Changing field 'Club.contact_person'
        db.alter_column('clubreview_club', 'contact_person', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Club.contact_phone'
        db.alter_column('clubreview_club', 'contact_phone', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))

        # Changing field 'Event.location'
        db.alter_column('clubreview_event', 'location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Review.ratings'
        db.alter_column('clubreview_review', 'ratings', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Review.content'
        db.alter_column('clubreview_review', 'content', self.gf('django.db.models.fields.TextField')(null=True))

    def backwards(self, orm):

        # Changing field 'Club.website'
        db.alter_column('clubreview_club', 'website', self.gf('django.db.models.fields.URLField')(default='', max_length=200))

        # Changing field 'Club.introduction'
        db.alter_column('clubreview_club', 'introduction', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Club.abbrev'
        db.alter_column('clubreview_club', 'abbrev', self.gf('django.db.models.fields.CharField')(default=1, max_length=80))

        # Changing field 'Club.contact_person'
        db.alter_column('clubreview_club', 'contact_person', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Club.contact_phone'
        db.alter_column('clubreview_club', 'contact_phone', self.gf('django.db.models.fields.CharField')(default='', max_length=10))

        # Changing field 'Event.location'
        db.alter_column('clubreview_event', 'location', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Review.ratings'
        db.alter_column('clubreview_review', 'ratings', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Review.content'
        db.alter_column('clubreview_review', 'content', self.gf('django.db.models.fields.TextField')(default=''))

    models = {
        'clubreview.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'clubreview.club': {
            'Meta': {'object_name': 'Club'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clubreview.Category']", 'null': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'hit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'review_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clubreview.School']"}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        'clubreview.event': {
            'Meta': {'object_name': 'Event'},
            'club': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['clubreview.Club']", 'symmetrical': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'clubreview.review': {
            'Meta': {'object_name': 'Review'},
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clubreview.Club']"}),
            'content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date_posted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clubreview.Event']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ratings': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'clubreview.school': {
            'Meta': {'object_name': 'School'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['clubreview']