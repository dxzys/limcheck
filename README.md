# limcheck
Limcheck is a simple tool which checks and lists limited items owned by a Roblox user, even if their inventory is private.

Setup:
- Place Roblox Cookies in cookies.txt (using cookies is required in order to make an API request to a Roblox endpoint. Multiple cookies are supported, one cookie per line)
- Install any potential requirements by running pip install in cmd (requests, asyncio, aiohttp may need to be installed if you haven't already installed them)

That's it! 

Your cookies file will be validated upon running 'main.py' and you'll be able to enter a Roblox user ID to check what limiteds they own.
A log folder will automatically be created which will store a simple log of each limited owned by the user ID after each use.
