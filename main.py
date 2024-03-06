from src.APIBeacon import Service


service = Service()
service.get_workspaces()

for workspace in service.workspaces:
    if workspace.id == "296b51c5-fe7c-4dee-8cd5-584adc6c5f3a":
        print(workspace)
        workspace.get_reports()
        for report in workspace.reports:
            print(report)
        workspace.get_semantic_models()
        for model in workspace.semantic_models:
            print(model)
        workspace.get_users()
        for user in workspace.users:
            print(user)
    
