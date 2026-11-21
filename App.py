
import streamlit as st
from google import genai
import time

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

MODEL_NAME = "gemini-3.1-flash-lite"

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
    "movie_title": "THE LAST SUNRISE",
    "continuity_memory": "",
    "continuity_reports": []
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

    max_attempts = 3

    for attempt in range(max_attempts):

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if response.text:
                return response.text

            st.error("AI returned an empty response.")
            return None

        except Exception as e:

            error_message = str(e).upper()

            temporary_error = any(
                code in error_message
                for code in [
                    "503",
                    "UNAVAILABLE",
                    "500",
                    "INTERNAL",
                    "504",
                    "DEADLINE_EXCEEDED"
                ]
            )

            if temporary_error and attempt < max_attempts - 1:

                wait_seconds = 2 ** (attempt + 1)

                st.warning(
                    f"Google server busy. "
                    f"Retrying in {wait_seconds} seconds... "
                    f"Attempt {attempt + 2}/{max_attempts}"
                )

                time.sleep(wait_seconds)
                continue

            st.error(f"Gemini API Error: {e}")
            return None

    st.error(
        "Google AI server is still unavailable. "
        "Please try again later."
    )
    return None


# ================= CONTINUITY RESPONSE PARSER =================

def extract_section(text, start_marker, end_marker=None):

    start = text.find(start_marker)

    if start == -1:
        return ""

    start += len(start_marker)

    if end_marker:
        end = text.find(end_marker, start)

        if end == -1:
            return text[start:].strip()

        return text[start:end].strip()

    return text[start:].strip()


# ================= AUTOMATIC CONTINUITY CHECKER =================

def check_continuity(scene_text, scene_number, previous_memory):

    if scene_number == 1:
        previous_info = """
This is the FIRST scene of the movie.
There is no previous scene.

Check that the scene establishes:
- A clear opening frame.
- Character appearances and positions.
- Initial props and equipment positions.
- Location and screen geography.
- A precise final frame for Scene 2.
"""
    else:
        previous_info = f"""
PREVIOUS SCENE CONTINUITY MEMORY:
{previous_memory}

The new scene MUST begin from the exact physical state
described in the previous scene's ending frame.

Do not invent a different starting position.
Do not reset character positions, props or injuries.
"""

    checker_prompt = f"""
You are a professional Hollywood film continuity supervisor
and cinematic scene editor.

Your job is to inspect and repair the supplied scene prompt
before it is approved for the movie.

CURRENT SCENE NUMBER: {scene_number}

{previous_info}

NEW SCENE PROMPT TO CHECK:
{scene_text}

CHECK ALL FIVE CONTINUITY CATEGORIES:

1. ENDING FRAME TO OPENING FRAME:
For Scene 1, verify that opening and ending frames are clearly
defined.
For later scenes, compare the previous scene's exact ending
frame with this scene's opening frame.
The new scene must continue naturally from that exact moment.

2. CHARACTER APPEARANCE:
Check exact face, age, hairstyle, hair color, eye color,
body structure, clothing, footwear, accessories and injuries.
No unexplained changes are allowed.

3. PROPS AND EQUIPMENT:
Check weapons, bags, tools, vehicles and other objects.
Preserve which hand holds each object and its physical position.
No unexplained disappearance, duplication or teleportation.

4. LOCATION AND ENVIRONMENT:
Check location, surroundings, weather, lighting and geography.
A location change is allowed ONLY when the scene describes
a believable transition or passage of time.

5. MOVEMENT AND CAMERA DIRECTION:
Check character movement direction, body orientation,
screen geography, camera position and action direction.
Maintain believable cinematic screen continuity.

IMPORTANT HOLLYWOOD RULES:

- The movie must feel like one continuous professionally edited film.
- Do not make scenes feel like unrelated video clips.
- Do not unnecessarily repeat the previous scene.
- Camera angles may change naturally, but physical continuity
  must remain correct.
- Do not change the story or invent new characters.
- Do not remove important actions.
- Preserve the original scene's creative intention.
- If any continuity problem exists, rewrite the scene prompt
  to correct it before approving.
- The final scene must contain a precise ending frame.
- For every scene after Scene 1, clearly describe how its
  opening frame continues from the previous ending frame.

UPDATED CONTINUITY MEMORY:

After checking and repairing the scene, create a concise but
detailed continuity record for the NEXT scene.

Include:
- Exact final frame composition.
- Every character's exact position and body direction.
- Character appearance and current injuries.
- Clothing condition.
- Props and equipment, including which hand holds them.
- Exact location and environment.
- Movement direction and current action.
- Camera position and screen geography.
- Any unresolved action that must continue.

OUTPUT FORMAT IS STRICT.
Return these exact section headings:

CONTINUITY_STATUS:
PASS or REPAIRED or FAIL

CONTINUITY_REPORT:
Explain what was checked and what was corrected.
Mention all five categories.

FINAL_SCENE_PROMPT:
Write the complete final approved scene prompt here.
Do not shorten it.

UPDATED_CONTINUITY_MEMORY:
Write the complete continuity record for the next scene.

If you cannot correct a critical continuity problem,
return FAIL and explain why.
"""

    result = generate(checker_prompt)

    if not result:
        return None

    status = extract_section(
        result,
        "CONTINUITY_STATUS:",
        "CONTINUITY_REPORT:"
    ).upper()

    report = extract_section(
        result,
        "CONTINUITY_REPORT:",
        "FINAL_SCENE_PROMPT:"
    )

    final_scene = extract_section(
        result,
        "FINAL_SCENE_PROMPT:",
        "UPDATED_CONTINUITY_MEMORY:"
    )

    updated_memory = extract_section(
        result,
        "UPDATED_CONTINUITY_MEMORY:"
    )

    status = status.splitlines()[0].strip() if status else ""

    if not final_scene or not updated_memory:
        st.error(
            "Continuity Checker returned an incomplete response. "
            "Scene was not saved. Please try again."
        )
        return None

    if "FAIL" in status:
        st.error("Continuity check FAILED. Scene was not saved.")
        st.warning(report or "The checker found an unresolved problem.")
        return None

    if "PASS" not in status and "REPAIRED" not in status:
        st.error(
            "Continuity status was unclear. "
            "Scene was not saved."
        )
        return None

    return {
        "scene": final_scene,
        "memory": updated_memory,
        "status": status,
        "report": report
    }


