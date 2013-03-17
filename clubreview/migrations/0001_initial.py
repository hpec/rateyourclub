# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'School'
        db.create_table('clubreview_school', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('clubreview', ['School'])

        # Adding model 'Category'
        db.create_table('clubreview_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('clubreview', ['Category'])

        # Adding model 'Club'
        db.create_table('clubreview_club', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('school', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clubreview.School'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clubreview.Category'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('abbrev', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('contact_person', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('contact_phone', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('contact_email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('introduction', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('review_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('hit', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('clubreview', ['Club'])

        # Adding model 'Event'
        db.create_table('clubreview_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('clubreview', ['Event'])

        # Adding M2M table for field club on 'Event'
        db.create_table('clubreview_event_club', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('event', models.ForeignKey(orm['clubreview.event'], null=False)),
            ('club', models.ForeignKey(orm['clubreview.club'], null=False))
        ))
        db.create_unique('clubreview_event_club', ['event_id', 'club_id'])

        # Adding model 'Review'
        db.create_table('clubreview_review', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('club', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clubreview.Club'])),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['clubreview.Event'], null=True, blank=True)),
            ('ratings', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('anonymous', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_posted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal('clubreview', ['Review'])


    def backwards(self, orm):
        # Deleting model 'School'
        db.delete_table('clubreview_school')

        # Deleting model 'Category'
        db.delete_table('clubreview_category')

        # Deleting model 'Club'
        db.delete_table('clubreview_club')

        # Deleting model 'Event'
        db.delete_table('clubreview_event')

        # Removing M2M table for field club on 'Event'
        db.delete_table('clubreview_event_club')

        # Deleting model 'Review'
        db.delete_table('clubreview_review')


    models = {
        'clubreview.category': {
            'Meta': {'object_name': 'Category'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'clubreview.club': {
            'Meta': {'object_name': 'Club'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clubreview.Category']", 'null': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'contact_person': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'hit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'introduction': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'review_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'school': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clubreview.School']"}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'clubreview.event': {
            'Meta': {'object_name': 'Event'},
            'club': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['clubreview.Club']", 'symmetrical': 'False'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'clubreview.review': {
            'Meta': {'object_name': 'Review'},
            'anonymous': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'club': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clubreview.Club']"}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'date_posted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['clubreview.Event']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ratings': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'clubreview.school': {
            'Meta': {'object_name': 'School'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['clubreview']