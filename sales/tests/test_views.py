from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from sales.models import Sale

User = get_user_model()


class SaleViewBaseTest(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username='viewstaff',
            email='viewstaff@test.com',
            password='testpass123',
            is_staff=True,
            is_superuser=True,
        )
        self.non_staff_user = User.objects.create_user(
            username='viewuser',
            email='viewuser@test.com',
            password='testpass123',
            is_staff=False,
        )
        self.sale = Sale.objects.create(
            sale_number='SALE-20000',
            customer_name='Cliente Vista',
            customer_email='cliente.vista@test.com',
            seller=self.staff_user,
        )


class SaleListViewTest(SaleViewBaseTest):
    def test_requires_login(self):
        response = self.client.get(reverse('sales:sale_list'))
        self.assertEqual(response.status_code, 403)

    def test_staff_can_access_list(self):
        self.client.login(username='viewstaff', password='testpass123')
        response = self.client.get(reverse('sales:sale_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sale.sale_number)

    def test_non_staff_forbidden(self):
        self.client.login(username='viewuser', password='testpass123')
        response = self.client.get(reverse('sales:sale_list'))
        self.assertEqual(response.status_code, 403)

    def test_search_filter(self):
        self.client.login(username='viewstaff', password='testpass123')
        response = self.client.get(reverse('sales:sale_list'), {'search': 'Vista'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sale.sale_number)


class SaleCreateViewTest(SaleViewBaseTest):
    def test_create_sale_success(self):
        self.client.login(username='viewstaff', password='testpass123')
        response = self.client.post(
            reverse('sales:sale_create'),
            data={
                'customer_name': 'Nuevo Cliente',
                'customer_email': 'nuevo@test.com',
                'customer_phone': '+54 9 11 2222-2222',
                'notes': 'Creado desde test',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Sale.objects.filter(customer_name='Nuevo Cliente').exists())


class SaleDetailAndDeleteViewTest(SaleViewBaseTest):
    def test_detail_view(self):
        self.client.login(username='viewstaff', password='testpass123')
        response = self.client.get(reverse('sales:sale_detail', args=[self.sale.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.sale.customer_name)

    def test_soft_delete_view(self):
        self.client.login(username='viewstaff', password='testpass123')
        response = self.client.post(reverse('sales:sale_delete', args=[self.sale.pk]))
        self.assertEqual(response.status_code, 302)
        self.sale.refresh_from_db()
        self.assertFalse(self.sale.is_active)
