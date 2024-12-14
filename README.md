# Telegram Bot for Uploading TCX and FIT Files from Kinomap to Garmin Connect

This Telegram bot automates the process of converting and uploading TCX files from Kinomap to Garmin Connect. Users can easily send their workout data through the bot, simplifying integration with the Garmin ecosystem.

---

## Features

- **Easy Authorization**: During the first use, the bot requests your Garmin Connect login and password. These credentials are used to obtain an access token, which is securely stored for future sessions.
- **Flexible File Support**: The bot accepts:
  - Single TCX files.
  - ZIP archives containing multiple TCX files (only TCX files are processed; other files are ignored).
  - FIT files (uploaded directly to Garmin Connect without processing).
- **Automated Conversion and Upload**: After receiving files, the bot:
  1. Converts them to the required format (for TCX files).
  2. Uploads them to your Garmin Connect account.
  If a workout already exists in Garmin Connect, the bot notifies you and returns the converted TCX files.
- **User Commands**:
  - `/start`: Start the bot and check its status.
  - `/stop`: Remove stored authorization data.

---

## Setup Instructions

### Prerequisites

1. Place a `.env` file in the project root with the following environment variable:
   ```
   TOKEN_API_BOT_TCX=<your_telegram_bot_token>
   ```

### Docker Build and Run

#### Build Docker Image

To build the Docker image for the bot, run:

```bash
sudo docker build -t tcx-bot-img .
```

#### Run Docker Container

To start the bot in a Docker container with auto-restart on failure:

```bash
sudo docker run -d --name tcx-bot-container --restart unless-stopped --env-file .env tcx-bot-img
```

#### View Logs

To monitor the bot's logs in real-time:

```bash
sudo docker logs -f tcx-bot-container
```

---

### Recreating the Docker Environment

If you need to rebuild the bot from scratch:

1. Stop and remove the existing container:
   ```bash
   sudo docker stop tcx-bot-container
   sudo docker container prune
   sudo docker image prune -a
   ```
2. Follow the build and run instructions above.

---

## Usage Notes

- The bot securely encrypts and stores your Garmin Connect credentials for seamless future logins.
- If you encounter issues, check the logs or ensure that your `.env` file is correctly configured.

---

## Example Workflows

### Sending a Single TCX or FIT File

1. Open the chat with the bot in Telegram.
2. Send a TCX or FIT file as an attachment.
3. The bot processes and uploads the file to Garmin Connect (FIT files are uploaded without conversion).

### Sending Multiple Files

1. Compress multiple TCX files into a ZIP archive.
2. Send the ZIP file to the bot.
3. The bot processes and uploads all TCX files in the archive (other file types in the ZIP are ignored).

---

## License

This project is open-source and available under the MIT License. Contributions are welcome!

---

## Notes from the Author

This bot was created "on the fly" over a couple of evenings for personal use and is not intended as a reference implementation. If you have constructive suggestions (not just criticism), I’d be happy to hear them!

