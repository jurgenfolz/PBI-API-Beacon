from .api import PbiAPI

class Report:
    
    def __init__(self,parent: object, **kwargs) -> None:
        
        self.original_data = kwargs
        self.parent = parent  # Workspace object where the report is located
        self.api = PbiAPI(proxy_url=None).pbi_api
        
        self.app_id = kwargs.get("appId")
        self.dataset_id = kwargs.get("datasetId")
        self.description = kwargs.get("description")
        self.embed_url = kwargs.get("embedUrl")
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.original_report_id = kwargs.get("originalReportId")
        self.type = kwargs.get("reportType")  # Report type
        self.web_url = kwargs.get("webUrl")
        self.modified_by = kwargs.get("modifiedBy")
        self.created_by = kwargs.get("createdBy")
    
    def __hash__(self) -> int:
        """Returns an integer hash value which is unique for distinct objects, and the same for similar objects"""
        return hash((self.dataset_id, self.id))

    def __eq__(self, other) -> bool:
        """Used to compare two objects for equality"""
        if isinstance(other, Report):
            return self.dataset_id == other.dataset_id and self.id == other.id
        return False

    def __str__(self) -> str:
        """Returns a string representation of the object"""
        return f"{self.name} ({self.id})"