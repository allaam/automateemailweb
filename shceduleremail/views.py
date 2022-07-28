import sched
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from matplotlib.style import context
from .models import Log, Shcedule, Cabang, DetailTransaksi, Log, Running, Login, Template
from .forms import FormShcedule, FormEmail, FormLogin, FormTemplate
from django.core.paginator import Paginator
from django.views.generic import View
from django.db.models import Sum
from .utils import render_to_pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.core.mail import EmailMultiAlternatives
from automateemail import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import *
from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date
import traceback 
from django.db.models.functions import TruncMonth
from django.db.models import Count
from django.db.models import Max
from django.db.models.functions import TruncMonth

# module import
# import shceduleremail.dashboard_module as module

# ---------------------------Package Comment---------------------------
# from numpy import trunc
# from pymysql import NULL
# from sqlalchemy import values
# from django.forms import inlineformset_factory
# from django.forms import modelformset_factory
# from django.urls import reverse
# from django.contrib.auth.decorators import login_required
# from django.urls import reverse_lazy
# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.models import User
# import requests
# from django.db.models.functions import ExtractYear, ExtractMonth
# import json
# ---------------------------------------------------------------------

#------------------
# Laman login admin -> 'templates/login.html'
#------------------
def login_admin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = Login.objects.filter(email = email)
        if user.exists():
            if user[0].password == password: 
                userlog = Login.objects.get(email = email)
                if userlog is not None:
                    login(request, userlog)
                    request.session['email'] = email
                    return HttpResponseRedirect('/dashboard')
                else:
                    return HttpResponseRedirect('/')
            else:
                return HttpResponseRedirect ('/')
        else:
            return HttpResponseRedirect ('/')
    else:
        return render(request, 'login.html', {})

#-------------
# Laman logout -> 'templates/index.html'
# ------------   
def logout_view(request):
    logout(request)
    return render(request, 'login.html', {})

#---------------
#laman dashboard -> 'templates/dashboard.html'
#---------------
def dashboard(request):
    # cek nilai session pada login
    if request.session.get('email') is None:
        return HttpResponseRedirect('/login')

    # module.dashboard_(request)
    # ambil data table schedule, dengan kolom
    schedule = Shcedule.objects.order_by('-running_id').values('running_id', 'waktu_eksekusi', 'jam_eksekusi', 'status', 'periodic', 'template', 'id_template', 'format_laporan').distinct()
    
    obj_t = Shcedule.objects.filter(status = True).order_by('running_id').values('running_id').distinct()
    obj_f = Shcedule.objects.filter(status = False).order_by('running_id').values('running_id').distinct()
    obj_true = obj_t.count()
    obj_false = obj_f.count()
    today = date.today()

    paginator = Paginator(schedule, 5)
    page_number = request.GET.get('page')
    schedule = paginator.get_page(page_number)

    template = Template.objects.values('nama_template', 'id_template')

    # --------------------------------------------------------------------
    # context sebagai wadah tapungan yang akan dilarikan ke dashboard.html
    #---------------------------------------------------------------------
    context = {
        'schedule': schedule,
        'obj_true': obj_true,
        'obj_false': obj_false,
        'today':today,
        'template':template,
    }

    return render(request, 'dashbord.html', context)
    
