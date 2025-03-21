from celery import shared_task
from .models import LoanApplication
from .services.scoring_service import ScoringService
from django.conf import settings

@shared_task
def check_loan_score(loan_id):
    """
    Background task to check the status of a loan application's score.
    Implements retry logic for score checking.
    
    Args:
        loan_id: UUID of the loan application to check
    
    The task will:
    1. Attempt to retrieve the score
    2. Update loan status if score is ready
    3. Schedule another attempt if score isn't ready and retries aren't exhausted
    4. Mark as failed if retries are exhausted
    """
    loan_application = LoanApplication.objects.get(id=loan_id)
    scoring_service = ScoringService()

    try:
        score_result = scoring_service.get_score(loan_application.scoring_token)
        
        if score_result['status'] == 'COMPLETED':
            # Score is ready - update loan status
            if score_result['approved']:
                loan_application.status = 'APPROVED'
            else:
                loan_application.status = 'REJECTED'
            loan_application.save()
            return True
        
        # Score not ready - handle retry logic
        if loan_application.retry_count < settings.MAX_SCORING_RETRIES:
            loan_application.retry_count += 1
            loan_application.save()
            # Schedule another check after the configured delay
            check_loan_score.apply_async(
                args=[loan_id],
                countdown=settings.SCORING_RETRY_DELAY
            )
        else:
            # Retries exhausted - mark as failed
            loan_application.status = 'FAILED'
            loan_application.save()
            
    except Exception as e:
        # Handle any errors by marking the application as failed
        loan_application.status = 'FAILED'
        loan_application.save() 