import streamlit as st
from google import genai

st.set_page_config(
    page_title="AI Movie Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= GEMINI SECRET KEY =================

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=API_KEY)
except Exception:
    client = None

# ================= DESIGN =================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #080E1D, #111C35, #10172B);
    color: #F4F6FC;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101C36, #080F20);
    border-right: 1px solid #293D62;
}
h1, h2, h3 {
    color: #F3C66A !important;
}
p, label, .stMarkdown {
    color: #E0E8F8;
}
.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input {
    background-color: #10264A !important;
    color: white !important;
    border: 1px solid #34547F !important;
    border-radius: 10px !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #A9B9D2 !important;
}
.stButton > button, .stDownloadButton > button {
    background: linear-gradient(100deg, #B77A25, #F3CD76) !important;
    color: #10172B !important;
    border: none !important;
    border-radius: 11px !important;
    font-weight: 800 !important;
    min-height: 46px;
    width: 100%;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background: linear-gradient(100deg, #F3CD76, #FFE5A3) !important;
    color: #080E1D !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(22, 42, 76, 0.65);
    border: 1px solid #30496E;
    border-radius: 15px;
}
div[data-testid="stMetric"] {
    background: #142847;
    border: 1px solid #38567F;
    padding: 14px;
    border-radius: 12px;
}
hr {
    border-color: #30496E;
}
.stProgress > div > div {
    background-color: #E6B64D;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================

defaults = {
    "story": "",
    "characters": "",
    "scenes": [],
    "scene_number": 0,
    "movie_context": "",
    "movie_title": "THE LAST SUNRISE"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ================= GEMINI AI =================

def generate(prompt):

    if client is None:
        st.error(
            "Gemini API Secret missing. "
            "Please add GEMINI_API_KEY in Streamlit Secrets."
        )
        return None

    try:
        response = client.models.generate_content(
            model=st.session_state.get(
                "model_name", "gemini-2.5-flash"
            ),
            contents=prompt
        )

        if response.text:
            return response.text

        st.error("AI returned an empty response.")
        return None

    except Exception as e:
        st.error(f"Gemini API Error: {e}")
        return None

# ================= HEADER =================

st.markdown("""
<div style="
    background:linear-gradient(110deg,#172B50,#263C60);
    border:1px solid #49668F;
    border-radius:18px;
    padding:24px;
    margin-bottom:20px;
">
<h1 style="margin:0;color:#F3C66A!important;">
🎬 AI MOVIE STUDIO
</h1>
<p style="margin-top:8px;color:#D5E1F5;">
Create Hollywood Stories • Design Characters • Generate Cinematic Scenes
</p>
</div>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================

with st.sidebar:

    st.markdown("## ⚙️ AI SETTINGS")

    model = st.selectbox(
        "AI Model",
        ["gemini-2.5-flash", "gemini-2.5-pro"]
    )

    st.session_state.model_name = model

    st.divider()

    st.markdown("### 🎥 Movie Settings")

    lock = st.checkbox(
        "Character Consistency Lock",
        value=True
    )

    realistic = st.checkbox(
        "Hollywood Photorealism",
        value=True
    )

    dialogue = st.checkbox(
        "Sparse Natural Dialogue",
        value=True
    )

    st.divider()

    st.caption("AI MOVIE STUDIO")
    st.caption("Powered by Google Gemini")

# ================= MOVIE SETUP =================

st.markdown("## 🎞️ 01 — MOVIE CREATOR")

col1, col2 = st.columns(2)

with col1:

    title = st.text_input(
        "Movie Title",
        "THE LAST SUNRISE"
    )

    genre = st.selectbox(
        "Movie Genre",
        [
            "Sci-Fi Action",
            "Fantasy Action",
            "Adventure",
            "Survival",
            "Horror",
            "Mystery Thriller",
            "Epic War",
            "Romance",
            "Custom"
        ]
    )

    duration = st.selectbox(
        "Movie Duration",
        [
            "5 minutes",
            "10 minutes",
            "15 minutes",
            "20 minutes",
            "30 minutes",
            "45 minutes",
            "60 minutes"
        ],
        index=4
    )

with col2:

    environment = st.selectbox(
        "Movie Environment",
        [
            "Multiple Locations",
            "Futuristic City",
            "Dense Jungle",
            "Desert",
            "Mountains",
            "Ocean",
            "Ancient Kingdom",
            "Magical World"
        ]
    )

    scene_length = st.selectbox(
        "Video Scene Duration",
        ["10 seconds", "15 seconds", "20 seconds"]
    )

    visual_style = st.selectbox(
        "Visual Quality",
        [
            "Realistic Hollywood Cinematic",
            "Epic Fantasy Realism",
            "Photorealistic Action",
            "Dark Cinematic Thriller"
        ]
    )

story_idea = st.text_area(
    "💡 Movie Story Idea",
    placeholder="Describe your movie idea...",
    height=110
)

col1, col2 = st.columns(2)

with col1:
    hero = st.text_area(
        "🦸 Hero / Heroine Details",
        placeholder="Age, face, hair, clothes, abilities...",
        height=100
    )

with col2:
    villain = st.text_area(
        "👹 Villain Details",
        placeholder="Appearance, powers, motivation...",
        height=100
    )

extra = st.text_area(
    "📝 Additional Instructions",
    placeholder="Any special requirements for your movie...",
    height=80
)

# ================= CONTEXT =================

context = f"""
MOVIE TITLE: {title}
GENRE: {genre}
DURATION: {duration}
ENVIRONMENT: {environment}
SCENE LENGTH: {scene_length}
VISUAL STYLE: {visual_style}

STORY IDEA:
{story_idea}

HERO:
{hero or 'Create an original protagonist.'}

VILLAIN:
{villain or 'Create an original antagonist.'}

ADDITIONAL RULES:
{extra}

CHARACTER LOCK:
{lock}. Maintain exact face, age, body, hair,
clothing, accessories and appearance.

VISUAL REALISM:
{realistic}. Use realistic lighting, natural textures
and physically believable movements.

DIALOGUE:
{dialogue}. Keep dialogue purposeful and natural.

Write prompts in professional English.
"""

# ================= STORY GENERATOR =================

st.divider()

st.markdown("## 📖 02 — STORY GENERATOR")

if st.button("✨ GENERATE COMPLETE MOVIE STORY", key="story_btn"):

    with st.spinner("Creating your Hollywood movie story..."):

        prompt = context + """

Create a complete original Hollywood movie story.

Include:

1. Powerful opening hook.
2. Main characters and motivations.
3. Central conflict.
4. Suspense and action.
5. Original plot twists.
6. Emotional moments.
7. Multiple interesting locations.
8. Major climax.
9. Satisfying ending.

Create a detailed story structure suitable
for the selected movie duration.

Do not generate individual scenes yet.
"""

        result = generate(prompt)

        if result:
            st.session_state.story = result
            st.session_state.characters = ""
            st.session_state.scenes = []
            st.session_state.scene_number = 0
            st.session_state.movie_context = context
            st.session_state.movie_title = title

if st.session_state.story:

    with st.container(border=True):

        st.markdown("### 🎬 YOUR MOVIE STORY")
        st.markdown(st.session_state.story)

        st.download_button(
            "⬇️ DOWNLOAD MOVIE STORY",
            st.session_state.story,
            file_name="movie_story.txt"
        )

# ================= CHARACTER BIBLE =================

st.divider()

st.markdown("## 👥 03 — CHARACTER DESIGN STUDIO")

if st.button("🎨 GENERATE CHARACTER BIBLE", key="character_btn"):

    if not st.session_state.story:
        st.warning("Generate the movie story first.")

    else:

        with st.spinner("Designing movie characters..."):

            prompt = st.session_state.movie_context + f"""

MOVIE STORY:
{st.session_state.story}

Create a detailed character design bible.

For every important character include:

- Exact age
- Face and facial features
- Hair and eye color
- Body structure
- Clothing and footwear
- Accessories and weapons
- Personality
- Abilities
- Character purpose

Write a locked visual description for each character.

All characters must look identical in every scene.
Also describe important creatures and props.
"""

            result = generate(prompt)

            if result:
                st.session_state.characters = result

if st.session_state.characters:

    with st.container(border=True):

        st.markdown("### 👤 CHARACTER BIBLE")
        st.markdown(st.session_state.characters)

        st.download_button(
            "⬇️ DOWNLOAD CHARACTER BIBLE",
            st.session_state.characters,
            file_name="character_bible.txt"
        )

# ================= SCENE GENERATOR =================

st.divider()

st.markdown("## 🎥 04 — CINEMATIC SCENE STUDIO")

scene_count = (
    int(duration.split()[0]) * 60
    // int(scene_length.split()[0])
)

col1, col2 = st.columns(2)

with col1:
    st.metric("TOTAL MOVIE SCENES", scene_count)

with col2:
    st.metric(
        "GENERATED SCENES",
        len(st.session_state.scenes)
    )

if st.session_state.story:

    if not st.session_state.scenes:

        if st.button("🎬 GENERATE SCENE 1", key="first_scene"):

            with st.spinner("Creating cinematic Scene 1..."):

                prompt = st.session_state.movie_context + f"""

MOVIE STORY:
{st.session_state.story}

CHARACTER BIBLE:
{st.session_state.characters}

Generate SCENE 1 ONLY.

Duration: {scene_length}

Include:

1. Scene title and number.
2. Exact location and atmosphere.
3. Character appearance and positions.
4. Body direction and screen geography.
5. Camera angle and lens perspective.
6. Camera movement.
7. Second-by-second action progression.
8. Realistic physical movements and reactions.
9. Natural dialogue only when important.
10. Exact final frame.

Use professional cinematic video prompt language.

Do not let characters look directly into the camera.
The final frame must be suitable for Scene 2 continuity.

Return only the scene prompt.
"""

                result = generate(prompt)

                if result:
                    st.session_state.scenes.append(result)
                    st.session_state.scene_number = 1
                    st.rerun()

if st.session_state.scenes:

    current = st.session_state.scenes[-1]

    with st.container(border=True):

        st.markdown(
            f"### 🎞️ SCENE {st.session_state.scene_number}"
        )

        st.markdown(current)

        st.download_button(
            "⬇️ DOWNLOAD THIS SCENE",
            current,
            file_name=f"scene_{st.session_state.scene_number}.txt"
        )

    if st.session_state.scene_number < scene_count:

        if st.button(
            "➡️ GENERATE NEXT SCENE",
            key=f"next_{st.session_state.scene_number}"
        ):

            previous = st.session_state.scenes[-1]

            with st.spinner("Creating next continuous scene..."):

                prompt = st.session_state.movie_context + f"""

MOVIE STORY:
{st.session_state.story}

CHARACTER BIBLE:
{st.session_state.characters}

PREVIOUS SCENE:
{previous}

Generate SCENE {st.session_state.scene_number + 1} ONLY.

Duration: {scene_length}

CONTINUITY IS CRITICAL:

- Begin from the exact previous final frame.
- Preserve character faces and appearance.
- Preserve costumes and accessories.
- Preserve injuries and props.
- Preserve physical positions and action.
- Do not repeat the previous scene.
- Advance the story naturally.
- Use new locations when appropriate.
- Specify camera angle and movement.
- Describe second-by-second action.
- Include realistic movement and reactions.
- Keep dialogue purposeful.
- No direct camera eye contact.
- End with an exact final frame.

Return only the scene prompt.
"""

                result = generate(prompt)

                if result:
                    st.session_state.scenes.append(result)
                    st.session_state.scene_number += 1
                    st.rerun()

    else:
        st.success("All planned scenes have been generated!")

# ================= DOWNLOAD ALL =================

if st.session_state.scenes:

    all_scenes = "\n\n".join(
        f"SCENE {i+1}\n{scene}"
        for i, scene in enumerate(st.session_state.scenes)
    )

    st.divider()

    st.download_button(
        "📦 DOWNLOAD ALL GENERATED SCENES",
        all_scenes,
        file_name="complete_movie_scenes.txt"
    )

# ================= RESET =================

st.divider()

if st.button("🔄 RESET MOVIE PROJECT"):

    st.session_state.story = ""
    st.session_state.characters = ""
    st.session_state.scenes = []
    st.session_state.scene_number = 0
    st.session_state.movie_context = ""

    st.rerun()

st.markdown("""
<div style="
    text-align:center;
    padding:22px;
    color:#AAB9D4;
    border-top:1px solid #30496E;
">
    🎬 AI MOVIE STUDIO<br>
    <small>Powered by Google Gemini AI</small>
</div>
""", unsafe_allow_html=True)