#--------------------------------
# buat penjadwalan email otomatis -> 'templates/schduler.html'
#--------------------------------
def scheduler(request):
    # cek session
    if request.session.get('email') is None:
        return HttpResponseRedirect('/login')  
    
    form = FormShcedule(request.POST)
    tomorrow = datetime.now()
    today = tomorrow.strftime("%Y-%m-%d")
    today2 = datetime.strptime(today, "%Y-%m-%d")
    template = Template.objects.all()

    if request.method == 'POST':
        periodic = request.POST.get('periodic')
        running_id = Running.objects.values('running_id')
        if form.is_valid():
            # jika periodik secara daily, maka insert penjadwalan, 
            # berdasarkan waktu saja.
            if periodic == 'daily':
                # waktu_eksekusi = request.POST.get('waktu_eksekusi')
                jam_eksekusi = request.POST.get('jam_eksekusi')
                status = True if form.data.get('status') == "on" else False
                terakhir_eksekusi = request.POST.get('terakhir_eksekusi')
                template = request.POST.get('template')
                format_laporan = request.POST.get('format_template')
                temp = Template.objects.values('template').filter(pk = template)
                periode = Template.objects.values('periode').filter(pk = template)
                print(periode)
                id_template = Template.objects.values('id_template').filter(pk = template)
                cabang = Cabang.objects.all()
                for cabang in cabang : 
                    form = Shcedule(jam_eksekusi = jam_eksekusi, status = status, periodic = periodic, template = temp, terakhir_eksekusi = terakhir_eksekusi, 
                                    running_id = running_id, email_penerima = cabang.email_cabang, kode_cabang = cabang.kode_cabang, waktu_eksekusi = today2, 
                                    periode = periode, id_template = id_template, format_laporan = format_laporan)
                    form.save()
                messages.success(request, 'Data berhasil ditambahkan' )
                obj = Running.objects.first()
                field_object = Running._meta.get_field('running_id')
                field_value = field_object.value_from_object(obj)
                field_value2 = field_value + 1
                print(field_value2)
                Running.objects.filter(idRunning = 1).update(running_id=field_value2) 
            # selain pengiriman secara periodik, maka insert penjadwalan
            # berdasarkan tanggal dan waktu.
            else : 
                waktu_eksekusi = request.POST.get('waktu_eksekusi')
                jam_eksekusi = request.POST.get('jam_eksekusi')
                status = True if form.data.get('status') == "on" else False
                terakhir_eksekusi = request.POST.get('terakhir_eksekusi')
                template = request.POST.get('template')
                format_laporan = request.POST.get('format_template')
                temp = Template.objects.values('template').filter(pk = template)
                periode = Template.objects.values('periode').filter(pk = template)
                print(periode)
                id_template = Template.objects.values('id_template').filter(pk = template)
                cabang = Cabang.objects.all()
                for cabang in cabang : 
                    form = Shcedule(waktu_eksekusi = waktu_eksekusi, jam_eksekusi = jam_eksekusi, status = status, periodic = periodic, template=temp, 
                                    terakhir_eksekusi = terakhir_eksekusi, running_id = running_id, email_penerima = cabang.email_cabang, 
                                    kode_cabang = cabang.kode_cabang, periode = periode, id_template = id_template, format_template = format_laporan)
                    form.save()
                messages.success(request, 'Data berhasil ditambahkan' )
                obj = Running.objects.first()
                field_object = Running._meta.get_field('running_id')
                field_value = field_object.value_from_object(obj)
                field_value2 = field_value + 1
                print(field_value2)
                Running.objects.filter(idRunning = 1).update(running_id=field_value2) 

    return HttpResponseRedirect('/dashboard')

# -----------------------------------------------------------------
# Pada laman table dashboard, ada beberapa fucntion sebagai berikut,
# -----------------------------------------------------------------

# 1. Status (Aktif dan Pending) -> 'templates/dashboard.html'
# ---------------------------------------
# function status aktif dan pending email 
# ---------------------------------------
# status aktif -> maka email akan dikirimkan
def status_on(request, running_id):
    statusUpdate = Shcedule.objects.filter(running_id = running_id)

    statusUpdate.update(status = True) #update tb status pada schedule menjadi true

    return HttpResponseRedirect('/dashboard/')

# status pending -> maka email tidak akan dikirim
def status_off(request, running_id):
    statusUpdate = Shcedule.objects.filter(running_id = running_id)

    statusUpdate.update(status = False) #update tb status pada schedule menjadi false

    return HttpResponseRedirect('/dashboard/')

