# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'RMDBEntry.has_traces'
        db.add_column('repository_rmdbentry', 'has_traces', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'RMDBEntry.has_traces'
        db.delete_column('repository_rmdbentry', 'has_traces')


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
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'has_traces': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publication': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.Publication']"}),
            'revision_status': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'rmdb_id': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        }
    }

    complete_apps = ['repository']
