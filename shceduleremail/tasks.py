# from automateemail.celery import shared_task, app
from datetime import timedelta, datetime, date
# import datetime

from anyio import current_time
from pymysql import NULL
from sqlalchemy import null
from .models import Shcedule, Log
from .views import send_email_func
from celery import shared_task
from dateutil.relativedelta import relativedelta
# from django.conf import settings

# @shared_task(bind = True)
# def test_func(self):
#     for i in range(10):
#         print(i)
#     return "done"

@shared_task(bind = True)
def job(self):
    # print('testing')
    
    today = date.today()
    Time = datetime.now().strftime("%H:%M:%S")
    currentTimes = datetime.strptime(Time, '%H:%M:%S').time()

    dateNow = datetime.now()
    
    # format date 
    shcedule_monthly = dateNow.strftime("%Y-%m-%d")
    month = datetime.strptime(shcedule_monthly, "%Y-%m-%d") 
    monthly = month.day
    shcedule_yearly = dateNow.strftime("%Y-%m-%d") 
    year = datetime.strptime(shcedule_yearly, "%Y-%m-%d")
    yearly = year.month
   
    schedule = Shcedule.objects.all()
    # monthlyDB = Shcedule.objects.filter(Fecha=date.strftime("%MM-%DD"))
    # monthlyDB2 = datetime.strptime(monthlyDB, '%m-%d')
    #----------------
    # Next Day
    #----------------
    tomorrow = datetime.now() + timedelta(days=1)
    nextDay = tomorrow.strftime("%Y-%m-%d")
    nextDay2 = datetime.strptime(nextDay, "%Y-%m-%d")
    print(nextDay2)
    #----------------
    #Next month 
    #----------------
    d2 = datetime.now()
    d3 = d2 + relativedelta(months=1)
    nextmonth = d3.strftime("%Y-%m-%d")
    nextMonth = datetime.strptime(nextmonth, "%Y-%m-%d")
    print(d3)
    #----------------
    #Next year
    #----------------
    y2 = datetime.now()
    y3 = y2 + relativedelta(months=12)
    nextyear = y3.strftime("%Y-%m-%d")
    nextYear = datetime.strptime(nextyear, "%Y-%m-%d")

    for schedules in schedule:
        dates = schedules.waktu_eksekusi
        times = schedules.jam_eksekusi     
        status = schedules.status
        email = schedules.email_penerima
        # eksekusi = schedules.terakhir_eksekusi
        id_job = schedules.id_job
        period = schedules.periodic
        status_job = schedules.status_job

        # Periodic tanggal
        if period == 'daily':
            if status == True and status_job == True:
                if times == currentTimes:
                    if send_email_func(id_job):                        
                        Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                        Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextDay2)
                        job = Shcedule.objects.get(pk = id_job)
                        log = Log(id_job = job, status = True, eksekusi = dateNow, running_id = job.running_id, email_penerima = email)
                        log.save()
                    else:
                        Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                        Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextDay2)
                        job = Shcedule.objects.get(pk = id_job)
                        log = Log(id_job = job, status = False, eksekusi = dateNow, running_id = job.running_id, email_penerima = email)
                        log.save()
            if status == True and status_job == False:
                if times == currentTimes:
                    Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                    Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextDay2)
            if status == False:
                if times == currentTimes:
                    Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                    Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextDay2)
            else:
                print('waiting')
        elif period == 'monthly':
            if status == True and status_job == True:
                if dates == today:
                    if monthly ==  dates.day:
                        if times == currentTimes:
                            if send_email_func(id_job):
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextMonth)
                                job = Shcedule.objects.get(pk = id_job)
                                log = Log(id_job = job, status = True, eksekusi = dateNow, running_id = job.running_id, email_penerima = email)
                                log.save()
                            else:
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextMonth)
                                job = Shcedule.objects.get(pk = id_job)
                                log = Log(id_job = job, status = False, eksekusi = dateNow, running_id = job.running_id, email_penerima = email)
                                log.save()
            if status == True and status_job == False:
                if dates == today:
                    if monthly ==  dates.day:
                        if times == currentTimes:
                            Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                            Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextMonth)
            if status == False:
                if dates == today:
                    if monthly ==  dates.day:
                        if times == currentTimes:
                            Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                            Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextMonth)
            else:
                print('waiting')
        elif period == 'yearly':
            if status == True and status_job == True:
                if dates == today:
                    if yearly == dates.month:
                        if monthly == dates.day: 
                            if times == currentTimes:
                                if send_email_func(id_job):
                                    Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                    Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextYear)
                                    job = Shcedule.objects.get(pk = id_job)
                                    log = Log(id_job = job, status = True, eksekusi = dateNow, running_id = job.running_id, email_penerima = email)
                                    log.save()
                                else:
                                    Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                    Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextYear)
                                    job = Shcedule.objects.get(pk = id_job)
                                    log = Log(id_job = job, status = False, eksekusi = dateNow, running_id = job.running_id, email_penerima = email)
                                    log.save()
            if status == True and status_job == False:
                if dates == today:
                    if yearly == dates.month:
                        if monthly == dates.day: 
                            if times == currentTimes:
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextYear)
            if status == False:
                if dates == today:
                    if yearly == dates.month:
                        if monthly == dates.day: 
                            if times == currentTimes:
                                Shcedule.objects.filter(pk = id_job).update(terakhir_eksekusi = today)
                                Shcedule.objects.filter(pk = id_job).update(waktu_eksekusi = nextYear)
            else:
                print('waiting')
        else: 
            print('waiting')       
    