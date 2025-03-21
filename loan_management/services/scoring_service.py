import requests
from django.conf import settings
from ..models import ScoringEngineConfig
import uuid

class ScoringService:
    """
    Service class for interacting with the Scoring Engine.
    Handles registration, score initiation, and score retrieval.
    """
    def __init__(self):
        self.config = None
        self.base_url = settings.SCORING_ENGINE_BASE_URL
        self.use_local = settings.USE_LOCAL_SCORING
        try:
            self.config = ScoringEngineConfig.objects.latest()
        except ScoringEngineConfig.DoesNotExist:
            # It's ok if no config exists yet
            pass

    def register_endpoint(self, url, name, username, password):
        """
        Registers endpoint - handles both local and external scoring engine
        """
        if self.use_local:
            return self._register_local(url, name, username, password)
        else:
            return self._register_external(url, name, username, password)

    def _register_local(self, url, name, username, password):
        """Local development registration"""
        mock_response = {
            "id": 1,
            "url": url,
            "name": name,
            "username": username,
            "password": password,
            "token": str(uuid.uuid4())
        }
        
        self.config = ScoringEngineConfig.objects.create(
            client_id=mock_response['id'],
            url=mock_response['url'],
            name=mock_response['name'],
            username=mock_response['username'],
            password=mock_response['password'],
            token=mock_response['token']
        )
        
        return mock_response

    def _register_external(self, url, name, username, password):
        """External scoring engine registration"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/client/createClient",
                json={
                    "url": url,
                    "name": name,
                    "username": username,
                    "password": password
                },
                timeout=10  # Add timeout to prevent hanging
            )
            if response.status_code == 200:
                data = response.json()
                self.config = ScoringEngineConfig.objects.create(
                    client_id=data['id'],
                    url=data['url'],
                    name=data['name'],
                    username=data['username'],
                    password=data['password'],
                    token=data['token']
                )
                return data
            raise Exception(f"Failed to register endpoint: {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"External service error: {str(e)}")

    def initiate_scoring(self, customer_number):
        """
        Initiates the scoring process for a customer.
        
        Args:
            customer_number: The customer to be scored
        Returns:
            Dict containing the scoring token
        Raises:
            Exception: If scoring initiation fails
        """
        if self.use_local:
            return self._initiate_scoring_local(customer_number)
        else:
            return self._initiate_scoring_external(customer_number)

    def _initiate_scoring_local(self, customer_number):
        """Local scoring initiation"""
        return {"token": str(uuid.uuid4())}

    def _initiate_scoring_external(self, customer_number):
        """External scoring initiation"""
        if not self.config:
            raise Exception("No scoring configuration found")
        
        response = requests.get(
            f"{self.base_url}/api/v1/scoring/initiateQueryScore/{customer_number}",
            headers={"client-token": self.config.token},
            timeout=10
        )
        if response.status_code != 200:
            raise Exception("Failed to initiate scoring")
        return {"token": response.json()["token"]}

    def get_score(self, token):
        """
        Retrieves the score result using a token.
        
        Args:
            token: The token from initiate_scoring
        Returns:
            Dict containing score results
        Raises:
            Exception: If score retrieval fails
        """
        if self.use_local:
            return self._get_score_local(token)
        else:
            return self._get_score_external(token)

    def _get_score_local(self, token):
        """Local score retrieval"""
        return {
            "id": 9,
            "customerNumber": "234774784",
            "score": 564,
            "limitAmount": 30000,
            "exclusion": "No Exclusion",
            "exclusionReason": "No Exclusion"
        }

    def _get_score_external(self, token):
        """External score retrieval"""
        if not self.config:
            raise Exception("No scoring configuration found")
            
        response = requests.get(
            f"{self.base_url}/api/v1/scoring/queryScore/{token}",
            headers={"client-token": self.config.token},
            timeout=10
        )
        if response.status_code != 200:
            raise Exception("Failed to get score")
        return response.json() 