# 2. Action - update -> 'templates/scheduler.html'
# ----------------------------------------
# function berupa update dari penjadwalan 
# ----------------------------------------
def update(request, running_id):
    schedule = Shcedule.objects.filter(running_id = running_id).first()
    if request.method == 'POST':
        periodic = request.POST.get('periodic')
        if periodic == 'daily':
            jam_eksekusi = request.POST.get('jam_eksekusi')
            status = True if request.POST.get('status') == 'on' else False
            waktu_eksekusi = request.POST.get('waktu_eksekusi')
            format_laporan = request.POST.get('format_template')
            template = request.POST.get('template')
            Shcedule.objects.filter(running_id = running_id).update( running_id=running_id, periodic = periodic, jam_eksekusi = jam_eksekusi, 
                                                                    template = template, status=status, waktu_eksekusi = waktu_eksekusi, format_laporan = format_laporan)
            messages.success(request, 'Data berhasil diperbarui' )
        else : 
            jam_eksekusi = request.POST.get('jam_eksekusi')
            status = True if request.POST.get('status') == 'on' else False
            waktu_eksekusi = request.POST.get('waktu_eksekusi')
            format_laporan = request.POST.get('format_template')
            template = request.POST.get('template')
            Shcedule.objects.filter(running_id = running_id).update( running_id=running_id, periodic = periodic, jam_eksekusi = jam_eksekusi, 
                                                                    waktu_eksekusi = waktu_eksekusi, template = template,status=status, format_laporan = format_laporan)
            messages.success(request, 'Data berhasil diperbarui' )

    return HttpResponseRedirect('/dashboard')

def update_schedule(request, running_id):
    schedule = Shcedule.objects.filter(running_id = running_id)
    template = Template.objects.all()
    running_id = Shcedule.objects.filter(running_id = running_id).values('running_id', 'waktu_eksekusi', 'jam_eksekusi', 'status', 'periodic', 'template', 'id_template', 'format_laporan').distinct()

    context = {
        'schedule' : schedule,
        'running_id' : running_id,
        'template' : template,
        'form' : form
    }
    return render(request, 'scheduler.html', context)

# 3. Action - delete -> 'templates/dashboard.html'
# ------------------
# function berupa delete penjadwalan
# ----------------------------------
def delete_schedule(self, running_id):
    delschedule = Shcedule.objects.filter(running_id = running_id)
    delschedule.delete()

    schedule = Shcedule.objects.all()

    context = {
        'schedule' : schedule
    }

    return HttpResponseRedirect('/dashboard/', context)

# 4. Lihat detail -> 'templates/detail-scheduler.html'
#-------------------------------------------------------------
# detail scheduler, yang mana sebagai riwayat pengiriman email
# ------------------------------------------------------------
def detail_scheduler(request, running_id):
    if request.session.get('email') is None:
        return HttpResponseRedirect('/login')  
    schedule = Shcedule.objects.filter(running_id = running_id)

    obj_t = Log.objects.filter(status = True)
    obj_f = Log.objects.filter(status = False)
    true = obj_t.filter(id_job__running_id__contains = running_id)
    false = obj_f.filter(id_job__running_id__contains = running_id)
    obj_true = true.count()
    obj_false = false.count()
    today = date.today()

    log = Log.objects.filter(running_id = running_id).order_by('-id_log')

    paginator = Paginator(log, 9)
    page_number = request.GET.get('page')
    log = paginator.get_page(page_number)

    running_id = Shcedule.objects.values('running_id')

    context = {
        'schedule': schedule,
        'obj_true': obj_true,
        'obj_false': obj_false,
        'today':today,
        'log' : log,
        'running_id':running_id,
    }

    return render(request, 'detail-scheduler.html', context)
# -----------------------------------------------------------------

# -----------------------------------
# function konfigurasi template email -> 'templates/configures_templates.html'
# -----------------------------------
def template_report(request):
    if request.session.get('email') is None:
        return HttpResponseRedirect('/login')  
    template = Template.objects.all()

    paginator = Paginator(template, 5)
    page_number = request.GET.get('page')
    templatepage = paginator.get_page(page_number)

    context = {
        'template' : template,
        'templatepage' : templatepage
    }

    return render(request,'configure_template.html', context)

