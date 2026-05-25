## LLM Log Analyzer

### What does it do?

The LLM Log Analyzer takes `.pcapng` or `.pcap` files and uses an LLM to analyze and then explains network activity in plain English, allowing non-technical professionals to understand logs.

### How does it work?

The LLM Log Analyzer uses Streamlit python for a sleek, easy-to-navigate UI and the qwen2.5-coder:7B model from ollama. During production, the LLM was successfully run from a USB drive, but if your system has the appropriate resources, feel free to run it locally. The only trade off is that USB drive LLMs take slightly longer to respond to prompts. Regardless of how you store the LLM, the project is fully offline and chats are stored in Streamlit's session state, which clears every time the page is reloaded. This means that you can upload raw, unfiltered data to the LLM and receive an analysis without worrying about sensitive info like IPs and MAC addresses being stored in its memory. 

### Prerequisites: 

An active Ollama installation is required for this project. Assuming you are using a Windows environment, the instructions for setting this up are as follows:

Download Ollama's official installer and pull the qwen2.5 model with this command:

```ollama pull qwen2.5-coder:7B```

Note that this is simply the model that I chose for my specific needs. The project will work with any Ollama model, although the performance of the LLM itself depends on its parameters and training.

When the download finishes, verify that the model works by running:

```ollama run qwen2.5-coder:7B```

If the installation succeeded, you should be able to converse with the LLM. You will notice that it is only capable of outputting generic, oftentimes inaccurate responses, but that will change once it receives its system prompt. Exit the chat by typing: ```/bye```.

Proceed to the setup guide.

### Setup Guide:

Clone the repository and cd into it. You will find a modelfile already created for you, which contains the system prompt for the LLM. You may edit the system prompt as you see fit, but for the purposes of initial testing, it is recommended to leave it as it is until you observe its abilities firsthand.

Run this command to create a custom LLM with the provided modelfile (networkLog is the name that was chosen during production. You may change this to fit your needs, but you will have to edit the MODEL_NAME variable in the source code.):

```ollama create networkLog -f Modelfile```

And finally, run:

```streamlit run log_analyzer.py```

The web app should spin up posthaste. You may either send log snippets directly through the chat interface, or upload .pcap or .pcapng files up to 200MB in size. Observe the LLM's response and enjoy easier log analysis.  


### Disclaimer:

AI is prone to hallucinations and can occasionally be inaccurate despite rigorous system prompting. There is no absolute guarantee that an LLM will consistently follow instructions, stay entirely within scope, or identify complex network anomalies with 100% accuracy. This tool is meant to assist, not replace, human analysts. Context evaulation and final validation still require human expertise.



