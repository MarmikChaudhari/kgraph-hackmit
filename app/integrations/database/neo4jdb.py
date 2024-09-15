# app/integrations/database/neo4j.py
import os
from neo4j import GraphDatabase
from typeid import TypeID
from .base import DatabaseIntegration

class Neo4jIntegration(DatabaseIntegration):
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        if not self.password:
            raise ValueError("NEO4J_PASSWORD environment variable is not set")
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self.driver.verify_connectivity()

    def add_entity(self, data):
        type_id = TypeID(prefix="entity")
        entity_id = str(type_id)
        data["id"] = entity_id

        query = (
            "CREATE (n:Entity $props) "
            "RETURN n.id AS id"
        )

        with self.driver.session() as session:
            result = session.run(query, props=data)
            result.single()

    def get_entity(self, entity_id):
        query = (
            "MATCH (n:Entity {id: $id}) "
            "RETURN n"
        )

        with self.driver.session() as session:
            result = session.run(query, id=entity_id)
            record = result.single()
            if record:
                return dict(record["n"])

    def update_entity(self, entity_id, data):
        query = (
            "MATCH (n:Entity {id: $id}) "
            "SET n += $props "
            "RETURN n.id AS id"
        )

        with self.driver.session() as session:
            result = session.run(query, id=entity_id, props=data)
            return result.single() is not None

    def delete_entity(self, entity_id):
        query = (
            "MATCH (n:Entity {id: $id}) "
            "DETACH DELETE n"
        )

        with self.driver.session() as session:
            result = session.run(query, id=entity_id)
            return result.consume().counters.nodes_deleted > 0

    def add_relationship(self, data):
        query = (
            "MATCH (a:Entity {id: $from_id}), (b:Entity {id: $to_id}) "
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
        nodes_query = "MATCH (n:Entity) RETURN n"
        relationships_query = "MATCH (a:Entity)-[r]->(b:Entity) RETURN a.id AS from_id, b.id AS to_id, type(r) AS relationship, r.snippet AS snippet"

        with self.driver.session() as session:
            nodes = session.run(nodes_query)
            relationships = session.run(relationships_query)

            entities = {}
            for record in nodes:
                node = record["n"]
                entities[node["id"]] = dict(node)

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
        query = f"MATCH (n:Entity) WHERE {conditions} RETURN n"

        with self.driver.session() as session:
            result = session.run(query, props=search_params)
            return [dict(record["n"]) for record in result]

    def search_relationships(self, search_params):
        conditions = " AND ".join([f"r.{key} CONTAINS $props.{key}" for key in search_params.keys()])
        query = f"MATCH (a:Entity)-[r]->(b:Entity) WHERE {conditions} RETURN a.id AS from_id, b.id AS to_id, type(r) AS relationship, r.snippet AS snippet"

        with self.driver.session() as session:
            result = session.run(query, props=search_params)
            return [dict(record) for record in result]

    def close(self):
        self.driver.close()

def register(integration_manager):
    integration_manager.register('neo4j', Neo4jIntegration())