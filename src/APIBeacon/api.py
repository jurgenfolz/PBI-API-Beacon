import jwt
import requests
from azure.identity import InteractiveBrowserCredential
from requests.exceptions import HTTPError, RequestException, Timeout, TooManyRedirects
import time


from .logger import Logger
from .singleton import SingletonMeta
from .api_custom_exceptions import APIError, InternalServerError, JSONDecodeError, TokenExpiredError, TooManyRequestsError, UnauthorizedError, PowerBIEntityNotFoundError
 
class PbiAPI(metaclass=SingletonMeta):
    """
    #### Description:
        Singleton instance of PBI rest API interface.

    ###Attributes:
        proxy_url (str): proxy URL to pass as an argument to API calls.
        saved_token (str): if there's still a valid token available (1h duration) use this argument.
        _pbi_api (BasicPbiAPI): instance of BasicPbiAPI class
    """

    def __init__(self, proxy_url=None, saved_token=None) -> None:
        self.proxy_url = proxy_url
        self.saved_token = saved_token
        self._pbi_api = None

    @property
    def pbi_api(self):
        """Returns an instance of the class BasicPbiAPI with lazy loading.

        Returns:
            BasicPbiAPI: BasicPbiAPI instance.
        """
        if self._pbi_api is None:
            self._pbi_api = AbstractPbiAPI(self.proxy_url, self.saved_token)
        return self._pbi_api

