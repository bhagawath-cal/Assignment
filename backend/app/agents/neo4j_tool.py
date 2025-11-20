"""
Neo4j query tool for LangGraph agent.
"""
from langchain_core.tools import tool
from app.neo4j_client import neo4j_client
from typing import Optional


@tool
def execute_neo4j_query(query: str) -> str:
    """
    Execute a Cypher query against the Neo4j graph database.
    
    Use this tool to query the movie database graph. The graph contains:
    - Movie nodes with properties: title, release_year, rating, description, duration_minutes, budget, revenue, language, country, enrichment_score, popularity_tier
    - Actor nodes with properties: name (only)
    - Director nodes with properties: name (only)
    - Genre nodes with properties: name (only)
    - Relationships: ACTED_IN (Actor->Movie), DIRECTED (Director->Movie), HAS_GENRE (Movie->Genre)
    
    Examples of useful queries:
    - Find movies with high enrichment scores: 
      MATCH (m:Movie) WHERE m.enrichment_score >= 70 RETURN m.title, m.enrichment_score, m.popularity_tier ORDER BY m.enrichment_score DESC
    
    - Find movies with low enrichment scores:
      MATCH (m:Movie) WHERE m.enrichment_score < 50 RETURN m.title, m.enrichment_score, m.popularity_tier ORDER BY m.enrichment_score ASC
    
    - Find actors who worked with a specific director:
      MATCH (d:Director)-[:DIRECTED]->(m:Movie)<-[:ACTED_IN]-(a:Actor) WHERE d.name = 'Christopher Nolan' RETURN DISTINCT a.name
    
    - Find movies connected to a specific actor:
      MATCH (a:Actor)-[:ACTED_IN]->(m:Movie) WHERE a.name = 'Leonardo DiCaprio' RETURN m.title, m.release_year, m.rating
    
    - Find related movies (same genre or shared actors):
      MATCH (m1:Movie)-[:HAS_GENRE]->(g:Genre)<-[:HAS_GENRE]-(m2:Movie) WHERE m1.title = 'Inception' AND m1 <> m2 RETURN m2.title, g.name
    
    Args:
        query: A valid Cypher query string
        description: Optional description (not used, for tool signature compatibility)
    
    Returns:
        JSON string representation of query results, or error message
    """
    try:
        results = neo4j_client.execute_query(query)
        
        if not results:
            return "Query executed successfully but returned no results."
        
        # Format results for readability
        formatted_results = []
        for record in results:
            formatted_record = {}
            for key, value in record.items():
                # Handle node objects
                if hasattr(value, 'get'):
                    if hasattr(value, 'labels'):
                        # It's a node
                        formatted_record[key] = {
                            'type': 'node',
                            'labels': list(value.labels),
                            'properties': dict(value)
                        }
                    elif hasattr(value, 'type'):
                        # It's a relationship
                        formatted_record[key] = {
                            'type': 'relationship',
                            'type_name': value.type,
                            'properties': dict(value)
                        }
                    else:
                        formatted_record[key] = value
                else:
                    formatted_record[key] = value
            formatted_results.append(formatted_record)
        
        import json
        return json.dumps(formatted_results, indent=2, default=str)
    
    except Exception as e:
        return f"Error executing query: {str(e)}"

