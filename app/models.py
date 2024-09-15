current_db_integration = None

def set_database_integration(db_integration_instance):
    global current_db_integration
    current_db_integration = db_integration_instance

def add_entity(data):
    if current_db_integration is None:
        raise ValueError("Database integration is not set.")
    return current_db_integration.add_entity(data)

def get_full_graph():
    if current_db_integration is None:
        raise ValueError("Database integration is not set.")
    return current_db_integration.get_full_graph()

def get_entity(entity_id):
    if current_db_integration is None:
        raise ValueError("Database integration is not set.")
    return current_db_integration.get_entity(entity_id)

def get_all_entities():
    if current_db_integration is None:
        raise ValueError("Database integration is not set.")
    return current_db_integration.get_all_entities()

def update_entity(entity_id, data):
    if current_db_integration is None:
        raise ValueError("Database integration is not set.")
    return current_db_integration.update_entity(entity_id, data)

def delete_entity(entity_id):
    if current_db_integration is None:
        raise ValueError("Database integration is not set.")
    return current_db_integration.delete_entity(entity_id)

def add_relationship(data):
    if current_db_integration is None:
        raise ValueError("Database integration is not set.")
    return current_db_integration.add_relationship(data)

def search_entities(search_params):
    if current_db_integration is None:
        raise ValueError("Database integration is not set.")
    return current_db_integration.search_entities(search_params)

def search_relationships(search_params):
    if current_db_integration is None:
        raise ValueError("Database integration is not set.")
    return current_db_integration.search_relationships(search_params)

def search_entities_with_type(entity_type, search_params):
    # Implementation here
    pass