import streamlit as st
import yt_dlp
from yt_dlp.utils import DownloadError
import pathlib
import os

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
    st.header("🎥 YouTube Video Downloader For PC & Laptops")

    st.write("Download YouTube videos in 1080p resolution")

    link = st.text_input("Enter YouTube Video Link")
    file_name = st.text_input("Enter a File Name")
    download_path = st.text_input("Download Path (e.g., C:\\Users\\YourUsername\\Downloads)")

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
                    # Resolve and create the download path
                    download_path_obj = pathlib.Path(download_path).resolve()
                    if not download_path_obj.exists():
                        download_path_obj.mkdir(parents=True, exist_ok=True)

                    file_path = str(download_path_obj / f"{file_name}.mp4")

                    # Check if the file already exists
                    if os.path.exists(file_path):
                        st.error("A file with this name already exists. Please choose a different file name.")
                    else:
                        st.session_state['progress_bar'] = st.empty()
                        st.session_state['status_text'] = st.empty()
                        st.session_state['is_downloading'] = True

                        with st.spinner("Downloading..."):
                            downloaded_file = download_video(link, file_path)

                        # Verify file existence
                        if os.path.exists(downloaded_file):
                            st.success("Video downloaded successfully!")
                            st.info(f"File saved at: {downloaded_file}")
                        else:
                            st.error("Download completed, but file not found at the specified location.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                finally:
                    st.session_state['is_downloading'] = False

if __name__ == "__main__":
    main()
