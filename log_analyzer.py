import streamlit as st
import ollama
from scapy.all import rdpcap, IP, TCP, UDP 
import io

#config 

OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "networkLog"
#initialize the Ollama client 
client = ollama.Client(host=OLLAMA_HOST)

#UI

st.set_page_config(page_title="LLM Log Analyzer", page_icon="🤖", layout="wide")
st.title("Log Analyzer")
st.subheader(f"Connected to: {OLLAMA_HOST} ({MODEL_NAME})")


#initialize chat history in session state if it doesn't exist

if "messages" not in st.session_state:
    st.session_state.messages = []

#sidebar for file uploads

with st.sidebar:
    st.header("Upload Captures")
    uploaded_pcap = st.file_uploader("Upload a Wireshark PCAP file", type=["pcap", "pcapng"])
    if uploaded_pcap is not None:
        st.success("PCAP loaded successfully!")
        if st.button("Analyze Packet Traffic:"):
            with st.spinner("Parsing packet data..."):
                try:
                    pcap_bytes = io.BytesIO(uploaded_pcap.read())
                    
                    # 1. Clear status update to let you know the USB read finished
                    status_text = st.empty()
                    status_text.text("File read into memory. Initializing Scapy parser...")
                    
                    # Scapy reads the file
                    packets = rdpcap(pcap_bytes)
                    total_pkts = len(packets)
                    
                    status_text.text(f"Found {total_pkts} total packets. Extracting summaries...")
                    
                    packet_summary = []
                    # Only look at up to 40 packets, but show progress
                    for i, pkt in enumerate(packets[:40]):
                        if pkt.haslayer(IP):
                            src = pkt[IP].src
                            dst = pkt[IP].dst
                            proto = "Other"
                            sport = ""
                            dport = ""
                            #makes sure model can see the ports in the log file
                            if pkt.haslayer(TCP):
                                proto = "TCP"
                                sport = f" | SrcPort: {pkt[TCP].sport}"
                                dport = f" | DstPort: {pkt[TCP].dport}"
                            elif pkt.haslayer(UDP):
                                proto = "UDP"
                                sport = f" | SrcPort: {pkt[UDP].sport}"
                                dport = f" | DstPort: {pkt[UDP].dport}"
                            
                            size = len(pkt)
                            # Detailed string giving the LLM the vital port context
                            packet_summary.append(f"Pkt {i}: {src} -> {dst} | Proto: {proto}{sport}{dport} | Size: {size} bytes")
                    
                    status_text.text("Handing summary data to Ollama...")
                    
                    pcap_text_block = "\n".join(packet_summary)
                    pcap_prompt = (
                        f"Analyze this packet capture summary extracted from a network log. "
                        f"Identify suspicious traffic patterns, odd communication ports, or unexpected IP mappings:\n\n"
                        f"```text\n{pcap_text_block}\n```"
                    )
                    
                    st.session_state.messages.append({"role": "user", "content": pcap_prompt})
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error parsing PCAP: {e}")

#Main chat interface


#display previous chat messages when app reruns

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


#react to user text input

if prompt := st.chat_input("Enter logs..."):
    #display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    #add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()


# Process and stream the LLM response when a new user message is present
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    #display LLM response container
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            #stream the response from the Ollama model
            stream = client.chat(
                model=MODEL_NAME,
                messages=st.session_state.messages,
                stream=True,
            )

            for chunk in stream:
                full_response += chunk['message']['content'] or ""
                #dynamically update the UI text as it arrives
                response_placeholder.markdown(full_response + "▌")

            # remove the cursor block once finished
            response_placeholder.markdown(full_response)

            #add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"Failed to connect to Ollama server. Error: {e}")
            st.info("Check if the host IP is correct and Ollama is configured to accept outside connections.")
