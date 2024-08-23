from django.db import models


class Registration(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)
    blood_group = models.CharField(max_length=5)
    role = models.CharField(max_length=20)
    

    class Meta:
        db_table = 'registrations'
def __str__(self):
        return f"{self.first_name} {self.last_name}"