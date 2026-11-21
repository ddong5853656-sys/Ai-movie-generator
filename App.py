import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="AI Movie Prompt Generator",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 AI Movie Prompt Generator")
st.caption("Hollywood-style cinematic stories and AI video prompts")

with st.sidebar:
    st.header("AI Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    model = st.text_input("AI Model", value="gpt-4o-mini")

    st.divider()
    character_lock = st.checkbox(
        "Character consistency lock",
        value=True
    )
    cinematic_style = st.checkbox(
        "Photorealistic Hollywood style",
        value=True
    )
    sparse_dialogue = st.checkbox(
        "Sparse purposeful dialogue",
        value=True
    )


def generate(prompt):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        return None

    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Hollywood movie writer, "
                        "character designer and cinematic AI video "
                        "prompt engineer. Create original, detailed, "
                        "professional cinematic content."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8
        )

        return response.choices[0].message.content

    except Exception as e:
        st.error(f"Error: {e}")
        return None


st.header("1. Movie Setup")

col1, col2, col3 = st.columns(3)

with col1:
    movie_title = st.text_input(
        "Movie Title",
        "THE LAST SUNRISE"
    )

    genre = st.selectbox(
        "Movie Genre",
        [
            "Sci-Fi Action",
            "Fantasy Action",
            "Survival",
            "Adventure",
            "Mystery Thriller",
            "Horror",
            "Action",
            "Custom"
        ]
    )

with col2:
    duration = st.selectbox(
        "Story Duration",
        [
            "5 minutes",
            "10 minutes",
            "15 minutes",
            "20 minutes",
            "30 minutes",
            "45 minutes",
            "60 minutes"
        ]
    )

    environment = st.selectbox(
        "Environment",
        [
            "Futuristic Earth",
            "Jungle",
            "Desert",
            "Mountains",
            "Island",
            "Ocean",
            "Ancient World",
            "Multiple Locations"
        ]
    )

with col3:
    scene_duration = st.selectbox(
        "Scene Duration",
        ["10 seconds", "15 seconds", "20 seconds"]
    )

    visual_style = st.selectbox(
        "Visual Style",
        [
            "Photorealistic Hollywood",
            "Epic Cinematic Realism",
            "Grounded Realistic Action"
        ]
    )

story_idea = st.text_area(
    "Story Idea",
    height=120,
    value=(
        "In the future, Earth's natural sun begins to dim. "
        "Humanity builds an artificial sun, but a ruthless "
        "industrial ruler takes control of its energy."
    )
)

hero_details = st.text_area(
    "Hero / Heroine Details",
    placeholder="Age, appearance, clothing, personality, powers..."
)

villain_details = st.text_area(
    "Villain Details",
    placeholder="Appearance, motivation, powers and purpose..."
)

extra_instructions = st.text_area(
    "Additional Instructions",
    placeholder="Anything else you want in your movie..."
)

movie_context = f"""
MOVIE TITLE: {movie_title}
GENRE: {genre}
DURATION: {duration}
ENVIRONMENT: {environment}
SCENE LENGTH: {scene_duration}
VISUAL STYLE: {visual_style}

STORY IDEA:
{story_idea}

HERO:
{hero_details}

VILLAIN:
{villain_details}

ADDITIONAL INSTRUCTIONS:
{extra_instructions}

CHARACTER CONSISTENCY:
{character_lock}

CINEMATIC STYLE:
{cinematic_style}

DIALOGUE:
{sparse_dialogue}
"""

if "story" not in st.session_state:
    st.session_state.story = ""

if "characters" not in st.session_state:
    st.session_state.characters = ""

if "scenes" not in st.session_state:
    st.session_state.scenes = []

if "scene_number" not in st.session_state:
    st.session_state.scene_number = 0


st.divider()
st.header("2. Generate Complete Movie Story")

if st.button(
    "✨ Generate Movie Story",
    type="primary",
    use_container_width=True
):

    prompt = movie_context + """

Create an original Hollywood-style cinematic movie story.

Include:

1. Powerful opening hook
2. Main characters
3. Character motivations
4. Central conflict
5. Suspense and action escalation
6. Original twists
7. Emotional moments
8. Multiple interesting locations
9. Powerful climax
10. Satisfying ending

Write a detailed story outline suitable for the selected duration.

Do NOT generate individual video scenes yet.
"""

    result = generate(prompt)

    if result:
        st.session_state.story = result
        st.session_state.characters = ""
        st.session_state.scenes = []
        st.session_state.scene_number = 0


