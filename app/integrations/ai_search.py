import os
import openai
from flask import jsonify
import json
from app.models import get_full_graph, search_entities, search_relationships
import re as regex

openai.api_key = os.getenv('OPENAI_API_KEY')

def collect_connections(entities, relationships):
    graph = get_full_graph()
    triplets = []

    # Process the relationships to construct triplets
    for relationship in relationships:
        from_id = relationship['from_id']
        to_id = relationship['to_id']
        relationship_desc = relationship.get('snippet', f'Unknown relationship from {from_id} to {to_id}')
        triplets.append(relationship_desc)

    # Find additional connections for each entity
    for entity in entities:
        additional_triplets = find_connected_triplets(entity['id'], graph)
        triplets.extend(additional_triplets)

    return triplets

def find_connected_triplets(entity_id, graph):
    connected_triplets = []
    for relationship in graph['relationships']:
        if relationship['from_id'] == entity_id or relationship['to_id'] == entity_id:
            from_node = next((node for node in graph['entities'] if node['id'] == relationship['from_id']), None)
            to_node = next((node for node in graph['entities'] if node['id'] == relationship['to_id']), None)
            from_name = from_node['name'] if from_node else 'Unknown'
            to_name = to_node['name'] if to_node else 'Unknown'
            relationship_type = relationship.get('relationship', 'connected to')
            triplet = relationship.get('snippet', f"{from_name} {relationship_type} {to_name}")
            connected_triplets.append(triplet)
    
    return connected_triplets


def generate_search_parameters(input_text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": """You are a helpful assistant expected to generate search parameters in an array format for entities and relationships based on the given user input. Output should be in array format that looks like this with "name" as the key for every parameter. User: Did Johnny Appleseed plant apple seeds? Assistant:[{"name":"John"},{"name":"Appleseed"},{"name":"Apple"},{"name":"Seed"}]."""},
                {"role": "user", "content": f"User input:{input_text}"}
            ],
        )
        search_parameters = response.choices[0].message.content
        print("search_para: ", search_parameters)
        
        if search_parameters:
            # Ensure we're parsing a list of dictionaries
            parsed_parameters = json.loads(search_parameters)
            if isinstance(parsed_parameters, list) and all(isinstance(item, dict) for item in parsed_parameters):
                return parsed_parameters
            else:
                print("Invalid format: Expected a list of dictionaries")
                return []
        else:
            print("No content in API response")
            return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []
    except Exception as e:
        print(f"Error generating search parameters: {e}")
        return []
  

def ai_search(app, input_text):
    print("ai_search start")
    with app.app_context():
        search_parameters = generate_search_parameters(input_text)
        print("search_parameters", search_parameters)
        if not search_parameters:
            return jsonify({"error": "Failed to generate search parameters"}), 400

        entity_results = []
        relationship_results = []

        for param in search_parameters:
            for key, value in param.items():
                param_dict = {key: value}
                print(f"param_dict: {param_dict}")
                entity_results.extend(search_entities(param_dict))
                relationship_results.extend(search_relationships(param_dict))

        print("entity_results: ", entity_results)
        print("relationship_results: ", relationship_results)
        triplets = collect_connections(entity_results, relationship_results)
        print("triplet: ", triplets)

        if triplets:
            message = f"Based on the user input '{input_text}', here are the relationships found: {', '.join(triplets)}. Generate an insightful response."
        else:
            message = f"Based on the user input '{input_text}', no specific relationships were found. Generate a general insight."

        print("message: ", message)

        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You're an assistant that generates a concise answer to the user input based on the data provided following the user input."},
                    {"role": "user", "content": message}
                ]
            )
            answer = response.choices[0].message.content
            print("answer: ", answer)
            return jsonify({"answer": answer, "triplets": str(triplets)}), 200
        except Exception as e:
            print(f"Error processing AI search: {e}")
            return jsonify({"error": str(e)}), 500

def register(integration_manager):
    integration_manager.register('ai_search', ai_search)