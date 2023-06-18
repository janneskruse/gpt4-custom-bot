from flask import Flask, render_template, request

app = Flask(__name__)

#create a model at mindsdb with the following code:
#CREATE MODEL mindsdb.gpt4
#PREDICT response
#USING
#engine = 'openai',
#max_tokens = 2500,
#-- api_key = 'your openai key, in cloud accounts we provide one',
#model_name = 'gpt-4', -- you can also use 'text-davinci-003' or 'gpt-3.5-turbo'
#prompt_template = 'Respond to: {{text}} in the following format: Hola Miguel, como estás? Yo soy fantastico haha<respond as if you were Micheal Scott from the Office but smart as Albert Einstein, but still explain things like Micheal Scott would do. If you give back code, only give back the relevant parts and not unnecessearyy long parts as svg path.'


import mindsdb_sdk
import sys

server = mindsdb_sdk.connect('https://cloud.mindsdb.com', login='', password='')
project = server.get_project('mindsdb')


# Initialize the conversation
initial_conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hello, how can I help you"},
]

conversation = initial_conversation

@app.route('/reset_conversation', methods=['GET'])
def reset_conversation():
    global conversation
    conversation = initial_conversation
    return "Conversation reset"

threshold = [25000,1024 * 1024] #set threshold to 25000 characters and 1mb storage memory


def store(text):
    return sys.getsizeof(text)

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

# Function to escape special characters in conversation content
def remove_doublequotes(text):
    return text.replace('"', '')

# Function to get a response based on user question
def call_chattie(question):
    try:
        if (len(question)<25000):
            #remove conversations if storage too big  
            remove_conversation(conversation, question, threshold)
            
            # Add user question to the conversation
            conversation.append({"role": "user", "content": remove_doublequotes(question)})

            # Convert the conversation to a formatted string
            formatted_conversation = "\n".join([f"{message['role']}: {message['content']}" for message in conversation])

            # Perform an SQL query within the project with conversation context -->gpt4 is your model from the project
            query = project.query(f'SELECT response from mindsdb.gpt4 WHERE author_username = "mindsdb" AND text="{formatted_conversation}";')

            # Fetch the results
            results = query.fetch()

            # Extract the response
            response = results['response'][0]

            # Add assistant response to the conversation
            conversation.append({"role": "assistant", "content": remove_doublequotes(response)})

            # Return the response
            return response
        else:
            return "Your request is too long. Please reduce to a maximum of 25000 characters"
    
    except RuntimeError as e:
        if 'maximum context length' in str(e):
            return "Too many requests at a time. Please refresh the page"
        else:
            return "An unexpected error occurred. Please try again later."





# Define a route to handle the HTML page
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    # Get the data from the form
    input_data = request.form['input']

    # Call the call_chattie function with the input data
    response = call_chattie(input_data)

    # Return the response to be displayed
    return response

if __name__ == '__main__':
    app.run(debug=True)
