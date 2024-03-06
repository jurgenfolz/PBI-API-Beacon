class Dashboard:
    def __init__(self,parent: object, **kwargs):
        self.parent = parent
        self.original_data = kwargs
        
        self.id = kwargs.get("id")
        self.name = kwargs.get("displayName")
        self.is_read_only = kwargs.get("isReadOnly")
        self.embed_url = kwargs.get("embedUrl")

   