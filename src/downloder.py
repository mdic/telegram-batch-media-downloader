import asyncio
import os
from dotenv import load_dotenv
from colorama import Fore, Style
from tqdm.asyncio import tqdm
from telethon import TelegramClient
from telethon.tl.types import (
    DocumentAttributeFilename,
    InputMessagesFilterVideo,
    InputMessagesFilterPhotos,
    InputMessagesFilterDocument,
)

# Load environment variables
load_dotenv()

# Retrieve values from .env
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
session_name = os.getenv("SESSION_NAME", "default_session")
batch_size = int(os.getenv("BATCH_SIZE", 5))


async def download_file(message, folder_name, progress_bars):
    try:
        # Get the file size
        file_size = (
            message.video.size
            if message.video
            else message.document.size if message.document else 0
        )

        # Initialize the progress bar
        progress_bar = tqdm(
            total=file_size,
            desc=f"Downloading {message.id}",
            ncols=100,
            unit="B",
            unit_scale=True,
            leave=True,  # Keep progress bar visible after completion
            bar_format=(
                "{l_bar}%s{bar}%s| {n_fmt}/{total_fmt} {unit} "
                "| Elapsed: {elapsed}/{remaining} | {rate_fmt}"
                % (Fore.BLUE, Style.RESET_ALL)
            ),
        )
        progress_bars.append(progress_bar)

        # Download media with progress
        await message.download_media(
            file=f"./{folder_name}/",
            progress_callback=lambda current, total: (
                progress_bar.update(current - progress_bar.n) if total else None
            ),
        )

        # After download finishes, change the color to green
        progress_bar.bar_format = (
            "{l_bar}%s{bar}%s| {n_fmt}/{total_fmt} {unit} "
            "| Elapsed: {elapsed}/{rate_fmt}" % (Fore.GREEN, Style.RESET_ALL)
        )
        progress_bar.set_description(f"Finished {message.id}")
        progress_bar.n = progress_bar.total  # Ensure the progress bar shows 100%
        progress_bar.update(0)  # Force update to display the changes

    except Exception as e:
        print(f"Error downloading media: {e}")


async def download_in_batches(messages, folder_name, batch_size):
    tasks = []
    progressbar = []
    for i, message in enumerate(messages, 1):
        # tasks.append(download_file(message, folder_name))
        tasks.append(download_file(message, folder_name, progressbar))
        # Run in batches of batch_size
        if len(tasks) == batch_size or i == len(messages):
            await asyncio.gather(*tasks)
            tasks.clear()  # Clear tasks after each batch


async def main():
    async with TelegramClient(session_name, api_id, api_hash) as client:
        print(f"{Fore.GREEN}Connected successfully!{Style.RESET_ALL}")
        channel_username = input(
            f"{Fore.CYAN}Enter the channel name or username: {Style.RESET_ALL}"
        )
        # Get the channel entity
        channel = await client.get_entity(channel_username)
        print(
            f"{Fore.YELLOW}Fetched channel: {channel.title} (ID: {channel.id}){Style.RESET_ALL}"
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
