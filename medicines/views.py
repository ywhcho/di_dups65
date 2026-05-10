from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Medicine, DrugInfo


def duplicate_check(request):
    """의약품 중복성분 보기"""
    query = request.GET.get('q', '').strip()
    search_results = []
    if query:
        search_results = Medicine.objects.filter(htname__icontains=query).values('htname').distinct()

    # 선택 목록은 세션에 저장
    selected = request.session.get('selected_medicines', [])

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('medicine_name', '').strip()
            if name and name not in selected:
                selected.append(name)
                request.session['selected_medicines'] = selected
        elif action == 'remove':
            name = request.POST.get('medicine_name', '').strip()
            if name in selected:
                selected.remove(name)
                request.session['selected_medicines'] = selected
        elif action == 'clear':
            selected = []
            request.session['selected_medicines'] = selected

    # 선택 목록 페이지네이션 (7개씩)
    paginator = Paginator(selected, 7)
    page_number = request.GET.get('spage', 1)
    selected_page = paginator.get_page(page_number)

    # 중복성분 비교
    comparison_result = None
    if request.method == 'POST' and request.POST.get('action') == 'compare':
        selected = request.session.get('selected_medicines', [])
        comparison_result = compare_ingredients(selected)

    context = {
        'query': query,
        'search_results': search_results,
        'selected_page': selected_page,
        'selected': selected,
        'comparison_result': comparison_result,
    }
    return render(request, 'medicines/duplicate_check.html', context)


def compare_ingredients(selected_names):
    """선택된 약품들의 성분 비교"""
    if len(selected_names) < 2:
        return None

    medicines_data = {}
    for name in selected_names:
        meds = Medicine.objects.filter(htname=name)
        if meds.exists():
            ingreds = set()
            for med in meds:
                for ing in med.ingred.split(','):
                    ingreds.add(ing.strip())
            medicines_data[name] = ingreds

    if len(medicines_data) < 2:
        return {'error': '선택된 약품의 데이터를 찾을 수 없습니다.'}

    # 모든 성분 수집
    all_ingreds = set()
    for ingreds in medicines_data.values():
        all_ingreds.update(ingreds)

    # 각 성분이 어떤 약에 있는지 매핑
    ingred_map = {}
    for ingred in all_ingreds:
        ingred_map[ingred] = [name for name, ingreds in medicines_data.items() if ingred in ingreds]

    duplicate_ingreds = {k: v for k, v in ingred_map.items() if len(v) >= 2}
    unique_ingreds = {k: v for k, v in ingred_map.items() if len(v) == 1}

    return {
        'medicines_data': {k: sorted(v) for k, v in medicines_data.items()},
        'duplicate_ingreds': duplicate_ingreds,
        'unique_ingreds': unique_ingreds,
        'has_duplicates': len(duplicate_ingreds) > 0,
    }


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
