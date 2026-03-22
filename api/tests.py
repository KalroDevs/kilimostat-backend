from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from core.models import *

class KilimoSTATAPITestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = APIClient()
        
        # Create test data
        self.area = Area.objects.create(
            name='Test Area',
            level='ADMIN_1',
            code='TEST01'
        )
        
        self.indicator = Indicator.objects.create(
            name='Test Indicator',
            code='TEST01',
            unit_of_measure='Tonnes/hectare'
        )
        
        self.unit = Unit.objects.create(
            name='Tonnes per hectare',
            symbol='t/ha',
            category='rate'
        )
        
        self.data_record = KilimoSTATData.objects.create(
            area=self.area,
            indicator=self.indicator,
            unit=self.unit,
            time_period='2021',
            data_value=100.5
        )
    
    def test_get_data_list(self):
        """Test getting list of data records"""
        response = self.client.get('/api/data/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
    
    def test_get_data_detail(self):
        """Test getting single data record"""
        response = self.client.get(f'/api/data/{self.data_record.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data_value'], 100.5)
    
    def test_filter_by_area(self):
        """Test filtering by area"""
        response = self.client.get(f'/api/data/?area={self.area.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['area'], self.area.id)
    
    def test_search(self):
        """Test search functionality"""
        response = self.client.get('/api/data/?search=Test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_export_csv(self):
        """Test CSV export"""
        response = self.client.get('/api/data/export/csv/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
    
    def test_summary_stats(self):
        """Test summary statistics"""
        response = self.client.get('/api/data/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('total_records' in response.data)