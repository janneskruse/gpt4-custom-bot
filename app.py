from flask import Flask, render_template, request, jsonify
import mindsdb_sdk
import sys
import os
import threading
import webbrowser


app = Flask(__name__)

# Define a route to handle the HTML page
@app.route('/')
def index():
    return render_template('index.html')


@app.route("/login_endpoint", methods=["POST"])
def login():
    email = request.json["email"]
    password = request.json["password"]

    # Verify login credentials using the MindsDB SDK
    try:
        mindsdb_sdk.connect('https://cloud.mindsdb.com', login=email, password=password)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

server=""
project=None
conversation=[]
threshold = [25000,1024 * 1024] #set threshold to 25000 characters and 1mb storage memory

@app.route("/setup_page", methods=["POST"])
def setupConnection():
    global project, conversation  # Use global keyword to update the vars
    try:
        email = request.json["email"]
        password = request.json["password"]
        server = mindsdb_sdk.connect('https://cloud.mindsdb.com', login=email, password=password)
        project = server.get_project('mindsdb')
        print("project connected")
        # Initialize the conversation
        conversation = [
            {"role": "system", "content": "You are a helpful assistant like Micheal Scott with the intelligence of Albert Einstein."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hello, how can I help you"},]
        print("setup")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Function to get size of the input text
def store(text):
    return sys.getsizeof(text)

# Function to escape special characters in conversation content
def remove_doublequotes(text):
    return text.replace('"', '')

# Function to remove conversation messages if greater than threshold
def remove_conversation(conversation, addon, threshold):
    total_length= len([store(message['content']) for message in conversation])+len(addon)
    total_space= sum([store(message['content']) for message in conversation])+store(addon)
    #print("Storage space:", total_space, "Bytes", "total length:", total_length)

    while total_length > threshold[0] or total_space >threshold[1]:
        #print("Storage space:", total_space, "Bytes", "total length:", total_length)
        #display(conversation)
        conversation.pop(0)
        total_length= len([store(message['content']) for message in conversation])+len(addon)
        total_space= sum([store(message['content']) for message in conversation])+store(addon)



# Function to get a response based on user question
def call_chattie(question):
    try:
        if (len(question)<25000):
            remove_conversation(conversation, question, threshold) #call remove conversation function 
            
            # Add user question to the conversation
            conversation.append({"role": "user", "content": remove_doublequotes(question)})
            # Convert the conversation of all messages to a formatted string
            formatted_conversation = "\n".join([f"{message['role']}: {message['content']}" for message in conversation])
            # Perform an SQL query within the project with conversation context -->gpt4 is your model from the project mindsdb (demo project)
            query = project.query(f'SELECT response from mindsdb.gpt4 WHERE author_username = "mindsdb" AND text="{formatted_conversation}";')

            results = query.fetch()
            response = results['response'][0]

            # Add gpt response to the conversation
            conversation.append({"role": "assistant", "content": remove_doublequotes(response)})
            # Return the response to the html
            return response
        else:
            return "Your request is too long. Please reduce to a maximum of 25000 characters"
    
    except RuntimeError as e:
        if 'maximum context length' in str(e):
            return "Too many requests at a time. Please refresh the page"
        else:
            return "An unexpected error occurred. Please try again later."


#Handeling the chat input
@app.route('/submit', methods=['POST'])
def submit():
    # Get the data from the chat
    input_data = request.form['question'] 
    response = call_chattie(input_data) # Call the call_chattie function with the input data
    
    return response



##def run_flask_server():
##    app.run()

if __name__ == '__main__':
    url = "http://127.0.0.1:5000/"
    ## Open the URL in the web browser
    webbrowser.open(url)
    ## Run the Flask server in a separate thread to avoid opening the url twice
    #server_thread = threading.Thread(target=run_flask_server)
    #server_thread.start()
    #os.system(f"python -m webbrowser -t {url}")
    app.run()


