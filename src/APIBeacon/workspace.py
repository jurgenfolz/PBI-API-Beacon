from .report import Report
from .user import User
from .semantic_model import SemanticModel
from .dashboard import Dashboard
from .api import PbiAPI
from .logger import Logger

class Workspace:
    
    def __init__(self, parent: object, **kwargs) -> None:
       
        self.original_data = kwargs
        self.parent = parent
        self.api = PbiAPI(proxy_url=None).pbi_api
        self.logger = Logger(__name__).get_logger()  # Logger object
        
        self.id = kwargs.get("id")  # Workspace ID
        self.name = kwargs.get("name")  # Workspace name
        self.is_read_only = kwargs.get("isReadOnly")  # Workspace is read only
        self.is_on_dedicated_capacity = kwargs.get("isOnDedicatedCapacity")  # Workspace is on a premium workspace? if yes this value will not be None
        self.capacity_id = kwargs.get("capacityId")  # Capacity ID
        
        #object sets
        self.reports = set()
        self.semantic_models = set()
        self.dataflows = set()
        self.dashboards = set()
        self.data_sources = set()
        self.users = set()

    def __hash__(self) -> int:
        """Returns an integer hash value which is unique for distinct objects, and the same for similar objects"""
        return hash((self.id))

    def __eq__(self, other) -> bool:
        """Used to compare two objects for equality"""
        if isinstance(other, Workspace):
            return self.id == other.id
        return False

    def __str__(self) -> str:
        """Returns a string representation of the object"""
        return f"{self.name} ({self.id})"
    
    def get_reports(self) -> None:
        """Get all the reports and paginated reports from the workspace

        Raises:
            TypeError: Case the API response is not a dictionary.
        """
        url = self.api.BASE_URL + f"groups/{self.id}/reports"
        response = self.api.make_api_get_request(url=url, headers=self.api.header, proxies=self.api.proxies)
        data = response.json()
        if isinstance(data, dict):
            self.reports = {Report(self,**report) for report in data.get("value")}
               
        else:
            self.logger = Logger(__name__).get_logger()  # Logger object
            raise TypeError(f"Failed to get reports from workspace {self.name}.")
        
    def get_semantic_models(self) -> None:
        """Get all the semantic models from the workspace

        Raises:
            TypeError: Case the API response is not a dictionary.
        """
        url = self.api.BASE_URL + f"groups/{self.id}/datasets"
        response = self.api.make_api_get_request(url=url, headers=self.api.header, proxies=self.api.proxies)
        data = response.json()
        if isinstance(data, dict):
            self.semantic_models = {SemanticModel(self,**model) for model in data.get("value")}
        else:
            self.logger.error(f"Failed to get semantic models from workspace {self.name}.")
            raise TypeError("The response must be a dictionary.")
    
    def get_users(self, top: int = None, skip: int = None):
        """Get users in the workspace

        Args:
            top (int, optional): Number of users to return. Defaults to None.
            skip (int, optional): Number of users to skip. Defaults to None.

        Raises:
            TypeError: Case the API response is not a dictionary.
        """
        uri_top = f"$top={top}" if top else ""
        uri_skip = f"$skip={skip}" if skip else ""
        
        uri_params = "&".join([param for param in [uri_top, uri_skip] if param])
        
        url = self.api.BASE_URL + f"groups/{self.id}/users?" + uri_params
        response = self.api.make_api_get_request(url=url, headers=self.api.header, proxies=self.api.proxies)
        data = response.json()
        if isinstance(data, dict):
            self.users = {User(self,**user) for user in data.get("value")}
        else:
            self.logger.error(f"Error getting users: {response}")
            raise TypeError("The response must be a dictionary.")
        
    def get_dashboards(self):
        url = self.api.BASE_URL + f"groups/{self.id}/dashboards"
        response = self.api.make_api_get_request(url=url, headers=self.api.header, proxies=self.api.proxies)
        data = response.json()
        if isinstance(data, dict):
            self.dashboards = {Dashboard(self,**dashboard) for dashboard in data.get("value")}
        else:
            self.logger.error(f"Error getting dashboards: {response}")
            raise TypeError("The response must be a dictionary.")