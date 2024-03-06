class App:
    def __init__(self, service: object, **kwargs) -> None:
        self.original_data = kwargs
        self.service = service

        self.id = kwargs.get("id")
        self.description = kwargs.get("description")
        self.name = kwargs.get("name")
        self.published_by = kwargs.get("publishedBy")
        self.last_update = kwargs.get("lastUpdate")
              

    def __hash__(self) -> int:
        return hash((self.id))
    
    def __eq__(self, other) -> bool:
        if isinstance(other, App):
            return self.id == other.id
        return False
    
    def __str__(self) -> str:
        return f"{self.name} ({self.id})"