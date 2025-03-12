import subprocess
import sys

def install_playwright_browsers():
    print("Installing Playwright browsers...")
    try:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("Successfully installed Playwright browsers.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing Playwright browsers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_playwright_browsers() 