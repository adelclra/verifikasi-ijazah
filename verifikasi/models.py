from django.db import models


class VerifikasiIjazah(models.Model):
    STATUS_CHOICES = [
        ("MENUNGGU VERIFIKASI", "Menunggu"),
        ("VALID", "Valid"),
        ("TIDAK MEMENUHI SYARAT", "Tidak Valid"),
        ("TIDAK TERDETEKSI", "Tidak Terdeteksi"),
    ]

    nama = models.CharField(max_length=100)
    nama_ocr = models.CharField(max_length=100, blank=True, default="")
    nim = models.CharField(max_length=20)

    file = models.FileField(upload_to='ijazah/', null=True, blank=True)

    extracted_year = models.CharField(max_length=10, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="MENUNGGU VERIFIKASI")

    created_at = models.DateTimeField(auto_now_add=True)

    hasil_benar = models.BooleanField(default=False)
    tidak_terbaca = models.BooleanField(default=False)
    salah_tahun = models.BooleanField(default=False)

    cer = models.FloatField(null=True, blank=True)
    wer = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.nama} - {self.status}"