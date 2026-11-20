
import streamlit as st
import requests
import time

st.set_page_config(
    page_title="AI Video Studio",
    page_icon="🎬",
    layout="wide"
)

API_URL = "https://apihub.agnes-ai.com/v1/videos"
STATUS_URL = "https://apihub.agnes-ai.com/agnesapi"

MODEL_NAME = "agnes-video-2.5-flash"

st.markdown("""
<style>
.stApp {
    background: linear-gradient(
        135deg,
        #1A1420,
        #302317,
        #17130D
    );
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

.stButton > button {
    background: linear-gradient(
        135deg,
        #D4AF37,
        #FFD700,
        #C99700
    );
    color: #171717;
    border-radius: 12px;
    border: 1px solid #E6C65C;
    height: 48px;
    font-weight: bold;
}

.stButton > button:hover {
    background: linear-gradient(
        135deg,
        #FFE55C,
        #FFD700
    );
    color: black;
}

.stDownloadButton > button {
    background: linear-gradient(
        135deg,
        #D4AF37,
        #FFD700
    );
    color: black;
    border-radius: 12px;
    font-weight: bold;
    border: none;
}

.stDownloadButton > button:hover {
    background: #FFE55C;
    color: black;
}

textarea {
    background-color: #123A73 !important;
    color: white !important;
    border: 2px solid #4A90E2 !important;
    border-radius: 12px !important;
}

textarea::placeholder {
    color: #D6E8FF !important;
}

input {
    border-radius: 8px !important;
}

.stProgress > div > div {
    background-color: #FFD700;
}

section[data-testid="stSidebar"] {
    background: #211A25;
}
</style>
""", unsafe_allow_html=True)

st.title("🎬 AI VIDEO STUDIO")

st.caption(
    "Create cinematic AI videos with Agnes AI"
)

with st.sidebar:

    st.header("⚙️ Settings")

    api_key = st.secrets.get(
        "AGNES_API_KEY",
        ""
    )

    st.caption("Model: Agnes Video 2.5 Flash")
    st.caption("Video duration: 5 seconds")
    st.caption("Resolution: 720P")
    st.caption("Aspect ratio: 16:9")

st.divider()

st.subheader("Create Your Video")

prompt = st.text_area(
    "Describe your video",
    placeholder="A cinematic scene of a warrior walking through a mysterious jungle...",
    height=150
)

prompt_optimizer = st.toggle(
    "AI Prompt Optimizer",
    value=True
)

if st.button(
    "✨ GENERATE VIDEO",
    use_container_width=True
):

    if not api_key.strip():

        st.error(
            "Agnes API key is missing. "
            "Add it in Streamlit Secrets."
        )

    elif not prompt.strip():

        st.error(
            "Please enter a video prompt."
        )

    else:

        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL_NAME,
            "prompt": prompt.strip(),
            "mode": "text",
            "seconds": "5",
            "size": "720P",
            "aspect_ratio": "16:9",
            "n": 1
        }

        try:

            with st.spinner(
                "Submitting video request..."
            ):

                response = requests.post(
                    API_URL,
                    headers=headers,
                    json=payload,
                    timeout=90
                )

            if response.status_code not in (
                200,
                201,
                202
            ):

                st.error(
                    f"Agnes API Error: "
                    f"{response.status_code}"
                )

                st.code(response.text)

            else:

                project = response.json()

                video_id = project.get("video_id")

                if not video_id:
                    video_id = project.get("id")

                if not video_id:
                    video_id = project.get("task_id")

                if not video_id:

                    st.error(
                        "No video ID returned by Agnes."
                    )

                    st.code(str(project))

                else:

                    progress = st.progress(0)

                    status_text = st.empty()

                    start_time = time.time()

                    video_url = None

                    while True:

                        elapsed = int(
                            time.time() - start_time
                        )

                        progress.progress(
                            min(
                                int(elapsed / 600 * 95),
                                95
                            )
                        )

                        status_text.info(
                            f"Generating video... "
                            f"{elapsed} seconds"
                        )

                        if elapsed > 900:

                            st.error(
                                "Generation is taking too long. "
                                "Please check your Agnes project."
                            )

                            break

                        time.sleep(5)

                        check = requests.get(
                            STATUS_URL,
                            headers=headers,
                            params={
                                "video_id": video_id,
                                "model_name": MODEL_NAME
                            },
                            timeout=30
                        )

                        if check.status_code not in (
                            200,
                            201
                        ):

                            st.error(
                                f"Agnes status error: "
                                f"{check.status_code}"
                            )

                            st.code(check.text)

                            break

                        result = check.json()

                        status = result.get(
                            "status",
                            ""
                        ).lower()

                        if status == "completed":

                            video_url = result.get("url")

                            if not video_url:

                                metadata = result.get(
                                    "metadata",
                                    {}
                                )

                                video_url = metadata.get(
                                    "url"
                                )

                            if not video_url:

                                downloads = result.get(
                                    "downloads",
                                    []
                                )

                                if downloads:

                                    if isinstance(
                                        downloads[0],
                                        dict
                                    ):

                                        video_url = (
                                            downloads[0].get("url")
                                        )

                                    else:

                                        video_url = downloads[0]

                            break

                        elif status in (
                            "failed",
                            "error",
                            "canceled"
                        ):

                            st.error(
                                "Video generation failed."
                            )

                            st.code(str(result))

                            break

                    if video_url:

                        progress.progress(100)

                        status_text.success(
                            "Your video is ready!"
                        )

                        video_response = requests.get(
                            video_url,
                            timeout=180
                        )

                        video_response.raise_for_status()

                        video_bytes = (
                            video_response.content
                        )

                        st.video(video_bytes)

                        st.download_button(
                            "⬇️ Download Video",
                            data=video_bytes,
                            file_name="ai_video.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )

                    elif not status_text:

                        st.warning(
                            "Video URL was not returned."
                        )

        except requests.exceptions.RequestException as error:

            st.error(
                "Connection error with Agnes AI."
            )

            st.code(str(error))

        except Exception as error:

            st.error(
                "Something went wrong."
            )

            st.code(str(error))

st.divider()

st.caption(
    "Powered by Agnes AI • Video 2.5 Flash"
      )
                  
