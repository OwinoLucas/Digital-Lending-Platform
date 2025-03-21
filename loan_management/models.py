from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

class Customer(models.Model):
    """
    Customer model to store basic customer information.
    Links to the bank's Core Banking System (CBS) via customer_number.
    """
    customer_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_number} - {self.first_name} {self.last_name}"

class LoanApplication(models.Model):
    """
    Stores loan applications and their current status.
    Tracks the scoring process through scoring_token and retry_count.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),      # Initial state
        ('PROCESSING', 'Processing'), # Waiting for scoring
        ('APPROVED', 'Approved'),     # Loan approved
        ('REJECTED', 'Rejected'),     # Loan rejected based on score
        ('FAILED', 'Failed'),        # Technical failure in scoring
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[
            MinValueValidator(1.00),  # Minimum loan amount
            MaxValueValidator(1000000.00)  # Maximum loan amount
        ]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    scoring_token = models.CharField(max_length=255, null=True, blank=True)
    retry_count = models.IntegerField(default=0)  # Tracks scoring retry attempts
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan Application {self.id} - {self.customer.customer_number}"

class ScoringEngineConfig(models.Model):
    """
    Stores configuration for the Scoring Engine integration.
    Maintains credentials and tokens needed for API communication.
    Only the latest configuration is used (get_latest_by).
    """
    client_id = models.IntegerField()
    url = models.URLField()
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        get_latest_by = 'created_at' 