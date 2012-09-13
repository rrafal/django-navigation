# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Sitemap'
        db.create_table('navigation_sitemap', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('navigation', ['Sitemap'])

        # Adding model 'SitemapItem'
        db.create_table('navigation_sitemapitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sitemap', self.gf('django.db.models.fields.related.ForeignKey')(related_name='item_set', to=orm['navigation.Sitemap'])),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, on_delete=models.SET_NULL, to=orm['navigation.SitemapItem'])),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('status', self.gf('django.db.models.fields.CharField')(default='enabled', max_length=16)),
        ))
        db.send_create_signal('navigation', ['SitemapItem'])

        # Adding model 'Menu'
        db.create_table('navigation_menu', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('sitemap', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='menu_set', null=True, to=orm['navigation.Sitemap'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('navigation', ['Menu'])

        # Adding model 'MenuItem'
        db.create_table('navigation_menuitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('my_parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['navigation.MenuItem'], null=True, db_column='parent_id', blank=True)),
            ('menu', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['navigation.Menu'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('sync_title', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('status', self.gf('django.db.models.fields.CharField')(default='auto', max_length=16)),
            ('sitemap_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['navigation.SitemapItem'], null=True, blank=True)),
            ('sitemap_item_status', self.gf('django.db.models.fields.CharField')(max_length=16, null=True)),
        ))
        db.send_create_signal('navigation', ['MenuItem'])


    def backwards(self, orm):
        # Deleting model 'Sitemap'
        db.delete_table('navigation_sitemap')

        # Deleting model 'SitemapItem'
        db.delete_table('navigation_sitemapitem')

        # Deleting model 'Menu'
        db.delete_table('navigation_menu')

        # Deleting model 'MenuItem'
        db.delete_table('navigation_menuitem')


    models = {
        'navigation.menu': {
            'Meta': {'ordering': "['name']", 'object_name': 'Menu'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'sitemap': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'menu_set'", 'null': 'True', 'to': "orm['navigation.Sitemap']"})
        },
        'navigation.menuitem': {
            'Meta': {'ordering': "['order']", 'object_name': 'MenuItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['navigation.Menu']"}),
            'my_parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['navigation.MenuItem']", 'null': 'True', 'db_column': "'parent_id'", 'blank': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'sitemap_item': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['navigation.SitemapItem']", 'null': 'True', 'blank': 'True'}),
            'sitemap_item_status': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'auto'", 'max_length': '16'}),
            'sync_title': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'navigation.sitemap': {
            'Meta': {'object_name': 'Sitemap'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'navigation.sitemapitem': {
            'Meta': {'object_name': 'SitemapItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['navigation.SitemapItem']"}),
            'sitemap': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'item_set'", 'to': "orm['navigation.Sitemap']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'enabled'", 'max_length': '16'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['navigation']