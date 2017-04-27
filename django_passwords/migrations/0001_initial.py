import django.db.models.deletion
from django.db import migrations, models


def create_default_backend(apps, schema_editor):
	PasswordBackend = apps.get_model("django_passwords", "PasswordBackend")

	db_alias = schema_editor.connection.alias

	if not len(PasswordBackend.objects.using(db_alias).all()):
		PasswordBackend.objects.using(db_alias).bulk_create([
			PasswordBackend(order=1, url="db://"),
		])

class Migration(migrations.Migration):

	initial = True

	dependencies = [
	]

	operations = [
		migrations.CreateModel(
			name='PasswordBackend',
			fields=[
				('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
				('order', models.IntegerField(verbose_name='order')),
				('url', models.URLField(verbose_name='URL')),
				('copy_passwords_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='django_passwords.PasswordBackend', verbose_name='Copy passwords to')),
			],
			options={
				'ordering': ['order'],
			},
		),
		migrations.RunPython(create_default_backend, migrations.RunPython.noop),
	]
