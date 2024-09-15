import openai
from flask import jsonify
from integration_manager import get_integration_function

def latent_input(app, data):
    """ """
    with app.app_context():
        user_input = data.get('natural_input')
        if not user_input:
            return jsonify({"error": "Input is required"}), 400

        try:
            # OpenAI Chat Completion request
            print(f"User input: {user_input}")
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI who writes long and detailed answers describing all entities and their relationships based on a given input. Include as many entities and relationships as possible in your answer. The relationships described should always include two clear parties. Be as comprehensive as possible including as much of your available knowledge in the answer, never excluding anything that you know about. Make sure to specify as many relationships as possible, and not just the entities. Every entity should be connected to another entity through at least one path."},
                    {"role": "user", "content": user_input}
                ]
            )

            # Extracting the assistant's reply
            assistant_reply = response.choices[0].message.content
            print(f"Assistant reply: {assistant_reply}")

            result = {
                'natural_input': assistant_reply
            }

            # Retrieve the natural_input_flexible integration function
            natural_input_function = get_integration_function('natural_input_flexible')
            if natural_input_function:
                # Call the natural_input_flexible integration with the assistant's reply
                ni_response, status_code = natural_input_function(app, result)
                if status_code == 200:
                    return jsonify(ni_response), 200
                else:
                    return jsonify({"error": "Failed to process with natural_input_flexible"}), status_code
            else:
                return jsonify({"error": "natural_input_flexible integration not found"}), 404
        except Exception as e:
            return jsonify({"error": f"Failed to call OpenAI API: {str(e)}"}), 500

def register(integration_manager):
    # Register this integration with the Integration Manager
    integration_manager.register('latent_input', latent_input)