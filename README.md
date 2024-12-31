# Telegram Bulk Media Downloader

Telegram Bulk Media Downloader is a Python-based tool that allows users to download various types of media files (videos, images, PDFs, ZIPs, etc.) from Telegram channels and groups. The downloader supports resumable downloads, batch processing, and progress tracking, making it ideal for managing large volumes of media efficiently.

## Features

-   **Resumable Downloads**: Automatically resumes downloads from where they stopped.
-   **Batch Processing**: Downloads media in configurable batches for better resource management.
-   **Multi-Media Support**: Supports videos, images, PDFs, ZIP files, and more.
-   **Progress Tracking**: Displays detailed progress bars for each download.
-   **Configurable Settings**: Easily customizable batch size and session settings via `.env` file.
-   **Cross-Platform**: Runs on Windows, macOS, and Linux.
-   **Lightweight**: Requires only Python and a few libraries to run.

## Requirements

-   Python 3.8+
-   Telegram API credentials (API ID and API Hash)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/vinodkr494/telegram-media-downloader.git
    cd telegram-media-downloader
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file and configure it:

    ```env
    API_ID=your_api_id
    API_HASH=your_api_hash
    SESSION_NAME=default_session
    BATCH_SIZE=5
    ```

4. Run the script:
    ```bash
    python src/downloader.py
    ```

## Usage

1. **Start the script**:

    ```bash
    python src/downloader.py
    ```

2. Enter the Telegram channel username or group link when prompted.

3. Select the type of media to download (e.g., videos, images, PDFs).

4. Watch as your files are downloaded with detailed progress bars!

## Advanced Configuration

### Resuming Downloads

The downloader automatically saves the progress of completed files in a `download_state.json` file. To resume downloads, simply restart the script, and it will skip already downloaded files.

### Batch Size

To adjust the number of files downloaded in parallel, update the `BATCH_SIZE` value in the `.env` file.

### Supported Media Types

The tool supports the following media types:

-   Videos
-   Images
-   PDFs
-   ZIP files
-   Any other Telegram media

## Roadmap

### Version 1.1

-   Add support for audio files.
-   Retry mechanism for failed downloads.

### Version 2.0

-   Build a GUI for non-technical users.

## Contributing

We welcome contributions of all kinds! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on how to get started.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

-   [Telethon](https://github.com/LonamiWebs/Telethon) - For making Telegram API integration easy.
-   [TQDM](https://github.com/tqdm/tqdm) - For elegant progress bars.
-   [Colorama](https://github.com/tartley/colorama) - For colorful console output.

---

Made with ❤️ by [Vinod Kumar](https://github.com/vinodkr494).
