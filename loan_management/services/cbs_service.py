from django.conf import settings
from zeep import Client
from zeep.transports import Transport
from requests import Session

class CBSService:
    """
    Service class for interacting with the Core Banking System (CBS).
    Handles SOAP API calls for KYC and transaction data.
    """
    def __init__(self):
        self.use_local = getattr(settings, 'USE_LOCAL_CBS', True)  # Default to local mode
        if not self.use_local:
            session = Session()
            session.verify = False
            transport = Transport(session=session)
            
            self.kyc_client = Client(
                settings.CBS_KYC_WSDL_URL,
                transport=transport
            )
            self.transaction_client = Client(
                settings.CBS_TRANSACTION_WSDL_URL,
                transport=transport
            )

    def get_customer_info(self, customer_number):
        """
        Fetches customer KYC information from CBS.
        Args:
            customer_number: The unique identifier for the customer
        Returns:
            Dict containing customer information
        Raises:
            Exception: If CBS call fails
        """
        if self.use_local:
            return self._get_mock_customer_info(customer_number)
        
        try:
            return self.kyc_client.service.getCustomerInfo(customer_number)
        except Exception as e:
            raise Exception(f"Error fetching customer info: {str(e)}")

    def get_transaction_history(self, customer_number):
        """
        Fetches customer transaction history from CBS.
        Args:
            customer_number: The unique identifier for the customer
        Returns:
            List of transaction records
        Raises:
            Exception: If CBS call fails
        """
        if self.use_local:
            return self._get_mock_transaction_history(customer_number)
            
        try:
            return self.transaction_client.service.getTransactionHistory(customer_number)
        except Exception as e:
            raise Exception(f"Error fetching transaction history: {str(e)}")

    def _get_mock_customer_info(self, customer_number):
        """Mock customer info for local development"""
        test_customers = {
            "234774784": {"first_name": "John", "last_name": "Regular"},
            "318411216": {"first_name": "Alice", "last_name": "HighValue"},
            "340397370": {"first_name": "Bob", "last_name": "New"},
            "366585630": {"first_name": "Charlie", "last_name": "Existing"},
            "397178638": {"first_name": "David", "last_name": "Rejected"}
        }
        
        if customer_number not in test_customers:
            raise Exception("Invalid customer number")
            
        return test_customers[customer_number]

    def _get_mock_transaction_history(self, customer_number):
        """Mock transaction history for local development"""
        return [{
            "accountNumber": f"ACC-{customer_number}",
            "monthlyBalance": 100000.00,
            "credittransactionsAmount": 50000.00,
            "monthlydebittransactionsAmount": 30000.00,
            "lastTransactionDate": "2024-03-21"
        }] 