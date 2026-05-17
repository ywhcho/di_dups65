from django.core.paginator import Paginator
from django.shortcuts import render
from medicines.models import Medicine
import re

MASS_UNIT_FACTORS_TO_MCG = {
    'kg': 1_000_000_000,
    'g': 1_000_000,
    'mg': 1_000,
    'mcg': 1,
}


def duplicate_check(request):
    """의약품 중복성분 보기"""
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
        'search_page': search_page,
        'selected_page': selected_page,
        'selected': selected,
        'comparison_result': comparison_result,
    }
    return render(request, 'med_dup/duplicate_check.html', context)


def _split_ingredient_entries(raw_ingred):
    if not raw_ingred:
        return []
    if '_' in raw_ingred:
        parts = raw_ingred.split('_')
    else:
        parts = raw_ingred.split(',')
    return [part.strip() for part in parts if part.strip()]


def _parse_dose_info(dose_text):
    cleaned = (dose_text or '').strip().replace('/', '')
    cleaned = re.sub(r'(?<=\d),(?=\d)', '', cleaned)
    match = re.search(r'(\d+(?:\.\d+)?)\s*([^\d\s]+)?', cleaned)
    if not match:
        return cleaned, None, None

    value = float(match.group(1))
    unit = (match.group(2) or '').strip()
    if unit:
        normalized = f"{value:g}{unit}"
    else:
        normalized = f"{value:g}"
    return normalized, value, unit


def _parse_ingredient_entry(entry):
    if ':' in entry:
        ingredient, dose_raw = entry.split(':', 1)
    else:
        ingredient, dose_raw = entry, ''
    ingredient = ingredient.strip()
    dose_display, dose_value, dose_unit = _parse_dose_info(dose_raw)
    return ingredient, dose_display, dose_value, dose_unit


def _normalize_mass_unit(unit):
    normalized = (unit or '').strip().lower().replace('μ', 'u')
    if normalized in {'mcg', 'ug'}:
        return 'mcg'
    if normalized in {'mg', 'g', 'kg'}:
        return normalized
    return None


def _format_total_dose(amounts):
    mass_amounts = []
    other_totals = {}

    for amount in amounts:
        value = amount['value']
        unit = amount['unit']
        mass_unit = _normalize_mass_unit(unit)
        if mass_unit:
            mass_amounts.append((value, mass_unit))
        else:
            other_totals[unit] = other_totals.get(unit, 0.0) + value

    parts = []
    if mass_amounts:
        target_unit = min(
            {unit for _, unit in mass_amounts},
            key=lambda unit: MASS_UNIT_FACTORS_TO_MCG[unit],
        )
        total_mcg = sum(value * MASS_UNIT_FACTORS_TO_MCG[unit] for value, unit in mass_amounts)
        total_value = total_mcg / MASS_UNIT_FACTORS_TO_MCG[target_unit]
        parts.append(f"{total_value:g}{target_unit}")

    for unit, total in sorted(other_totals.items()):
        parts.append(f"{total:g}{unit}")

    return ' + '.join(parts) if parts else '-'


def compare_ingredients(selected_names):
    """선택된 약품들의 성분 비교"""
    if len(selected_names) < 2:
        return None

    medicines_data = {}
    ingredient_usage = {}

    for name in selected_names:
        meds = Medicine.objects.filter(htname=name)
        if meds.exists():
            ingreds = {}
            for med in meds:
                for entry in _split_ingredient_entries(med.ingred):
                    ingredient, dose_display, dose_value, dose_unit = _parse_ingredient_entry(entry)
                    if not ingredient:
                        continue
                    ingreds[ingredient] = {
                        'dose_display': dose_display,
                        'dose_value': dose_value,
                        'dose_unit': dose_unit,
                    }
            medicines_data[name] = sorted(
                [
                    f"{ingredient}:{data['dose_display']}" if data['dose_display'] else ingredient
                    for ingredient, data in ingreds.items()
                ]
            )

            for ingredient, dose_data in ingreds.items():
                usage = ingredient_usage.setdefault(ingredient, {'details': [], 'amounts': []})
                detail = {
                    'medicine': name,
                    'dose': dose_data['dose_display'] or '-',
                }
                usage['details'].append(detail)

                if dose_data['dose_value'] is not None and dose_data['dose_unit']:
                    usage['amounts'].append(
                        {
                            'value': dose_data['dose_value'],
                            'unit': dose_data['dose_unit'],
                        }
                    )

    if len(medicines_data) < 2:
        return {'error': '선택된 약품의 데이터를 찾을 수 없습니다.'}

    duplicate_ingreds = []
    for ingredient, usage in ingredient_usage.items():
        details = usage['details']
        if len(details) < 2:
            continue

        total_dose = _format_total_dose(usage['amounts'])

        duplicate_ingreds.append(
            {
                'ingredient': ingredient,
                'count': len(details),
                'total_dose': total_dose,
                'details': details,
            }
        )

    duplicate_ingreds.sort(key=lambda item: item['ingredient'])

    return {
        'medicines_data': medicines_data,
        'duplicate_ingreds': duplicate_ingreds,
        'has_duplicates': len(duplicate_ingreds) > 0,
    }
