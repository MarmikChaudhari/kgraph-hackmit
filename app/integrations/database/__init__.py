import os

from .memory import InMemoryDatabase
from .neo4jdb import Neo4jIntegration

db_type = os.getenv("DATABASE_TYPE", "memory").lower()

if db_type == 'neo4j':
  CurrentDBIntegration = Neo4jIntegration
else:
  CurrentDBIntegration = InMemoryDatabase
