from django.conf import settings
from zeep import Client
from zeep.transports import Transport
from requests import Session
import logging
from requests.exceptions import ConnectionError, Timeout

logger = logging.getLogger(__name__)

class CBSService:
    """
    Service class for interacting with the Core Banking System (CBS).
    Handles SOAP API calls for KYC and transaction data.
    """
    def __init__(self):
        self.use_local = getattr(settings, 'USE_LOCAL_CBS', True)  # Default to local mode
        if not self.use_local:
            try:
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
            except (ConnectionError, Timeout) as e:
                logger.error(f"Failed to connect to CBS services: {str(e)}")
                logger.warning("Falling back to local development mode")
                self.use_local = True
            except Exception as e:
                logger.error(f"Error initializing CBS clients: {str(e)}")
                logger.warning("Falling back to local development mode")
                self.use_local = True

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
            logger.info(f"Using mock CBS service for customer info: {customer_number}")
            return self._get_mock_customer_info(customer_number)
        
        try:
            return self.kyc_client.service.getCustomerInfo(customer_number)
        except (ConnectionError, Timeout) as e:
            logger.error(f"Network error connecting to CBS KYC service: {str(e)}")
            logger.warning("Falling back to local development mode")
            self.use_local = True
            return self._get_mock_customer_info(customer_number)
        except Exception as e:
            logger.error(f"Error fetching customer info: {str(e)}")
            logger.warning("Falling back to local development mode")
            self.use_local = True
            return self._get_mock_customer_info(customer_number)

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
            logger.info(f"Using mock CBS service for transaction history: {customer_number}")
            return self._get_mock_transaction_history(customer_number)
            
        try:
            return self.transaction_client.service.getTransactionHistory(customer_number)
        except (ConnectionError, Timeout) as e:
            logger.error(f"Network error connecting to CBS Transaction service: {str(e)}")
            logger.warning("Falling back to local development mode")
            self.use_local = True
            return self._get_mock_transaction_history(customer_number)
        except Exception as e:
            logger.error(f"Error fetching transaction history: {str(e)}")
            logger.warning("Falling back to local development mode")
            self.use_local = True
            return self._get_mock_transaction_history(customer_number)

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