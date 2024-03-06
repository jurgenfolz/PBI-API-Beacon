class SemanticModel:
    
    def __init__(self, parent: object, **kwargs) -> None:

        self.original_data = kwargs
        self.parent = parent
        
        self.id = kwargs.get("id")  # semantic_model ID
        self.name = kwargs.get("name")  # semantic_model name
        self.configured_by = kwargs.get("configuredBy")  # Configured by
        self.is_refreshable = kwargs.get("isRefreshable")  # Is refreshable
        self.created_date = kwargs.get("createdDate")  # Created date
        self.storage_mode = kwargs.get("targetStorageMode") # Storage mode

    def __hash__(self) -> int:
        """Returns an integer hash value which is unique for distinct objects, and the same for similar objects"""
        return hash((self.id))

    def __eq__(self, other) -> bool:
        """Used to compare two objects for equality"""
        if isinstance(other, SemanticModel):
            return self.id == other.id
        return False

    def __str__(self) -> str:
        """Returns a string representation of the object"""
        return f"{self.name} ({self.id})"
