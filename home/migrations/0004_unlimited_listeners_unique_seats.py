from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0003_roommembership_seat_number_alter_room_max_listeners"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="room",
            name="max_listeners",
        ),
        migrations.AddConstraint(
            model_name="roommembership",
            constraint=models.UniqueConstraint(
                fields=("room", "seat_number"),
                condition=models.Q(seat_number__isnull=False),
                name="unique_room_seat",
            ),
        ),
    ]
