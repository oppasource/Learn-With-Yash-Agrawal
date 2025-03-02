# Fine-tuning-DeepSeek-R1-Distill-Qwen-1.5B-for-ReAct

The ReAct prompt is used to build agents which can use tools if needed. DeepSeek-R1-Distill-Qwen-1.5B runs on local with minimal resources but does not give good results on ReAct prompt. This repo contains code to fine-tune the DeepSeek-R1-Distill-Qwen-1.5B model with ReAct example so that the final trained model can be used for ReAct prompts giving better results and thus able to build agents locally.

`react_dataset.jsonl` - This is the dataset of 60 samples for ReAct. It is curated through output of bigger models as well as manual efforts (of course it can be improved further with different cases).

`ReAct_DeepSeek_Training.ipynb` - This notebook gives details on actual training procedure using Unsloth and saving LoRA weights of the trained model.

`ReAct_Model_Export.ipynb` - This notebook shows how the trained model can be pushed to huggingface hub, converted to GGUF format along with quantization and use that final model through ollama so it can be used locally to build agents.

# Use the Fine-Tuned Model via Ollama

## Download the Fine-Tuned Model
Pull the model from Hugging Face to your local system:

```python
import ollama
ollama.pull('hf.co/yashagrawal/react_deepseek_1.5B-Q8_0-GGUF:latest')
```

## Run the Model
Use the model in a chat loop with ReAct-style prompting. Replace tools with your own tools and examples in the prompt.

```python
from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='hf.co/yashagrawal/react_deepseek_1.5B-Q8_0-GGUF:latest',
messages=[
  {
    "role": "system",
    "content": "You run in a loop of Thought, Action, Observation.\nAt the end of the loop, you output an Answer.\n\nUse Thought to describe your thoughts about the question you have been asked.\nUse Action to run one of the actions available to you - then wait for getting the observation of action in next message.\nObservation will be the result of running those actions.\n\nIf the tool requires arguments and the user has not provided them, **ask the user for the missing details** instead of assuming values. Do not make arbitrary selections when multiple options are available—ask the user to choose.\n\nYour available actions are:\n```\nfind_movie:\nusage - find_movie: \ne.g. find_movie: Comedy\nReturns a list of movies matching the given genre.\n\nbook_ticket:\nusage - book_ticket: , , \ne.g. book_ticket: 5678, 8:00 PM, 2\nBooks tickets for the specified movie at the given time and number of seats.\n```\n\nExample session:\n```\nQuestion: I want to watch a movie. Thought: The user hasn't specified what genre they prefer. I need to ask for their preference. Answer: Sure! What genre of movie are you in the mood for?\n\nQuestion: I feel like watching a sci-fi movie. Thought: I should search for sci-fi movies. Action: find_movie: Sci-Fi\n\n\n```"
  },
  {
    "role": "user",
    "content": "I feel like watching a movie maybe."
  }
])

print(response.message.content)
```

## Video Demo  
Watch the demo full walkthrough of this project here: https://youtu.be/mRmhJWKJ3co