# insert konfigurasi template
def configure_template(request):    
    form_temp = FormTemplate(request.POST)
    template = Template.objects.all()
    id_template = Template.objects.latest('id_template')
    field_object = Template._meta.get_field('id_template')
    field_value = field_object.value_from_object(id_template)
    field_value2 = field_value + 1

    if request.method == 'POST':
        if form_temp.is_valid():
            nama_template = request.POST.get('nama_template')
            template = request.POST.get('template')
            periode = request.POST.get('periode')
            form_temp = Template(id_template = field_value2, nama_template = nama_template, template = template ,periode = periode)
            form_temp.save()
    
    return HttpResponseRedirect('/template-report')

# hapus konfigurasi template report 
def delete_template(request, id_template):
    deletemplate = Template.objects.filter(id_template=id_template)
    deletemplate.delete()

    return HttpResponseRedirect('/template-report/', context)

# perbarui konfigurasi template report
def update_template(request, id_template):
    if request.method == 'POST':
        nama_template = request.POST.get('nama_template')
        template = request.POST.get('template')
        periode = request.POST.get('periode')
        Template.objects.filter(id_template = id_template).update(nama_template = nama_template, template = template, periode = periode)
        messages.success(request, 'Data berhasil diperbarui' )

    return HttpResponseRedirect('/template-report/', context)

def update_template_form(request, id_template):
    template = Template.objects.filter(id_template = id_template)

    context = {
        'template' : template,
        'id_template' : id_template,
        'formtemplate' : formtemplate,
    }

    return render(request, 'configure_template.html', context)
#-----------------------------------------------------------------------------

def form(request):
    schedule = Shcedule.objects.all()
    template = Template.objects.all()

    context = {
        'schedule': schedule,
        'template': template
    }

    return render(request, 'scheduler.html', context)

def formcabang(request):
    email = Cabang.objects.all()

    context = {
        'email': email
    }

    return render(request, 'tambah-email.html', context)

def formtemplate(request):
    template = Template.objects.all()

    context = {
        'template': template
    }

    return render(request, 'tambah-email.html', context)

# ----------------------------------------------
# Menampilkan laporan pdf yang telah dikirimkan.
# ----------------------------------------------
class GenerateReportLog(View):
    # Pada pembuatan pdf akan dilakukan inputan 2 kali dari database.
    # Database email dan database detail transaksi.
    def get(self, request, id_log,  *args, **kwargs):
        try:
            log = Log.objects.get(pk = id_log)
        except  Exception as e:
            traceback.format_exc()
        
        if log.id_job.template == 1:
            today = log.eksekusi
            startdate = today - timedelta(1)
            enddate = today + relativedelta(day=1)
            transaksi = DetailTransaksi.objects.filter(tanggal_transaksi__range=[enddate, startdate]).order_by('tanggal_transaksi')

            trunct_month = transaksi.annotate(month = TruncMonth('tanggal_transaksi')).values('month').annotate(c=Sum('total_harga')).values('month', 'c', 'kode_cabang').order_by('kode_cabang')
            sumTransaksi = transaksi.values('kode_cabang').order_by("kode_cabang").annotate(total_harga = Sum('total_harga'))
            month_date = transaksi.annotate(month=TruncMonth('tanggal_transaksi')).values_list('month')
            # print(log.id_job.kode_cabang)
            data = {
                'id' : log.id_job,
                'waktu' : log.eksekusi,
                'email_penerima' : log.email_penerima,
                'cabang' : log.id_job.kode_cabang,
                'running_id' :log.running_id,
                'trunct_month' :trunct_month,
                'month_date' : month_date,
                'detail_transaksi':transaksi,
                'today':today,
                'total_harga':sumTransaksi,
            }
            pdf = render_to_pdf('report.html', data)
            return HttpResponse(pdf, content_type="application/pdf")
        else: 
            today = log.eksekusi
            startdate = today - timedelta(1)
            enddate = today + relativedelta(day=1)

            transaksi = DetailTransaksi.objects.filter(tanggal_transaksi__range=[enddate, startdate]).order_by('tanggal_transaksi')
            sumTransaksi = transaksi.values("kode_cabang").order_by("kode_cabang").annotate(total_harga = Sum('total_harga'))
            # startdate = today - timedelta(1)

            # QueryTransaksi = DetailTransaksi.objects.raw('SELECT * FROM detail_transaksi')
            # print(QueryTransaksi)
            
            data = {
                'id' : log.id_job,
                'waktu' : log.eksekusi,
                'email_penerima' : log.email_penerima,
                'cabang' : log.id_job.kode_cabang,
                'running_id' :log.running_id,
                'startdate' : startdate,
                'enddate' : enddate,
                'detail_transaksi':transaksi,
                'today':today,
                'total_harga':sumTransaksi,
            }
            pdf = render_to_pdf('report2.html', data)
            return HttpResponse(pdf, content_type="application/pdf")    

