from django.db import models

# Create your models here.

class Cabang(models.Model):
    kode_cabang = models.CharField(primary_key=True, max_length=255)
    nama_cabang = models.CharField(max_length=255)
    email_cabang = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'cabang'

class DetailTransaksi(models.Model):
    id_transaksi = models.AutoField(primary_key=True)
    kode_cabang = models.CharField(unique=True, max_length=255)
    tanggal_transaksi = models.DateField()
    tahun = models.IntegerField(null=True, blank=True)
    bulan = models.CharField(max_length=255)
    tanggal = models.IntegerField(null=True, blank=True)
    wholesale = models.IntegerField(null=True, blank=True)
    ritel =  models.IntegerField(null=True, blank=True)
    mikro = models.IntegerField(null=True, blank=True)
    syariah = models.IntegerField(null=True, blank=True)
    digital = models.IntegerField(null=True, blank=True)
    total_harga = models.IntegerField(null=True, blank=True)
    # kode_produk = models.CharField(unique=True, max_length=255)
    # jumlah_pembelian = models.IntegerField()
    # harga_satuan = models.IntegerField()
    # total_harga = models.IntegerField()
    # tanggal_transaksi = models.DateField()

    class Meta:
        managed = False
        db_table = 'report_transaksi'

class Template(models.Model):
    id_template = models.AutoField(primary_key=True)
    nama_template = models.CharField(null = True, blank = True, max_length=255)
    template = models.IntegerField(null = True, blank = True)
    periode = models.CharField(null=True, blank=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'template'

class Shcedule(models.Model):
    id_job = models.AutoField(primary_key=True)
    waktu_eksekusi = models.DateField(null=True, blank=True)
    jam_eksekusi = models.TimeField(null=True, blank=True)
    status = models.BooleanField(default = False)
    terakhir_eksekusi = models.DateField(null=True, blank=True)
    periodic = models.CharField(max_length=255)
    template = models.IntegerField()
    running_id = models.IntegerField(null=True, blank=True, unique = True)
    email_penerima = models.CharField(null = True, blank = True, max_length=255)
    kode_cabang = models.CharField(null=True, blank=True, max_length=255)
    # kode_cabang = models.ForeignKey("Cabang", db_column='kode_cabang', on_delete=models.DO_NOTHING)
    # id_template = models.ForeignKey("Template", db_column='id_template', on_delete=models.DO_NOTHING)
    id_template = models.IntegerField(null=True, blank=True)
    status_job = models.BooleanField(default = True)
    periode = models.CharField(null=True, blank=True, max_length=255)
    format_laporan = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return '%s %s %s %s %s %s %s %s %s %s %s %s %s' % (self.id_job, self.waktu_eksekusi, self.jam_eksekusi, self.status, self.terakhir_eksekusi, self.periodic, self.template, self.running_id, self.email_penerima, self.kode_cabang, self.id_template.pk, self.status_job, self.periode)

    class Meta:
        managed = False
        db_table = 'shcedule'

class KodeProduk(models.Model):
    kode_produk = models.CharField(primary_key=True, max_length=255)
    nama_produk = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'kode_produk'

class Log(models.Model):
    id_log = models.AutoField(primary_key=True)
    id_job = models.ForeignKey("Shcedule", db_column='id_job', on_delete=models.DO_NOTHING)
    status = models.BooleanField(default = False)
    eksekusi = models.DateTimeField(null=True, blank=True)
    running_id = models.IntegerField(null=True, blank=True)
    email_penerima = models.CharField(null = True, blank = True, max_length=255)
    tanggal_awal_laporan = models.DateField(null=True, blank=True)
    tanggal_akhir_laporan = models.DateField(null=True, blank=True)

    def __str__(self):
        return '%s %s %s %s' % (self.id_log, self.id_job.pk, self.status, self.eksekusi)

    class Meta:
        managed = False
        db_table = 'log'

class Running(models.Model):
    idRunning= models.AutoField(primary_key=True)
    running_id = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'running'

class Login(models.Model):
    login_admin_id = models.AutoField(primary_key=True)
    email = models.CharField(null = True, blank = True, max_length=255)
    password = models.CharField(null = True, blank = True, max_length=255)
    last_login  = models.DateTimeField(auto_now = True)

    class Meta:
        managed = False
        db_table = 'login_admin'