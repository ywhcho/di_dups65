from django.db import models


class MedInteractionMfname(models.Model):
    """
    DB: med_interaction_mfname
    기존 필드: wfco, fname, igrno1, igrno2, igrno3, igrno4
    추가 필드: ingrnd_t(영문성분명), kingrnd_t(한글성분명), cfno(효능분류번호)
    """
    wfco = models.CharField('활성성분코드', max_length=20, blank=True, default='')
    fname = models.CharField('성분명', max_length=255, blank=True, default='')
    igrno1 = models.CharField(max_length=20, blank=True, default='')
    igrno2 = models.CharField(max_length=20, blank=True, default='')
    igrno3 = models.CharField(max_length=20, blank=True, default='')
    igrno4 = models.CharField(max_length=20, blank=True, default='')
    ingrnd_t = models.CharField('영문성분명', max_length=255, blank=True, default='')
    kingrnd_t = models.CharField('한글성분명', max_length=255, blank=True, default='')
    cfno = models.CharField('효능분류번호', max_length=20, blank=True, default='')

    class Meta:
        db_table = 'med_interaction_mfname'
        managed = False

    def __str__(self):
        return f"{self.wfco} {self.kingrnd_t}"


class MedicinesMedicine(models.Model):
    """
    DB: medicines_medicine
    기존 필드: no(pk), wfco, htname, ingred, company
    추가 필드: cfno(효능분류), deriv2(성분계열), ypri24(연생산실적)
    """
    wfco = models.CharField('활성성분코드', max_length=20, blank=True, default='')
    htname = models.CharField('제품명', max_length=255, blank=True, default='')
    ingred = models.CharField('성분', max_length=255, blank=True, default='')
    company = models.CharField('회사', max_length=255, blank=True, default='')
    cfno = models.CharField('효능분류', max_length=20, blank=True, default='')
    deriv2 = models.CharField('성분계열', max_length=100, blank=True, default='')
    ypri24 = models.CharField('연생산실적', max_length=50, blank=True, default='')

    class Meta:
        db_table = 'medicines_medicine'
        managed = False

    def __str__(self):
        return f"{self.htname} ({self.wfco})"
