from .workspace import Workspace
from .logger import Logger
from .api import PbiAPI
from .app import App

class Service:
    
    def __init__(self, proxy_url: str = None, saved_token: str = None):
    
        self.api = PbiAPI(proxy_url, saved_token).pbi_api  # API object
        self.logger = Logger(__name__).get_logger()  # Logger object
        
        self.workspaces = set()
        self.apps = set()
        
    def get_workspaces(self, filter: str = None, top: int = None, skip: int = None):
        """ Get workspaces that the user has access to."""
        
        uri_filter = f"$filter={filter}" if filter else ""
        uri_top = f"$top={top}" if top else ""
        uri_skip = f"$skip={skip}" if skip else ""
        
        uri_params = "&".join([param for param in [uri_filter, uri_top, uri_skip] if param])
        
        url = self.api.BASE_URL + "groups?" + uri_params
        response = self.api.make_api_get_request(url=url, headers=self.api.header, proxies=self.api.proxies)
        data = response.json()
        if isinstance(data, dict):
            self.workspaces = {Workspace(self,**workspace) for workspace in data.get("value")}
        else:
            self.logger.error(f"Error getting workspaces: {response}")
            raise TypeError("The response must be a dictionary.")
    
    def get_workspace(self, workspace_id: str):
        """ Get a workspace by its ID."""
        
        url = self.api.BASE_URL + f"groups/{workspace_id}"
        response = self.api.make_api_get_request(url=url, headers=self.api.header, proxies=self.api.proxies)
        data = response.json()
        if isinstance(data, dict):
            return Workspace(self,**data)
        else:
            self.logger.error(f"Error getting workspace: {response}")
            raise TypeError("The response must be a dictionary.")
    
    def get_apps(self):
        """ Get apps in the specified workspace."""
        
        url = self.api.BASE_URL + f"apps"
        response = self.api.make_api_get_request(url=url, headers=self.api.header, proxies=self.api.proxies)
        data = response.json()
        if isinstance(data, dict):
            self.apps = {App(self,**app) for app in data.get("value")}
        else:
            self.logger.error(f"Error getting apps: {response}")
            raise TypeError("The response must be a dictionary.")