if st.session_state.story:

    st.subheader("📖 Movie Story")

    st.markdown(st.session_state.story)

    st.download_button(
        "Download Story",
        st.session_state.story,
        file_name="movie_story.txt"
    )


st.divider()
st.header("3. Character Design Bible")

if st.button(
    "👥 Generate Character Designs",
    use_container_width=True
):

    if not st.session_state.story:
        st.warning("First generate your movie story.")

    else:

        prompt = movie_context + f"""

MOVIE STORY:

{st.session_state.story}

Create a detailed character design bible.

For every important character include:

- Exact age
- Facial appearance
- Hair
- Eyes
- Skin texture
- Body type
- Clothing
- Footwear
- Accessories
- Personality
- Abilities
- Weapons
- Movement style
- Character purpose

Create a short LOCKED VISUAL DESCRIPTION for each character.

Characters must look exactly the same in every scene.

Also describe important creatures, vehicles and props.
"""

        result = generate(prompt)

        if result:
            st.session_state.characters = result


if st.session_state.characters:

    st.subheader("Character Bible")

    st.markdown(st.session_state.characters)

    st.download_button(
        "Download Character Bible",
        st.session_state.characters,
        file_name="character_bible.txt"
    )


st.divider()
st.header("4. Generate Cinematic Video Scenes")

st.info(
    "Generate one scene at a time. "
    "Each new scene continues from the previous scene's ending."
)

if st.session_state.story:

    if st.button(
        "🎥 Generate Scene 1",
        type="primary",
        use_container_width=True
    ):

        prompt = movie_context + f"""

MOVIE STORY:

{st.session_state.story}

CHARACTER BIBLE:

{st.session_state.characters}

Generate SCENE 1 ONLY.

The scene must be exactly {scene_duration}.

Include:

- Scene number
- Scene title
- Exact location
- Time and weather
- Atmosphere
- Character appearance
- Character screen positions
- Body direction
- Camera angle
- Lens perspective
- Camera movement
- Second-by-second action
- Realistic action and reactions
- Important dialogue only
- Exact final frame

Do not make characters look directly into the camera.

The final frame must be suitable for direct continuation
into Scene 2.

Return only the cinematic video prompt.
"""

        result = generate(prompt)

        if result:
            st.session_state.scenes = [result]
            st.session_state.scene_number = 1


if st.session_state.scenes:

    current_scene = st.session_state.scenes[-1]

    st.subheader(
        f"🎞️ Scene {st.session_state.scene_number}"
    )

    st.markdown(current_scene)

    st.download_button(
        "Download Current Scene",
        current_scene,
        file_name=f"scene_{st.session_state.scene_number}.txt"
    )

    scene_count = int(
        duration.split()[0]
    ) * 60 // int(
        scene_duration.split()[0]
    )

    if st.session_state.scene_number < scene_count:

        if st.button(
            "➡️ Generate Next Scene",
            type="primary",
            use_container_width=True
        ):

            previous_scene = st.session_state.scenes[-1]

            prompt = movie_context + f"""

MOVIE STORY:

{st.session_state.story}

CHARACTER BIBLE:

{st.session_state.characters}

PREVIOUS SCENE:

{previous_scene}

Generate SCENE {st.session_state.scene_number + 1} ONLY.

CONTINUITY RULES:

- Continue directly from the exact previous final frame.
- Maintain the same character faces.
- Maintain exact hair, clothes and accessories.
- Maintain injuries and physical condition.
- Maintain props and weapons.
- Maintain location unless the story shows a transition.
- Do not repeat the previous scene.
- Advance the story naturally.
- Specify camera angle and movement.
- Specify character positions and directions.
- Include second-by-second action.
- Dialogue must be sparse and purposeful.
- No characters looking directly at the camera.
- No unexplained teleporting or transformations.
- End with an exact final frame for the next scene.

Return only the cinematic video prompt.
"""

            result = generate(prompt)

            if result:
                st.session_state.scenes.append(result)
                st.session_state.scene_number += 1
                st.rerun()


if len(st.session_state.scenes) > 1:

    all_scenes = "\n\n".join(
        [
            f"SCENE {i+1}\n{scene}"
            for i, scene in enumerate(
                st.session_state.scenes
            )
        ]
    )

    st.download_button(
        "📦 Download All Generated Scenes",
        all_scenes,
        file_name="movie_scenes.txt"
    )


st.divider()

if st.button("🔄 Reset Movie Project"):

    st.session_state.story = ""
    st.session_state.characters = ""
    st.session_state.scenes = []
    st.session_state.scene_number = 0

    st.rerun()


st.caption(
    "AI API usage may incur charges. "
    "Your API key is used during this session."
)
