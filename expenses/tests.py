from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Expense
import json

class UserViewsTests(TestCase):
    def setUp(self):
        # Initialize the test client
        self.client = Client()
        
        # Create test data
        self.user = User.objects.create(
            email='testuser@gmail.com',
            name='Test User',
            mobile_number='1234567890'
        )
        self.user_url = reverse('user_details', args=[self.user.id])
        self.add_expenses_url = reverse('add')
        self.user_expenses_url = reverse('user_expenses', args=[self.user.id])
        self.overall_expenses_url = reverse('all_expenses')
        self.download_balance_sheet_url = reverse('download_balance_sheet', args=[self.user.id])
        
    def test_create_user(self):
        response = self.client.post(reverse('home'), data=json.dumps({
            'email': 'newuser@gmail.com',
            'name': 'New User',
            'mobile_number': '0987654321'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.json())
        
    def test_user_details(self):
        response = self.client.get(self.user_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'Test User')
        self.assertEqual(data['email'], 'testuser@gmail.com')
        
    def test_add_expenses(self):
        response = self.client.post(self.add_expenses_url, data=json.dumps({
            'event': 'Lunch',
            'amount': 100.00,
            'split_method': 'EQUAL',
            'participants': [self.user.id]
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Expense.objects.count(), 1)
        
    def test_user_expenses(self):
        Expense.objects.create(
            Event='Dinner',
            user_id=self.user.id,
            amount=50.00,
            split_method='EQUAL'
        )
        response = self.client.get(self.user_expenses_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['Event'], 'Dinner')
        
    def test_overall_expenses(self):
        response = self.client.get(self.overall_expenses_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data), 0)  # Check that data is returned
        
    def test_download_balance_sheet(self):
        Expense.objects.create(
            Event='Event1',
            user_id=self.user.id,
            amount=200.00,
            split_method='EXACT'
        )
        response = self.client.get(self.download_balance_sheet_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    def test_invalid_method(self):
        response = self.client.post(self.user_url)  # POST method instead of GET
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid method')

    def test_create_user_invalid_email(self):
        response = self.client.post(reverse('home'), data=json.dumps({
            'email': 'invalidemail.com',
            'name': 'Invalid User',
            'mobile_number': '1234567890'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid email address')
        
    def test_create_user_invalid_mobile(self):
        response = self.client.post(reverse('home'), data=json.dumps({
            'email': 'validemail@gmail.com',
            'name': 'Invalid Mobile',
            'mobile_number': '12345'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'Invalid mobile number')
