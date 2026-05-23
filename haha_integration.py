"""
HAHA Vending Machine API Integration Module

This module provides integration with HAHA Vending machines for:
- Real-time machine data synchronization
- Inventory tracking and updates
- Revenue data collection
- Machine status monitoring
- Automatic data refresh intervals
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from functools import wraps
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HAHAVendingAPI:
    """
    HAHA Vending Machine API Client
    
    Handles authentication, data synchronization, and real-time updates
    from HAHA vending machines.
    """
    
    def __init__(self, merchant_id: str, api_key: str, base_url: str = "https://api.hahavending.com"):
        """
        Initialize HAHA API client
        
        Args:
            merchant_id: HAHA merchant ID
            api_key: HAHA API key for authentication
            base_url: Base URL for HAHA API (default: production)
        """
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Snaxology-Portal/1.0'
        })
        self.last_sync = {}
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make HTTP request to HAHA API with error handling
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            Response JSON data
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout connecting to HAHA API: {endpoint}")
            return {'error': 'API timeout', 'status': 'error'}
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to HAHA API: {endpoint}")
            return {'error': 'Connection failed', 'status': 'error'}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error from HAHA API: {e.response.status_code}")
            return {'error': f'HTTP {e.response.status_code}', 'status': 'error'}
        except Exception as e:
            logger.error(f"Unexpected error in HAHA API request: {str(e)}")
            return {'error': str(e), 'status': 'error'}
    
    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached data if still valid"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None
    
    def _set_cache(self, key: str, data: Dict) -> None:
        """Cache data with timestamp"""
        self.cache[key] = (data, time.time())
    
    def authenticate(self) -> bool:
        """
        Authenticate with HAHA API
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            response = self._make_request('GET', 'v1/auth/verify')
            if response.get('status') == 'success':
                logger.info(f"Successfully authenticated with HAHA API for merchant {self.merchant_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    def get_machines(self, force_refresh: bool = False) -> List[Dict]:
        """
        Get all machines for the merchant
        
        Args:
            force_refresh: Force refresh from API (ignore cache)
            
        Returns:
            List of machine data dictionaries
        """
        cache_key = f"machines_{self.merchant_id}"
        
        if not force_refresh:
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        response = self._make_request('GET', f'v1/merchants/{self.merchant_id}/machines')
        
        if response.get('status') == 'success':
            machines = response.get('data', [])
            self._set_cache(cache_key, machines)
            self.last_sync['machines'] = datetime.utcnow().isoformat()
            return machines
        
        logger.warning(f"Failed to fetch machines: {response.get('error')}")
        return []
    
    def get_machine_status(self, device_id: str) -> Dict:
        """
        Get real-time status of a specific machine
        
        Args:
            device_id: HAHA device ID
            
        Returns:
            Machine status data
        """
        response = self._make_request('GET', f'v1/devices/{device_id}/status')
        
        if response.get('status') == 'success':
            return response.get('data', {})
        
        logger.warning(f"Failed to fetch machine status for {device_id}")
        return {}
    
    def get_machine_inventory(self, device_id: str) -> List[Dict]:
        """
        Get current inventory for a machine
        
        Args:
            device_id: HAHA device ID
            
        Returns:
            List of inventory items with quantities
        """
        response = self._make_request('GET', f'v1/devices/{device_id}/inventory')
        
        if response.get('status') == 'success':
            return response.get('data', [])
        
        logger.warning(f"Failed to fetch inventory for {device_id}")
        return []
    
    def get_machine_revenue(self, device_id: str, 
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> List[Dict]:
        """
        Get revenue data for a machine
        
        Args:
            device_id: HAHA device ID
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            
        Returns:
            List of revenue records
        """
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.utcnow().strftime('%Y-%m-%d')
        
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        response = self._make_request('GET', f'v1/devices/{device_id}/revenue', params=params)
        
        if response.get('status') == 'success':
            return response.get('data', [])
        
        logger.warning(f"Failed to fetch revenue for {device_id}")
        return []
    
    def get_all_revenue(self, start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> List[Dict]:
        """
        Get aggregated revenue for all machines
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            
        Returns:
            List of revenue records across all machines
        """
        if not start_date:
            start_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.utcnow().strftime('%Y-%m-%d')
        
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        response = self._make_request('GET', f'v1/merchants/{self.merchant_id}/revenue', params=params)
        
        if response.get('status') == 'success':
            return response.get('data', [])
        
        logger.warning("Failed to fetch aggregated revenue")
        return []
    
    def get_machine_transactions(self, device_id: str, limit: int = 100) -> List[Dict]:
        """
        Get recent transactions for a machine
        
        Args:
            device_id: HAHA device ID
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction records
        """
        params = {'limit': limit}
        response = self._make_request('GET', f'v1/devices/{device_id}/transactions', params=params)
        
        if response.get('status') == 'success':
            return response.get('data', [])
        
        logger.warning(f"Failed to fetch transactions for {device_id}")
        return []
    
    def update_machine_settings(self, device_id: str, settings: Dict) -> bool:
        """
        Update machine settings
        
        Args:
            device_id: HAHA device ID
            settings: Settings dictionary to update
            
        Returns:
            True if successful, False otherwise
        """
        response = self._make_request('PUT', f'v1/devices/{device_id}/settings', json=settings)
        
        if response.get('status') == 'success':
            logger.info(f"Successfully updated settings for machine {device_id}")
            return True
        
        logger.warning(f"Failed to update machine settings: {response.get('error')}")
        return False
    
    def report_machine_issue(self, device_id: str, issue_type: str, description: str) -> bool:
        """
        Report an issue with a machine
        
        Args:
            device_id: HAHA device ID
            issue_type: Type of issue (e.g., 'dispenser_jam', 'payment_error')
            description: Detailed description of the issue
            
        Returns:
            True if reported successfully, False otherwise
        """
        data = {
            'issue_type': issue_type,
            'description': description,
            'reported_at': datetime.utcnow().isoformat()
        }
        
        response = self._make_request('POST', f'v1/devices/{device_id}/issues', json=data)
        
        if response.get('status') == 'success':
            logger.info(f"Issue reported for machine {device_id}")
            return True
        
        logger.warning(f"Failed to report issue: {response.get('error')}")
        return False


class HAHADataSyncManager:
    """
    Manages synchronization of HAHA data with local database
    """
    
    def __init__(self, haha_api: HAHAVendingAPI, db_client=None):
        """
        Initialize data sync manager
        
        Args:
            haha_api: HAHAVendingAPI instance
            db_client: Database client for storing synced data
        """
        self.haha_api = haha_api
        self.db = db_client
        self.sync_intervals = {
            'machines': 3600,      # 1 hour
            'inventory': 1800,     # 30 minutes
            'revenue': 3600,       # 1 hour
            'transactions': 300    # 5 minutes
        }
        self.last_sync_time = {}
    
    def should_sync(self, sync_type: str) -> bool:
        """Check if enough time has passed to sync"""
        now = time.time()
        last_sync = self.last_sync_time.get(sync_type, 0)
        interval = self.sync_intervals.get(sync_type, 3600)
        return (now - last_sync) >= interval
    
    def sync_machines(self, force: bool = False) -> Tuple[bool, str]:
        """
        Sync machine data from HAHA to local database
        
        Args:
            force: Force sync regardless of interval
            
        Returns:
            Tuple of (success, message)
        """
        if not force and not self.should_sync('machines'):
            return True, "Skipped (too soon)"
        
        try:
            machines = self.haha_api.get_machines(force_refresh=force)
            
            if not machines:
                return False, "No machines returned from HAHA API"
            
            # Store in database (if db client available)
            if self.db:
                for machine in machines:
                    self._store_machine(machine)
            
            self.last_sync_time['machines'] = time.time()
            logger.info(f"Successfully synced {len(machines)} machines")
            return True, f"Synced {len(machines)} machines"
        
        except Exception as e:
            logger.error(f"Error syncing machines: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def sync_inventory(self, device_id: str, force: bool = False) -> Tuple[bool, str]:
        """
        Sync inventory data for a specific machine
        
        Args:
            device_id: HAHA device ID
            force: Force sync regardless of interval
            
        Returns:
            Tuple of (success, message)
        """
        if not force and not self.should_sync('inventory'):
            return True, "Skipped (too soon)"
        
        try:
            inventory = self.haha_api.get_machine_inventory(device_id)
            
            if self.db:
                for item in inventory:
                    self._store_inventory_item(device_id, item)
            
            self.last_sync_time['inventory'] = time.time()
            logger.info(f"Successfully synced inventory for {device_id}")
            return True, f"Synced {len(inventory)} items"
        
        except Exception as e:
            logger.error(f"Error syncing inventory: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def sync_revenue(self, device_id: Optional[str] = None, force: bool = False) -> Tuple[bool, str]:
        """
        Sync revenue data
        
        Args:
            device_id: Specific device ID (None for all machines)
            force: Force sync regardless of interval
            
        Returns:
            Tuple of (success, message)
        """
        if not force and not self.should_sync('revenue'):
            return True, "Skipped (too soon)"
        
        try:
            if device_id:
                revenue = self.haha_api.get_machine_revenue(device_id)
                label = f"device {device_id}"
            else:
                revenue = self.haha_api.get_all_revenue()
                label = "all machines"
            
            if self.db:
                for record in revenue:
                    self._store_revenue_record(record)
            
            self.last_sync_time['revenue'] = time.time()
            logger.info(f"Successfully synced revenue for {label}")
            return True, f"Synced {len(revenue)} revenue records"
        
        except Exception as e:
            logger.error(f"Error syncing revenue: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def sync_all(self, force: bool = False) -> Dict[str, Tuple[bool, str]]:
        """
        Perform full data synchronization
        
        Args:
            force: Force sync regardless of intervals
            
        Returns:
            Dictionary of sync results
        """
        results = {}
        
        # Sync machines
        success, msg = self.sync_machines(force)
        results['machines'] = (success, msg)
        
        # Sync all machine data
        if success:
            machines = self.haha_api.get_machines()
            for machine in machines:
                device_id = machine.get('device_id')
                
                # Sync inventory
                success, msg = self.sync_inventory(device_id, force)
                results[f'inventory_{device_id}'] = (success, msg)
                
                # Sync revenue
                success, msg = self.sync_revenue(device_id, force)
                results[f'revenue_{device_id}'] = (success, msg)
        
        return results
    
    def _store_machine(self, machine: Dict) -> None:
        """Store machine data in database"""
        if not self.db:
            return
        
        # Implementation depends on database client
        logger.debug(f"Storing machine: {machine.get('device_id')}")
    
    def _store_inventory_item(self, device_id: str, item: Dict) -> None:
        """Store inventory item in database"""
        if not self.db:
            return
        
        logger.debug(f"Storing inventory item for {device_id}")
    
    def _store_revenue_record(self, record: Dict) -> None:
        """Store revenue record in database"""
        if not self.db:
            return
        
        logger.debug(f"Storing revenue record")


class HAHAWebhookHandler:
    """
    Handles webhooks from HAHA for real-time updates
    """
    
    def __init__(self, db_client=None):
        """
        Initialize webhook handler
        
        Args:
            db_client: Database client for storing webhook data
        """
        self.db = db_client
        self.handlers = {}
    
    def register_handler(self, event_type: str, handler_func):
        """Register a handler for a specific event type"""
        self.handlers[event_type] = handler_func
        logger.info(f"Registered handler for event type: {event_type}")
    
    def handle_webhook(self, event_type: str, data: Dict) -> bool:
        """
        Handle incoming webhook
        
        Args:
            event_type: Type of event
            data: Event data
            
        Returns:
            True if handled successfully
        """
        try:
            if event_type in self.handlers:
                self.handlers[event_type](data)
                logger.info(f"Handled webhook event: {event_type}")
                return True
            
            logger.warning(f"No handler for event type: {event_type}")
            return False
        
        except Exception as e:
            logger.error(f"Error handling webhook: {str(e)}")
            return False
    
    def on_transaction(self, data: Dict) -> None:
        """Handle transaction event"""
        logger.info(f"Transaction event: {data}")
    
    def on_inventory_update(self, data: Dict) -> None:
        """Handle inventory update event"""
        logger.info(f"Inventory update: {data}")
    
    def on_machine_status_change(self, data: Dict) -> None:
        """Handle machine status change event"""
        logger.info(f"Machine status change: {data}")
    
    def on_error(self, data: Dict) -> None:
        """Handle error event"""
        logger.warning(f"Machine error: {data}")


# Demo/Mock implementation for testing without real HAHA credentials
class HAHAVendingAPIMock(HAHAVendingAPI):
    """Mock HAHA API for testing and demonstration"""
    
    def __init__(self, merchant_id: str = "demo_merchant"):
        """Initialize mock API"""
        self.merchant_id = merchant_id
        self.api_key = "demo_key"
        self.base_url = "https://api.hahavending.com"
        self.cache = {}
        self.cache_ttl = 300
        self.last_sync = {}
        
        # Mock data
        self.mock_machines = [
            {
                'device_id': 'HAHA-001',
                'machine_id': 'MX-001',
                'location': 'Downtown Mall',
                'status': 'online',
                'temperature': 4.2,
                'last_transaction': datetime.utcnow().isoformat(),
                'total_revenue': 1250.50,
                'units_sold': 245
            },
            {
                'device_id': 'HAHA-002',
                'machine_id': 'MX-002',
                'location': 'Airport Terminal',
                'status': 'online',
                'temperature': 3.8,
                'last_transaction': datetime.utcnow().isoformat(),
                'total_revenue': 2100.75,
                'units_sold': 412
            }
        ]
    
    def authenticate(self) -> bool:
        """Mock authentication"""
        logger.info("Mock: Authenticated successfully")
        return True
    
    def get_machines(self, force_refresh: bool = False) -> List[Dict]:
        """Return mock machines"""
        return self.mock_machines
    
    def get_machine_status(self, device_id: str) -> Dict:
        """Return mock machine status"""
        return {
            'device_id': device_id,
            'status': 'online',
            'temperature': 4.0,
            'battery': 95,
            'signal_strength': -45
        }
    
    def get_machine_inventory(self, device_id: str) -> List[Dict]:
        """Return mock inventory"""
        return [
            {'slot': 'A1', 'product': 'Coca-Cola', 'quantity': 45, 'capacity': 50},
            {'slot': 'A2', 'product': 'Sprite', 'quantity': 12, 'capacity': 50},
            {'slot': 'B1', 'product': 'Water', 'quantity': 38, 'capacity': 50},
            {'slot': 'B2', 'product': 'Juice', 'quantity': 5, 'capacity': 50}
        ]
    
    def get_machine_revenue(self, device_id: str,
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> List[Dict]:
        """Return mock revenue data"""
        revenue = []
        for i in range(30):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            revenue.append({
                'date': date,
                'device_id': device_id,
                'units_sold': 8 + (i % 5),
                'total_revenue': 40.00 + (i * 2.5),
                'average_transaction': 5.00
            })
        return revenue
    
    def get_all_revenue(self, start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> List[Dict]:
        """Return mock aggregated revenue"""
        revenue = []
        for i in range(30):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            revenue.append({
                'date': date,
                'total_revenue': 150.00 + (i * 5),
                'units_sold': 30 + (i * 2),
                'machine_count': 2
            })
        return revenue


# Export main classes
__all__ = [
    'HAHAVendingAPI',
    'HAHADataSyncManager',
    'HAHAWebhookHandler',
    'HAHAVendingAPIMock'
]
