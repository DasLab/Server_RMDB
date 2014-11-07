# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Publication'
        db.create_table('repository_publication', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.TextField')()),
            ('authors', self.gf('django.db.models.fields.TextField')()),
            ('pubmed_id', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('repository', ['Publication'])

        # Adding model 'RMDBEntry'
        db.create_table('repository_rmdbentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('comments', self.gf('django.db.models.fields.TextField')()),
            ('publication', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repository.Publication'])),
            ('authors', self.gf('django.db.models.fields.TextField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('datacount', self.gf('django.db.models.fields.IntegerField')()),
            ('constructcount', self.gf('django.db.models.fields.IntegerField')()),
            ('revision_status', self.gf('django.db.models.fields.CharField')(max_length=3)),
        ))
        db.send_create_signal('repository', ['RMDBEntry'])

        # Adding model 'ConstructSection'
        db.create_table('repository_constructsection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repository.RMDBEntry'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sequence', self.gf('django.db.models.fields.TextField')()),
            ('offset', self.gf('django.db.models.fields.IntegerField')()),
            ('xsel', self.gf('django.db.models.fields.TextField')()),
            ('seqpos', self.gf('django.db.models.fields.TextField')()),
            ('mutpos', self.gf('django.db.models.fields.TextField')()),
            ('data_type', self.gf('django.db.models.fields.TextField')()),
            ('structure', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('repository', ['ConstructSection'])

        # Adding model 'DataSection'
        db.create_table('repository_datasection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('construct_section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repository.ConstructSection'])),
            ('trace', self.gf('django.db.models.fields.TextField')()),
            ('xsel', self.gf('django.db.models.fields.TextField')()),
            ('values', self.gf('django.db.models.fields.TextField')()),
            ('errors', self.gf('django.db.models.fields.TextField')()),
            ('seqpos', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('repository', ['DataSection'])

        # Adding model 'EntryAnnotation'
        db.create_table('repository_entryannotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repository.RMDBEntry'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('repository', ['EntryAnnotation'])

        # Adding model 'ConstructAnnotation'
        db.create_table('repository_constructannotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repository.ConstructSection'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('repository', ['ConstructAnnotation'])

        # Adding model 'DataAnnotation'
        db.create_table('repository_dataannotation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['repository.DataSection'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('repository', ['DataAnnotation'])


    def backwards(self, orm):
        
        # Deleting model 'Publication'
        db.delete_table('repository_publication')

        # Deleting model 'RMDBEntry'
        db.delete_table('repository_rmdbentry')

        # Deleting model 'ConstructSection'
        db.delete_table('repository_constructsection')

        # Deleting model 'DataSection'
        db.delete_table('repository_datasection')

        # Deleting model 'EntryAnnotation'
        db.delete_table('repository_entryannotation')

        # Deleting model 'ConstructAnnotation'
        db.delete_table('repository_constructannotation')

        # Deleting model 'DataAnnotation'
        db.delete_table('repository_dataannotation')


    models = {
        'repository.constructannotation': {
            'Meta': {'object_name': 'ConstructAnnotation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.ConstructSection']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'repository.constructsection': {
            'Meta': {'object_name': 'ConstructSection'},
            'data_type': ('django.db.models.fields.TextField', [], {}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.RMDBEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mutpos': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'offset': ('django.db.models.fields.IntegerField', [], {}),
            'seqpos': ('django.db.models.fields.TextField', [], {}),
            'sequence': ('django.db.models.fields.TextField', [], {}),
            'structure': ('django.db.models.fields.TextField', [], {}),
            'xsel': ('django.db.models.fields.TextField', [], {})
        },
        'repository.dataannotation': {
            'Meta': {'object_name': 'DataAnnotation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.DataSection']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'repository.datasection': {
            'Meta': {'object_name': 'DataSection'},
            'construct_section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.ConstructSection']"}),
            'errors': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seqpos': ('django.db.models.fields.TextField', [], {}),
            'trace': ('django.db.models.fields.TextField', [], {}),
            'values': ('django.db.models.fields.TextField', [], {}),
            'xsel': ('django.db.models.fields.TextField', [], {})
        },
        'repository.entryannotation': {
            'Meta': {'object_name': 'EntryAnnotation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.RMDBEntry']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'repository.publication': {
            'Meta': {'object_name': 'Publication'},
            'authors': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pubmed_id': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'repository.rmdbentry': {
            'Meta': {'object_name': 'RMDBEntry'},
            'authors': ('django.db.models.fields.TextField', [], {}),
            'comments': ('django.db.models.fields.TextField', [], {}),
            'constructcount': ('django.db.models.fields.IntegerField', [], {}),
            'datacount': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publication': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.Publication']"}),
            'revision_status': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['repository']
