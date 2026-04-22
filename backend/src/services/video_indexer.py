import os
import time
import yt_dlp
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiVideoProcessor:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in .env file")
        genai.configure(api_key=api_key)

    def download_youtube_video(self, url: str, output_path: str = "temp_video.mp4"):
        print(f"Downloading video stream from {url}...")

        ydl_opts = {
            'format': 'best[ext=mp4]/best', 
            'outtmpl': output_path,
            'quiet': True,
            'no_warnings': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return output_path
        except Exception as e:
            raise RuntimeError(f"yt-dlp failed to download the video: {e}")

    def process_video(self, url: str) -> str:
        video_path = "temp_video.mp4"
        uploaded_file = None

        try:
            video_path = self.download_youtube_video(url, video_path)

            print("Uploading video to Gemini...")
            uploaded_file = genai.upload_file(path=video_path)

            print("Waiting for processing", end="")
            while uploaded_file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)

            print("\nVideo processed")

            print("Extracting content...")
            model = genai.GenerativeModel(model_name="gemini-3.1-flash-lite-preview")

            prompt = """
            You are a video indexing system. Analyze this video and extract:

            1. TRANSCRIPT: Detailed summary of spoken content
            2. ON-SCREEN TEXT: Any visible text, disclaimers, brands
            3. KEY CLAIMS: Sponsorships, health claims, guarantees, financial advice

            Format clearly for compliance analysis.
            """

            response = model.generate_content([uploaded_file, prompt])
            return response.text

        except Exception as e:
            print(f"Error during video processing: {e}")
            return f"Error extracting video data: {e}"

        finally:
            if uploaded_file:
                try:
                    genai.delete_file(uploaded_file.name)
                except:
                    pass
            if os.path.exists(video_path):
                os.remove(video_path)