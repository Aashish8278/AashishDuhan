import streamlit as st

# Set background image
st.markdown("""
    <style>
        .reportview-container {
            background: url('https://example.com/your-image.jpg') no-repeat center center fixed;
            background-size: cover;
            color: white;
        }
        .hero-section {
            position: relative;
            height: 100vh;
            background: url('https://example.com/hero-image.jpg') no-repeat center center;
            background-size: cover;
            text-align: center;
        }
        .hero-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 4em;
            font-weight: bold;
            color: #f1c40f;
        }
        .fade-in {
            animation: fadeIn 2s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .stButton button:hover {
            background-color: #f1c40f;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

# Hero Section
st.markdown('<div class="hero-section"><div class="hero-text">Your Cinematic Music Experience</div></div>', unsafe_allow_html=True)

# Fade-in effect
st.markdown('<div class="fade-in">Welcome to your immersive music journey!</div>', unsafe_allow_html=True)

# Add buttons
st.button("Click Me")

# Add background music (optional)
st.markdown("""
    <audio autoplay loop>
        <source src="https://example.com/your-music.mp3" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)
