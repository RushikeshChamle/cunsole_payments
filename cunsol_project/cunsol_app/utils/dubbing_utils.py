# dubbing/utils/dubbing_utils.py

import os
import time
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()

# Retrieve the API key
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError(
        "ELEVENLABS_API_KEY environment variable not found. "
        "Please set the API key in your environment variables."
    )

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def download_dubbed_file(dubbing_id: str, language_code: str) -> str:
    dir_path = f"data/{dubbing_id}"
    os.makedirs(dir_path, exist_ok=True)
    file_path = f"{dir_path}/{language_code}.mp4"
    with open(file_path, "wb") as file:
        for chunk in client.dubbing.get_dubbed_file(dubbing_id, language_code):
            file.write(chunk)
    return file_path

def wait_for_dubbing_completion(dubbing_id: str) -> bool:
    MAX_ATTEMPTS = 120
    CHECK_INTERVAL = 10  # In seconds
    for _ in range(MAX_ATTEMPTS):
        metadata = client.dubbing.get_dubbing_project_metadata(dubbing_id)
        if metadata.status == "dubbed":
            return True
        elif metadata.status == "dubbing":
            time.sleep(CHECK_INTERVAL)
        else:
            return False
    return False
