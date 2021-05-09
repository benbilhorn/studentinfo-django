from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg, Count
from studentinfo.models import Studentdetails, Coursedetails, Studentenrollment
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import connection


# Create your views here.


@login_required
def home(request):
    request.session['successflag'] = "Select a course to enroll in"
    cursorobj = connection.cursor()
    cursorobj.execute(
        "SELECT c.coursetitle, Count(s.courseid) AS coursepopularity FROM studentinfo.studentinfo_studentenrollment AS s INNER JOIN studentinfo.studentinfo_coursedetails AS c ON s.courseid = c.courseid GROUP BY s.courseid ORDER BY coursepopularity DESC")
    chartdata = dictfetchall(cursorobj)
    cursorobj.execute(
        "SELECT COUNT(s.year) as countyear, s.year FROM studentinfo.studentinfo_studentdetails AS s GROUP BY s.year;")
    yearchartdata = dictfetchall(cursorobj)
    chartdataasdict = chartdata[0:5]
    studentgpa = Studentdetails.objects.aggregate(average=Avg('GPA'))
    studentgpavalue = float(studentgpa.get('average'))
    roundedgpa = round(studentgpavalue, 1)
    numberofstudents = Studentdetails.objects.aggregate(totalstudents=Count('firstname'))
    numberofcourses = Coursedetails.objects.aggregate(totalcourses=Count('courseid'))
    context = {
        'studentgpa': roundedgpa,
        'numberofstudents': numberofstudents,
        'chartdataasdict': chartdataasdict,
        'yearchartdata': yearchartdata,
        'numberofcourses': numberofcourses
    }
    return render(request, 'studentinfo/home.html', context)


@login_required
def studentdetails(request):
    studentdata = Studentdetails.objects.all().order_by('studentid')
    paginator = Paginator(studentdata, 10)
    page = request.GET.get('page')
    minidata = paginator.get_page(page)
    context = {'data': minidata}
    return render(request, 'studentinfo/studentdetails.html', context)


@login_required
def coursedetails(request):
    coursedata = Coursedetails.objects.all().order_by('courseid')
    paginator = Paginator(coursedata, 10)
    page = request.GET.get('page')
    minidata = paginator.get_page(page)
    context = {'data': minidata}
    return render(request, 'studentinfo/coursedetails.html', context)


# def studentenrollment(request):
#    studentdata = Studentdetails.objects.all()
#    coursedata = Coursedetails.objects.all()
#    enrollmentdata = Studentenrollment.objects.all()
#    context = {'studentdata':studentdata, 'coursedata': coursedata, 'enrollmentdata': enrollmentdata}
#    return render(request, 'studentinfo/studentenrollment.html', context)
@login_required
def saveenrollment(request):
    if ('studentid' in request.GET and 'courseid' not in request.GET):
        request.session['studentid'] = request.GET.get('studentid')
    if ('studentid' and 'courseid' in request.GET):
        studentid = request.GET.get('studentid')
        courseid = request.GET.get('courseid')
        cursorobj = connection.cursor()
        cursorobj.execute(
            "SELECT COUNT(studentinfo.studentinfo_studentenrollment.studentid) AS coursecounter FROM studentinfo.studentinfo_studentenrollment WHERE studentinfo.studentinfo_studentenrollment.studentid = %s" % studentid)
        coursecount = dictfetchall(cursorobj)
        cursorobj.execute(
            "SELECT COUNT(studentinfo.studentinfo_studentenrollment.courseid) AS courseid, studentinfo.studentinfo_studentenrollment.studentid as studentid FROM studentinfo.studentinfo_studentenrollment WHERE courseid = %s AND studentid = %s" % (courseid, studentid))
        enrolledcheck = dictfetchall(cursorobj)
        enrolledcheckasdict = enrolledcheck[0]
        coursecountasdict = coursecount[0]
        if coursecountasdict.get('coursecounter') < 3 and enrolledcheckasdict.get('courseid') < 1:
            enrollmentobj = Studentenrollment(studentid=studentid, courseid=courseid)
            enrollmentobj.save()
            request.session['successflag'] = "Enrollment successful!"
        elif coursecountasdict.get('coursecounter') >= 3:
            request.session['successflag'] = "Student already enrolled in full course load"
        elif enrolledcheckasdict.get('courseid') >= 1:
            request.session['successflag'] = "Student is already enrolled in that course"
    return HttpResponse('Success')

@login_required
def studentenrollment(request):
    cursorobj = connection.cursor()
    studentdata = Studentdetails.objects.all()
    coursedata = Coursedetails.objects.all()
    if 'studentid' in request.session:
        filterstudentid = request.session['studentid']
        cursorobj.execute(
            "SELECT CONCAT(studentinfo.studentinfo_studentdetails.firstname, ' ', studentinfo.studentinfo_studentdetails.lastname) AS studentname, studentinfo.studentinfo_coursedetails.coursetitle AS coursetitle FROM studentinfo.studentinfo_studentenrollment INNER JOIN studentinfo.studentinfo_studentdetails ON studentinfo.studentinfo_studentenrollment.studentid =  studentinfo.studentinfo_studentdetails.studentid  INNER JOIN studentinfo.studentinfo_coursedetails ON studentinfo.studentinfo_studentenrollment.courseid = studentinfo.studentinfo_coursedetails.courseid WHERE studentinfo.studentinfo_studentenrollment.studentid = %s" % filterstudentid)
        enrollmentdata = dictfetchall(cursorobj)
        cursorobj.execute(
            "SELECT CONCAT(studentinfo.studentinfo_studentdetails.firstname, ' ', studentinfo.studentinfo_studentdetails.lastname) AS studentname FROM studentinfo.studentinfo_studentdetails  WHERE studentinfo.studentinfo_studentdetails.studentid = %s" % filterstudentid)
        filterstudentname = dictfetchall(cursorobj)
        filterstudentnameasdict = filterstudentname[0]
        request.session['filterstudentname'] = filterstudentnameasdict.get('studentname')
    else:
        cursorobj.execute(
            "SELECT CONCAT(studentinfo.studentinfo_studentdetails.firstname, ' ', studentinfo.studentinfo_studentdetails.lastname) AS studentname, studentinfo.studentinfo_coursedetails.coursetitle AS coursetitle FROM studentinfo.studentinfo_studentenrollment INNER JOIN studentinfo.studentinfo_studentdetails ON studentinfo.studentinfo_studentenrollment.studentid =  studentinfo.studentinfo_studentdetails.studentid  INNER JOIN studentinfo.studentinfo_coursedetails ON studentinfo.studentinfo_studentenrollment.courseid = studentinfo.studentinfo_coursedetails.courseid")
        enrollmentdata = dictfetchall(cursorobj)
    paginator = Paginator(enrollmentdata, 10)
    page = request.GET.get('page')
    minidata = paginator.get_page(page)
    context = {'studentdata': studentdata, 'coursedata': coursedata, 'enrollmentdata': minidata}
    return render(request, 'studentinfo/studentenrollment.html', context)


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