import xlwt

def export_excel(request, id_log):
    try:
        log = Log.objects.get(pk = id_log)
    except  Exception as e:
        traceback.format_exc()

    startdate = today - timedelta(1)
    enddate = today + relativedelta(day=1)

    response = HttpResponse(content_type="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=Expenses' +\
        str(datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding = 'utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['id_branch','tahun', 'bulan', 'tanggal','wholesale','ritel','mikro','syariah','digital','total', 'tanggal_transaksi']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = DetailTransaksi.objects.filter(tanggal_transaksi__range=[enddate, startdate]).order_by('tanggal_transaksi').values_list('kode_cabang', 'tahun', 'bulan', 'tanggal', 'wholesale','ritel','mikro','syariah','digital','total_harga', 'tanggal_transaksi')    

    for row in rows:
        row_num += 1
        if(log.id_job.kode_cabang == row[:][0]):
            for col_num in range(len(row)):
                ws.write(row_num, col_num, str(row[col_num]), font_style)
        else: 
            pass
    wb.save(response)

    return response

def update_job(request, id_job):
    update_schedule = Shcedule.objects.get(pk = id_job)

    context = {
        'updateSchedule' : update_schedule
    }

    return render(request, 'update-scheduler.html', context)
# import schedule
# import time
from datetime import date, datetime
from .models import Shcedule

# -------------------------
# Pengiriman function email
# -------------------------
def send_email_func(id_job):
    try:
        schedule = Shcedule.objects.get(pk = id_job)
    except  Exception as e:
        traceback.format_exc()

    today = date.today()
    d = today + relativedelta(day=31)  
    ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)

    # Ambil data satu hari sebelum pengiriman.
    if schedule.template == 1:

        today = date.today()
        d = today + relativedelta(day=31)
       
        ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)

        if schedule.periode == 'harian':
            startdate = today - timedelta(1)
            enddate = today - timedelta(365)
        elif schedule.periode == 'bulanan':
                # temp_month
            if d == today:
                startdate = today + relativedelta(day=30)
            else: 
                startdate = today - timedelta(1)

            enddate = today + relativedelta(day=1)
        else:
            if ending_day_of_current_year == today:
                startdate = datetime.now().date().replace(month=12, day=30)
            else:
                startdate = today - timedelta(1)

            enddate = datetime.now().date().replace(month=1, day=1) 
        
        if schedule.format_laporan == 'pdf':

            transaksi = DetailTransaksi.objects.filter(tanggal_transaksi__range=[enddate, startdate]).order_by('tanggal_transaksi')
            cabang = Shcedule.objects.get(pk = id_job)
            sumTransaksi = transaksi.values("kode_cabang").order_by("kode_cabang").annotate(total_harga = Sum('total_harga'))
            trunct_month = transaksi.annotate(month = TruncMonth('tanggal_transaksi')).values('month').annotate(c=Sum('total_harga')).values('month', 'c', 'kode_cabang').order_by('kode_cabang')
            month_date = transaksi.annotate(month=TruncMonth('tanggal_transaksi')).values_list('month')

            template = get_template('report.html')

            data = {
                'id' : schedule.id_job,
                'tanggal' : schedule.jam_eksekusi,
                'waktu' : schedule.waktu_eksekusi,
                'email_penerima' : schedule.email_penerima,
                'cabang' : schedule.kode_cabang,
                'running_id' :schedule.running_id,
                'trunct_month' :trunct_month,
                'month_date' : month_date,
                'detail_transaksi':transaksi,
                'today':today,
                'total_harga':sumTransaksi,
                'judul_format': schedule.periode,
            }

            html  = template.render(data)
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
            pdf = result.getvalue()
            filename = 'Report_' + str(data['id']) + '.pdf'

            subject_email = 'Laporan transaksi otomatis'
            message_email = 'Email ini dikirimkan otomatis oleh sistem'
            email_cabang = cabang.email_penerima

            msg = EmailMultiAlternatives(
                subject_email,
                message_email,
                settings.EMAIL_HOST_USER,
                [email_cabang],
            )
            # print(msg)
            msg.attach_alternative(message_email, "text/html"), 
            msg.attach(filename, pdf, 'application/pdf')

            msg.send()
        else :
            cabang = Shcedule.objects.get(pk = id_job)
            response = HttpResponse(content_type="application/ms-excel")
            filename = response['Content-Disposition'] = 'attachment; filename=Expenses' +\
                str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding = 'utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            columns = ['id_branch','tahun', 'bulan', 'tanggal','wholesale','ritel','mikro','syariah','digital','total', 'tanggal_transaksi']

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            font_style = xlwt.XFStyle()

            rows = DetailTransaksi.objects.filter(tanggal_transaksi__range=[enddate, startdate]).order_by('tanggal_transaksi').values_list('kode_cabang', 'tahun', 'bulan', 'tanggal', 'wholesale','ritel','mikro','syariah','digital','total_harga', 'tanggal_transaksi')    

            for row in rows:
                row_num += 1
                if(schedule.kode_cabang == row[:][0]):
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, str(row[col_num]), font_style)
                else: 
                    pass
            wb.save(response)

            subject_email = 'Laporan transaksi otomatis'
            message_email = 'Email ini dikirimkan otomatis oleh sistem'
            email_cabang = cabang.email_penerima

            msg = EmailMultiAlternatives(
                subject_email,
                message_email,
                settings.EMAIL_HOST_USER,
                [email_cabang],
            )
            # print(msg)
            msg.attach_alternative(message_email, "text/html"), 
            msg.attach(filename, response.getvalue(), 'application/vnd.ms-excel')

            msg.send()
  
    else :
        today = date.today()
        d = today + relativedelta(day=31)  
        ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)

        if schedule.periode == 'harian':
            startdate = today - timedelta(1)
            enddate = today - timedelta(2)
        elif schedule.periode == 'bulanan':
            # temp_month
            if d == today:
                startdate = today + relativedelta(day=30)
            else: 
                startdate = today - timedelta(1)

            enddate = today + relativedelta(day=1)
        else:
            if ending_day_of_current_year == today:
                startdate = datetime.now().date().replace(month=12, day=30)
            else:
                startdate = today - timedelta(1)

            enddate = datetime.now().date().replace(month=1, day=1) 

        if schedule.format_laporan == 'pdf':
            transaksi = DetailTransaksi.objects.filter(tanggal_transaksi__range=[enddate, startdate]).order_by('tanggal_transaksi')
            cabang = Shcedule.objects.get(pk = id_job)
            sumTransaksi = transaksi.values("kode_cabang").order_by("kode_cabang").annotate(total_harga = Sum('total_harga'))

            template = get_template('report2.html')

            data = {
                'id' : schedule.id_job,
                'tanggal' : schedule.jam_eksekusi,
                'waktu' : schedule.waktu_eksekusi,
                'running_id' :schedule.running_id,
                'today':today,
                'detail_transaksi':transaksi,
                'total_harga':sumTransaksi,
                'start_date' : startdate,
                'end_date' : enddate,
                'judul_format': schedule.periode,
            }

            html  = template.render(data)
            result = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
            pdf = result.getvalue()
            filename = 'Report_' + str(data['id']) + '.pdf'

            subject_email = 'Laporan transaksi otomatis'
            message_email = 'Email ini dikirimkan otomatis oleh sistem'
            email_cabang = cabang.email_penerima

            msg = EmailMultiAlternatives(
                subject_email,
                message_email,
                settings.EMAIL_HOST_USER,
                [email_cabang],
            )
            # print(msg)
            msg.attach_alternative(message_email, "text/html"), 
            msg.attach(filename, pdf, 'application/pdf')

            msg.send()
        else:
            cabang = Shcedule.objects.get(pk = id_job)
            response = HttpResponse(content_type="application/ms-excel")
            filename = response['Content-Disposition'] = 'attachment; filename=Expenses' +\
                str(datetime.now()) + '.xls'
            wb = xlwt.Workbook(encoding = 'utf-8')
            ws = wb.add_sheet('Expenses')
            row_num = 0
            font_style = xlwt.XFStyle()
            font_style.font.bold = True

            columns = ['id_branch','tahun', 'bulan', 'tanggal','wholesale','ritel','mikro','syariah','digital','total', 'tanggal_transaksi']

            for col_num in range(len(columns)):
                ws.write(row_num, col_num, columns[col_num], font_style)

            font_style = xlwt.XFStyle()

            rows = DetailTransaksi.objects.filter(tanggal_transaksi__range=[enddate, startdate]).order_by('tanggal_transaksi').values_list('kode_cabang', 'tahun', 'bulan', 'tanggal', 'wholesale','ritel','mikro','syariah','digital','total_harga', 'tanggal_transaksi')    

            for row in rows:
                row_num += 1
                if(schedule.kode_cabang == row[:][0]):
                    for col_num in range(len(row)):
                        ws.write(row_num, col_num, str(row[col_num]), font_style)
                else: 
                    pass
            wb.save(response)
            
            subject_email = 'Laporan transaksi otomatis'
            message_email = 'Email ini dikirimkan otomatis oleh sistem'
            email_cabang = cabang.email_penerima

            msg = EmailMultiAlternatives(
                subject_email,
                message_email,
                settings.EMAIL_HOST_USER,
                [email_cabang],
            )
            # print(msg)
            msg.attach_alternative(message_email, "text/html"), 
            msg.attach(filename, response.getvalue(), 'application/vnd.ms-excel')
            
            msg.send()

    return HttpResponse ('email berhasil dikrim')

