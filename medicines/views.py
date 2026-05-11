from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import DrugInfo


# ---------- 의약정보 보기 ----------

def druginfo_list(request):
    """의약정보 목록 - 성분/회사/효능별 검색"""
    ingred_filter = request.GET.get('ingred', '').strip()
    company_filter = request.GET.get('company', '').strip()
    ee_filter = request.GET.get('ee', '').strip()
    search_q = request.GET.get('q', '').strip()

    drugs = DrugInfo.objects.all()

    if ingred_filter:
        drugs = drugs.filter(ingred__icontains=ingred_filter)
    if company_filter:
        drugs = drugs.filter(company__icontains=company_filter)
    if ee_filter:
        drugs = drugs.filter(ee__icontains=ee_filter)
    if search_q:
        drugs = drugs.filter(htname__icontains=search_q)

    # 필터 옵션 목록 (DB에 있는 값들)
    all_ingreds = sorted(set(
        ing.strip()
        for d in DrugInfo.objects.values_list('ingred', flat=True)
        for ing in d.split(',')
        if ing.strip()
    ))
    all_companies = sorted(DrugInfo.objects.values_list('company', flat=True).distinct())
    all_ee = sorted(set(
        e.strip()
        for d in DrugInfo.objects.values_list('ee', flat=True)
        for e in d.split(',')
        if e.strip()
    ))

    paginator = Paginator(drugs, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'all_ingreds': all_ingreds,
        'all_companies': all_companies,
        'all_ee': all_ee,
        'ingred_filter': ingred_filter,
        'company_filter': company_filter,
        'ee_filter': ee_filter,
        'search_q': search_q,
    }
    return render(request, 'medicines/druginfo_list.html', context)


def druginfo_detail(request, pk):
    """의약정보 상세 보기"""
    drug = get_object_or_404(DrugInfo, pk=pk)
    return render(request, 'medicines/druginfo_detail.html', {'drug': drug})
