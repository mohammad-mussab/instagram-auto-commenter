# Instagram Comment Poster 🤖

Automatically monitor comments on a specific Instagram post or reel and reply with witty, Pakistani/Indian-style humor using OpenAI!

## Features

- **Monitors a single Instagram post or reel** for new comments.
- **Auto-replies** to comments with humorous, locally-flavored responses powered by OpenAI (GPT-3.5).
- **Avoids spam, self-replies, and repeats**.
- **Session saving** for faster logins (supports 2FA).

## Requirements

- Python 3.7+
- [instagrapi](https://github.com/adw0rd/instagrapi)
- [openai](https://github.com/openai/openai-python)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mohammad-mussab/instagram-auto-commenter.git
   cd Instagram-Comment-Poster
   ```

2. **Install dependencies:**
   ```bash
   pip install instagrapi openai
   ```

## Usage

1. **Run the script:**
   ```bash
   python comment_monitor.py
   ```

2. **Follow the prompts:**
   - Enter your Instagram username and password.
   - Choose whether to enable auto-reply (requires OpenAI API key).
   - Enter your OpenAI API key (if auto-reply enabled).
   - Paste the Instagram post or reel URL to monitor.
   - Set the check interval (in seconds).

3. **Let it run!**
   - The script will monitor for new comments and reply automatically if enabled.

## Example

```
Enter your Instagram username: myusername
Enter your Instagram password: ********
Enable auto-reply with OpenAI humor? (y/n, default=y): y
Enter your OpenAI API key: sk-...
Enter the Instagram post/reel URL to monitor: https://www.instagram.com/p/DMaw1wpoNba/
Enter check interval in seconds (default 30): 30
```

## Notes

- **2FA Support:** If you have two-factor authentication enabled, you’ll be prompted for your code on first login.
- **Session Saving:** Your session is saved to a file for faster future logins.
- **OpenAI API Key:** Required only if you want auto-replies. Get one from [OpenAI](https://platform.openai.com/account/api-keys).

## Disclaimer

- Use responsibly and respect Instagram’s terms of service.
- This tool is for educational and entertainment purposes only. 
