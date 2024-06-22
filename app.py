import streamlit as st
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import os
import uuid
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from io import BytesIO
import base64

clientO = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
clientE = ElevenLabs(api_key=ELEVENLABS_API_KEY)

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

st.markdown(
    """
    <style>
    </style>
    <script>
    </script>
    """,
    unsafe_allow_html=True
)


st.markdown("<div class='main center'>", unsafe_allow_html=True)
st.text_input("chat", key="input", placeholder="Type something to Steve...", label_visibility="collapsed")

audio_bytes = audio_recorder(
    text="Say something to Steve.",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    #icon_name="fa-solid fa-microphone",
    icon_size="1x",
)

path = os.path.join('responses', f"{uuid.uuid4()}.mp3")
with open(path, "wb") as f:
    f.write(audio_bytes)

#audio display
#if audio_bytes:
#st.audio(audio_bytes, format="audio/mp3")

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
        #st.write("Steve is talking...")
    else:
        st.write("Please enter some text to talk to Steve Jobs.")
  
st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <script>
    document.getElementsByName('input')[0].id = 'user-input';
    document.getElementsByClassName('stButton')[0].firstElementChild.id = 'send-button';
    </script>
    """,
    unsafe_allow_html=True
)