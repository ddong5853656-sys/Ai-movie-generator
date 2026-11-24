import io
import streamlit as st
from google import genai
from google.genai import types
import time
import re
import json
from streamlit_local_storage import LocalStorage
st.set_page_config(
    page_title="AI Movie Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("AI Movie Studio")

st.markdown("""
Create cinematic movies with AI.

Generate original movie stories, detailed character designs,
and professional scene-by-scene video prompts.

Bring your imagination to life with AI Movie Studio.
""")

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
    "aspect_ratio": "16:9",
    "movie_ideas": [],
    "selected_movie_idea": "",
    "story_idea_input": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ================= AUTO SAVE SYSTEM =================

def get_local_storage():
    return LocalStorage()

localS = get_local_storage()

SAVE_KEY = "ai_movie_studio_projects"

# ================= LOAD SAVED PROJECT =================

if "saved_project_loaded" not in st.session_state:
    st.session_state.saved_project_loaded = False

if not st.session_state.saved_project_loaded:
    saved_data = localS.getItem(SAVE_KEY)

    if saved_data:
        try:
            if isinstance(saved_data, str):
                saved_data = json.loads(saved_data)

            for key, value in saved_data.items():
                if key in st.session_state:
                    st.session_state[key] = value

        except Exception:
            pass

    st.session_state.saved_project_loaded = True
    
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


# ================= CHARACTER LOCK INSTRUCTIONS =================



CHARACTER_LOCK_RULES = """
STRICT CHARACTER BIBLE ENFORCEMENT — ABSOLUTE PRIORITY:

The complete CHARACTER BIBLE is the permanent source of truth.
Never sacrifice character consistency for shorter prompts.

FOR EVERY SCENE:

1. Identify every character and creature visibly appearing.
2. Retrieve their complete description from the Character Bible.
3. Include ALL permanent identifying details in the scene prompt.
4. Never shorten, summarize, skip or silently omit any permanent detail.
5. Do not assume that a detail is optional just because it is not important to the action.

PERMANENT IDENTITY LOCK:

Always preserve:
- Exact age and apparent age.
- Face shape, jawline and cheekbones.
- Skin tone and permanent skin features.
- Eye color and distinctive eye characteristics.
- Hair color, length, texture and hairstyle.
- Exact height and body structure.
- Clothing design, colors, patterns and materials.
- Footwear design, colors and materials.
- Every permanent accessory, weapon and equipment item.
- Every scar, mole, mark, tattoo and unique identifying feature.

CRITICAL IDENTIFIER ENFORCEMENT:

Every unique identifier in the Character Bible is mandatory.
Never omit tattoos, scars, serial numbers, jewelry, watches,
rings, harnesses, interface ports or other identifying details.

Example:
If Elara has a small "01" serial tattoo on her inner right wrist,
this detail must remain part of her locked identity.
Whenever her right wrist is visible, explicitly describe the tattoo.
Never replace it with a different number or location.

If a body part is not visible in a particular shot,
do not falsely describe it as visible.
However, do not change or forget its permanent design.

ACCESSORY ENFORCEMENT:

Never silently remove, replace or redesign established accessories,
weapons, equipment or clothing components.

UNDEFINED DETAILS:

Never invent permanent character details that are not specified.
Keep undefined details neutral and consistent.

COSTUME AND WEATHERING CONTINUITY:

Separate permanent clothing design from temporary dirt, snow,
ice, blood, damage, wetness and environmental effects.

Temporary changes must follow the story and previous scenes.
Never change original clothing colors, materials or design.

CHARACTER IDENTITY:

Never redesign, reinterpret, beautify, age or de-age a character.
Never change facial features, body proportions or identity.
Never create duplicate versions or mix features between characters.

HOLOGRAM AND PROJECTION LOCK:

If an established character appears as a hologram, projection,
reflection or digital avatar, preserve their established identity.
Do not invent a new face, hairstyle, eye design or appearance.
Only apply projection effects such as transparency, flickering
or distortion without changing the character's actual design.

SCENE RELEVANCE:

Include only characters and creatures actually appearing in the scene.
Do not introduce random characters, creatures or villains.
For every appearing character, include all applicable locked details.

FINAL CHARACTER BIBLE AUDIT:

Before returning each scene prompt, compare every appearing
character against the complete Character Bible.

Check every permanent identifier individually.
If any applicable detail is missing, add it before returning the prompt.

Every scene must work independently in an AI video generator.
Never rely on phrases such as "same character as previous scene".

Expressions, poses, movement and temporary environmental effects
may change naturally. Permanent visual identity must never change.
"""


# ================= SCENE PROMPT BUILDER =================

def build_scene_prompt(
    scene_number,
    story,
    characters,
    movie_context,
    scene_length,
    aspect_ratio,
    previous_scene=None
):

    continuity_section = ""

    if previous_scene:

        continuity_section = f"""
PREVIOUS SCENE:
{previous_scene}

CONTINUITY REQUIREMENTS:

- Begin from the exact final frame of the previous scene.
- Maintain the established screen geography.
- Preserve character positions, body direction and movement continuity.
- Preserve costumes, weapons, accessories, injuries and carried objects.
- Continue the action naturally from the previous final moment.
- Do not repeat the previous scene's events.
- Advance the story meaningfully.
- Change location only when the story naturally requires it.
- Do not create an unexplained time jump.
- Make the transition physically and visually believable.
"""

    return f"""
{movie_context}

MOVIE STORY:
{story}

COMPLETE CHARACTER DESIGN BIBLE:
{characters if characters else
'No character bible has been generated yet. Use only established story details and do not invent conflicting character appearances.'}

{CHARACTER_LOCK_RULES}

{continuity_section}

GENERATE SCENE {scene_number} ONLY.

SCENE DURATION: {scene_length}

ASPECT RATIO: {aspect_ratio}

ASPECT RATIO RULES:

- Generate specifically for {aspect_ratio}.
- If 16:9, use horizontal widescreen composition.
- If 9:16, use vertical portrait composition.
- Compose character positions, action and camera framing for the selected ratio.
- Never switch to another aspect ratio.

SCENE REQUIREMENTS:

1. Scene number and cinematic title.
2. Exact location and atmosphere.
3. Relevant locked character appearances.
4. Exact character positions and screen geography.
5. Body direction and gaze direction.
6. Camera position, angle and lens perspective.
7. Camera movement.
8. Second-by-second action progression.
9. Realistic physical movements and reactions.
10. Natural dialogue only when important.
11. Environmental details and sound atmosphere when useful.
12. Exact final frame for continuity.

CAMERA AND MOVEMENT RULES:

- Use cinematic camera angles appropriate to the action.
- Specify whether the camera is front-facing, side-facing,
  three-quarter, overhead, low-angle or over-the-shoulder.
- Explain the camera's physical position.
- Characters must focus on the action, other characters or threats,
  not randomly stare into the camera.
- Avoid repetitive camera angles.
- Keep movement physically believable.
- Avoid unnatural floating, sliding, teleporting or duplicated movements.

FINAL FRAME:

Describe the exact final positions, body directions, expressions,
environment and camera framing.

The final frame must be suitable for the next scene.

Return only the complete professional cinematic video scene prompt.
Do not add explanations outside the scene.
"""


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

    st.caption("AI MOVIE STUDIO")
    st.caption("Powered by Google Gemini")


# ================= MOVIE TITLE =================

st.markdown("## 🎞️ 01 — START YOUR MOVIE")

title = st.text_input(
    "🎬 Enter Your Movie Story Title",
    key="movie_title_input",
    placeholder="Example: THE LAST DRAGON"
)


# ================= 20 MOVIE IDEAS =================

st.markdown("### 💡 GENERATE 20 STORY IDEAS")

st.write(
    "Pehle apni movie ka title likhein. "
    "AI isi title ke mutabiq 20 different story ideas Roman Urdu mein banayega."
)

if st.button("✨ GENERATE 20 MOVIE IDEAS", key="ideas_btn"):

    if not title.strip():
        st.warning("Please enter your movie title first.")

    else:

        with st.spinner("Creating 20 unique movie ideas in Roman Urdu..."):

            ideas_prompt = f"""
MOVIE TITLE: {title}

Create EXACTLY 20 different and original movie story ideas
based on this exact movie title.

IMPORTANT LANGUAGE RULE:
- Write everything in Roman Urdu.
- Use Urdu language written with English/Roman letters.
- Do NOT use Urdu script.
- Do NOT write the ideas in English.

IDEA REQUIREMENTS:
- Every idea must have a different storyline.
- All 20 ideas must relate strongly to the given title.
- Give each idea a short, interesting title or concept.
- Explain each idea in 2 to 3 Roman Urdu sentences.
- Make ideas cinematic, exciting and suitable for a Hollywood movie.
- Use variety in suspense, emotion, action, adventure and twists.
- Do not repeat the same plot with slightly changed wording.
- Do not write the complete movie story.
- Do not generate scenes or character descriptions.

STRICT OUTPUT FORMAT:
Write exactly 20 numbered ideas.
Each idea must be on a separate line.

Return ONLY the 20 ideas.
"""

            result = generate(ideas_prompt)

            if result:

                parsed_ideas = []

                for line in result.splitlines():

                    line = line.strip()

                    if not line:
                        continue

                    match = re.match(
                        r"^\s*\d+\s*[\.\)\-:]\s*(.+)$",
                        line
                    )

                    if match:
                        idea = match.group(1).strip()

                        if idea:
                            parsed_ideas.append(idea)

                if len(parsed_ideas) >= 20:
                    parsed_ideas = parsed_ideas[:20]

                elif len(parsed_ideas) == 0:
                    parsed_ideas = [
                        line.strip()
                        for line in result.splitlines()
                        if line.strip()
                    ]

                st.session_state.movie_ideas = parsed_ideas
                st.session_state.selected_movie_idea = ""

                st.success(
                    f"{len(parsed_ideas)} movie ideas generated!"
                )


# ================= DISPLAY AND SELECT IDEAS =================

if st.session_state.movie_ideas:

    with st.container(border=True):

        st.markdown("### 🎬 YOUR MOVIE IDEAS")

        for index, idea in enumerate(
            st.session_state.movie_ideas,
            start=1
        ):
            st.markdown(f"**{index}.** {idea}")

        st.divider()

        st.markdown("### 👇 CHOOSE YOUR FAVORITE IDEA")

        selected_idea = st.selectbox(
            "Select one story idea:",
            options=["-- Select an idea --"] +
            st.session_state.movie_ideas,
            key="idea_selector"
        )

        if st.button(
            "✅ USE SELECTED IDEA",
            key="use_idea_btn"
        ):

            if selected_idea == "-- Select an idea --":
                st.warning("Please select an idea first.")

            else:
                st.session_state["story_idea_input"] = selected_idea
                st.session_state.selected_movie_idea = selected_idea

                st.success(
                    "Your selected idea has been added to Movie Story Idea!"
                )

        st.download_button(
            "⬇️ DOWNLOAD ALL 20 IDEAS",
            "\n".join(
                f"{i}. {idea}"
                for i, idea in enumerate(
                    st.session_state.movie_ideas,
                    start=1
                )
            ),
            file_name="20_movie_ideas.txt"
        )


# ================= MOVIE SETTINGS =================

st.divider()

st.markdown("## 🎥 MOVIE SETTINGS")

col1, col2 = st.columns(2)

with col1:

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


# ================= ASPECT RATIO =================

st.markdown("### 📐 SCENE ASPECT RATIO")

aspect_ratio = st.radio(
    "Select your video format:",
    options=["16:9", "9:16"],
    format_func=lambda x: (
        "16:9 — Landscape (YouTube)"
        if x == "16:9"
        else "9:16 — Portrait (Shorts / TikTok)"
    ),
    horizontal=True,
    key="aspect_ratio"
)


# ================= STORY IDEA =================

story_idea = st.text_area(
    "💡 Movie Story Idea",
    placeholder="Your selected idea will appear here. You can also write your own idea...",
    height=110,
    key="story_idea_input"
)


# ================= HERO AND VILLAIN =================

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
ASPECT RATIO: {aspect_ratio}

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

    if not title.strip():
        st.warning("Please enter your movie title first.")

    elif not story_idea.strip():
        st.warning("Please select a movie idea or write your own story idea.")

    else:

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

Follow the selected movie title and story idea carefully.
Do not replace the selected idea with a different story.

Keep the story internally consistent.
Do not introduce random characters or villains.

Write the complete movie story in professional English.

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
                
                # AUTO SAVE MOVIE PROJECT
                project_data = {
                    "story": st.session_state.story,
                    "characters": st.session_state.characters,
                    "scenes": st.session_state.scenes,
                    "scene_number": st.session_state.scene_number,
                    "movie_context": st.session_state.movie_context,
                    "movie_title": st.session_state.movie_title,
                    "aspect_ratio": st.session_state.aspect_ratio
                }

                localS.setItem(
                    SAVE_KEY,
                    json.dumps(project_data)
        )

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

Create a detailed and highly specific CHARACTER DESIGN BIBLE.

For every important character include:

1. Exact age and apparent age.
2. Face shape and facial features.
3. Skin tone and texture.
4. Exact eye color and distinctive eye features.
5. Hair color, length, texture and hairstyle.
6. Exact height and body structure.
7. Clothing, armor and footwear.
8. Accessories, jewelry and weapons.
9. Scars, marks, tattoos or unique physical details.
10. Personality and behavior.
11. Abilities and limitations.
12. Character purpose in the story.

For each character, write a complete LOCKED VISUAL DESCRIPTION
that can be copied directly into an independent AI video prompt.

IMPORTANT CHARACTER BIBLE RULES:

- Give each character a clearly distinct identity.
- Avoid vague descriptions.
- Do not leave important visual details undefined.
- Do not give the same appearance to different characters.
- Keep the design realistic and suitable for the selected visual style.
- Describe only characters that exist in the movie story.
- Include important creatures and recurring props in separate sections.
- Clearly identify permanent appearance details that must never change.

The CHARACTER BIBLE will be the permanent visual source of truth
for every scene generated later.

Write in professional English.
"""

            result = generate(prompt)

            if result:
                st.session_state.characters = result
                st.session_state.scenes = []
                st.session_state.scene_number = 0

                st.session_state.pop("thumbnail_bytes", None)

                # AUTO SAVE CHARACTER BIBLE
                project_data = {
                    "story": st.session_state.story,
                    "characters": st.session_state.characters,
                    "scenes": st.session_state.scenes,
                    "scene_number": st.session_state.scene_number,
                    "movie_context": st.session_state.movie_context,
                    "movie_title": st.session_state.movie_title,
                    "aspect_ratio": st.session_state.aspect_ratio
                }

                localS.setItem(
                    SAVE_KEY,
                    json.dumps(project_data)
                )

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

# ================= YOUTUBE THUMBNAIL GENERATOR =================

if st.session_state.story and st.session_state.characters:

    st.divider()

    st.markdown("## 🎬 04 — HOLLYWOOD THUMBNAIL STUDIO")

    st.write(
        "Create a professional cinematic YouTube thumbnail "
        "based on your movie story and locked characters."
    )

    if st.button(
        "🎨 GENERATE YOUTUBE THUMBNAIL",
        key="thumbnail_btn"
    ):

        st.session_state.pop("thumbnail_bytes", None)

        thumbnail_prompt = f"""
Create an extremely professional, clickable Hollywood movie
thumbnail for YouTube.

MOVIE TITLE:
{st.session_state.movie_title}

MOVIE STORY:
{st.session_state.story}

LOCKED CHARACTER DESIGN BIBLE:
{st.session_state.characters}

VISUAL REQUIREMENTS:

- Ultra-realistic Hollywood cinematic photography.
- Professional movie-poster composition.
- Powerful emotional expressions.
- Dramatic action and visual storytelling.
- Epic cinematic lighting.
- Preserve exact character appearances from the Character Bible.
- Show only characters and creatures that exist in the story.
- Create a visually exciting and instantly understandable scene.
- Strong foreground and background depth.
- Professional Hollywood color grading.
- No random characters.
- No watermarks or logos.
- No unwanted text.
- Wide landscape composition, 16:9 aspect ratio.
- Designed to attract YouTube viewers.

Create one premium-quality movie thumbnail.
"""

        try:

            with st.spinner(
                "Creating your Hollywood movie thumbnail..."
            ):

                response = client.models.generate_content(
                    model="gemini-3.1-flash-image",
                    contents=thumbnail_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(
                            aspect_ratio="16:9",
                            output_mime_type="image/png"
                        )
                    )
                )

                thumbnail_bytes = None

                for part in response.parts:

                    if part.inline_data:
                        thumbnail_bytes = part.inline_data.data
                        break

                if thumbnail_bytes:

                    st.session_state.thumbnail_bytes = thumbnail_bytes

                else:

                    st.error(
                        "Image was not generated. Please try again."
                    )

        except Exception as e:

            st.error(f"Thumbnail generation failed: {e}")

    if st.session_state.get("thumbnail_bytes"):

        st.markdown("### 🖼️ YOUR MOVIE THUMBNAIL")

        st.image(
            st.session_state.thumbnail_bytes,
            use_container_width=True
        )

        st.download_button(
            "⬇️ DOWNLOAD YOUTUBE THUMBNAIL",
            data=st.session_state.thumbnail_bytes,
            file_name="movie_thumbnail.png",
            mime="image/png"
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

                prompt = build_scene_prompt(
                    scene_number=1,
                    story=st.session_state.story,
                    characters=st.session_state.characters,
                    movie_context=st.session_state.movie_context,
                    scene_length=scene_length,
                    aspect_ratio=aspect_ratio
                )

                result = generate(prompt)

                if result:
                    st.session_state.scenes.append(result)
                    st.session_state.scene_number = 1

                    # AUTO SAVE GENERATED SCENES
                    project_data = {
                        "story": st.session_state.story,
                        "characters": st.session_state.characters,
                        "scenes": st.session_state.scenes,
                        "scene_number": st.session_state.scene_number,
                        "movie_context": st.session_state.movie_context,
                        "movie_title": st.session_state.movie_title,
                        "aspect_ratio": st.session_state.aspect_ratio
                    }

                    
                    localS.setItem(
                        SAVE_KEY,
                        json.dumps(project_data)
                    )

                    time.sleep(1.5)
                    st.rerun()
                 
                    

    # AUTO SAVE GENERATED SCENES
    project_data = {
        "story": st.session_state.story,
        "characters": st.session_state.characters,
        "scenes": st.session_state.scenes,
        "scene_number": st.session_state.scene_number,
        "movie_context": st.session_state.movie_context,
        "movie_title": st.session_state.movie_title,
        "aspect_ratio": st.session_state.aspect_ratio
    }



if st.session_state.scenes:

    current = st.session_state.scenes[-1]

    with st.container(border=True):

        st.markdown(
            f"### 🎞️ SCENE {st.session_state.scene_number}"
        )

        st.code(
            current,
            language=None
        )

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

                prompt = build_scene_prompt(
                    scene_number=st.session_state.scene_number + 1,
                    story=st.session_state.story,
                    characters=st.session_state.characters,
                    movie_context=st.session_state.movie_context,
                    scene_length=scene_length,
                    aspect_ratio=aspect_ratio,
                    previous_scene=previous
                )

                result = generate(prompt)

                if result:
                    st.session_state.scenes.append(result)
                    st.session_state.scene_number += 1
                    st.rerun()

    else:

        st.success(
            "🎉 All planned movie scenes have been generated successfully!"
        )

    # ================= DOWNLOAD ALL SCENES =================

    all_scenes_text = "\n\n".join(
        f"================ SCENE {index} ================\n\n{scene}"
        for index, scene in enumerate(
            st.session_state.scenes,
            start=1
        )
    )

    st.download_button(
        "⬇️ DOWNLOAD ALL GENERATED SCENES",
        all_scenes_text,
        file_name="all_movie_scenes.txt",
        mime="text/plain"
    )


# ================= PROJECT PROGRESS =================

if st.session_state.story:

    st.divider()
    st.markdown("### 📊 MOVIE PROJECT PROGRESS")

    progress = min(
        len(st.session_state.scenes) / max(scene_count, 1),
        1.0
    )

    st.progress(progress)

    st.write(
        f"Generated {len(st.session_state.scenes)} "
        f"out of {scene_count} planned scenes."
    )


# ================= RESET PROJECT =================

st.divider()

st.markdown("## 🔄 PROJECT CONTROLS")

if st.button("🗑️ RESET ENTIRE MOVIE PROJECT", key="reset_project"):

    keys_to_reset = [
        "story",
        "characters",
        "scenes",
        "scene_number",
        "movie_context",
        "movie_ideas",
        "selected_movie_idea",
        "story_idea_input"
    ]

    for key in keys_to_reset:
        if key in st.session_state:
            if key == "scenes" or key == "movie_ideas":
                st.session_state[key] = []
            elif key == "scene_number":
                st.session_state[key] = 0
            else:
                st.session_state[key] = ""

    st.rerun()
