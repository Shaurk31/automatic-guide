import streamlit as st
from openai import OpenAI
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from io import BytesIO
import base64
from deepgram import Deepgram
import asyncio

clientO = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
DEEPGRAM_API_KEY = st.secrets["DEEPGRAM_API_KEY"]

clientE = ElevenLabs(api_key=ELEVENLABS_API_KEY)
dg_client = Deepgram(DEEPGRAM_API_KEY)

def steve_gpt(prompt):
    context = """
    Embody Steve Jobs, the co-founder of Apple Inc., with a precise focus on his distinctive 
    communication style, mannerisms, and personality traits. 
    Respond with the visionary passion, assertiveness, and intensity he was known for. 
    Your responses should be concise, direct, and often curt, reflecting his no-nonsense approach. 
    Speak with confidence, emphasizing principles of innovation, simplicity, design excellence, and user experience. 
    Inject a sense of urgency and conviction in your words, showing his relentless drive for perfection. 
    Use pauses for effect, and occasionally adopt his famous rhetorical questions to provoke thought. 
    Critique ideas bluntly yet thoughtfully, maintaining an air of authority and inspiration. 
    Channel his mix of formality and casualness, ensuring responses are succinct and impactful, 
    resembling a true Steve Jobs conversation.
    Communicate in a semi-formal manner suited for a casual call. Keep responses under 75 words.
    """
    response = clientO.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )  # 75~ words
    return response.choices[0].message.content

def generate_audio_response(text):
    response = clientE.text_to_speech.convert(
        voice_id="90X0q8hW9UBezSmbMCRm",  # steve id
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_turbo_v2",
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
        ),
    )
    audio = BytesIO()
    for chunk in response:
        if chunk:
            audio.write(chunk)
    audio.seek(0)
    return audio

async def transcribe_audio(audio_file):
    with open(audio_file, 'rb') as f:
        source = {'buffer': f, 'mimetype': 'audio/mp3'}
        response = await dg_client.transcription.prerecorded(source, {'punctuate': True})
        return response['results']['channels'][0]['alternatives'][0]['transcript']

st.markdown(
    """
    <style>
    .main {
        background-color: #1f2c56;
        padding-top: 50px;
        text-align: center;
        color: white;
        height: 100vh;
    }
    .center {
        display: flex;
        justify-content: center;
        align-items: center;
        flex-direction: column;
        height: 100%;
    }
    .input-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 20px;
    }
    .input-box {
        width: 300px;
        padding: 10px;
        border: none;
        border-radius: 5px;
        margin-right: 10px;
    }
    .button {
        width: 100px;
        padding: 10px;
        margin: 10px;
        border: none;
        border-radius: 50px;
        color: white;
        font-size: 16px;
        cursor: pointer;
        display: inline-block;
        background-color: #28a745;
    }
    .audio-response {
        margin-top: 20px;
    }
    </style>
    """
)

st.markdown("<div class='main center'>", unsafe_allow_html=True)

# File uploader
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav"])

if uploaded_file is not None:
    with open("uploaded_audio.mp3", "wb") as f:
        f.write(uploaded_file.getbuffer())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    transcription = loop.run_until_complete(transcribe_audio("uploaded_audio.mp3"))
    st.write(f"Transcription: {transcription}")
    response = steve_gpt(transcription)
    audio = generate_audio_response(response)
    audio_base64 = base64.b64encode(audio.getvalue()).decode('utf-8')
    audio_tag = f"""
    <audio autoplay="true" class="audio-response">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """
    st.markdown(audio_tag, unsafe_allow_html=True)
else:
    st.text_input("chat", key="input", placeholder="Say something to Steve...", label_visibility="collapsed")
    if st.button("Send", key="send"):
        user_input = st.session_state.get("input", "")
        if user_input:
            response = steve_gpt(user_input)
            audio = generate_audio_response(response)
            audio_base64 = base64.b64encode(audio.getvalue()).decode('utf-8')
            audio_tag = f"""
            <audio autoplay="true" class="audio-response">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            """
            st.markdown(audio_tag, unsafe_allow_html=True)
        else:
            st.write("Please enter some text to talk to Steve Jobs.")
  
st.markdown("</div>", unsafe_allow_html=True)
