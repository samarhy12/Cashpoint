"""
Seed the database with comprehensive test data.

This wipes the existing database and recreates the schema, then adds:
- Admin, office staff, and agent users
- Sample customers with various profiles
- Active and completed loans
- Guarantors
- Repayments
- Expenses
- Cash transactions
- Business day records

Usage:
    python seed.py
"""
from app import create_app
from extensions import db
from models import (
    Staff, Customer, Guarantor, Loan, Repayment, 
    CashTransaction, Expense, BusinessDay, EXPENSE_CATEGORIES,
    next_registration_number, generate_transaction_id, TermType
)
from datetime import date, timedelta, datetime
import os
import random


def main():
    app = create_app()
    with app.app_context():
        print(">> Resetting database and creating comprehensive test data...")
        db.drop_all()
        db.create_all()

        # Create admin user
        username = os.environ.get("ADMIN_USERNAME", "admin")
        password = os.environ.get("ADMIN_PASSWORD") or os.environ.get("INITIAL_ADMIN_PASSWORD")
        if not password:
            raise RuntimeError("ADMIN_PASSWORD must be configured in the environment or .env file")

        admin = Staff(full_name="System Administrator", username=username, role="admin")
        admin.set_password(password)
        admin.must_change_password = True
        db.session.add(admin)
        db.session.commit()

        print(f">> Admin created — username: {username} / password: {password}")

        # Create office staff
        office_staff = Staff(
            full_name="Office Manager",
            username="office",
            role="office_staff"
        )
        office_staff.set_password("office123")
        db.session.add(office_staff)

        # Create agents
        agents = []
        agent_names = [
            ("Kwame Mensah", "kwame"),
            ("Ama Ofori", "ama"),
            ("Kofi Asante", "kofi"),
        ]
        for full_name, username in agent_names:
            agent = Staff(full_name=full_name, username=username, role="agent")
            agent.set_password("agent123")
            db.session.add(agent)
            agents.append(agent)

        db.session.commit()
        print(f">> Created 1 office staff and {len(agents)} agents")

        # Create customers
        customers = []
        customer_data = [
            {
                "full_name": "John Doe",
                "gender": "Male",
                "date_of_birth": date(1985, 5, 15),
                "id_type": "Ghana Card",
                "id_number": "GHA-123456789-0",
                "phone_number": "0241234567",
                "residential_address": "123 Main Street, Accra",
                "occupation": "Trader",
                "employment_status": "Self-employed",
                "business_type": "Retail Shop",
            },
            {
                "full_name": "Jane Smith",
                "gender": "Female",
                "date_of_birth": date(1990, 8, 22),
                "id_type": "Voter ID",
                "id_number": "VOT-987654321-1",
                "phone_number": "0209876543",
                "residential_address": "45 Market Road, Kumasi",
                "occupation": "Farmer",
                "employment_status": "Self-employed",
                "business_type": "Crop Farming",
            },
            {
                "full_name": "Emmanuel Osei",
                "gender": "Male",
                "date_of_birth": date(1978, 3, 10),
                "id_type": "Ghana Card",
                "id_number": "GHA-987654321-2",
                "phone_number": "0551122334",
                "residential_address": "78 Industrial Area, Tema",
                "occupation": "Driver",
                "employment_status": "Employed",
                "business_type": None,
            },
            {
                "full_name": "Grace Appiah",
                "gender": "Female",
                "date_of_birth": date(1995, 11, 30),
                "id_type": "Passport",
                "id_number": "PASS-A1234567",
                "phone_number": "0275566778",
                "residential_address": "12 School Lane, Cape Coast",
                "occupation": "Teacher",
                "employment_status": "Employed",
                "business_type": None,
            },
            {
                "full_name": "Samuel Addo",
                "gender": "Male",
                "date_of_birth": date(1982, 7, 8),
                "id_type": "Ghana Card",
                "id_number": "GHA-456789123-3",
                "phone_number": "0509988776",
                "residential_address": "56 Hospital Road, Tamale",
                "occupation": "Contractor",
                "employment_status": "Self-employed",
                "business_type": "Construction",
            },
        ]

        for i, data in enumerate(customer_data):
            customer = Customer(
                registration_number=next_registration_number(),
                created_by_id=admin.id,
                **data
            )
            db.session.add(customer)
            customers.append(customer)

        db.session.commit()
        print(f">> Created {len(customers)} customers")

        # Create guarantors (both standalone and from customers)
        guarantors = []
        
        # Standalone guarantors
        standalone_guarantors = [
            {
                "full_name": "Michael Johnson",
                "gender": "Male",
                "date_of_birth": date(1975, 2, 14),
                "id_type": "Ghana Card",
                "id_number": "GHA-111222333-4",
                "phone_number": "0245556667",
                "residential_address": "99 Avenue A, Accra",
                "occupation": "Civil Servant",
                "employment_status": "Employed",
                "business_type": None,
            },
            {
                "full_name": "Elizabeth Mensah",
                "gender": "Female",
                "date_of_birth": date(1980, 6, 25),
                "id_type": "Voter ID",
                "id_number": "VOT-444555666-5",
                "phone_number": "0207778889",
                "residential_address": "33 Street B, Kumasi",
                "occupation": "Nurse",
                "employment_status": "Employed",
                "business_type": None,
            },
        ]

        for data in standalone_guarantors:
            guarantor = Guarantor(**data)
            db.session.add(guarantor)
            guarantors.append(guarantor)

        db.session.commit()
        print(f">> Created {len(guarantors)} guarantors")

        # Create loans with different statuses
        today = date.today()
        loans = []
        
        loan_data = [
            {
                "customer": customers[0],
                "principal": 5000.0,
                "interest_rate": 0.10,
                "duration_value": 6,
                "term_type": "monthly",
                "start_date": today - timedelta(days=30),
                "guarantor_customer": customers[1],
                "created_by": admin,
                "status": "active",
            },
            {
                "customer": customers[1],
                "principal": 3000.0,
                "interest_rate": 0.12,
                "duration_value": 8,
                "term_type": "weekly",
                "start_date": today - timedelta(days=60),
                "guarantor": guarantors[0],
                "created_by": agents[0],
                "status": "active",
            },
            {
                "customer": customers[2],
                "principal": 2000.0,
                "interest_rate": 0.08,
                "duration_value": 20,
                "term_type": "daily",
                "start_date": today - timedelta(days=90),
                "guarantor_customer": customers[0],
                "created_by": agents[1],
                "status": "completed",
            },
            {
                "customer": customers[3],
                "principal": 4000.0,
                "interest_rate": 0.10,
                "duration_value": 4,
                "term_type": "monthly",
                "start_date": today - timedelta(days=45),
                "guarantor": guarantors[1],
                "created_by": office_staff,
                "status": "active",
            },
            {
                "customer": customers[4],
                "principal": 1500.0,
                "interest_rate": 0.15,
                "duration_value": 12,
                "term_type": "weekly",
                "start_date": today - timedelta(days=15),
                "guarantor_customer": customers[1],
                "created_by": agents[2],
                "status": "active",
            },
        ]

        for data in loan_data:
            loan = Loan(
                customer=data["customer"],
                principal=data["principal"],
                interest_rate=data["interest_rate"],
                duration_value=data["duration_value"],
                term_type=data["term_type"],
                start_date=data["start_date"],
                created_by=data["created_by"],
                status=data["status"],
            )
            
            # Set guarantor
            if "guarantor_customer" in data:
                loan.guarantor_customer_id = data["guarantor_customer"].id
            elif "guarantor" in data:
                loan.guarantor_id = data["guarantor"].id
            
            # Compute loan schedule
            end_date, total_interest, total_repayable, installment, num_installments = Loan.compute_schedule(
                loan.principal,
                loan.interest_rate,
                loan.term_type,
                loan.duration_value,
                loan.start_date
            )
            
            loan.end_date = end_date
            loan.total_interest = total_interest
            loan.total_repayable = total_repayable
            loan.installment_amount = installment
            loan.number_of_installments = num_installments
            
            db.session.add(loan)
            loans.append(loan)

        db.session.commit()
        print(f">> Created {len(loans)} loans")

        # Create repayments
        repayments = []
        
        # Add repayments for the completed loan (loans[2])
        completed_loan = loans[2]
        for i in range(completed_loan.number_of_installments):
            repayment_date = completed_loan.start_date + timedelta(days=i * 5)  # Daily loan
            repayment = Repayment(
                transaction_id=generate_transaction_id(completed_loan.customer, repayment_date),
                loan_id=completed_loan.id,
                amount=completed_loan.installment_amount,
                date=repayment_date,
                agent_id=agents[1].id,
                recorded_by_id=agents[1].id,
            )
            db.session.add(repayment)
            repayments.append(repayment)

        # Add partial repayments for active loans
        for loan in [loans[0], loans[1], loans[3]]:
            num_payments = random.randint(1, min(3, loan.number_of_installments))
            for i in range(num_payments):
                payment_date = loan.start_date + timedelta(days=i * 30 if loan.term_type == "monthly" else i * 7)
                repayment = Repayment(
                    transaction_id=generate_transaction_id(loan.customer, payment_date),
                    loan_id=loan.id,
                    amount=loan.installment_amount,
                    date=payment_date,
                    agent_id=random.choice(agents).id,
                    recorded_by_id=random.choice([admin.id, office_staff.id]),
                )
                db.session.add(repayment)
                repayments.append(repayment)

        db.session.commit()
        print(f">> Created {len(repayments)} repayments")

        # Create cash transactions
        cash_transactions = []
        
        # Initial capital injection
        capital_in = CashTransaction(
            tx_type="capital_in",
            amount=50000.0,
            description="Initial capital injection",
            staff_id=admin.id,
            date=today - timedelta(days=120),
        )
        db.session.add(capital_in)
        cash_transactions.append(capital_in)

        # Loan disbursements
        for loan in loans:
            disbursement = CashTransaction(
                tx_type="disbursement",
                amount=-loan.principal,
                description=f"Loan disbursement - {loan.loan_code}",
                loan_id=loan.id,
                customer_id=loan.customer_id,
                staff_id=loan.created_by_id,
                date=loan.start_date,
            )
            db.session.add(disbursement)
            cash_transactions.append(disbursement)

        # Repayment collections
        for repayment in repayments:
            collection = CashTransaction(
                tx_type="repayment",
                amount=repayment.amount,
                description=f"Repayment - {repayment.transaction_id}",
                loan_id=repayment.loan_id,
                customer_id=repayment.loan.customer_id,
                staff_id=repayment.agent_id,
                date=repayment.date,
            )
            db.session.add(collection)
            cash_transactions.append(collection)

        db.session.commit()
        print(f">> Created {len(cash_transactions)} cash transactions")

        # Create expenses
        expenses = []
        expense_data = [
            {
                "description": "Office rent for July",
                "category": "Rent",
                "amount": 2500.0,
                "date": today - timedelta(days=5),
            },
            {
                "description": "Fuel for field visits",
                "category": "Transport",
                "amount": 350.0,
                "date": today - timedelta(days=3),
            },
            {
                "description": "Office internet bundle",
                "category": "Airtime & Data",
                "amount": 200.0,
                "date": today - timedelta(days=2),
            },
            {
                "description": "Electricity bill",
                "category": "Utilities",
                "amount": 450.0,
                "date": today - timedelta(days=1),
            },
            {
                "description": "Office supplies and stationery",
                "category": "Office Supplies",
                "amount": 150.0,
                "date": today,
            },
            {
                "description": "Staff transportation allowance",
                "category": "Transport",
                "amount": 500.0,
                "date": today - timedelta(days=7),
            },
            {
                "description": "Printer maintenance",
                "category": "Maintenance",
                "amount": 120.0,
                "date": today - timedelta(days=10),
            },
        ]

        for data in expense_data:
            expense = Expense(
                description=data["description"],
                category=data["category"],
                amount=data["amount"],
                date=data["date"],
                recorded_by_id=admin.id,
            )
            db.session.add(expense)
            expenses.append(expense)

            # Create corresponding cash transaction
            cash_tx = CashTransaction(
                tx_type="expense",
                amount=-data["amount"],
                description=f"{data['category']}: {data['description']}",
                expense_id=expense.id,
                staff_id=admin.id,
                date=data["date"],
            )
            db.session.add(cash_tx)
            cash_transactions.append(cash_tx)

        db.session.commit()
        print(f">> Created {len(expenses)} expenses")

        # Create business day records
        business_days = []
        for days_ago in range(14, 0, -1):
            day_date = today - timedelta(days=days_ago)
            if day_date.weekday() < 5:  # Weekdays only
                business_day = BusinessDay(
                    date=day_date,
                    opened_at=datetime.combine(day_date, datetime.min.time()) + timedelta(hours=8),
                    opened_by_id=admin.id,
                    closed_at=datetime.combine(day_date, datetime.min.time()) + timedelta(hours=17),
                    closed_by_id=office_staff.id,
                )
                db.session.add(business_day)
                business_days.append(business_day)

        db.session.commit()
        print(f">> Created {len(business_days)} business day records")

        print("\n>> Database seeding completed successfully!")
        print(f">> Summary:")
        print(f"   - 1 admin user")
        print(f"   - 1 office staff")
        print(f"   - {len(agents)} agents")
        print(f"   - {len(customers)} customers")
        print(f"   - {len(guarantors)} guarantors")
        print(f"   - {len(loans)} loans")
        print(f"   - {len(repayments)} repayments")
        print(f"   - {len(cash_transactions)} cash transactions")
        print(f"   - {len(expenses)} expenses")
        print(f"   - {len(business_days)} business day records")
        print("\n>> Login credentials:")
        print(f"   Admin: {username} / {password}")
        print(f"   Office: office / office123")
        print(f"   Agents: kwame, ama, kofi / agent123")


if __name__ == "__main__":
    main()
