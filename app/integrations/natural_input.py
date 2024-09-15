# This code demonstrates integrating OpenAI's GPT-4 model within a Flask application for processing natural language inputs
# to automatically generate a structured knowledge graph. The integration leverages the application's integration manager system
# for enhanced functionality.

# The `create_knowledge_graph` function invokes OpenAI's ChatCompletion API with a specialized prompt that guides the AI to
# process the given natural language input. It aims to construct a knowledge graph identifying entities such as people, organizations,
# and events, along with their interrelationships, based on the input. The function specifies a strict output structure, including
# node types and details about the relationships, to ensure the generated knowledge graph adheres to a predefined format useful for
# application purposes. After receiving the AI's response, the function extracts and returns the structured knowledge graph data.

# The `natural_input` function acts as an integration endpoint within the Flask application. It receives natural language input,
# employs the `create_knowledge_graph` function to generate a knowledge graph from this input, and processes the resulting data.
# Key to this function is the invocation of the `add_multiple_conditional_function`, retrieved through the application's integration
# manager. This function is responsible for adding the generated knowledge graph entities and their relationships into the application's
# data model, based on conditional logic predefined within the integration. This allows for dynamic and automated updates to the
# application's data based on the content of the natural language input processed.

# Error handling is incorporated to ensure a graceful response in case of failures, which could arise from the OpenAI API call,
# data processing errors, or issues in retrieving or executing the `add_multiple_conditional_function`. The system is designed to
# return a structured JSON response indicating the nature of the error encountered.

# Additionally, the `register` function is used to associate the `natural_input` functionality with the application's integration
# manager. This registration facilitates the invocation of the `natural_input` process as a part of the application's broader set
# of integrations, seamlessly integrating AI-driven natural language processing capabilities into the application's ecosystem.

# This integration exemplifies the use of AI to enrich web applications, enabling the transformation of natural language inputs
# into structured data through automated knowledge graph generation and the conditional addition of this data into the application's
# operational context, leveraging the `add_multiple_conditional_function` for dynamic data integration based on AI-generated content.

# This code demonstrates integrating OpenAI's GPT-4 model within a Flask application for processing natural language inputs
# to automatically generate a structured knowledge graph. The integration leverages the application's integration manager system
# for enhanced functionality.

# The `create_knowledge_graph` function invokes OpenAI's ChatCompletion API with a specialized prompt that guides the AI to
# process the given natural language input. It aims to construct a knowledge graph identifying entities such as people, organizations,
# and events, along with their interrelationships, based on the input. The function specifies a strict output structure, including
# node types and details about the relationships, to ensure the generated knowledge graph adheres to a predefined format useful for
# application purposes. After receiving the AI's response, the function extracts and returns the structured knowledge graph data.

# The `natural_input` function acts as an integration endpoint within the Flask application. It receives natural language input,
# employs the `create_knowledge_graph` function to generate a knowledge graph from this input, and processes the resulting data.
# Key to this function is the invocation of the `add_multiple_conditional_function`, retrieved through the application's integration
# manager. This function is responsible for adding the generated knowledge graph entities and their relationships into the application's
# data model, based on conditional logic predefined within the integration. This allows for dynamic and automated updates to the
# application's data based on the content of the natural language input processed.

# Error handling is incorporated to ensure a graceful response in case of failures, which could arise from the OpenAI API call,
# data processing errors, or issues in retrieving or executing the `add_multiple_conditional_function`. The system is designed to
# return a structured JSON response indicating the nature of the error encountered.

# Additionally, the `register` function is used to associate the `natural_input` functionality with the application's integration
# manager. This registration facilitates the invocation of the `natural_input` process as a part of the application's broader set
# of integrations, seamlessly integrating AI-driven natural language processing capabilities into the application's ecosystem.

# This integration exemplifies the use of AI to enrich web applications, enabling the transformation of natural language inputs
# into structured data through automated knowledge graph generation and the conditional addition of this data into the application's
# operational context, leveraging the `add_multiple_conditional_function` for dynamic data integration based on AI-generated content.

from flask import Flask, request, jsonify
import openai
import json
from app.integrations.integration_manager import get_integration_function

app = Flask(__name__)

def create_knowledge_graph(app, natural_input):
    with app.app_context():
        try:
            print("start openai call")

            completion = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """
                    You are an AI expert specializing in knowledge graph creation with the goal of capturing relationships based on a given input or request.
                    You are given input in various forms such as paragraph, email, text files, and more.
                    Your task is to create a knowledge graph based on the input.
                    Add all relevant entities and their relationships, regardless of their type.
                    Ensure that every entity is connected to at least one other entity.
                    """
                    },
                    {
                        "role": "user",
                        "content": f"Create a knowledge graph from the following text: {natural_input}"
                    }
                ],
                functions=[{
                    "name": "knowledge_graph",
                    "description": "Generate a knowledge graph with entities and relationships based on the input. Capture all relevant relationships. Do not abbreviate anything.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "nodes": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "name": {"type": "string"}
                                    },
                                    "required": ["id", "name"]
                                }
                            },
                            "relationships": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "from_id": {"type": "integer"},
                                        "to_id": {"type": "integer"},
                                        "relationship": {"type": "string"},
                                        "snippet": {"type": "string"}
                                    },
                                    "required": ["from_id", "to_id", "relationship", "snippet"]
                                }
                            }
                        },
                        "required": ["nodes", "relationships"]
                    }
                }
            ],
                function_call={"name": "knowledge_graph"}
            )
   
            print("OPENAI END")
            print(completion.choices[0])

            response_data = completion.choices[0].message.function_call

            if response_data and response_data.arguments:
                return json.loads(response_data.arguments)
            else:
                raise ValueError("No valid function call arguments found in the API response")
            
        except Exception as e:
            print(f"Error during knowledge graph creation: {e}")
            return None


def natural_input(app, data):
    with app.app_context():
        try:
            # Get the natural input from the data
            natural_input_text = data.get('natural_input')
            if not natural_input_text:
                return jsonify({"error": "No natural input provided"}), 400

            # Create the knowledge graph
            knowledge_graph_data = create_knowledge_graph(app, natural_input_text)
            
            if knowledge_graph_data is None:
                return jsonify({"error": "Failed to create knowledge graph"}), 500

            # Retrieve the callable function for the add_multiple_conditional integration
            print("get function")
            add_multiple_conditional_function = get_integration_function("add_multiple_conditional")

            if not add_multiple_conditional_function:
                return jsonify({"error": "Target integration function not found"}), 500

            # Call the target integration function and get the response
            print("start adding")
            response, status_code = add_multiple_conditional_function(app, knowledge_graph_data)

            # The response should already be a Flask response object, so we can return it directly
            return response, status_code
        
        except Exception as e:
            print(f"Failed to process natural input: {e}")
            return jsonify({"error": str(e)}), 500

def register(integration_manager):
    integration_manager.register("natural_input", natural_input)