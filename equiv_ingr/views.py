from django.core.paginator import Paginator
from django.shortcuts import render

from .models import MedInteractionMfname, MedicinesMedicine

PAGE_SIZE = 10


def search_view(request):
    """
    메인 검색 화면.
    - Table 1: med_interaction_mfname 검색 (wfco / ingrnd_t / kingrnd_t / cfno)
    - Table 2: Table 1에서 선택한 행의 wfco 앞 6자리로 동일성분 검색
    - Table 3: Table 2에서 선택한 행의 wfco 전체로 medicines_medicine 검색
    """
    query_type = request.GET.get('type', '')
    query_val = request.GET.get('val', '').strip()
    wfco6 = request.GET.get('wfco6', '').strip()
    wfco_full = request.GET.get('wfco', '').strip()

    # ── Table 1 ──────────────────────────────────────────────────────────────
    table1_page = None
    if query_val:
        filter_map = {
            'wfco': 'wfco__icontains',
            'ingrnd_t': 'ingrnd_t__icontains',
            'kingrnd_t': 'kingrnd_t__icontains',
            'cfno': 'cfno__icontains',
        }
        lookup = filter_map.get(query_type)
        qs1 = (
            MedInteractionMfname.objects.filter(**{lookup: query_val})
            if lookup
            else MedInteractionMfname.objects.none()
        )
        p1 = Paginator(qs1, PAGE_SIZE)
        table1_page = p1.get_page(request.GET.get('page1', 1))

    # ── Table 2 ──────────────────────────────────────────────────────────────
    table2_page = None
    if wfco6:
        qs2 = MedInteractionMfname.objects.filter(wfco__startswith=wfco6)
        p2 = Paginator(qs2, PAGE_SIZE)
        table2_page = p2.get_page(request.GET.get('page2', 1))

    # ── Table 3 ──────────────────────────────────────────────────────────────
    table3_page = None
    if wfco_full:
        qs3 = MedicinesMedicine.objects.filter(wfco=wfco_full)
        p3 = Paginator(qs3, PAGE_SIZE)
        table3_page = p3.get_page(request.GET.get('page3', 1))

    return render(request, 'equiv_ingr/search.html', {
        'query_type': query_type,
        'query_val': query_val,
        'table1_page': table1_page,
        'wfco6': wfco6,
        'table2_page': table2_page,
        'wfco_full': wfco_full,
        'table3_page': table3_page,
    })
