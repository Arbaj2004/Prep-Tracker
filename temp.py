from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/check_api', methods=['GET'])
def check_api():
    # Get the parameter from the query string
    param = 'arbaj_2004'

    if not param:
        print("noooooooo")
        return jsonify({'error': 'Missing parameter'}), 400

    # Define the API endpoint and parameters
    api_url = 'https://alfa-leetcode-api.onrender.com/'  # Replace with the actual API URL
    params = {'param': param}

    try:
        # Make the API request
        response = requests.get(api_url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            return jsonify({'data': data}), 200
        else:
            # Handle different types of errors
            return jsonify({'error': 'API returned an error', 'status_code': response.status_code}), response.status_code

    except requests.RequestException as e:
        # Handle network-related errors
        return jsonify({'error': 'Failed to connect to the API', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
