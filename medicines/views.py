from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import DrugInfo


# ---------- 의약정보 보기 ----------

def druginfo_list(request):
    """의약정보 목록 - 분야 선택 + 검색어로 검색"""
    field_map = {
        'htname': ('htname', '약품명'),
        'ingred': ('ingred', '성분'),
        'company': ('company', '회사'),
        'ee': ('ee', '효능'),
    }
    search_field = request.GET.get('field', 'htname').strip()
    search_q = request.GET.get('q', '').strip()
    if search_field not in field_map:
        search_field = 'htname'

    drugs = DrugInfo.objects.all()

    if search_q:
        filter_field = field_map[search_field][0]
        drugs = drugs.filter(**{f'{filter_field}__icontains': search_q})

    paginator = Paginator(drugs, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_field': search_field,
        'search_field_label': field_map[search_field][1],
        'search_q': search_q,
    }
    return render(request, 'medicines/druginfo_list.html', context)


def druginfo_detail(request, pk):
    """의약정보 상세 보기"""
    drug = get_object_or_404(DrugInfo, pk=pk)
    return render(request, 'medicines/druginfo_detail.html', {'drug': drug})
