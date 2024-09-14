# app/integrations/database/neo4j.py

import os
import json
from neo4j import GraphDatabase
from typeid import TypeID
from .base import DatabaseIntegration

class Neo4jIntegration(DatabaseIntegration):
    def __init__(self, schema_file_path="schema.json"):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        if not self.password:
            raise ValueError("NEO4J_PASSWORD environment variable is not set")
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.driver.verify_connectivity()
        self.schema = self._load_schema(schema_file_path)
        self._ensure_db_schema()

    def _load_schema(self, schema_file_path):
        with open(schema_file_path, "r") as file:
            return json.load(file)

    def _ensure_db_schema(self):
        with self.driver.session() as session:
            for node_type, details in self.schema.items():
                # Create constraints for each node type
                session.run(f"CREATE CONSTRAINT IF NOT EXISTS ON (n:{node_type}) ASSERT n.id IS UNIQUE")
                
                # Create indexes for searchable properties
                for property_name in details.get("edge_types", {}).keys():
                    session.run(f"CREATE INDEX IF NOT EXISTS FOR (n:{node_type}) ON (n.{property_name})")

    def add_entity(self, entity_type, data):
        type_id = TypeID(prefix=entity_type.lower())
        entity_id = str(type_id)
        actual_data = data["data"]
        actual_data["id"] = entity_id

        query = (
            f"CREATE (n:{entity_type} $props) "
            f"RETURN n.id AS id"
        )

        with self.driver.session() as session:
            result = session.run(query, props=actual_data)
            return result.single()["id"]

    def get_entity(self, entity_type, entity_id):
        query = (
            f"MATCH (n:{entity_type} {{id: $id}}) "
            f"RETURN n"
        )

        with self.driver.session() as session:
            result = session.run(query, id=entity_id)
            record = result.single()
            if record:
                return dict(record["n"])
            return None

    def update_entity(self, entity_type, entity_id, data):
        actual_data = data["data"]
        query = (
            f"MATCH (n:{entity_type} {{id: $id}}) "
            f"SET n += $props "
            f"RETURN n.id AS id"
        )

        with self.driver.session() as session:
            result = session.run(query, id=entity_id, props=actual_data)
            return result.single() is not None

    def delete_entity(self, entity_type, entity_id):
        query = (
            f"MATCH (n:{entity_type} {{id: $id}}) "
            f"DETACH DELETE n"
        )

        with self.driver.session() as session:
            result = session.run(query, id=entity_id)
            return result.consume().counters.nodes_deleted > 0

    def add_relationship(self, data):
        query = (
            "MATCH (a {id: $from_id}), (b {id: $to_id}) "
            "CREATE (a)-[r:RELATED {type: $relationship, snippet: $snippet}]->(b) "
            "RETURN id(r) AS relationship_id"
        )

        with self.driver.session() as session:
            result = session.run(query, 
                                 from_id=data["from_id"],
                                 to_id=data["to_id"],
                                 relationship=data["relationship"],
                                 snippet=data.get("snippet", ""))
            return result.single()["relationship_id"]

    def get_full_graph(self):
        nodes_query = "MATCH (n) RETURN n"
        relationships_query = "MATCH (a)-[r]->(b) RETURN a.id AS from_id, b.id AS to_id, type(r) AS relationship, r.snippet AS snippet"

        with self.driver.session() as session:
            nodes = session.run(nodes_query)
            relationships = session.run(relationships_query)

            entities = {}
            for record in nodes:
                node = record["n"]
                entity_type = list(node.labels)[0]  # Assuming one label per node
                if entity_type not in entities:
                    entities[entity_type] = {}
                entities[entity_type][node["id"]] = dict(node)

            relationships_list = [
                {
                    "from_id": rel["from_id"],
                    "to_id": rel["to_id"],
                    "relationship": rel["relationship"],
                    "snippet": rel["snippet"]
                }
                for rel in relationships
            ]

        return {
            "entities": entities,
            "relationships": relationships_list
        }

    def search_entities(self, search_params):
        conditions = " AND ".join([f"n.{key} CONTAINS $props.{key}" for key in search_params.keys()])
        query = f"MATCH (n) WHERE {conditions} RETURN n"

        with self.driver.session() as session:
            result = session.run(query, props=search_params)
            return [dict(record["n"]) for record in result]

    def search_relationships(self, search_params):
        conditions = " AND ".join([f"r.{key} CONTAINS $props.{key}" for key in search_params.keys()])
        query = f"MATCH (a)-[r]->(b) WHERE {conditions} RETURN a.id AS from_id, b.id AS to_id, type(r) AS relationship, r.snippet AS snippet"

        with self.driver.session() as session:
            result = session.run(query, props=search_params)
            return [dict(record) for record in result]

    def close(self):
        self.driver.close()

def register(integration_manager):
    integration_manager.register('neo4j', Neo4jIntegration())