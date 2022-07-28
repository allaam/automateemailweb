import sched
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from matplotlib.style import context
from .shceduleremail.models import Shcedule, Template
from .shceduleremail.forms import FormShcedule, FormEmail, FormLogin, FormTemplate
from django.core.paginator import Paginator
from django.views.generic import View
from django.db.models import Sum
from .shceduleremail.utils import render_to_pdf
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

def dashboard_(request):
    # ambil data table schedule, dengan kolom
    schedule = Shcedule.objects.order_by('-running_id').values('running_id', 'waktu_eksekusi', 'jam_eksekusi', 'status', 'periodic', 'template', 'id_template').distinct()
    
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

