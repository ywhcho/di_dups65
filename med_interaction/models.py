from django.db import models


class Mfname(models.Model):
    """wfco별 성분/상호작용코드 매핑"""
    wfco = models.CharField(max_length=10, db_index=True, verbose_name='성분코드')
    fname = models.CharField(max_length=200, blank=True, verbose_name='성분명')
    igrno1 = models.CharField(max_length=20, blank=True, verbose_name='상호작용성분코드1')
    igrno2 = models.CharField(max_length=20, blank=True, verbose_name='상호작용성분코드2')
    igrno3 = models.CharField(max_length=20, blank=True, verbose_name='상호작용성분코드3')
    igrno4 = models.CharField(max_length=20, blank=True, verbose_name='상호작용성분코드4')

    class Meta:
        verbose_name = '상호작용 성분코드 매핑'
        verbose_name_plural = '상호작용 성분코드 매핑 목록'
        ordering = ['wfco']

    def __str__(self):
        return f'{self.wfco} - {self.fname}'


class Mintef(models.Model):
    """상호작용성분코드 쌍별 위험도/설명"""
    igrno_a = models.CharField(max_length=20, db_index=True, verbose_name='상호작용코드 A')
    igrno_b = models.CharField(max_length=20, db_index=True, verbose_name='상호작용코드 B')
    irisk = models.CharField(max_length=20, blank=True, verbose_name='위험도')
    idesc = models.TextField(blank=True, verbose_name='상호작용 유형')
    ireco = models.TextField(blank=True, verbose_name='대처 방법')

    class Meta:
        verbose_name = '약품 상호작용'
        verbose_name_plural = '약품 상호작용 목록'
        ordering = ['igrno_a', 'igrno_b']

    def __str__(self):
        return f'{self.igrno_a} - {self.igrno_b}'
