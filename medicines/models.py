from django.db import models


class Medicine(models.Model):
    """의약품 모델 (약품명, 성분명, 회사명, 주성분코드)"""
    htname = models.CharField(max_length=200, verbose_name='약품명')
    ingred = models.CharField(max_length=500, verbose_name='성분명')
    company = models.CharField(max_length=200, verbose_name='회사명')
    wfco = models.CharField(max_length=10, blank=True, default='', db_index=True, verbose_name='주성분코드')

    class Meta:
        verbose_name = '의약품'
        verbose_name_plural = '의약품 목록'
        ordering = ['htname']

    def __str__(self):
        return self.htname


class DrugInfo(models.Model):
    """의약정보 상세 모델 (htname, ingred, ee, ud, nb, company)"""
    htname = models.CharField(max_length=200, verbose_name='약품명')
    ingred = models.CharField(max_length=500, verbose_name='성분명')
    ee = models.TextField(blank=True, verbose_name='효능')
    ud = models.TextField(blank=True, verbose_name='용량')
    nb = models.TextField(blank=True, verbose_name='주의사항')
    company = models.CharField(max_length=200, verbose_name='회사명')

    class Meta:
        verbose_name = '의약정보'
        verbose_name_plural = '의약정보 목록'
        ordering = ['htname']

    def __str__(self):
        return self.htname
