from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from datetime import datetime

import click
from flask import current_app, g

# TO RUN:
# flask --app webapp e2e

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)
# See: https://github.com/SeleniumHQ/seleniumhq.github.io/blob/trunk//examples/python/tests/browsers/test_chrome.py#L9-L10

screenshots_folder_name = 'screenshots'
if not os.path.exists(screenshots_folder_name):
    os.mkdir(screenshots_folder_name)

def init_app(app):
    #app.teardown_appcontext(teardown_command)
    app.cli.add_command(e2e_command)


@click.command('e2e')
def e2e_command():
    """Clear the existing data and create new tables."""
    test_screenshot()
    #driver.quit()

#def teardown_command(e=None):
#    driver.quit()

def test_screenshot():
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(0.5)
    driver.get("https://www.selenium.dev/selenium/web/web-form.html")
    title = driver.title
    filename = f'image-{datetime.utcnow():%Y%m%d-%H%M%S}.png'
    driver.get_screenshot_as_file(f'{screenshots_folder_name}/{filename}')
    driver.quit()
