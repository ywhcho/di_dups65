from django.core.paginator import Paginator
from django.shortcuts import render

from .models import MedInteractionMfname, MedicinesMedicine

PAGE_SIZE = 10


def search_view(request):
    """
    상품명으로 동일성분 찾기.
    - Table 1: medicines_medicine 에서 htname(상품명) 검색
    - Table 2: Table 1 행 선택 → wfco 앞 6자리로 med_interaction_mfname 검색
    - Table 3: Table 2 행 선택 → wfco 전체(10자리)로 medicines_medicine 검색
    """
    htname_q = request.GET.get('htname', '').strip()
    wfco6 = request.GET.get('wfco6', '').strip()   # Table1 행 선택 시 wfco 앞 6자리
    wfco_full = request.GET.get('wfco', '').strip() # Table2 행 선택 시 wfco 전체

    # ── Table 1: 상품명 검색 ────────────────────────────────────────────────
    table1_page = None
    if htname_q:
        qs1 = MedicinesMedicine.objects.filter(
            htname__icontains=htname_q
        ).order_by('htname', 'id')
        p1 = Paginator(qs1, PAGE_SIZE)
        table1_page = p1.get_page(request.GET.get('page1', 1))

    # ── Table 2: wfco 앞 6자리 비교 ────────────────────────────────────────
    table2_page = None
    if wfco6:
        qs2 = MedInteractionMfname.objects.filter(
            wfco__startswith=wfco6
        ).order_by('wfco', 'id')
        p2 = Paginator(qs2, PAGE_SIZE)
        table2_page = p2.get_page(request.GET.get('page2', 1))

    # ── Table 3: wfco 전체(10자리) 비교 ─────────────────────────────────────
    table3_page = None
    if wfco_full:
        qs3 = MedicinesMedicine.objects.filter(
            wfco=wfco_full
        ).order_by('htname', 'id')
        p3 = Paginator(qs3, PAGE_SIZE)
        table3_page = p3.get_page(request.GET.get('page3', 1))

    # 페이지 로드 후 자동 스크롤 대상
    auto_focus = ''
    if wfco_full:
        auto_focus = 'table3-section'
    elif wfco6:
        auto_focus = 'table2-section'

    return render(request, 'equiv_htname/search.html', {
        'htname_q': htname_q,
        'wfco6': wfco6,
        'wfco_full': wfco_full,
        'table1_page': table1_page,
        'table2_page': table2_page,
        'table3_page': table3_page,
        'auto_focus': auto_focus,
    })
