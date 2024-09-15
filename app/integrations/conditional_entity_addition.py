# This Flask integration, `conditional_entity_addition`, uses OpenAI to conditionally add entities to a knowledge graph, 
# ensuring no duplicates are created based on the entity's data content. It interfaces with the application's model layer 
# to search existing entities and decide on new additions.

# First, the function checks for an 'entity_type' in the provided data, returning an error if it's missing. It then extracts 
# 'entity_data' from the data payload for search purposes.

# It conducts a search within the knowledge graph for each piece of entity data provided, aiming to find any potential 
# matches. This search is sensitive to string values, looking for partial matches.

# The search results are consolidated, ensuring unique entries are considered for comparison against the new entity data.

# The function prepares a message for the OpenAI API, articulating a task to determine if the new entity data matches any 
# of the search results, considering variations in name matching and additional entity details for a robust comparison.

# An OpenAI ChatCompletion call is made with the constructed message, with the AI tasked to return an entity ID if a match 
# is found or indicate 'No Matches' otherwise.

# Based on the AI's response, the function either adds the new entity to the knowledge graph (if no matches are found) and 
# returns a success response including the new entity's ID, or it returns a response indicating a match was found with the 
# matched entity's ID.

# Error handling is included to catch and report issues during the OpenAI API call process.

# Finally, a `register` function is provided to make `conditional_entity_addition` available within the application's 
# integration manager, allowing it to be dynamically loaded and invoked as part of the application's integration ecosystem.

# This integration highlights a sophisticated use of AI for data deduplication within web applications, ensuring data integrity 
# and reducing redundancy in knowledge graph construction and expansion.


# app/integrations/conditional_entity_addition.py
import os
import openai
from flask import jsonify
from app.models import search_entities, add_entity

openai.api_key = os.environ['OPENAI_API_KEY']
OPENAI_MODEL_NAME = "gpt-4-turbo"

def conditional_entity_addition(app, data):
    with app.app_context():
        if not isinstance(data, dict) or 'name' not in data:
            return jsonify({"error": "Invalid entity data. 'name' is required."}), 400

        search_results = []

        # Run a search for the entity name
        search_params = {'name': data['name']}
        print(f"Search parameters: {search_params}")
        results = search_entities(search_params)
        print(f"Search results: {results}")
        search_results.extend(results)

        try:
            response = openai.chat.completions.create(
                model=os.environ.get('OPENAI_MODEL_NAME', OPENAI_MODEL_NAME),
                messages=[
            {"role": "system", "content": "You are a helpful assistant specializing in determining if new input data matches existing data in our database. Review the search results provided and compare them against the input data. If there's a match, respond with the ID number of the match, and only the ID number. If there are no matches, respond with 'No Matches'. Your response should ALWAYS be either an ID number alone or 'No Matches'. Consider that names may not match perfectly (e.g., nicknames, partial names). If there's a strong likelihood of a match based on available information, respond with the ID number. If the likelihood is low, respond with 'No Matches'."},
            {"role": "user", "content": f"Here are the search results: {search_results}. Does any entry match the input data: {data}?"}]
            )
            ai_response = response.choices[0].message.content if response.choices else None

            if ai_response is None:
                raise ValueError("No response from OpenAI")
            
            ai_response = ai_response.strip()
            
            print(f"AI response: {ai_response}")

            if "no matches" in ai_response.lower():
                # If no match found, add the new entity
                entity_id = add_entity(data)
                return jsonify({"success": True, "entity_id": entity_id}), 200
            else:
                # If a match is found, return the match details
                match_id = ai_response
                return jsonify({"success": False, "message": "Match found", "match_id": match_id}), 200

        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return jsonify({"error": str(e)}), 500

def register(integration_manager):
    integration_manager.register('conditional_entity_addition', conditional_entity_addition)