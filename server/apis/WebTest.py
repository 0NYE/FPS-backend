import asyncio
from pyppeteer import launch
import os

async def html_to_image(html_code, css_code, output_image_path):
    browser = await launch()
    page = await browser.newPage()
    await page.setContent(html_code)
    await page.addStyleTag(content=css_code)
    await page.screenshot({'path': output_image_path})
    await browser.close()

html_code = '''
<!DOCTYPE html>
<html>
<head>
    <title>HTML to Image</title>
</head>
<body>
    <h1>Hello, World!</h1>
</body>
</html>
'''

css_code = '''
h1 {
    color: red;
}
'''

print(os.getcwd())
output_image_path = os.getcwd() + '/app/static/image' + '/result.png'

asyncio.get_event_loop().run_until_complete(html_to_image(html_code, css_code, output_image_path))