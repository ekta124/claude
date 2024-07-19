from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    with open('index.html', 'r') as file:
        return file.read()

@app.route('/evaluate', methods=['POST'])
def evaluate():
    token = request.form['token']
    
    try:
        response = requests.get(
            "https://aiproxy.sanand.workers.dev/openai/v1/models",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        models = response.json()['data']
        
        points = 0
        explanation = []
        
        # Check if tts-1-1106 was created on 2023-11-08
        tts1106 = next((model for model in models if model['id'] == 'tts-1-1106'), None)
        if tts1106 and tts1106['created'] == 1699423214:  # Unix timestamp for 2023-11-08
            points += 4
            explanation.append("4 points: tts-1-1106 was created on 2023-11-08")
        else:
            explanation.append("0 points: tts-1-1106 was not created on 2023-11-08 or not found")
        
        # Check if gpt-3.5-turbo-instruct is at index 20
        if len(models) > 20 and models[20]['id'] == 'gpt-3.5-turbo-instruct':
            points += 2
            explanation.append("2 points: gpt-3.5-turbo-instruct is located at index 20")
        else:
            explanation.append("0 points: gpt-3.5-turbo-instruct is not at index 20")
        
        # Check if gpt-4-0613 was created 6 models before gpt-3.5-turbo
        gpt4_index = next((i for i, model in enumerate(models) if model['id'] == 'gpt-4-0613'), -1)
        gpt35_index = next((i for i, model in enumerate(models) if model['id'] == 'gpt-3.5-turbo'), -1)
        if gpt4_index != -1 and gpt35_index != -1 and gpt35_index - gpt4_index == 6:
            points += 1
            explanation.append("1 point: gpt-4-0613 was created 6 models before gpt-3.5-turbo")
        else:
            explanation.append("0 points: gpt-4-0613 was not created 6 models before gpt-3.5-turbo")
        
        result = f"""
        <h2>Results:</h2>
        <h3>Total Points: {points}</h3>
        <h4>Explanation:</h4>
        <ul>
        {"".join(f"<li>{e}</li>" for e in explanation)}
        </ul>
        <a href="/">Back to form</a>
        """
        return result
    
    except requests.RequestException as e:
        return f"Error: {str(e)}. Please check your token and try again. <a href='/'>Back to form</a>"

if __name__ == '__main__':
    app.run(debug=True)