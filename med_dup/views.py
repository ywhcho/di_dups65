from django.core.paginator import Paginator
from django.shortcuts import render
from medicines.models import Medicine


def duplicate_check(request):
    """의약품 중복성분 보기"""
    query = request.GET.get('q', '').strip()
    search_results = []
    if query:
        search_results = Medicine.objects.filter(htname__icontains=query).values('htname').distinct()

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

    paginator = Paginator(selected, 7)
    page_number = request.GET.get('spage', 1)
    selected_page = paginator.get_page(page_number)

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
    return render(request, 'med_dup/duplicate_check.html', context)


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

    all_ingreds = set()
    for ingreds in medicines_data.values():
        all_ingreds.update(ingreds)

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
