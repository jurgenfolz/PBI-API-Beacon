class User:

    def __init__(self, parent: object, **kwargs) -> None:
        
        self.original_data = kwargs
        self.parent = parent
        
        
        self.email = kwargs.get("emailAddress")
        self.access_right = kwargs.get("groupUserAccessRight")
        self.principal_type = kwargs.get("principalType")
        self.name = kwargs.get("displayName")
        
    def __hash__(self) -> int:
        """Returns an integer hash value which is unique for distinct objects, and the same for similar objects"""
        return hash((self.email))

    def __eq__(self, other) -> bool:
        """Used to compare two objects for equality"""
        if isinstance(other, User):
            return self.email == other.email
        return False

    def __str__(self) -> str:
        return f"{self.email}"
