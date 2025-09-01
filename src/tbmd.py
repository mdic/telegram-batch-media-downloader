import asyncio
import os
import re
import mimetypes
from dotenv import load_dotenv
from colorama import Fore, Style
from tqdm.asyncio import tqdm
from telethon import TelegramClient
from telethon.tl.types import (
    InputMessagesFilterVideo,
    InputMessagesFilterPhotos,
    InputMessagesFilterDocument,
    PeerChannel,
    PeerChat,
    PeerUser,
)

# Load environment variables
load_dotenv()

# Retrieve values from .env
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME", "default_session")
batch_size = int(os.getenv("BATCH_SIZE", 5))


def safe_filename(name: str, default_ext: str = ""):
    """Remove invalid characters from filenames and apply extension if missing."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    if default_ext and not name.endswith(default_ext):
        name += default_ext
    return name


def guess_extension(message):
    """Return the correct extension based on MIME type or media type."""
    if message.document and message.document.mime_type:
        ext = mimetypes.guess_extension(message.document.mime_type)
        if ext:
            return ext
    # fallback if MIME not available
    if message.video:
        return ".mp4"
    if message.photo:
        return ".jpg"
    return ""


async def download_file(message, folder_name, progress_bars):
    try:
        # Get the file size
        file_size = (
            message.video.size
            if message.video
            else message.document.size
            if message.document
            else 0
        )

        # Progress bar
        progress_bar = tqdm(
            total=file_size,
            desc=f"Downloading {message.id}",
            ncols=100,
            unit="B",
            unit_scale=True,
            leave=True,
            bar_format=(
                "{l_bar}%s{bar}%s| {n_fmt}/{total_fmt} {unit} "
                "| Elapsed: {elapsed}/{remaining} | {rate_fmt}"
                % (Fore.BLUE, Style.RESET_ALL)
            ),
        )
        progress_bars.append(progress_bar)

        # Decide custom filename if caption exists
        custom_name = None
        if message.text:  # caption presente
            ext = guess_extension(message)
            custom_name = safe_filename(message.text.strip(), ext)

        # Destination path
        if custom_name:
            dest = os.path.join("downloads", folder_name, custom_name)
        else:
            dest = f"./downloads/{folder_name}/"

        # Download
        await message.download_media(
            file=dest,
            progress_callback=lambda current, total: (
                progress_bar.update(current - progress_bar.n) if total else None
            ),
        )

        # After download finishes, update bar
        progress_bar.bar_format = (
            "{l_bar}%s{bar}%s| {n_fmt}/{total_fmt} {unit} "
            "| Elapsed: {elapsed}/{rate_fmt}" % (Fore.GREEN, Style.RESET_ALL)
        )
        progress_bar.set_description(f"Finished {message.id}")
        progress_bar.n = progress_bar.total
        progress_bar.update(0)

    except Exception as e:
        print(f"Error downloading media: {e}")


async def download_in_batches(messages, folder_name, batch_size):
    tasks = []
    progressbar = []
    for i, message in enumerate(messages, 1):
        tasks.append(download_file(message, folder_name, progressbar))
        # Run in batches of batch_size
        if len(tasks) == batch_size or i == len(messages):
            await asyncio.gather(*tasks)
            tasks.clear()


async def main():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print(f"{Fore.GREEN}Connected successfully!{Style.RESET_ALL}")
        chat_input = input(
            f"{Fore.CYAN}Enter the channel name or username: {Style.RESET_ALL}"
        )
        # Get the channel entity
        # OLD strategy failing with entity ID
        # if chat_input.isdigit():
        #     chat_id = int(chat_input)
        #     try:
        #         channel = await client.get_entity(PeerChannel(chat_id))
        #     except ValueError:
        #         try:
        #             channel = await client.get_entity(PeerChat(chat_id))
        #         except ValueError:
        #             channel = await client.get_entity(PeerUser(chat_id))
        # else:
        #     channel = await client.get_entity(chat_input)

        # Strategy for entity ID correct processing
        # MAY BREAK OTHER THINGS, but need to test it!
        # ::TODO::
        if chat_input.isdigit():
            chat_id = int(chat_input)
            channel = await client.get_entity(chat_id)
        else:
            channel = await client.get_entity(chat_input)

        # Strategy with entity ID

        print(
            f"{Fore.YELLOW}Fetched channel: {channel.title if hasattr(channel, 'title') else 'Private Chat'} "
            f"(ID: {channel.id}){Style.RESET_ALL}"
        )

        # Prompt the user for their choice
        print(
            f"{Fore.CYAN}Choose the type of content to download:{Style.RESET_ALL}\n"
            f"1. Images\n"
            f"2. Videos\n"
            f"3. PDFs\n"
            f"4. ZIP files\n"
            f"5. All types\n"
        )
        choice = input(f"{Fore.CYAN}Enter your choice (1-5): {Style.RESET_ALL}")

        folder_name = ""
        filter_type = None

        if choice == "1":
            filter_type = InputMessagesFilterPhotos()
            folder_name = "images"
        elif choice == "2":
            filter_type = InputMessagesFilterVideo()
            folder_name = "videos"
        elif choice in ["3", "4"]:
            filter_type = InputMessagesFilterDocument()
            folder_name = "pdfs" if choice == "3" else "zips"
        elif choice == "5":
            filter_type = None
            folder_name = "all_media"
        else:
            print(f"{Fore.RED}Invalid choice! Exiting...{Style.RESET_ALL}")
            return

        download_path = f"downloads/{folder_name}"
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        print(f"{Fore.YELLOW}Fetching media messages...{Style.RESET_ALL}")
        media_messages = await client.get_messages(
            channel, filter=filter_type, limit=2000
        )

        if choice == "3":
            media_messages = [
                msg
                for msg in media_messages
                if msg.document and msg.document.mime_type == "application/pdf"
            ]
        elif choice == "4":
            media_messages = [
                msg
                for msg in media_messages
                if msg.document and msg.document.mime_type == "application/zip"
            ]

        print(f"Found {len(media_messages)} messages matching your choice.")

        if media_messages:
            await download_in_batches(media_messages, folder_name, batch_size)
        else:
            print(f"{Fore.RED}No media found for the selected type.{Style.RESET_ALL}")


if __name__ == "__main__":
    asyncio.run(main())
