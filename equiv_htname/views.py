from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.db.models import IntegerField, Sum, Value
from django.db.models.functions import Cast, Coalesce, Replace
from django.shortcuts import render

from .models import MedInteractionMfname, MedicinesMedicine

PAGE_SIZE = 10


def _format_amount(value):
    text = str(value or '').strip()
    if not text:
        return ''
    normalized = text.replace(',', '')
    try:
        return f"{int(Decimal(normalized)):,}"
    except (InvalidOperation, ValueError):
        return text


def _annotate_ypri24(qs):
    """ypri24(CharField) → ypri24_num(IntegerField) 어노테이션 추가."""
    return qs.annotate(
        ypri24_num=Cast(Replace('ypri24', Value(','), Value('')), IntegerField())
    )


def _ypri24_total(qs):
    agg = qs.aggregate(
        total=Coalesce(Sum('ypri24_num'), Value(0), output_field=IntegerField())
    )
    return _format_amount(str(agg['total'])) if agg['total'] else ''


def _set_ypri24_display(page):
    for row in page.object_list:
        row.ypri24_display = _format_amount(row.ypri24)


SEARCH_TYPES = {
    'htname':  ('htname__icontains',   '상품명'),
    'ingr_t':  ('ingr_t__icontains',   '성분명'),
    'company': ('company__icontains',  '회사'),
    'cfno':    ('cfno__icontains',     '효능분류번호'),
    'atc':     ('atc__istartswith',    'ATC분류'),
    'wfco':    ('wfco__startswith',    'wfco'),
}


def search_view(request):
    """
    medicines_medicine 에서 여러 조건으로 동일성분 찾기.
    - Table 1: stype/sval 로 medicines_medicine 검색 (6가지 검색 종류)
    - Table 2: Table 1 행 선택 → wfco 앞 6자리로 med_interaction_mfname 검색
    - Table 3: Table 2 행 선택 → wfco 전체(10자리)로 medicines_medicine 검색
    모든 테이블: ypri24 내림차순 정렬, 합계 표시
    """
    stype = request.GET.get('stype', 'htname').strip()
    if stype not in SEARCH_TYPES:
        stype = 'htname'
    sval = request.GET.get('sval', '').strip()

    # 하위호환: 기존 htname 파라미터 지원
    if not sval:
        legacy = request.GET.get('htname', '').strip()
        if legacy:
            sval = legacy
            stype = 'htname'

    wfco6 = request.GET.get('wfco6', '').strip()     # Table1 행 선택 시 wfco 앞 6자리
    wfco_t1 = request.GET.get('wfco_t1', '').strip() # Table1 선택 행의 wfco 전체(Table2 하이라이트용)
    wfco_full = request.GET.get('wfco', '').strip()   # Table2 행 선택 시 wfco 전체
    sort3_raw = request.GET.get('sort3', '')          # Table 3 정렬 기준
    sort3 = sort3_raw if sort3_raw in ('htname', 'company', 'ypri24') else 'ypri24'

    # ── Table 1: 검색 ────────────────────────────────────────────────────────
    table1_page = None
    table1_ypri24_total = ''
    if sval:
        field_lookup, _ = SEARCH_TYPES[stype]
        qs1 = _annotate_ypri24(
            MedicinesMedicine.objects.filter(**{field_lookup: sval})
        ).order_by('wfco', 'id')
        table1_ypri24_total = _ypri24_total(qs1)
        p1 = Paginator(qs1, PAGE_SIZE)
        table1_page = p1.get_page(request.GET.get('page1', 1))
        _set_ypri24_display(table1_page)

    # ── Table 2: wfco 앞 6자리 비교 ────────────────────────────────────────
    table2_page = None
    table2_ypri24_total = ''
    if wfco6:
        qs2 = _annotate_ypri24(
            MedInteractionMfname.objects.filter(wfco__startswith=wfco6)
        ).order_by('wfco', 'id')
        table2_ypri24_total = _ypri24_total(qs2)
        p2 = Paginator(qs2, PAGE_SIZE)
        table2_page = p2.get_page(request.GET.get('page2', 1))
        _set_ypri24_display(table2_page)

    # ── Table 3: wfco 전체(10자리) 비교 ─────────────────────────────────────
    table3_page = None
    table3_ypri24_total = ''
    if wfco_full:
        _sort3_map = {
            'htname': ('htname', 'id'),
            'company': ('company', 'id'),
            'ypri24': ('-ypri24_num', 'id'),
        }
        t3_order = _sort3_map[sort3]
        qs3 = _annotate_ypri24(
            MedicinesMedicine.objects.filter(wfco=wfco_full)
        ).order_by(*t3_order)
        table3_ypri24_total = _ypri24_total(qs3)
        p3 = Paginator(qs3, PAGE_SIZE)
        table3_page = p3.get_page(request.GET.get('page3', 1))
        _set_ypri24_display(table3_page)

    # 페이지 로드 후 자동 스크롤 대상
    auto_focus = ''
    if wfco_full:
        auto_focus = 'table3-section'
    elif wfco6:
        auto_focus = 'table2-section'

    return render(request, 'equiv_htname/search.html', {
        'stype': stype,
        'sval': sval,
        'search_types': SEARCH_TYPES,
        'wfco6': wfco6,
        'wfco_t1': wfco_t1,
        'wfco_full': wfco_full,
        'sort3': sort3,
        'table1_page': table1_page,
        'table1_ypri24_total': table1_ypri24_total,
        'table2_page': table2_page,
        'table2_ypri24_total': table2_ypri24_total,
        'table3_page': table3_page,
        'table3_ypri24_total': table3_ypri24_total,
        'auto_focus': auto_focus,
    })
