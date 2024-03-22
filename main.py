import requests, logging, time, os, asyncio, aiohttp, random

os.makedirs("logs", exist_ok=True)
log_file_path = os.path.join("logs", f'{time.strftime("%Y%m%d%H%M%S")}-limited_checker.log')
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(message)s')

def read_cookies(file_path='cookies.txt'):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            cookies = [line.strip() for line in file.readlines()]
        return cookies
    else:
        print(f"Error: Cookies file '{file_path}' not found.")
        return []

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'}

async def validate_cookie(session, cookie, cookie_number=None, cookies_file='cookies.txt'):
    async with session.get("https://users.roblox.com/v1/users/authenticated", headers=headers, cookies={'.ROBLOSECURITY': cookie}) as response:
        if response.status == 401:
            print(f"Cookie{cookie_number} is invalid. Removing from config file.")
            remove_invalid_cookie(cookie, cookies_file)
            return None
        user_data = await response.json()
        username = user_data.get('name', 'N/A')
        print(f"Cookie{cookie_number} is valid. User: {username}")
        return (f"Cookie{cookie_number}", cookie)

def remove_invalid_cookie(invalid_cookie, cookies_file='cookies.txt'):
    with open(cookies_file, 'r') as file:
        cookies = file.read().splitlines()
    cookies.remove(invalid_cookie)
    with open(cookies_file, 'w') as file:
        file.write('\n'.join(cookies))

async def validate_cookies(cookies):
    if not cookies:
        print("No cookies found.")
        return []
    print("Validating cookies...")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, cookie in enumerate(cookies, start=1):
            task = validate_cookie(session, cookie, i)
            tasks.append((i, task))
        tasks.sort(key=lambda x: x[0])
        results = [await task[1] for task in tasks]
    return results

def get_limiteds():
    response = requests.get("https://api.rolimons.com/items/v1/itemdetails", headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        print(f"Failed to limiteds from Rolimons API: {response.status_code}")
        return {}

async def check_ownership(session, user_id, asset_id, cookies):
    headers = {'Cookie': f'.ROBLOSECURITY={random.choice(cookies)}'}
    url = f"https://inventory.roblox.com/v1/users/{user_id}/items/asset/{asset_id}"
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return len(data.get("data", []))
        else:
            print(f"Failed to check limited ownership from Roblox API: {response.status}")
            return 0
        
async def getuser(session, user_id, cookies):
    headers = {'Cookie': f'.ROBLOSECURITY={random.choice(cookies)}'}
    async with session.get(f"https://users.roblox.com/v1/users/{user_id}", headers=headers) as response:
            userdata = await response.json()
            return userdata.get("name")

async def main():
    cookies = read_cookies()
    asyncio.set_event_loop(asyncio.new_event_loop())
    validated_cookies = [cookie[1] for cookie in (await validate_cookies(cookies)) if cookie]
    if not validated_cookies:
        print("No valid cookies found. Exiting.")
        return
    print()
    user_id = input("Enter PlayerId: ")
    async with aiohttp.ClientSession() as session:
        username = await getuser(session, user_id, validated_cookies)
        print(f"Fetching limiteds owned by {username} ({user_id})...")
        assets = get_limiteds()
        if not assets:
            print("Unable to fetch limiteds!")
            return
        tasks = []
        total_limiteds_owned = 0
        for limited_id, details in assets.items():
            name = details[0]
            asset_id = limited_id
            task = check_ownership(session, user_id, asset_id, validated_cookies)
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        await asyncio.sleep(1)
    owned_items = []
    for limited_id, response in zip(assets.keys(), responses):
        total_limiteds_owned += response
        if response:
            details = assets[limited_id]
            name, acronym, _, _, value, _, _, _, _, _ = details
            owned_items.append((name, acronym, value, response))
            if acronym:
                logging.info(f"{username} owns {name} ({acronym}) - Value: {value}" + (f" (x{response})" if response > 1 else ""))
            else:
                logging.info(f"{username} owns {name} - Value: {value}" + (f" (x{response})" if response > 1 else ""))
    owned_items_sorted = sorted(owned_items, key=lambda x: x[2], reverse=True)
    if not owned_items_sorted:
        logging.info(f"{username} doesn't own any limiteds!")
        print(f"\n{username} doesn't own any limiteds!")
        return
    print(f"\nLimiteds owned by {username} (Sorted by Value, Highest - Lowest):\n")
    for item in owned_items_sorted:
        item_name = f"{item[0]} ({item[1]})" if item[1] else item[0]
        item_info = f"{item_name} - Value: {item[2]}"
        if item[3] > 1:
            item_info += f" (x{item[3]})"
        print(item_info)
    logging.info(f"\nTotal limiteds owned by {username}: {total_limiteds_owned}")
    print(f"\nTotal limiteds owned by {username}: {total_limiteds_owned}")

asyncio.run(main())