# ================= SCENE APPROVAL PROCESS =================

def approve_scene(scene_text, scene_number):

    previous_memory = st.session_state.continuity_memory

    with st.spinner(
        f"Checking Scene {scene_number} continuity..."
    ):

        checked = check_continuity(
            scene_text,
            scene_number,
            previous_memory
        )

    if not checked:
        return False

    # Save only after continuity approval
    st.session_state.scenes.append(checked["scene"])
    st.session_state.scene_number = scene_number

    # Update memory for the next scene
    st.session_state.continuity_memory = checked["memory"]

    st.session_state.continuity_reports.append({
        "scene": scene_number,
        "status": checked["status"],
        "report": checked["report"]
    })

    return True


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
    st.info("AI Model: Gemini 3.1 Flash-Lite")

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

    st.markdown("### 🎞️ CONTINUITY SYSTEM")
    st.success("Automatic Continuity Checker: ON")
    st.caption("Master Continuity Memory: ON")
    st.caption("Automatic Scene Repair: ON")

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
            st.session_state.continuity_memory = ""
            st.session_state.continuity_reports = []

if st.session_state.story:

    with st.container(border=True):

        st.markdown("### 🎬 YOUR MOVIE STORY")

        st.code(
            st.session_state.story,
            language=None
        )

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

        st.code(
            st.session_state.characters,
            language=None
        )

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
        "APPROVED SCENES",
        len(st.session_state.scenes)
    )

st.markdown("### 🔗 MASTER CONTINUITY SYSTEM")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "CONTINUITY CHECKS",
        len(st.session_state.continuity_reports)
    )

with col2:
    st.metric(
        "SCENES REMAINING",
        max(0, scene_count - len(st.session_state.scenes))
    )

if st.session_state.continuity_reports:

    with st.expander("📋 VIEW CONTINUITY CHECK REPORTS"):

        for report in st.session_state.continuity_reports:

            st.markdown(
                f"**Scene {report['scene']} — {report['status']}**"
            )

            st.write(report["report"])

            st.divider()

if st.session_state.continuity_memory:

    with st.expander("🧠 VIEW MASTER CONTINUITY MEMORY"):

        st.code(
            st.session_state.continuity_memory,
            language=None
        )


# ================= FIRST SCENE =================

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

Create a professional Hollywood movie scene.

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
10. A precise opening frame.
11. A precise final frame.

HOLLYWOOD CINEMATIC RULES:

- Establish the physical geography clearly.
- Use professional film shot composition.
- Make the action feel natural and physically believable.
- Do not let characters look directly into the camera.
- Avoid random character or prop changes.
- End with a detailed exact frame that Scene 2 can continue from.

Return only the complete scene prompt.
"""

                result = generate(prompt)

                if result:

                    approved = approve_scene(
                        result,
                        1
                    )

           
