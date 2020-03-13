# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AbcHistory(models.Model):
    creation_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    user = models.CharField(max_length=40, blank=True, null=True)
    query_sm_all = models.ForeignKey('QuerySmAll', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'abc_history'


class AlembicVersion(models.Model):
    version_num = models.CharField(primary_key=True, max_length=32)

    class Meta:
        managed = False
        db_table = 'alembic_version'


class Dicts(models.Model):
    creation_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    path_input = models.CharField(max_length=500, blank=True, null=True)
    path_output = models.CharField(max_length=500, blank=True, null=True)
    checksum = models.CharField(max_length=32, blank=True, null=True)
    type = models.CharField(max_length=20, blank=True, null=True)
    last_modified = models.DateTimeField(blank=True, null=True)
    path_pickle = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dicts'


class PlWm(models.Model):
    creation_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    nazwa = models.CharField(max_length=500, blank=True, null=True)
    jedn_miary = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pl_wm'


class QuerySmAll(models.Model):
    creation_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    path = models.TextField(blank=True, null=True)
    query_sm = models.TextField(blank=True, null=True)
    ip = models.CharField(max_length=17, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'query_sm_all'

