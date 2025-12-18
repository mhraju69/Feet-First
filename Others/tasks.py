from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Finance

User = get_user_model()


@shared_task
def create_monthly_finance_records():
    
    now = timezone.now()
    current_year = now.year
    current_month = now.month

    partners = User.objects.filter(role='partner')
    created_count = 0

    for partner in partners:
        # 1️⃣ Skip if current month already exists
        if Finance.objects.filter(
            partner=partner,
            year=current_year,
            month=current_month
        ).exists():
            continue

        # 2️⃣ Get most recent finance record (previous month or older)
        prev_finance = (
            Finance.objects
            .filter(partner=partner)
            .order_by('-year', '-month')
            .first()
        )

        # 3️⃣ If no previous record → create initial finance
        if not prev_finance:
            Finance.objects.create(
                partner=partner,
                year=current_year,
                month=current_month,
                this_month_revenue=0,
                next_payout=0,
                balance=0,
                last_payout=0,
                reserved_amount=0,
            )
            created_count += 1
            continue

        # 4️⃣ Skip if previous month had no activity
        if prev_finance.this_month_revenue == 0 and prev_finance.next_payout == 0:
            continue

        # 5️⃣ Create new month with carry-over values
        Finance.objects.create(
            partner=partner,
            year=current_year,
            month=current_month,
            this_month_revenue=0,
            next_payout=prev_finance.this_month_revenue,
            balance=prev_finance.balance,
            last_payout=0,
            reserved_amount=prev_finance.reserved_amount,
        )

        created_count += 1

    return (
        f"Created {created_count} finance records "
        f"for {current_year}/{current_month:02d}"
    )
