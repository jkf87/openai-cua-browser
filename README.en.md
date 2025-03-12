# OpenAI Computer-Using Agent (CUA) - Browser Automation

This project is a simple example of using OpenAI's Computer-Using Agent (CUA) API to automate web browser tasks. It implements an AI agent that takes natural language commands from users and executes them in a browser.

![OpenAI CUA Browser Automation](https://raw.githubusercontent.com/openai/openai-assets/master/cua-demo-2.gif)

## Features

- Request browser tasks using natural language
- Perform various tasks like Google searches, weather checks, news searches
- Watch tasks executed in real-time
- Safety checks to prevent risky operations
- Real-time monitoring of keyboard/mouse actions

## Requirements

- Python 3.8 or higher
- OpenAI API key (set in `.env` file)
- Playwright browser drivers

## Installation

1. Clone the repository:
```bash
git clone https://github.com/jkf87/openai-cua-browser.git
cd openai-cua-browser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browser drivers:
```bash
python setup_playwright.py
```
Or directly:
```bash
playwright install chromium
```

4. Set up your OpenAI API key:
Create a `.env` file and add:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

Run the program with:
```bash
python cua_browser.py
```

When running:
1. A Chrome browser window will open
2. You'll be prompted to enter a task to perform
3. Specify a task in natural language (e.g., "Check the weather in Seoul", "Search for Python tutorials")
4. The AI agent will perform the task in real-time
5. After task completion, you can enter another task or exit

## Task Examples

- "Check today's weather on Naver"
- "Find the latest news about OpenAI"
- "Search for Python lectures on YouTube"
- "Look for flights from Seoul to New York"

## Troubleshooting

- Browser dependency errors: Run `playwright install` to install all required browsers
- OpenAI API errors: Verify your API key is correctly set in the `.env` file and you have sufficient credits
- Browser not appearing: Make sure `headless=False` is set in the script

## Safety Notes

- Confirmation messages will appear when safety checks are triggered
- Always monitor the actions performed by the agent
- Do not use this agent on sensitive websites or for sensitive tasks

## How It Works

1. User's natural language command is sent to OpenAI's Computer-Using Agent
2. AI model analyzes the screen and generates the next action for the task
3. The action is executed in the browser via Playwright
4. Browser screenshot is captured and sent back to the AI
5. This loop repeats until the task is completed

## License

MIT

## Related Resources

- [OpenAI Computer Use Documentation](https://platform.openai.com/docs/guides/computer-use)
- [Playwright Documentation](https://playwright.dev/python/docs/intro) 