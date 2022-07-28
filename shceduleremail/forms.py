# Untuk melakukan inser database

from pyexpat import model
from django import forms
from .models import Shcedule, Cabang, Login, Template

class FormShcedule(forms.ModelForm):
    class Meta:
        model = Shcedule
        # fields = ['id_job', 'waktu_eksekusi', 'jam_eksekusi', 'status']
        fields = "__all__"

class FormEmail(forms.ModelForm):
    class Meta:
        model = Cabang
        # fields = ['id_job', 'waktu_eksekusi', 'jam_eksekusi', 'status']
        fields = "__all__"

class FormLogin(forms.ModelForm):
    class Meta:
        model = Login
        # fields = ['id_job', 'waktu_eksekusi', 'jam_eksekusi', 'status']
        fields = "__all__"
    
class FormTemplate(forms.ModelForm):
    class Meta:
        model = Template
        fields = "__all__"
    
# class FormLog(forms.ModelForm):
#     class Meta:
#         model = Log
#         # fields = ['id_job', 'waktu_eksekusi', 'jam_eksekusi', 'status']
#         fields = "__all__"