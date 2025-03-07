import os
from typing import Optional

from dotenv import load_dotenv
from dubbing_utils import download_dubbed_file, wait_for_dubbing_completion
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


def create_dub_from_url(
    source_url: str,
    source_language: str,
    target_language: str,
) -> Optional[str]:
    """
    Downloads a video from a URL, and creates a dubbed version in the target language.

    Args:
        source_url (str): The URL of the source video to dub. Can be a YouTube link, TikTok, X (Twitter) or a Vimeo link.
        source_language (str): The language of the source video.
        target_language (str): The target language to dub into.

    Returns:
        Optional[str]: The file path of the dubbed file or None if operation failed.
    """

    response = client.dubbing.dub_a_video_or_an_audio_file(
    source_url=source_url, # URL of the source video/audio file.
    target_lang=target_language, # The Target language to dub the content into. Can be none if dubbing studio editor is enabled and running manual mode
    mode="automatic", # automatic or manual.
    source_lang=source_language, # Source language.
    num_speakers=1, # Number of speakers to use for the dubbing.
    watermark=True,  # Whether to apply watermark to the output video.
    )

    dubbing_id = response.dubbing_id
    if wait_for_dubbing_completion(dubbing_id):
        output_file_path = download_dubbed_file(dubbing_id, target_language)
        return output_file_path
    else:
        return None


if __name__ == "__main__":
    source_url = "https://youtu.be/4Vw8t9oYoQo?si=bB4SjWh5Tk5dZCcf"  # Charlie bit my finger
    source_language = "en"
    target_language = "hi"
    result = create_dub_from_url(source_url, source_language, target_language)
    if result:
        print("Dubbing was successful! File saved at:", result)
    else:
        print("Dubbing failed or timed out.")