"""
Neo4j client utility for graph database operations.
"""
from app.config import settings
from neo4j import GraphDatabase
from typing import List, Dict, Any


class Neo4jClient:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password)
        )
    
    def close(self):
        self.driver.close()
    
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Optional query parameters
            
        Returns:
            List of result records as dictionaries
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            records = []
            for record in result:
                records.append(dict(record))
            return records
    
    def verify_connectivity(self) -> bool:
        """Verify Neo4j connection."""
        try:
            self.driver.verify_connectivity()
            return True
        except Exception:
            return False


# Global instance
neo4j_client = Neo4jClient()

