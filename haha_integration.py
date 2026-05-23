"""
HAHA Vending Machine API Integration Module

This module handles all interactions with the HAHA Open Platform API
for retrieving real-time vending machine data.
"""

import requests
import os
from datetime import datetime
from typing import Dict, List, Optional

class HAHAVendingAPI:
    """Client for HAHA Vending Machine API"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.getenv('HAHA_API_KEY')
        self.base_url = base_url or os.getenv('HAHA_API_BASE_URL', 'https://thor-openapi.hahavending.com')
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_merchant_info(self, merchant_id: str) -> Dict:
        """Get merchant information from HAHA API"""
        endpoint = f'{self.base_url}/api/v1/merchants/{merchant_id}'
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def get_devices(self, merchant_id: str) -> List[Dict]:
        """Get all devices (vending machines) for a merchant"""
        endpoint = f'{self.base_url}/api/v1/merchants/{merchant_id}/devices'
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get('devices', [])
        except requests.exceptions.RequestException as e:
            return []
    
    def get_device_status(self, device_id: str) -> Dict:
        """Get real-time status of a specific device"""
        endpoint = f'{self.base_url}/api/v1/devices/{device_id}/status'
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def get_device_inventory(self, device_id: str) -> Dict:
        """Get current inventory for a device"""
        endpoint = f'{self.base_url}/api/v1/devices/{device_id}/inventory'
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def get_device_revenue(self, device_id: str, start_date: str = None, end_date: str = None) -> Dict:
        """Get revenue data for a device within a date range"""
        endpoint = f'{self.base_url}/api/v1/devices/{device_id}/revenue'
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def get_device_transactions(self, device_id: str, limit: int = 100) -> List[Dict]:
        """Get recent transactions for a device"""
        endpoint = f'{self.base_url}/api/v1/devices/{device_id}/transactions'
        params = {'limit': limit}
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('transactions', [])
        except requests.exceptions.RequestException as e:
            return []
    
    def get_device_alerts(self, device_id: str) -> List[Dict]:
        """Get active alerts for a device"""
        endpoint = f'{self.base_url}/api/v1/devices/{device_id}/alerts'
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get('alerts', [])
        except requests.exceptions.RequestException as e:
            return []
    
    def acknowledge_alert(self, alert_id: str) -> Dict:
        """Acknowledge an alert"""
        endpoint = f'{self.base_url}/api/v1/alerts/{alert_id}/acknowledge'
        try:
            response = requests.post(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def get_network_summary(self, merchant_id: str) -> Dict:
        """Get summary statistics for all devices in a merchant network"""
        endpoint = f'{self.base_url}/api/v1/merchants/{merchant_id}/summary'
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}


class HAHADataSyncService:
    """Service for syncing HAHA data with local database"""
    
    def __init__(self, haha_client: HAHAVendingAPI, db_session):
        self.haha_client = haha_client
        self.db = db_session
    
    def sync_merchant_devices(self, customer_id: int, merchant_id: str):
        """Sync all devices for a merchant from HAHA API to local database"""
        from models import Machine, Activity
        
        devices = self.haha_client.get_devices(merchant_id)
        
        for device in devices:
            # Check if machine already exists
            existing_machine = Machine.query.filter_by(
                haha_device_id=device.get('device_id')
            ).first()
            
            if not existing_machine:
                # Create new machine record
                machine = Machine(
                    customer_id=customer_id,
                    machine_id=device.get('device_name', device.get('device_id')),
                    haha_device_id=device.get('device_id'),
                    location=device.get('location', 'Unknown'),
                    status=device.get('status', 'online')
                )
                self.db.session.add(machine)
                self.db.session.flush()
                
                # Log activity
                activity = Activity(
                    machine_id=machine.id,
                    activity_type='machine_synced',
                    description=f'Machine synced from HAHA API: {machine.machine_id}'
                )
                self.db.session.add(activity)
        
        self.db.session.commit()
    
    def sync_device_status(self, machine_id: int, haha_device_id: str):
        """Sync device status from HAHA API to local database"""
        from models import Machine
        
        status_data = self.haha_client.get_device_status(haha_device_id)
        
        if 'error' not in status_data:
            machine = Machine.query.get(machine_id)
            if machine:
                machine.status = status_data.get('status', 'online')
                machine.inventory_percentage = status_data.get('inventory_level', 100)
                self.db.session.commit()
    
    def sync_device_inventory(self, machine_id: int, haha_device_id: str):
        """Sync device inventory from HAHA API to local database"""
        from models import Machine, Inventory
        
        inventory_data = self.haha_client.get_device_inventory(haha_device_id)
        
        if 'error' not in inventory_data:
            machine = Machine.query.get(machine_id)
            if machine:
                items = inventory_data.get('items', [])
                
                for item in items:
                    # Check if inventory item exists
                    existing_item = Inventory.query.filter_by(
                        machine_id=machine_id,
                        sku=item.get('sku')
                    ).first()
                    
                    if existing_item:
                        # Update existing item
                        existing_item.quantity = item.get('quantity', 0)
                        existing_item.product_name = item.get('product_name', existing_item.product_name)
                        
                        # Update status based on quantity
                        if existing_item.quantity == 0:
                            existing_item.status = 'out_of_stock'
                        elif existing_item.quantity <= existing_item.low_stock_threshold:
                            existing_item.status = 'low_stock'
                        else:
                            existing_item.status = 'in_stock'
                    else:
                        # Create new inventory item
                        new_item = Inventory(
                            machine_id=machine_id,
                            product_name=item.get('product_name', 'Unknown'),
                            sku=item.get('sku', ''),
                            quantity=item.get('quantity', 0),
                            low_stock_threshold=item.get('low_stock_threshold', 10),
                            status='in_stock' if item.get('quantity', 0) > 0 else 'out_of_stock'
                        )
                        self.db.session.add(new_item)
                
                self.db.session.commit()
    
    def sync_device_revenue(self, machine_id: int, haha_device_id: str, days: int = 30):
        """Sync device revenue from HAHA API to local database"""
        from models import Machine, Revenue
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        revenue_data = self.haha_client.get_device_revenue(
            haha_device_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        if 'error' not in revenue_data:
            machine = Machine.query.get(machine_id)
            if machine:
                daily_records = revenue_data.get('daily_revenue', [])
                
                for record in daily_records:
                    # Check if revenue record exists
                    existing_record = Revenue.query.filter_by(
                        machine_id=machine_id,
                        date=datetime.fromisoformat(record.get('date')).date()
                    ).first()
                    
                    if not existing_record:
                        # Create new revenue record
                        revenue = Revenue(
                            machine_id=machine_id,
                            date=datetime.fromisoformat(record.get('date')).date(),
                            units_sold=record.get('units_sold', 0),
                            total_revenue=record.get('total_revenue', 0.0),
                            average_transaction=record.get('average_transaction', 0.0)
                        )
                        self.db.session.add(revenue)
                
                # Update machine's monthly revenue
                monthly_revenue = sum([r.get('total_revenue', 0) for r in daily_records])
                machine.monthly_revenue = monthly_revenue
                
                self.db.session.commit()
