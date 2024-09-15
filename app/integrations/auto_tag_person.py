# this is an example integration that automatically triggers based on an entity creation using the blinker signals by importing entity_created from app.signals.
from flask import request, current_app, jsonify
from app.signals import entity_created

def tag_entity(sender, **extra):
    # Logic for tagging entity goes here
    print('Tagged entity with id:', extra.get('entity_id'))

def auto_tag_entity(next):
    def wrapper(*args, **kwargs):
        # Call the original function and get the response directly
        response = next(*args, **kwargs)
        
        # Ensure that you only proceed if the response is a tuple and has a successful status code
        if isinstance(response, tuple) and response[1] in (200, 201):
            data, status_code = response
            
            # Now you can work with `data` as it is the dictionary that was meant to be JSON
            if request.endpoint == 'main.create_entity':
                entity_id = data.get('id')
                if entity_id:
                    # Emit the signal here, after the entity has been created
                    entity_created.send(current_app, entity_id=entity_id)
                    print('Tagged entity after creation.')
        
        # Return the original response
        return response
    return wrapper

def register(integration_manager):
    app = integration_manager.app  # Get the app instance from the manager
    entity_created.connect(tag_entity, sender=app)
    
    # Apply the middleware to the create_entity view function
    integration_manager.app.view_functions['main.create_entity'] = auto_tag_entity(
        integration_manager.app.view_functions['main.create_entity']
    )