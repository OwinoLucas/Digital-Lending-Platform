from rest_framework import serializers
from .models import LoanApplication

class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = ['id', 'customer', 'amount', 'status', 'created_at', 'updated_at']

class TransactionDataSerializer(serializers.Serializer):
    accountNumber = serializers.CharField()
    monthlyBalance = serializers.DecimalField(max_digits=20, decimal_places=2)
    credittransactionsAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    monthlydebittransactionsAmount = serializers.DecimalField(max_digits=20, decimal_places=2)
    lastTransactionDate = serializers.DateTimeField()
    # Add other fields as needed from the transaction data response 