from .tasks import job
today = date.today()

# -------------------------------------
# terhubung dengan penjadwalan celery,
# task automateemail/celery.py
# -------------------------------------
def test(request, id_job):
    job.delay()
    
    return HttpResponse('done')

# --------------------------------------------------------------------------
def status_on_job(request, id_job, running_id):
    statusUpdate = Shcedule.objects.filter(pk = id_job)
    id_running = Shcedule.objects.filter(running_id = running_id)
    
    statusUpdate.update(status_job = True)

    obj = Shcedule.objects.get(pk = id_job)
    field_object = Shcedule._meta.get_field('running_id')
    field_value = field_object.value_from_object(obj)
    field_value2 = field_value
    
    return HttpResponseRedirect('/detail-scheduler/'+str(field_value2)+'')
    
def status_off_job(request, id_job, running_id):
    id_running = Shcedule.objects.filter(running_id = running_id)
    statusUpdate = Shcedule.objects.filter(pk = id_job)

    statusUpdate.update(status_job = False)
    
    obj = Shcedule.objects.get(pk = id_job)
    field_object = Shcedule._meta.get_field('running_id')
    field_value = field_object.value_from_object(obj)
    field_value2 = field_value
    
    return HttpResponseRedirect('/detail-scheduler/'+str(field_value2)+'')

