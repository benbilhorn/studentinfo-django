from django.db import models

# Create your models here.


class Studentdetails(models.Model):
    studentid = models.IntegerField()
    firstname = models.CharField(max_length=500)
    lastname = models.CharField(max_length=500)
    MAJOR_CHOICES = [
        ('IT', 'I.T.'),
        ('PHY', 'Physics'),
        ('CHM', 'Chemistry'),
        ('ST', 'Statistics'),
        ('MKT', 'Marketing'),
    ]
    major = models.CharField(max_length=500, choices=MAJOR_CHOICES)
    YEAR_IN_SCHOOL_CHOICES = [
        ('SO', 'Sophomore'),
        ('JR', 'Junior'),
        ('SR', 'Senior'),
    ]
    year = models.CharField(max_length=500, choices=YEAR_IN_SCHOOL_CHOICES)
    GPA = models.DecimalField(max_digits=2, decimal_places=1)


class Coursedetails(models.Model):
    courseid = models.IntegerField()
    coursename = models.CharField(max_length=500)
    coursetitle = models.CharField(max_length=500)
    sectioncode = models.IntegerField()
    coursedepartment = models.CharField(max_length=500)
    instructorname = models.CharField(max_length=500)


class Studentenrollment(models.Model):
    courseid = models.IntegerField()
    studentid = models.IntegerField()
