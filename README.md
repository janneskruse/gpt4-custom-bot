# GPT-4 custom chatbot

## Description
This project creates a gpt-4 chatbot from [OpenAI's](https://github.com/openai) GPT-4 model using third party provider [mindsdb](https://mindsdb.com). It is not a deployment ready application and not intended to replace OpenAIs gpt4 functionality but rather for educational purpose. However, you can use it to learn about GPT-4, customize your own chatbot and compare it against the GPT 3.5 model.

![](example.png)

To use the chatbot follow the instructions below!

## Installation


#create a model at mindsdb with the following code:
#CREATE MODEL mindsdb.gpt4
#PREDICT response
#USING
#engine = 'openai',
#max_tokens = 2500,
#-- api_key = 'your openai key, in cloud accounts we provide one',
#model_name = 'gpt-4', -- you can also use 'text-davinci-003' or 'gpt-3.5-turbo'
#prompt_template = 'Respond to: {{text}} in the following format: Hola Miguel, como estás? Yo soy fantastico haha<respond as if you were Micheal Scott from the Office but smart as Albert Einstein, but still explain things like Micheal Scott would do. If you give back code, only give back the relevant parts and not unnecessearyy long parts as svg path.'



## License
This project is for local usage only. Please dont integrate it in any comercial project! If you decide to use the chat bot or the code in any form of media (e.g. a youtube video), please refer to this repo and name the author: Jannes Kruse.

Apart from that: Happy chatting:D


# External packages and software used in this repo

- OpenAI's GPT-4 via mindsdb
    - mindsdb's [python api](https://docs.mindsdb.com/sdk/python-sdk)
- flask for using python with html
- jquery for working with the DOM
- highlight.js for code highlighting
