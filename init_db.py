#!/usr/bin/env python
"""
Database initialization script for Snaxology Customer Portal

This script creates all database tables and optionally seeds sample data.
"""

import os
from app import app, db
from models import User, Customer, Machine, Inventory, Revenue, SupportTicket, Activity
from datetime import datetime, timedelta

def init_database():
    """Initialize the database with all tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")

def seed_sample_data():
    """Seed the database with sample data for testing"""
    with app.app_context():
        # Check if data already exists
        if User.query.first():
            print("Database already contains data. Skipping seed.")
            return
        
        print("Seeding sample data...")
        
        # Create sample user
        user = User(
            email='demo@snaxology.com',
            first_name='Demo',
            last_name='Customer',
            phone='555-0100'
        )
        user.set_password('demo123')
        db.session.add(user)
        db.session.flush()
        
        # Create sample customer
        customer = Customer(
            user_id=user.id,
            company_name='Demo Vending Co.',
            haha_merchant_id='DEMO-MERCHANT-001',
            address='123 Main Street',
            city='San Francisco',
            state='CA',
            zip_code='94105'
        )
        db.session.add(customer)
        db.session.flush()
        
        # Create sample machines
        machines = []
        for i in range(3):
            machine = Machine(
                customer_id=customer.id,
                machine_id=f'MX-{1000 + i}',
                haha_device_id=f'DEVICE-{i+1}',
                location=f'Location {i+1}',
                status='online',
                inventory_percentage=85.0 - (i * 10),
                monthly_revenue=500.0 + (i * 100)
            )
            db.session.add(machine)
            machines.append(machine)
        
        db.session.flush()
        
        # Create sample inventory items
        products = [
            {'name': 'Coca-Cola', 'sku': 'COKE-001'},
            {'name': 'Pepsi', 'sku': 'PEPSI-001'},
            {'name': 'Sprite', 'sku': 'SPRITE-001'},
            {'name': 'Water', 'sku': 'WATER-001'},
            {'name': 'Chips', 'sku': 'CHIPS-001'},
        ]
        
        for machine in machines:
            for product in products:
                inventory = Inventory(
                    machine_id=machine.id,
                    product_name=product['name'],
                    sku=product['sku'],
                    quantity=50 - (machines.index(machine) * 10),
                    low_stock_threshold=10,
                    status='in_stock'
                )
                db.session.add(inventory)
        
        db.session.flush()
        
        # Create sample revenue records (last 30 days)
        for machine in machines:
            for day in range(30):
                date = datetime.utcnow().date() - timedelta(days=day)
                revenue = Revenue(
                    machine_id=machine.id,
                    date=date,
                    units_sold=20 + (day % 10),
                    total_revenue=100.0 + (day * 5),
                    average_transaction=5.0
                )
                db.session.add(revenue)
        
        db.session.flush()
        
        # Create sample support tickets
        tickets = [
            {
                'subject': 'Machine not accepting coins',
                'description': 'The coin acceptor on machine MX-1000 is not working properly.',
                'priority': 'high',
                'status': 'open'
            },
            {
                'subject': 'Low inventory alert',
                'description': 'Multiple products are running low on stock.',
                'priority': 'medium',
                'status': 'in_progress'
            },
            {
                'subject': 'Revenue report request',
                'description': 'Need detailed revenue breakdown for last month.',
                'priority': 'low',
                'status': 'resolved'
            }
        ]
        
        for ticket_data in tickets:
            ticket = SupportTicket(
                customer_id=customer.id,
                machine_id=machines[0].id if ticket_data['subject'] == 'Machine not accepting coins' else None,
                ticket_number=f"TKT-{ticket_data['subject'][:3].upper()}-001",
                subject=ticket_data['subject'],
                description=ticket_data['description'],
                priority=ticket_data['priority'],
                status=ticket_data['status']
            )
            db.session.add(ticket)
        
        db.session.flush()
        
        # Create sample activities
        activities = [
            {
                'machine_id': machines[0].id,
                'activity_type': 'low_inventory',
                'description': 'Coca-Cola inventory below threshold'
            },
            {
                'machine_id': machines[1].id,
                'activity_type': 'payment',
                'description': 'Payment processed: $150.00'
            },
            {
                'machine_id': machines[2].id,
                'activity_type': 'restock',
                'description': 'Machine restocked with new inventory'
            }
        ]
        
        for activity_data in activities:
            activity = Activity(
                machine_id=activity_data['machine_id'],
                activity_type=activity_data['activity_type'],
                description=activity_data['description']
            )
            db.session.add(activity)
        
        db.session.commit()
        print("✓ Sample data seeded successfully!")
        print(f"\nSample login credentials:")
        print(f"  Email: demo@snaxology.com")
        print(f"  Password: demo123")

def main():
    """Main function"""
    import sys
    
    print("Snaxology Customer Portal - Database Initialization")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Ask if user wants to seed sample data
    if len(sys.argv) > 1 and sys.argv[1] == '--seed':
        seed_sample_data()
    else:
        print("\nTo seed sample data, run: python init_db.py --seed")

if __name__ == '__main__':
    main()
