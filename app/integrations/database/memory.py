# This code snippet defines a simple in-memory graph data structure to simulate a database for storing and managing entities
# such as people, organizations, events, and their relationships. It uses a Python dictionary to hold the graph data and
# a global variable for unique entity IDs. Functions provided include:
# - add_entity: Adds a new entity (e.g., person, organization, event) to the graph with a unique ID, incrementing the ID counter.
# - get_full_graph: Returns the entire graph data including all entities and relationships.
# - get_entity: Retrieves a specific entity by its type and ID.
# - get_all_entities: Returns all entities of a specific type.
# - update_entity: Updates an entity's data if it exists in the graph.
# - delete_entity: Removes an entity from the graph by its type and ID.
# - add_relationship: Adds a relationship between entities to the graph.
# - search_entities: Searches for entities based on a set of search parameters.
# - search_entities_with_type: Searches for entities of a specific type based on search parameters.
# - search_relationships: Searches for relationships that match given search parameters.
# This representation is basic and intended for demonstration or prototyping. For production use, a database and an ORM (Object-Relational Mapping) should be utilized for data persistence and management.

# This is a very basic representation. For a real application, use a database and ORM.

from .base import DatabaseIntegration
from typing import Dict, Any

next_id = 1

class InMemoryDatabase(DatabaseIntegration):

    def __init__(self):
        self.graph = {
            "entities": {},  # Stores all entities by ID
            "relationships": [],  # Stores relationships
        }

    def add_entity(self, entity_type: str, data: Dict[str, Any]) -> None:
        global next_id
        entity_id = next_id
        self.graph["entities"][entity_id] = {"type": entity_type, "data": data}
        next_id += 1
        print(f"Added {entity_type} with ID: {entity_id}, next ID: {next_id}")

    def get_full_graph(self) -> None:
        self.graph

    def get_entity(self, entity_id: int) -> None:
        self.graph["entities"].get(entity_id)

    def get_all_entities(self) -> None:
        self.graph["entities"]

    def update_entity(self, entity_id: int, data: Dict[str, Any]) -> None:
        if entity_id in self.graph["entities"]:
            self.graph["entities"][entity_id]["data"].update(data)

    def delete_entity(self, entity_id: int) -> None:
        if entity_id in self.graph["entities"]:
            del self.graph["entities"][entity_id]
            self.graph["relationships"] = [
                relationship for relationship in self.graph["relationships"]
                if relationship["from_id"] != entity_id and relationship["to_id"] != entity_id
            ]

    def add_relationship(self, data: Dict[str, Any]) -> None:
        self.graph["relationships"].append(data)

    def search_entities(self, search_params: Dict[str, Any]) -> None:
        results = []
        for entity_id, entity_details in self.graph["entities"].items():
            entity_data = entity_details["data"]
            if all(
                str(value).lower() in str(entity_data.get(key, "")).lower()
                for key, value in search_params.items()
            ):
                results.append({"id": entity_id, "type": entity_details["type"], **entity_data})


    def search_relationships(self, search_params: Dict[str, Any]) -> None:
        results = []
        for relationship in self.graph["relationships"]:
            if all(
                str(value).lower() in str(relationship.get(key, "")).lower()
                for key, value in search_params.items()
            ):
                results.append(relationship)
