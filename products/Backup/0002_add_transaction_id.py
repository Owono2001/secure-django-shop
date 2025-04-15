from django.db import migrations, models
import uuid

def gen_uuid(apps, schema_editor):
    Order = apps.get_model('products', 'Order')
    for order in Order.objects.all():
        while True:
            new_id = uuid.uuid4().hex
            if not Order.objects.filter(transaction_id=new_id).exists():
                order.transaction_id = new_id
                order.save(update_fields=['transaction_id'])
                break

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0001_initial'),  # Replace with your actual previous migration
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(max_length=32, null=True, unique=False),
        ),
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='order',
            name='transaction_id',
            field=models.CharField(default=uuid.uuid4, max_length=32, unique=True),
        ),
    ]