class AbstractPbiAPI:
    """
    #### Description:
        Class for handling Power BI API operations.
    
    #### Attributes:
        BASE_URL (str): Base URL for Power BI API.
        logger (Logger): Logger object for logging.
        proxies (dict): Proxies for API requests.
        user (str): User email from the access token.
        saved_token (str): Saved token for authentication.
        access_token (str): Access token for API requests.
        header (dict): Header for API requests.
    
    #### Methods:
        __init__ (returns None): Initializes the BasicPbiAPI object.
        reauthenticate (returns str): Reauthenticates when the saved token expires.
        authenticate (returns None): Authenticates the user.
        __user_info (returns None): Gets the user email from the access token.
        make_api_get_request (returns dict or requests.models.Response): Makes a GET API request and handles potential errors.
        make_api_post_request (returns dict or requests.models.Response): Makes a POST API request and handles potential errors.
        make_api_delete_request (returns dict or requests.models.Response): Makes a DELETE API request and handles potential errors.
    """
    
    BASE_URL = "https://api.powerbi.com/v1.0/myorg/"

    def __init__(self, proxy_url=None, saved_token=None) -> None:
        """
        Args:
            proxy_url (str): proxy URL to pass as an argument to API calls.
            saved_token (str): if there's still a valid token available (1h duration) use this argument.
        """
        self.logger = Logger(__name__).get_logger()
        self.proxies = None
        self.user = None
        self.saved_token = saved_token
        if proxy_url:  # If proxy is set
            self.proxies = {
                "http": proxy_url
                ,"https": proxy_url
            }

        self.authenticate()

    def reauthenticate(self) -> str:
        """When the saved token expires, authenticates again.

        Returns:
            str: new access token.
        """
        self.saved_token = None
        self.authenticate()
        return self.access_token

    def authenticate(self):
        """If there's no saved token, opens the InteractiveBrowserCredential for the user to authenticate. In case, there's a saved token, just creates the header"""
        if not self.saved_token:
            api = "https://analysis.windows.net/powerbi/api/.default"
            auth = InteractiveBrowserCredential(authority="https://login.microsoftonline.com/")
            access_token = auth.get_token(api)
            self.access_token = access_token.token
        else:
            self.access_token = self.saved_token

        self.header = {"Authorization": f"Bearer {self.access_token}"}

        try:
            self.__user_info()
        except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError, jwt.exceptions.InvalidTokenError):
            self.logger.warning("Saved token has expired. Reauthenticating...")
            self.reauthenticate()
        except Exception:
            self.logger.exception("Unexpected error during user info retrieval. Reauthenticating...")
            self.reauthenticate()
        
        
    def __user_info(self):
        """Gets the user email from the access token."""

        def decode_token(access_token):
            decoded_token = jwt.decode(access_token, options={"verify_signature": False})
            return decoded_token

        decoded_token = decode_token(self.access_token)
        self.user = decoded_token["upn"]
    
    def _handle_response(self, response: requests.Response, url: str):
        
        if response.status_code in [200, 201, 202]:
            return response
        
        error_handlers = {
            401: (UnauthorizedError, "Unauthorized"),
            403: (TokenExpiredError, "Token expired"),
            404: (PowerBIEntityNotFoundError, "Cannot find entity or remove the user"),
            429: (TooManyRequestsError, "Too many requests"),
            500: (InternalServerError, "Internal server error")
        }

        error_class, message = error_handlers.get(response.status_code, (APIError, "API error"))
        self.logger.error(f"{message} {response.status_code} for {url}: {response.text}")
        raise error_class(f"{message} {response.status_code}: {response.text}")
        
    def _log_retry_attempt(self, url, attempt, max_retries, exception):
        self.logger.error(f"Request timed out for {url}. Retry {attempt + 1} of {max_retries}. Exception: {exception}")

    def make_api_get_request(self, url, headers=None, proxies=None, timeout_duration=10, max_retries=5):
        """Makes a GET API request and handles potential errors.

        Args:
            url (_type_): The API endpoint URL.
            headers (_type_, optional): the headers for the request. Defaults to None.
            proxies (_type_, optional): the proxies for the request. Defaults to None.
            timeout_duration (int, optional): The timeout duration for the request. Defaults to 10.
            max_retries (int, optional): The maximum number of retries for the request. Defaults to 3.
            json (bool, optional): If the response should be in JSON format. Defaults to True.

        Raises:
            APIError: When the API request fails.
            UnauthorizedError: When the API request fails with 401 status code.
            TokenExpiredError: When the API request fails with 403 status code.
            TooManyRequestsError: When the API request fails with 429 status code.
            InternalServerError: When the API request fails with 500 status code.

        Returns:
            dict or requests.models.Response: The response from the API. 
        """
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout_duration)
                self.logger.info(f"API GET: Response from {url}: {response.status_code}")
                return self._handle_response(response,url)

            except Timeout as e:
                self._log_retry_attempt(url, attempt, max_retries, e)
                time.sleep(2 ** attempt)  # Exponential backoff

            except (TooManyRedirects, HTTPError, RequestException) as e:
                self.logger.error(f"Request error for {url}: {str(e)}")
                raise APIError(f"Request error: {str(e)}") from e

            

        raise APIError("API request failed after maximum retries.")

    def make_api_post_request(self, url, headers=None, proxies=None, timeout_duration=10, max_retries=5, payload=None):
        """
        Makes an API request and handles potential errors.

        Parameters:
        - url (str): The API endpoint URL.
        - headers (dict, optional): Headers for the request.
        - proxies (dict, optional): Proxies for the request.
        - timeout_duration (int, optional): How long to wait before timing out the request. Default is 10 seconds.
        - max_retries (int, optional): Maximum number of retries for the request. Default is 3.

        Returns:
        - dict: Decoded JSON response from the API.

        Raises:
        - APIError: For any issues related to the API request.
        - JSONDecodeError: If the response is not in JSON format.
        - HTTPError: If the response status code is not 200.
        - TooManyRedirects: If there are too many redirects.
        - Timeout: If the request times out.
        - RequestException: For other types of requests exceptions.
        """
        
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, proxies=proxies, timeout=timeout_duration, json=payload)
                self.logger.info(f"API POST: Response from {url}: {response.status_code}")
                return self._handle_response(response,url)

            except (Timeout,TooManyRequestsError) as e:
                self.logger.error(f"Request timed out for {url}. Retry {attempt + 1} of {max_retries}. Exception: {e}")
                self._log_retry_attempt(url, attempt, max_retries, e)
                time.sleep(2 ** attempt)  # Exponential backoff

            except (TooManyRedirects, HTTPError, RequestException) as e:
                self.logger.error(f"Request error for {url}: {str(e)}")
                raise APIError(f"Request error: {str(e)}") from e

            
        raise APIError("API request failed after maximum retries.")
    
    def make_api_delete_request(self, url, headers=None, proxies=None, timeout_duration=10, max_retries=5):
        """
        Makes a DELETE API request and handles potential errors.

        Parameters:
        - url (str): The API endpoint URL.
        - headers (dict, optional): Headers for the request.
        - proxies (dict, optional): Proxies for the request.
        - timeout_duration (int, optional): How long to wait before timing out the request. Default is 10 seconds.
        - max_retries (int, optional): Maximum number of retries for the request. Default is 3.
        - json (dict, optional): JSON data to send in the request.

        Returns:
        - dict: Decoded JSON response from the API.

        Raises:
        - APIError: For any issues related to the API request.
        """
        for attempt in range(max_retries):
            try:
                response = requests.delete(url, headers=headers, proxies=proxies, timeout=timeout_duration)
                self.logger.info(f"API DELETE: Response from {url}: {response.status_code}")
                return self._handle_response(response, url)

            except Timeout as e:
                self._log_retry_attempt(url, attempt, max_retries, e)
                time.sleep(2 ** attempt)  # Exponential backoff

            except (TooManyRedirects, HTTPError, RequestException) as e:
                self.logger.error(f"Request error for {url}: {str(e)}")
                raise APIError(f"Request error: {str(e)}") from e


        raise APIError("API request failed after maximum retries.")
        
