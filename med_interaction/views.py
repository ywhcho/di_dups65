from itertools import combinations

from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from medicines.models import Medicine

from .models import Mfname, Mintef

RISK_GROUP_ORDER = ['A', 'B', 'C', 'D', 'E']
RISK_FILTER_OPTIONS = [
    ('', '전체'),
    ('A', 'A'),
    ('AB', 'AB'),
    ('BCDE', 'BCDE'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
]


def interaction_check(request):
    """의약품 상호작용 보기"""
    query = request.GET.get('q', '').strip()
    selected_risk_filter = request.session.get('selected_interaction_risk_filter', '')
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
        elif action == 'set_risk_filter':
            selected_risk_filter = request.POST.get('risk_filter', '').strip().upper()
            if selected_risk_filter not in {value for value, _ in RISK_FILTER_OPTIONS}:
                selected_risk_filter = ''
            request.session['selected_interaction_risk_filter'] = selected_risk_filter

    selected_paginator = Paginator(selected, 7)
    selected_page_number = request.GET.get('spage', 1)
    selected_page = selected_paginator.get_page(selected_page_number)

    interaction_result = None
    if request.method == 'POST' and request.POST.get('action') == 'check':
        selected = request.session.get('selected_interaction_medicines', [])
        selected_risk_filter = request.POST.get('risk_filter', '').strip().upper()
        if selected_risk_filter not in {value for value, _ in RISK_FILTER_OPTIONS}:
            selected_risk_filter = ''
        request.session['selected_interaction_risk_filter'] = selected_risk_filter
        interaction_result = check_interactions(selected, selected_risk_filter)

    context = {
        'query': query,
        'search_page': search_page,
        'selected_page': selected_page,
        'selected': selected,
        'interaction_result': interaction_result,
        'risk_filter_options': RISK_FILTER_OPTIONS,
        'selected_risk_filter': selected_risk_filter,
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


def _get_allowed_risks(risk_filter):
    mapping = {
        '': set(RISK_GROUP_ORDER),
        'A': {'A'},
        'AB': {'A', 'B'},
        'BCDE': {'B', 'C', 'D', 'E'},
        'B': {'B'},
        'C': {'C'},
        'D': {'D'},
        'E': {'E'},
    }
    return mapping.get(risk_filter, set(RISK_GROUP_ORDER))


def _normalize_risk(irisk):
    normalized = (irisk or '').strip().upper()[:1]
    if normalized in RISK_GROUP_ORDER:
        return normalized
    return ''


def check_interactions(selected_names, risk_filter=''):
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
    allowed_risks = _get_allowed_risks(risk_filter)

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

            risk_group = _normalize_risk(match.irisk)
            if risk_group and risk_group not in allowed_risks:
                continue
            if not risk_group and risk_filter:
                continue

            interaction_rows.append(
                {
                    'medicine_a': med_a,
                    'medicine_b': med_b,
                    'igrno_a': code_a,
                    'igrno_b': code_b,
                    'irisk': match.irisk or '-',
                    'risk_group': risk_group or '기타',
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

    interaction_groups = []
    for risk_code in RISK_GROUP_ORDER:
        rows = [row for row in interaction_rows if row['risk_group'] == risk_code]
        if rows:
            interaction_groups.append({'risk': risk_code, 'rows': rows})

    other_rows = [row for row in interaction_rows if row['risk_group'] == '기타']
    if other_rows:
        interaction_groups.append({'risk': '기타', 'rows': other_rows})

    return {
        'medicine_components': medicine_components,
        'interaction_rows': interaction_rows,
        'interaction_groups': interaction_groups,
        'has_interactions': len(interaction_rows) > 0,
        'medicines_without_mapping': medicines_without_mapping,
        'selected_risk_filter': risk_filter,
    }
