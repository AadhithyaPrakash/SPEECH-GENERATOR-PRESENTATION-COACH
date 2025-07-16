import streamlit as st
from speech_master import SpeechGenerator, PresentationCoach

st.set_page_config(
    page_title="Speech Master AI",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 500;
        color: #333;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .footer {
        text-align: center;
        font-size: 0.8rem;
        color: #666;
        margin-top: 3rem;
    }
    .feature-box {
        font-color: #555;
        border-left: 5px solid #1E88E5;
        padding: 15px;
        margin-bottom: 10px;
    }
    .badge {
        background-color: #E3F2FD;
        color: #1976D2;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .highlight {
        color: #1E88E5;
        font-weight: 600;
    }
    .results-container {
        padding: 15px;
        background-color: #f5f5f5;
        border-radius: 8px;
        margin-top: 15px;
    }
</style>
""",
    unsafe_allow_html=True,
)

if "api_key_saved" not in st.session_state:
    st.session_state.api_key_saved = False

if "generator" not in st.session_state:
    st.session_state.generator = None

if "coach" not in st.session_state:
    st.session_state.coach = PresentationCoach()

if "last_speech" not in st.session_state:
    st.session_state.last_speech = None

if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

st.markdown('<h1 class="main-header">🎤 Speech Master AI</h1>', unsafe_allow_html=True)


with st.sidebar:
    st.image("assets/logo.png", width=300)

    st.markdown("### Navigation")
    page = st.radio(
        "Choose a tool:", ["📝 Speech Generator", "🎯 Presentation Coach", "ℹ️ About"]
    )

    st.markdown("### Configuration")
    with st.expander("API Key Settings", expanded=not st.session_state.api_key_saved):
        api_key = st.text_input(
            "Groq API Key:",
            type="password",
            help="Enter your Groq API Key to enable speech generation",
        )
        if st.button("Save API Key"):
            if api_key:
                try:
                    st.session_state.generator = SpeechGenerator(api_key)
                    st.session_state.api_key_saved = True
                    st.success("API key saved successfully!")
                except Exception as e:
                    st.error(f"Error setting API key: {str(e)}")
            else:
                st.warning("Please enter an API key")

    st.markdown("---")
    st.markdown(
        '<p class="footer">Created with ❤️ by Aadhi Speech Master AI © 2025</p>',
        unsafe_allow_html=True,
    )


if page == "📝 Speech Generator":
    st.markdown(
        '<h2 class="sub-header">AI Speech Generator</h2>', unsafe_allow_html=True
    )

    if not st.session_state.api_key_saved:
        st.warning(
            "⚠️ Please enter your Groq API key in the sidebar to use the Speech Generator."
        )
    else:
        st.markdown(
            """
        <div class="feature-box">
            Create professional speeches tailored to your needs. Customize style, duration, 
            audience, and more. Get ready-to-deliver content with speaking notes included!
        </div>
        """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            with st.expander("Speech Configuration"):
                topic = st.text_input(
                    "Speech Topic:", value="Artificial Intelligence in Education"
                )
                duration = st.slider("Duration (minutes):", 1, 15, 3)
                emotion = st.selectbox(
                    "Speech Style:",
                    options=list(SpeechGenerator.STYLE_TEMPLATES.keys()),
                )
                audience = st.selectbox(
                    "Target Audience:",
                    options=list(SpeechGenerator.AUDIENCE_GUIDANCE.keys()),
                )

        with col2:
            with st.expander("Advanced Settings"):
                model = st.selectbox(
                    "LLM Model:",
                    options=list(SpeechGenerator.AVAILABLE_MODELS.keys()),
                    format_func=lambda x: f"{x} - {SpeechGenerator.AVAILABLE_MODELS[x]['description']}",
                )
                temperature = st.slider("Creativity (Temperature):", 0.1, 1.0, 0.7, 0.1)
                voice_type = st.radio(
                    "Text-to-Speech Voice:", options=["male", "female"]
                )
                additional_instructions = st.text_area(
                    "Additional Instructions:",
                    placeholder="E.g., Include a personal anecdote",
                    max_chars=200,
                )

        if st.button("Generate Speech", type="primary", use_container_width=True):
            with st.spinner("Generating your speech... This may take a moment"):
                try:
                    speech_text, metadata = st.session_state.generator.generate_speech(
                        topic=topic,
                        duration=duration,
                        emotion=emotion,
                        audience=audience,
                        model=model,
                        temperature=temperature,
                        additional_instructions=additional_instructions,
                    )
                    st.session_state.last_speech = speech_text
                    st.session_state.last_metadata = metadata

                    st.success(
                        f"✅ Speech generated successfully with {metadata['word_count']} words (~{duration} minutes)"
                    )

                except Exception as e:
                    st.error(f"Error generating speech: {str(e)}")

        if st.session_state.last_speech:
            st.markdown("### Generated Speech")

            if "last_metadata" in st.session_state:
                meta = st.session_state.last_metadata
                st.markdown(
                    f"""
                <p>
                <span class="badge">Topic: {meta["topic"]}</span> 
                <span class="badge">Style: {meta["emotion"]}</span> 
                <span class="badge">Audience: {meta["audience"]}</span> 
                <span class="badge">Words: {meta["word_count"]}</span>
                </p>
                """,
                    unsafe_allow_html=True,
                )

            speech_text = st.session_state.last_speech

            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(speech_text)
            st.markdown("</div>", unsafe_allow_html=True)

            audio_col1, audio_col2 = st.columns([3, 1])

            with audio_col1:
                if st.button("Generate Audio from Speech", use_container_width=True):
                    with st.spinner("Converting text to speech..."):
                        try:
                            audio_path = (
                                st.session_state.generator.generate_speech_audio(
                                    text=speech_text, voice=voice_type
                                )
                            )
                            st.session_state.last_audio = audio_path
                            st.success("Audio generated successfully!")
                        except Exception as e:
                            st.error(f"Error generating audio: {str(e)}")

            with audio_col2:
                if st.session_state.last_audio:
                    st.download_button(
                        label="Download Audio",
                        data=open(st.session_state.last_audio, "rb").read(),
                        file_name="speech_audio.mp3",
                        mime="audio/mp3",
                        use_container_width=True,
                    )

            if st.session_state.last_audio:
                st.audio(st.session_state.last_audio)

            st.download_button(
                label="Download Speech Text",
                data=speech_text,
                file_name=f"speech_{SpeechGenerator._sanitize_filename(topic)}.txt",
                mime="text/plain",
                use_container_width=True,
            )

elif page == "🎯 Presentation Coach":
    st.markdown(
        '<h2 class="sub-header">Presentation Coach</h2>', unsafe_allow_html=True
    )

    st.markdown(
        """
    <div class="feature-box">
        Analyze your speech delivery and get instant feedback on sentiment, 
        structure, and more. Perfect for rehearsing your presentations!
    </div>
    """,
        unsafe_allow_html=True,
    )

    user_speech = st.text_area(
        "Enter your speech or presentation here:",
        height=200,
        placeholder="Paste your speech or draft presentation text here for analysis...",
    )

    if (
        st.button("Analyze Speech", type="primary", use_container_width=True)
        and user_speech
    ):
        with st.spinner("Analyzing your speech..."):
            coach = st.session_state.coach

            sentiment_label, confidence = coach.analyze_sentiment(user_speech)
            structure_score, sentence_count = coach.structure_score(user_speech)
            complexity_score = coach.analyze_complexity(user_speech)
            suggestions = coach.suggest_improvements(
                sentiment_label, confidence, sentence_count, complexity_score
            )

            st.markdown('<div class="results-container">', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("### Sentiment")
                sentiment_color = (
                    "green"
                    if sentiment_label == "POSITIVE"
                    else "red"
                    if sentiment_label == "NEGATIVE"
                    else "blue"
                )
                st.markdown(
                    f"<h2 style='color: {sentiment_color}; text-align: center;'>{sentiment_label}</h2>",
                    unsafe_allow_html=True,
                )
                st.progress(confidence / 100)
                st.caption(f"Confidence: {confidence:.1f}%")

            with col2:
                st.markdown("### Structure")
                st.markdown(
                    f"<h2 style='text-align: center;'>{structure_score}/100</h2>",
                    unsafe_allow_html=True,
                )
                st.progress(structure_score / 100)
                st.caption(f"Based on {sentence_count} sentences")

            with col3:
                st.markdown("### Complexity")
                st.markdown(
                    f"<h2 style='text-align: center;'>{complexity_score}/100</h2>",
                    unsafe_allow_html=True,
                )
                st.progress(complexity_score / 100)
                complexity_level = (
                    "High"
                    if complexity_score > 70
                    else "Medium"
                    if complexity_score > 40
                    else "Low"
                )
                st.caption(f"Language complexity: {complexity_level}")

            st.markdown("### Improvement Suggestions")
            for suggestion in suggestions:
                st.markdown(f"- {suggestion}")

            words = user_speech.split()
            word_count = len(words)
            estimated_time = round(word_count / 130, 1)

            st.markdown("### Speech Statistics")
            st.markdown(f"- Word count: **{word_count}** words")
            st.markdown(f"- Estimated delivery time: **{estimated_time}** minutes")

            st.markdown("</div>", unsafe_allow_html=True)
elif page == "ℹ️ About":
    st.markdown(
        '<h2 style="color: white;" class="sub-header">About Speech Master AI</h2>',
        unsafe_allow_html=True,
    )

    # Hero Section
    st.markdown(
        """
        <div style="background-color: #1e1e1e; padding: 20px; border-radius: 8px;">
            <h3 style="color: #90caf9; margin-bottom: 15px;">🎤 Your AI-Powered Speaking Companion</h3>
            <p style="font-size: 1.1rem; line-height: 1.6; color: #e0e0e0;">
                Speech Master AI transforms the way you create and deliver presentations. From generating 
                compelling speeches to providing real-time coaching feedback, we're here to make you 
                a more confident and effective speaker.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Features Section
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style="background-color: #121212; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <h4 style="color: #90caf9; margin-bottom: 10px;">📝 Smart Speech Generation</h4>
                <ul style="margin-left: 20px; color: #cccccc;">
                    <li>AI-powered content creation tailored to your audience</li>
                    <li>Multiple speech styles and tones available</li>
                    <li>Customizable duration and complexity levels</li>
                    <li>Professional formatting with speaker notes</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="background-color: #121212; padding: 15px; border-radius: 8px;">
                <h4 style="color: #90caf9; margin-bottom: 10px;">🎯 Intelligent Coaching</h4>
                <ul style="margin-left: 20px; color: #cccccc;">
                    <li>Real-time sentiment analysis</li>
                    <li>Speech structure evaluation</li>
                    <li>Language complexity assessment</li>
                    <li>Personalized improvement suggestions</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style="background-color: #121212; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                <h4 style="color: #90caf9; margin-bottom: 10px;">🎵 Text-to-Speech</h4>
                <ul style="margin-left: 20px; color: #cccccc;">
                    <li>High-quality voice synthesis</li>
                    <li>Male and female voice options</li>
                    <li>Downloadable audio files</li>
                    <li>Perfect for practice and rehearsal</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div style="background-color: #121212; padding: 15px; border-radius: 8px;">
                <h4 style="color: #90caf9; margin-bottom: 10px;">⚡ Advanced AI Models</h4>
                <ul style="margin-left: 20px; color: #cccccc;">
                    <li>Multiple LLM options for diverse needs</li>
                    <li>Adjustable creativity and temperature settings</li>
                    <li>Context-aware content generation</li>
                    <li>Continuous model improvements</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Technology Stack
    st.markdown(
        """
        <div style="background-color: #1e1e1e; padding: 20px; border-radius: 8px;">
            <h3 style="color: #90caf9; margin-bottom: 15px;">🔧 Built with Cutting-Edge Technology</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px;">
                <span style="background-color: #2e2e2e; padding: 5px 10px; border-radius: 4px; color: #eeeeee;">Streamlit</span>
                <span style="background-color: #2e2e2e; padding: 5px 10px; border-radius: 4px; color: #eeeeee;">Groq API</span>
                <span style="background-color: #2e2e2e; padding: 5px 10px; border-radius: 4px; color: #eeeeee;">Natural Language Processing</span>
                <span style="background-color: #2e2e2e; padding: 5px 10px; border-radius: 4px; color: #eeeeee;">Sentiment Analysis</span>
                <span style="background-color: #2e2e2e; padding: 5px 10px; border-radius: 4px; color: #eeeeee;">Text-to-Speech</span>
                <span style="background-color: #2e2e2e; padding: 5px 10px; border-radius: 4px; color: #eeeeee;">Machine Learning</span>
            </div>
            <p style="font-style: italic; color: #aaaaaa;">
                Powered by state-of-the-art language models and speech synthesis technology
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Usage Statistics
    st.markdown(
        """
        <div style="background-color: #1e1e1e; padding: 20px; border-radius: 8px;">
            <h3 style="color: #90caf9; margin-bottom: 15px;">📊 Why Choose Speech Master AI?</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 15px;">
                <div style="text-align: center;">
                    <h2 style="color: #90caf9; margin: 0;">15+</h2>
                    <p style="margin: 5px 0; color: #e0e0e0;">Speech Styles</p>
                </div>
                <div style="text-align: center;">
                    <h2 style="color: #90caf9; margin: 0;">5+</h2>
                    <p style="margin: 5px 0; color: #e0e0e0;">AI Models</p>
                </div>
                <div style="text-align: center;">
                    <h2 style="color: #90caf9; margin: 0;">100%</h2>
                    <p style="margin: 5px 0; color: #e0e0e0;">Customizable</p>
                </div>
                <div style="text-align: center;">
                    <h2 style="color: #90caf9; margin: 0;">∞</h2>
                    <p style="margin: 5px 0; color: #e0e0e0;">Possibilities</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # How to Get Started
    st.markdown(
        """
        <div style="background-color: #1e1e1e; padding: 20px; border-radius: 8px;">
            <h3 style="color: #90caf9; margin-bottom: 15px;">🚀 Getting Started</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px;">
                <div style="padding: 15px; background: #2e2e2e; border-radius: 8px;">
                    <h4 style="color: #64b5f6; margin: 0 0 10px 0;">1. Setup API Key</h4>
                    <p style="margin: 0; font-size: 0.9rem; color: #cccccc;">Enter your Groq API key in the sidebar to unlock all features</p>
                </div>
                <div style="padding: 15px; background: #2e2e2e; border-radius: 8px;">
                    <h4 style="color: #81c784; margin: 0 0 10px 0;">2. Generate Speech</h4>
                    <p style="margin: 0; font-size: 0.9rem; color: #cccccc;">Choose your topic, style, and audience to create the perfect speech</p>
                </div>
                <div style="padding: 15px; background: #2e2e2e; border-radius: 8px;">
                    <h4 style="color: #ffb74d; margin: 0 0 10px 0;">3. Practice & Improve</h4>
                    <p style="margin: 0; font-size: 0.9rem; color: #cccccc;">Use the coaching tool to analyze and perfect your delivery</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Footer Info
    st.markdown(
        """
        <div style="background-color: #1e1e1e; text-align: center; margin-top: 30px; padding: 20px; border-radius: 8px;">
            <h3 style="color: #90caf9; margin-bottom: 15px;">💝 Created with Passion</h3>
            <p style="font-size: 1.1rem; margin-bottom: 10px; color: #e0e0e0;">
                <span style="color: #ffffff; font-weight: bold;">Speech Master AI</span> was crafted to empower speakers worldwide
            </p>
            <p style="color: #aaaaaa; font-style: italic;">
                "Great speakers are not born, they are made with practice and the right tools"
            </p>
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #444;">
                <span style="color: #64b5f6; font-weight: 600;">Version 1.0</span> • 
                <span style="color: #888;">Built with ❤️ by Aadhi</span> • 
                <span style="color: #888;">© 2025 Speech Master AI</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    try:
        if not hasattr(SpeechGenerator, "STYLE_TEMPLATES"):
            st.error("Error: Core functionality module not loaded correctly.")
    except Exception as e:
        st.error(f"Error loading core module: {str(e)}")
