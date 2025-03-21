from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LoanApplication, Customer
from .services.cbs_service import CBSService
from .services.scoring_service import ScoringService
from .serializers import LoanApplicationSerializer, TransactionDataSerializer
from django.shortcuts import get_object_or_404
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class LoanManagementViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        operation_summary="Register Client",
        operation_description="""
        Register this service with the scoring engine.
        This is a one-time setup step.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'url': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Your service endpoint URL",
                    example="http://127.0.0.1:8000/api/v1/transactions"
                ),
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Your service name",
                    example="Digital Lending Platform"
                ),
                'username': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Basic auth username",
                    example="admin"
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Basic auth password",
                    example="pwd123"
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="Client registration successful",
                examples={
                    "application/json": {
                        "id": 1,
                        "url": "http://127.0.0.1:8000/api/v1/transactions",
                        "name": "Digital Lending Platform",
                        "token": "uuid-token-string"
                    }
                }
            ),
            400: "Missing required fields",
            500: "Registration failed"
        }
    )
    def create_client(self, request):
        """
        Register this service with the scoring engine.
        """
        try:
            url = request.data.get('url')
            name = request.data.get('name')
            username = request.data.get('username')
            password = request.data.get('password')

            if not all([url, name, username, password]):
                return Response(
                    {"error": "Missing required fields"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            scoring_service = ScoringService()
            result = scoring_service.register_endpoint(
                url=url,
                name=name,
                username=username,
                password=password
            )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_summary="Subscribe Customer",
        operation_description="""
        Subscribe a customer to the lending service.
        Verifies customer existence in CBS.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'customer_number': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Customer's unique identifier",
                    example="234774784"
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="Subscription successful",
                examples={
                    "application/json": {
                        "message": "Subscription successful",
                        "customer_id": "uuid-string"
                    }
                }
            ),
            400: "Invalid customer number"
        }
    )
    def create_subscription(self, request):
        customer_number = request.data.get('customer_number')
        if not customer_number:
            return Response(
                {"error": "Customer number is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if customer exists in CBS
        cbs_service = CBSService()
        customer_info = cbs_service.get_customer_info(customer_number)
        
        # Create or update customer
        customer, created = Customer.objects.update_or_create(
            customer_number=customer_number,
            defaults={
                'first_name': customer_info['first_name'],
                'last_name': customer_info['last_name']
            }
        )

        return Response({
            "message": "Subscription successful",
            "customer_id": customer.id
        })

    @swagger_auto_schema(
        operation_summary="Request Loan",
        operation_description="""
        Submit a loan application.
        Checks for existing loans and initiates scoring process.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'customer_number': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Customer's unique identifier",
                    example="234774784"
                ),
                'amount': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Loan amount requested",
                    example=5000
                ),
            }
        ),
        responses={
            200: openapi.Response(
                description="Loan application submitted",
                examples={
                    "application/json": {
                        "message": "Loan application submitted successfully",
                        "loan_id": "uuid-string"
                    }
                }
            ),
            400: "Invalid input or existing loan",
            404: "Customer not found"
        }
    )
    def request_loan(self, request):
        customer_number = request.data.get('customer_number')
        amount = request.data.get('amount')

        if not customer_number or not amount:
            return Response(
                {"error": "Customer number and amount are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for existing active loan
        existing_loan = LoanApplication.objects.filter(
            customer__customer_number=customer_number,
            status__in=['PENDING', 'PROCESSING']
        ).first()

        if existing_loan:
            return Response(
                {"error": "Customer has an ongoing loan application"},
                status=status.HTTP_400_BAD_REQUEST
            )

        customer = get_object_or_404(Customer, customer_number=customer_number)
        
        # Create loan application
        loan_application = LoanApplication.objects.create(
            customer=customer,
            amount=amount,
            status='PROCESSING'
        )

        # Initiate scoring
        scoring_service = ScoringService()
        scoring_response = scoring_service.initiate_scoring(customer_number)
        
        loan_application.scoring_token = scoring_response['token']
        loan_application.save()

        return Response({
            "message": "Loan application submitted successfully",
            "loan_id": loan_application.id
        })

    @swagger_auto_schema(
        operation_summary="Check Loan Status",
        operation_description="Get the current status of a loan application",
        manual_parameters=[
            openapi.Parameter(
                'loan_id',
                openapi.IN_PATH,
                description="Loan application UUID",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Loan status retrieved",
                examples={
                    "application/json": {
                        "id": "uuid-string",
                        "customer": "customer-id",
                        "amount": 5000,
                        "status": "PROCESSING",
                        "created_at": "2024-03-21T10:00:00Z",
                        "updated_at": "2024-03-21T10:01:00Z"
                    }
                }
            ),
            404: "Loan application not found"
        }
    )
    def get_loan_status(self, request, loan_id):
        loan_application = get_object_or_404(LoanApplication, id=loan_id)
        serializer = LoanApplicationSerializer(loan_application)
        return Response(serializer.data)

    def initiate_query_score(self, request, customer_number):
        """
        Step 1: Initiate scoring process for a customer
        """
        try:
            scoring_service = ScoringService()
            result = scoring_service.initiate_scoring(customer_number)
            return Response({"token": result['token']})
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def query_score(self, request, token):
        """
        Step 2: Get scoring results using token
        """
        try:
            scoring_service = ScoringService()
            result = scoring_service.get_score(token)
            return Response(result)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TransactionDataViewSet(viewsets.ViewSet):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get Transaction Data",
        operation_description="""
        Retrieve customer transaction history.
        Requires Basic Authentication.
        """,
        manual_parameters=[
            openapi.Parameter(
                'customer_number',
                openapi.IN_PATH,
                description="Customer's unique identifier",
                type=openapi.TYPE_STRING,
                example="234774784",
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Transaction data retrieved",
                examples={
                    "application/json": [{
                        "accountNumber": "332216783322167234774784",
                        "monthlyBalance": 659722841.00,
                        "credittransactionsAmount": 609.29,
                        "monthlydebittransactionsAmount": 103262.90,
                        "lastTransactionDate": "2024-03-21T10:00:00Z"
                    }]
                }
            ),
            400: "Invalid customer number",
            401: "Authentication failed"
        },
        security=[{'Basic': []}]
    )
    def get_transactions(self, request, customer_number):
        # Add print statements for debugging
        print(f"Request user: {request.user}")
        print(f"Auth header: {request.headers.get('Authorization')}")

        if customer_number not in ['234774784', '318411216', '340397370', '366585630', '397178638']:
            return Response(
                {"error": "Invalid customer number"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        cbs_service = CBSService()
        transactions = cbs_service.get_transaction_history(customer_number)
        serializer = TransactionDataSerializer(transactions, many=True)
        return Response(serializer.data) 