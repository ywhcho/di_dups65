from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.shortcuts import render
from decimal import Decimal, InvalidOperation
from django.db.models import IntegerField, Sum, Value
from django.db.models.functions import Cast, Coalesce, Replace

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


def _get_table1_queryset(query_type, query_val):
    filter_map = {
        'ingrnd_t': 'ingrnd_t__icontains',
        'kingrnd_t': 'kingrnd_t__icontains',
        'cfno': 'cfno__icontains',
        'wfco': 'wfco__icontains',
        'ATC': 'ATC__istartswith',
    }
    lookup = filter_map.get(query_type)
    if not lookup:
        return MedInteractionMfname.objects.none()

    qs = MedInteractionMfname.objects.filter(**{lookup: query_val})
    if query_type == 'ATC':
        qs = qs.order_by('ATC', 'wfco', 'id')
    return qs


def _get_table2_base_queryset(wfco_full):
    return MedicinesMedicine.objects.filter(wfco=wfco_full).annotate(
        ypri24_num=Cast(Replace('ypri24', Value(','), Value('')), IntegerField())
    )


def _get_table2_queryset(wfco_full, sort2):
    sort_map = {
        'htname': ('htname', 'id'),
        'company': ('company', 'id'),
        'ypri24': ('-ypri24_num', 'id'),
    }
    order_by = sort_map.get(sort2, sort_map['ypri24'])
    return _get_table2_base_queryset(wfco_full).order_by(*order_by)


def _get_table2_sort_links(query_type, query_val, wfco_full, page1):
    base_params = {
        'type': query_type,
        'val': query_val,
        'wfco': wfco_full,
        'page1': page1,
        'page2': 1,
    }
    return {
        key: '?' + urlencode({**base_params, 'sort2': key})
        for key in ('htname', 'company', 'ypri24')
    }


def search_view(request):
    """
    동일성분 찾기 메인 화면.
    - Table 1: med_interaction_mfname 검색 (ingrnd_t / kingrnd_t / cfno / wfco / ATC)
    - Table 2: Table 1 행 선택 → wfco 전체로 medicines_medicine 목록
    """
    query_type = request.GET.get('type', 'ingrnd_t')
    query_val = request.GET.get('val', '').strip()
    wfco_full = request.GET.get('wfco', '').strip()
    sort2 = request.GET.get('sort2', 'ypri24').strip()

    # ── Table 1: 검색 결과 ──────────────────────────────────────────────────
    table1_page = None
    if query_val:
        qs1 = _get_table1_queryset(query_type, query_val)
        p1 = Paginator(qs1, PAGE_SIZE)
        table1_page = p1.get_page(request.GET.get('page1', 1))

    # ── Table 2: wfco 전체 일치 의약품 목록 ────────────────────────────────
    table2_page = None
    table2_ypri24_total = None
    if wfco_full:
        qs2 = _get_table2_queryset(wfco_full, sort2)
        agg = qs2.aggregate(total=Coalesce(Sum('ypri24_num'), Value(0), output_field=IntegerField()))
        table2_ypri24_total = _format_amount(str(agg['total'])) if agg['total'] else ''
        p2 = Paginator(qs2, PAGE_SIZE)
        table2_page = p2.get_page(request.GET.get('page2', 1))
        for row in table2_page.object_list:
            row.ypri24_display = _format_amount(row.ypri24)

    # 페이지 로드 후 자동 스크롤 대상 결정
    # Table 2가 생성된 경우 → table2 섹션으로 포커스
    auto_focus = ''
    if wfco_full:
        auto_focus = 'table2-section'

    return render(request, 'equiv_ingr/search.html', {
        'query_type': query_type,
        'query_val': query_val,
        'table1_page': table1_page,
        'table2_page': table2_page,
        'table2_ypri24_total': table2_ypri24_total,
        'table2_sort_links': _get_table2_sort_links(query_type, query_val, wfco_full, request.GET.get('page1', 1)),
        'wfco_full': wfco_full,
        'sort2': sort2,
        'auto_focus': auto_focus,
    })
