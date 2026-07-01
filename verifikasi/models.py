from django.db import models
from django.contrib.auth.models import User


class VerifikasiIjazah(models.Model):
    STATUS_CHOICES = [
    ("VALID", "Valid"),
    ("TIDAK MEMENUHI SYARAT", "Tidak Memenuhi Syarat"),
    ("PERLU DIPERIKSA", "Perlu Diperiksa"),
    ("TIDAK TERDETEKSI", "Tidak Terdeteksi"),
    ]

    nama = models.CharField(max_length=100)
    nama_ocr = models.CharField(max_length=100, blank=True, default="")
    nim = models.CharField(max_length=20)

    file = models.FileField(upload_to='ijazah/', null=True, blank=True)

    extracted_year = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="PERLU DIPERIKSA")

    created_at = models.DateTimeField(auto_now_add=True)

    hasil_benar = models.BooleanField(default=False)
    tidak_terbaca = models.BooleanField(default=False)
    salah_tahun = models.BooleanField(default=False)

    cer = models.FloatField(null=True, blank=True)
    wer = models.FloatField(null=True, blank=True)

    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifikasi')

    @property
    def cer_persen(self):
        return self.cer * 100 if self.cer is not None else None

    @property
    def wer_persen(self):
        return self.wer * 100 if self.wer is not None else None

    def __str__(self):
        return f"{self.nama} - {self.status}"