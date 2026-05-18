from itertools import combinations

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from medicines.models import Medicine

from .models import Mfname, Mintef


def interaction_check(request):
    """의약품 상호작용 보기"""
    query = request.GET.get('q', '').strip()
    search_results = Medicine.objects.none()
    search_page = None
    if query:
        search_results = (
            Medicine.objects.filter(htname__icontains=query)
            .values('htname')
            .distinct()
            .order_by('htname')
        )
        search_paginator = Paginator(search_results, 10)
        search_page_number = request.GET.get('qpage', 1)
        search_page = search_paginator.get_page(search_page_number)

    selected = request.session.get('selected_interaction_medicines', [])

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('medicine_name', '').strip()
            if name and name not in selected:
                selected.append(name)
                request.session['selected_interaction_medicines'] = selected
        elif action == 'remove':
            name = request.POST.get('medicine_name', '').strip()
            if name in selected:
                selected.remove(name)
                request.session['selected_interaction_medicines'] = selected
        elif action == 'clear':
            selected = []
            request.session['selected_interaction_medicines'] = selected

    selected_paginator = Paginator(selected, 7)
    selected_page_number = request.GET.get('spage', 1)
    selected_page = selected_paginator.get_page(selected_page_number)

    interaction_result = None
    if request.method == 'POST' and request.POST.get('action') == 'check':
        selected = request.session.get('selected_interaction_medicines', [])
        interaction_result = check_interactions(selected)

    context = {
        'query': query,
        'search_page': search_page,
        'selected_page': selected_page,
        'selected': selected,
        'interaction_result': interaction_result,
    }
    return render(request, 'med_interaction/interaction_check.html', context)


def _extract_igrnos(mfname_row):
    codes = []
    for field_name in ('igrno1', 'igrno2', 'igrno3', 'igrno4'):
        value = getattr(mfname_row, field_name, '')
        value = (value or '').strip()
        if value:
            codes.append(value)
    return codes


def check_interactions(selected_names):
    """선택 약품 간 상호작용 검사"""
    if len(selected_names) < 2:
        return None

    medicine_components = {}
    medicines_without_mapping = []

    for name in selected_names:
        medicines = Medicine.objects.filter(htname=name).exclude(wfco='')
        wfco_codes = {(med.wfco or '').strip()[:9] for med in medicines if (med.wfco or '').strip()}
        wfco_codes = {code for code in wfco_codes if code}
        if not wfco_codes:
            medicines_without_mapping.append(name)
            continue

        mfname_rows = Mfname.objects.filter(wfco__in=wfco_codes)
        igrnos = set()
        fnames = set()
        for row in mfname_rows:
            if row.fname:
                fnames.add(row.fname.strip())
            for igrno_code in _extract_igrnos(row):
                igrnos.add(igrno_code)

        if not igrnos:
            medicines_without_mapping.append(name)
            continue

        medicine_components[name] = {
            'wfco_codes': sorted(wfco_codes),
            'fnames': sorted(fnames),
            'igrnos': sorted(igrnos),
        }

    if len(medicine_components) < 2:
        return {'error': '상호작용 비교에 필요한 성분코드 정보를 찾을 수 없습니다.'}

    interaction_rows = []
    seen = set()

    for med_a, med_b in combinations(selected_names, 2):
        if med_a not in medicine_components or med_b not in medicine_components:
            continue

        igrnos_a = set(medicine_components[med_a]['igrnos'])
        igrnos_b = set(medicine_components[med_b]['igrnos'])
        if not igrnos_a or not igrnos_b:
            continue

        matches = Mintef.objects.filter(
            (Q(igrno_a__in=igrnos_a) & Q(igrno_b__in=igrnos_b))
            | (Q(igrno_a__in=igrnos_b) & Q(igrno_b__in=igrnos_a))
        )

        for match in matches:
            if match.igrno_a in igrnos_a and match.igrno_b in igrnos_b:
                code_a = match.igrno_a
                code_b = match.igrno_b
            else:
                code_a = match.igrno_b
                code_b = match.igrno_a

            dedup_key = (med_a, med_b, code_a, code_b, match.irisk, match.idesc, match.ireco)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            interaction_rows.append(
                {
                    'medicine_a': med_a,
                    'medicine_b': med_b,
                    'igrno_a': code_a,
                    'igrno_b': code_b,
                    'irisk': match.irisk or '-',
                    'idesc': match.idesc or '-',
                    'ireco': match.ireco or '-',
                }
            )

    interaction_rows.sort(
        key=lambda row: (
            row['medicine_a'],
            row['medicine_b'],
            row['irisk'],
            row['igrno_a'],
            row['igrno_b'],
        )
    )

    return {
        'medicine_components': medicine_components,
        'interaction_rows': interaction_rows,
        'has_interactions': len(interaction_rows) > 0,
        'medicines_without_mapping': medicines_without_mapping,
    }
