# This Flask application integration, `add_multiple_conditional`, dynamically adds multiple entities and relationships
# to a knowledge graph, leveraging other integrations `conditional_entity_addition` and `conditional_relationship_addition`.

# It starts by attempting to load these integrations using `get_integration_function`, to conditionally add entities
# and their relationships. The data processed includes entities (`nodes`) and relationships, with entities addressed first.

# Entities are added through `conditional_entity_add_function`, with a payload prepared for each entity containing its type
# and data. The response updates a mapping of temporary IDs to actual system-assigned IDs, essential for linking entities
# in relationships accurately.

# Post entities addition, it iterates over the `relationships` data, using the entity ID mapping to construct a payload
# for each relationship. This payload is then passed to `conditional_relationship_add_function`, which decides on the
# relationship's addition based on internal logic.

# The function prints outcomes (e.g., entity added, relationship exists) and handles errors gracefully, returning a JSON
# response with the operation's status and details on created or matched entities and relationships.

# A `register` function ensures `add_multiple_conditional` is available within the application's integration manager,
# enabling its invocation as part of the application's integrations ecosystem.

# This approach demonstrates complex data processing and dynamic integration invocation within a Flask application for
# enhanced knowledge graph management.

# app/integrations/add_multiple_nodes_and_relationships.py
from flask import jsonify
from app.integrations.integration_manager import get_integration_function

def add_multiple_conditional(app, data):
    with app.app_context():
        try:
            print(f"\n\nData received: {data}\n\n")
            print("ADD MULTIPLE NODES AND RELATIONSHIP INTEGRATION STARTED")
            created_entities = {}
            entity_names = {}

            # Retrieve the callable functions for the conditional additions
            conditional_entity_add_function = get_integration_function("conditional_entity_addition")
            conditional_relationship_add_function = get_integration_function("conditional_relationship_addition")

            if not conditional_entity_add_function or not conditional_relationship_add_function:
                raise ValueError("Integration function(s) not found")

            # Handle entity additions
            nodes = data.get("nodes", [])
            for entity in nodes:
                temp_id = entity["id"]
                name = entity["name"]
                entity_names[temp_id] = name
                print(f"\nProcessing entity {temp_id} with name {name}\n")

                # Prepare the payload as expected by the conditional_entity_addition
                payload = {"data": entity}
                # Use conditional_entity_addition to add the entity
                response, status_code = conditional_entity_add_function(app, payload)

                if status_code != 200:
                    print(f"Error while adding entity: Status code {status_code}")
                    continue

                response_data = response.get_json()
                print(f"Response data: {response_data}")

                if response_data.get("success") is False:
                    print(f"Match found, using existing entity with data: {response_data.get('match_data')}")
                    entity_id = response_data.get("match_id")
                else:
                    print(f"New entity added with data: {response_data.get('created_data')}")
                    entity_id = response_data.get("entity_id")

                if entity_id:
                    created_entities[temp_id] = entity_id
                else:
                    print(f"Warning: No entity ID returned for {name}")

            print(f"\n\nEntity Names: {entity_names}\n\n")
            print(f"Created Entities: {created_entities}\n\n")

            # Handle relationship additions
            relationships = data.get("relationships", [])
            for relationship in relationships:
                from_id = created_entities.get(relationship["from_id"])
                to_id = created_entities.get(relationship["to_id"])
                
                if from_id is None or to_id is None:
                    print(f"Error: Missing entity for relationship: {relationship}")
                    continue

                relationship_data = {
                    "from_id": from_id,
                    "to_id": to_id,
                    "relationship": relationship.get("relationship", "associated"),
                    "snippet": relationship.get("snippet", "")
                }

                # Use conditional_relationship_addition to add the relationship
                response, status_code = conditional_relationship_add_function(app, relationship_data)

                if status_code != 200:
                    print(f"Error while adding relationship: Status code {status_code}")
                    continue

                response_data = response.get_json()

                if response_data.get("success") is False:
                    print(f"Match found, relationship already exists with data: {response_data.get('match_data')}")
                else:
                    print(f"New relationship added with data: {relationship_data}")

            return jsonify({
                "success": True,
                "created_entities": created_entities
            }), 200
        except Exception as e:
            print(f"Failed to add multiple nodes and relationships: {e}")
            return jsonify({"error": str(e)}), 500

def register(integration_manager):
    integration_manager.register("add_multiple_conditional", add_multiple_conditional)