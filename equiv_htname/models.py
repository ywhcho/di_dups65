from django.db import models


class MedicinesMedicine(models.Model):
    """
    DB: medicines_medicine
    상품명(htname) 검색 및 wfco 전체 비교에 사용
    """
    wfco = models.CharField('활성성분코드', max_length=20, blank=True, default='')
    htname = models.CharField('상품명', max_length=255, blank=True, default='')
    ingr_t = models.CharField('성분명', max_length=255, blank=True, default='')
    company = models.CharField('회사', max_length=255, blank=True, default='')
    cfno = models.CharField('효능분류번호', max_length=20, blank=True, default='')
    atc = models.CharField('ATC분류', max_length=50, blank=True, default='')
    deriv2 = models.CharField('계열분류', max_length=100, blank=True, default='')
    ypri24 = models.CharField('년생산액', max_length=50, blank=True, default='')

    class Meta:
        db_table = 'medicines_medicine'
        managed = False

    def __str__(self):
        return f"{self.htname} ({self.wfco})"


class MedInteractionMfname(models.Model):
    """
    DB: med_interaction_mfname
    wfco 앞 6자리 비교로 동일성분 찾기에 사용
    """
    wfco = models.CharField('활성성분코드', max_length=20, blank=True, default='')
    ingr_t = models.CharField('성분명', max_length=255, blank=True, default='')
    cfno = models.CharField('효능분류', max_length=20, blank=True, default='')
    atc = models.CharField('ATC분류', max_length=50, blank=True, default='')
    deriv2 = models.CharField('계열분류', max_length=100, blank=True, default='')
    ypri24 = models.CharField('년생산액', max_length=50, blank=True, default='')

    class Meta:
        db_table = 'med_interaction_mfname'
        managed = False

    def __str__(self):
        return f"{self.wfco} {self.ingr_t}"
