from django.urls import path, include
from rest_framework.routers import DefaultRouter
from loan_management.views import LoanManagementViewSet, TransactionDataViewSet


router = DefaultRouter()

urlpatterns = [
    path('client/createClient/', LoanManagementViewSet.as_view({'post': 'create_client'})),
    path('subscribe/', LoanManagementViewSet.as_view({'post': 'create_subscription'})),
    path('loan/request/', LoanManagementViewSet.as_view({'post': 'request_loan'})),
    path('loan/status/<uuid:loan_id>/', LoanManagementViewSet.as_view({'get': 'get_loan_status'})),
    path('transactions/<str:customer_number>/', TransactionDataViewSet.as_view({'get': 'get_transactions'})),
    path('scoring/initiateQueryScore/<str:customer_number>/', 
         LoanManagementViewSet.as_view({'get': 'initiate_query_score'})),
    path('scoring/queryScore/<str:token>/', 
         LoanManagementViewSet.as_view({'get': 'query_score'})),
] 