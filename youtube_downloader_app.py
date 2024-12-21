import streamlit as st
import yt_dlp
import os
from yt_dlp.utils import DownloadError

# Initialize session state variables
if 'progress_bar' not in st.session_state:
    st.session_state['progress_bar'] = None
if 'status_text' not in st.session_state:
    st.session_state['status_text'] = None
if 'is_downloading' not in st.session_state:
    st.session_state['is_downloading'] = False

# Progress hook function
def progress_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes', 1)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        speed = d.get('speed', 0)
        eta = d.get('eta', 0)

        speed_text = f"{speed / 1e6:.2f} MB/s" if speed else "Calculating..."
        eta_text = f"{eta:.2f} seconds" if eta else "Calculating..."

        progress = min(downloaded_bytes / total_bytes, 1.0)

        if st.session_state['progress_bar']:
            st.session_state['progress_bar'].progress(progress)
        if st.session_state['status_text']:
            st.session_state['status_text'].text(
                f"Downloaded: {downloaded_bytes / 1e6:.2f} MB\n"
                f"Speed: {speed_text}\nETA: {eta_text}"
            )
    elif d['status'] == 'finished':
        if st.session_state['status_text']:
            st.session_state['status_text'].text("Download complete!")

# Video downloader function
def download_video(link, file_path):
    try:
        ydl_opts = {
            'outtmpl': file_path,
            'format': "bv*[height<=1080]+ba/b",
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([link])

        return file_path
    except DownloadError as e:
        raise Exception(f"Download failed: {e}")

# Streamlit App
def main():
    st.markdown(
        """
        <style>
        body {
            background-color: #f5f5f5;
            font-family: Arial, sans-serif;
        }
        .title {
            text-align: center;
            font-size: 2.5rem;
            color: #4CAF50;
            margin-bottom: 20px;
            animation: fadeIn 2s;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .spinner {
            margin: 20px auto;
            width: 40px;
            height: 40px;
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-top-color: #4CAF50;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        </style>
        <div class="title">🎥 YouTube Video Downloader</div>
        """,
        unsafe_allow_html=True,
    )

    st.write(":rainbow[Download YouTube videos in 1080p resolution]")

    link = st.text_input("Enter YouTube Video Link")
    file_name = st.text_input("Enter a File Name")
    download_path = st.text_input(
        "Enter Download Path",
        value=str(os.path.expanduser("~/Downloads"))
    )

    if st.session_state['is_downloading']:
        st.button("Downloading...", disabled=True)
    else:
        if st.button("Download Video"):
            if not link:
                st.error("Please provide a YouTube video link.")
            elif not file_name:
                st.error("Please specify a file name for the video.")
            elif not download_path:
                st.error("Please specify a valid download path.")
            else:
                try:
                    file_path = os.path.join(download_path, f"{file_name}.mp4")

                    st.session_state['progress_bar'] = st.empty()
                    st.session_state['status_text'] = st.empty()
                    st.session_state['is_downloading'] = True

                    with st.spinner("Downloading..."):
                        downloaded_file = download_video(link, file_path)

                    st.success("Video downloaded successfully!")
                    st.info(f"File saved at: {downloaded_file}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                finally:
                    st.session_state['is_downloading'] = False

if __name__ == "__main__":
    main()
