from unittest.mock import patch, sentinel

from django.test import SimpleTestCase
from django.urls import reverse

from equiv_ingr import views


class Table1QuerysetTests(SimpleTestCase):
    @patch('equiv_ingr.views.MedInteractionMfname.objects')
    def test_atc_search_uses_prefix_lookup_and_wfco_ordering(self, mock_manager):
        ordered_qs = object()
        mock_qs = mock_manager.filter.return_value
        mock_qs.order_by.return_value = ordered_qs

        result = views._get_table1_queryset('ATC', 'A10')

        mock_manager.filter.assert_called_once_with(ATC__istartswith='A10')
        mock_qs.order_by.assert_called_once_with('wfco', 'id')
        self.assertIs(result, ordered_qs)

    @patch('equiv_ingr.views.MedInteractionMfname.objects')
    def test_non_atc_search_uses_contains_lookup_with_wfco_ordering(self, mock_manager):
        ordered_qs = object()
        mock_qs = mock_manager.filter.return_value
        mock_qs.order_by.return_value = ordered_qs

        result = views._get_table1_queryset('wfco', '123')

        mock_manager.filter.assert_called_once_with(wfco__icontains='123')
        mock_qs.order_by.assert_called_once_with('wfco', 'id')
        self.assertIs(result, ordered_qs)

    @patch('equiv_ingr.views.MedInteractionMfname.objects')
    def test_unknown_search_type_returns_none_queryset(self, mock_manager):
        none_qs = sentinel.none_qs
        mock_manager.none.return_value = none_qs

        result = views._get_table1_queryset('unknown', 'value')

        mock_manager.none.assert_called_once_with()
        self.assertIs(result, none_qs)


class Table2QuerysetTests(SimpleTestCase):
    @patch('equiv_ingr.views.MedicinesMedicine.objects')
    def test_htname_sort_orders_by_product_name(self, mock_manager):
        ordered_qs = object()
        filtered_qs = mock_manager.filter.return_value
        annotated_qs = filtered_qs.annotate.return_value
        annotated_qs.order_by.return_value = ordered_qs

        result = views._get_table2_queryset('20745A10AT', 'htname')

        mock_manager.filter.assert_called_once_with(wfco='20745A10AT')
        annotated_qs.order_by.assert_called_once_with('htname', 'id')
        self.assertIs(result, ordered_qs)

    @patch('equiv_ingr.views.MedicinesMedicine.objects')
    def test_company_sort_orders_by_company(self, mock_manager):
        ordered_qs = object()
        annotated_qs = mock_manager.filter.return_value.annotate.return_value
        annotated_qs.order_by.return_value = ordered_qs

        result = views._get_table2_queryset('20745A10AT', 'company')

        annotated_qs.order_by.assert_called_once_with('company', 'id')
        self.assertIs(result, ordered_qs)

    @patch('equiv_ingr.views.MedicinesMedicine.objects')
    def test_invalid_sort_defaults_to_ypri24_desc(self, mock_manager):
        ordered_qs = object()
        annotated_qs = mock_manager.filter.return_value.annotate.return_value
        annotated_qs.order_by.return_value = ordered_qs

        result = views._get_table2_queryset('20745A10AT', 'unknown')

        annotated_qs.order_by.assert_called_once_with('-ypri24_num', 'id')
        self.assertIs(result, ordered_qs)


class Table2SortLinkTests(SimpleTestCase):
    def test_sort_links_preserve_search_state_and_reset_page2(self):
        links = views._get_table2_sort_links('ATC', 'A10', '20745A10AT', 3)

        self.assertEqual(
            links['htname'],
            '?type=ATC&val=A10&wfco=20745A10AT&page1=3&page2=1&sort2=htname',
        )
        self.assertEqual(
            links['company'],
            '?type=ATC&val=A10&wfco=20745A10AT&page1=3&page2=1&sort2=company',
        )
        self.assertEqual(
            links['ypri24'],
            '?type=ATC&val=A10&wfco=20745A10AT&page1=3&page2=1&sort2=ypri24',
        )


class NavigationIntegrationTests(SimpleTestCase):
    def test_home_page_lists_equiv_ingr_between_other_system_menus(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertLess(content.index('중복성분보기'), content.index('동일성분찾기'))
        self.assertLess(content.index('동일성분찾기'), content.index('의약정보보기'))
        self.assertContains(response, reverse('equiv_ingr:search'))

    def test_equiv_ingr_search_is_available_under_app_path(self):
        response = self.client.get(reverse('equiv_ingr:search'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '동일성분 찾기 (equiv_ingr)')

    def test_board_page_is_accessible(self):
        response = self.client.get(reverse('board'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '게시판')

    def test_about_page_is_accessible(self):
        response = self.client.get(reverse('about'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'About Us')

    def test_all_nav_items_present_on_home(self):
        response = self.client.get(reverse('home'))

        self.assertContains(response, '중복성분보기')
        self.assertContains(response, '동일성분찾기')
        self.assertContains(response, '의약정보보기')
        self.assertContains(response, '게시판')
        self.assertContains(response, 'About Us')
        self.assertContains(response, '로그인')