# --------------------------------------------
# untuk melihat tampilan report berbentuk pdf.
# -------------------------------------------- 
# class GenerateReport(View):
#     # Pada pembuatan pdf akan dilakukan inputan 2 kali dari database.
#     # Database email dan database detail transaksi.
#     def get(self, request, id_job,  *args, **kwargs):
#         try:
#             schedule = Shcedule.objects.get(pk = id_job)
#         except  Exception as e:
#             traceback.format_exc()

#         if schedule.template == 1:
#             today = date.today()
#             d = today + relativedelta(day=31)  
#             ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
            
#             if schedule.periode == 'harian':
#                 startdate = today - timedelta(1)
#                 enddate = today - timedelta(2)
#             elif schedule.periode == 'bulanan':
#                 # temp_month
#                 if d == today:
#                     startdate = today + relativedelta(day=30)
#                 else: 
#                     startdate = today - timedelta(1)

#                 enddate = today + relativedelta(day=1)
#             else:
#                 if ending_day_of_current_year == today:
#                     startdate = datetime.now().date().replace(month=12, day=30)
#                 else:
#                     startdate = today - timedelta(1)

#                 enddate = datetime.now().date().replace(month=1, day=1) 
        
#             transaksi = DetailTransaksi.objects.filter(tanggal_transaksi__range=[enddate, startdate]).order_by('tanggal_transaksi')
#             trunct_month = transaksi.annotate(month = TruncMonth('tanggal_transaksi')).values('month').annotate(c=Sum('total_harga')).values('month', 'c', 'kode_cabang').order_by('kode_cabang')
#             sumTransaksi = transaksi.values('kode_cabang').order_by("kode_cabang").annotate(total_harga = Sum('total_harga'))
#             month_date = transaksi.annotate(month=TruncMonth('tanggal_transaksi')).values_list('month')

