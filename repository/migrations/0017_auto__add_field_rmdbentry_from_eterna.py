# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'RMDBEntry.from_eterna'
        db.add_column('repository_rmdbentry', 'from_eterna', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'RMDBEntry.from_eterna'
        db.delete_column('repository_rmdbentry', 'from_eterna')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'repository.constructsection': {
            'Meta': {'object_name': 'ConstructSection'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.RMDBEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mutpos': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'offset': ('django.db.models.fields.IntegerField', [], {}),
            'seqpos': ('django.db.models.fields.TextField', [], {}),
            'sequence': ('django.db.models.fields.TextField', [], {}),
            'structure': ('django.db.models.fields.TextField', [], {}),
            'xsel': ('django.db.models.fields.TextField', [], {'blank': 'True'})
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
            'structure': ('django.db.models.fields.TextField', [], {'null': 'True'}),
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
        'repository.newsitem': {
            'Meta': {'object_name': 'NewsItem'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '400', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {})
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
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'datacount': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'from_eterna': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'has_traces': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'publication': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['repository.Publication']"}),
            'revision_status': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'rmdb_id': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'version': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['repository']