#             data = {
#                 'id' : schedule.id_job,
#                 'tanggal' : schedule.jam_eksekusi,
#                 'waktu' : schedule.waktu_eksekusi,
#                 'email_penerima' : schedule.email_penerima,
#                 'cabang' : schedule.kode_cabang,
#                 'running_id' :schedule.running_id,
#                 'trunct_month' :trunct_month,
#                 'month_date' : month_date,
#                 'detail_transaksi':transaksi,
#                 'today':today,
#                 'total_harga':sumTransaksi,
#             }
#             pdf = render_to_pdf('report.html', data)
#             return HttpResponse(pdf, content_type="application/pdf")
#         else: 
#             today = date.today()
#             d = today + relativedelta(day=31)  
#             ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
#             print(d)

#             if schedule.periode == 'harian':
#                 startdate = today - timedelta(1)
#                 enddate = today - timedelta(2)
#             elif schedule.periode == 'bulanan':
#                 # temp_month
#                 if d == today:
#                     startdate = today + relativedelta(day=30)
#                 else: 
#                     startdate = today - timedelta(1)

#                 enddate = today + relativedelta(day=1)
#             else:
#                 if ending_day_of_current_year == today:
#                     startdate = datetime.now().date().replace(month=12, day=30)
#                 else:
#                     startdate = today - timedelta(1)

#                 enddate = datetime.now().date().replace(month=1, day=1) 

#             transaksi = DetailTransaksi.objects.filter(tanggal_transaksi__range=[enddate, startdate]).order_by('tanggal_transaksi')
#             sumTransaksi = transaksi.values("kode_cabang").order_by("kode_cabang").annotate(total_harga = Sum('total_harga'))
#             # startdate = today - timedelta(1)

#             # QueryTransaksi = DetailTransaksi.objects.raw('SELECT * FROM detail_transaksi')
#             # print(QueryTransaksi)
            
#             data = {
#                 'id' : schedule.id_job,
#                 'tanggal' : schedule.jam_eksekusi,
#                 'waktu' : schedule.waktu_eksekusi,
#                 'running_id' :schedule.running_id,
#                 'today':today,
#                 'detail_transaksi':transaksi,
#                 'total_harga':sumTransaksi,
#                 'start_date' : startdate,
#                 'end_date' : enddate,
#             }
#             pdf = render_to_pdf('report2.html', data)
#             return HttpResponse(pdf, content_type="application/pdf")    
# -------------------------------------------------------------------------------------------------------------------------------


