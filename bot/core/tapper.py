import asyncio
import json
import traceback
from time import time
from urllib.parse import unquote
import base64

import aiohttp
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.types import InputBotAppShortName
from pyrogram.raw.functions.messages import RequestAppWebView
from soupsieve.util import lower

from bot.core.agents import generate_random_user_agent
from bot.config import settings
import cloudscraper

from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from random import randint, choices, choice, uniform
import secrets
import uuid
from faker import Faker
import string

fake = Faker()
min_length = 256
max_length = 1024

class Tapper:
    def __init__(self, tg_client: Client):
        self.tg_client = tg_client
        self.session_name = tg_client.name
        self.first_name = ''
        self.last_name = ''
        self.user_id = ''
        self.auth_token = ""
        self.last_claim = None
        self.last_checkin = None
        self.balace = 0
        self.access_token = None
        self.game_response = None
        self.game = None


    async def get_tg_web_data(self, proxy: str | None) -> str:
        ref_param = settings.REF_LINK.split("=")[1].split('&')[0]
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('Binance_Moonbix_bot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"<light-yellow>{self.session_name}</light-yellow> | FloodWait {fl}")
                    logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=peer,
                app=InputBotAppShortName(bot_id=peer, short_name="start"),
                platform='android',
                write_allowed=True,
                start_param=ref_param
            ))

            auth_url = web_view.url
            # print(auth_url)
            tg_web_data = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            # print(tg_web_data)

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()


            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Unknown error during Authorization: "
                         f"{error}")
            await asyncio.sleep(delay=3)

    def random_fingerprint(self, lengths=32):
        return ''.join(choices('0123456789abcdef', k=lengths))

    def generate_Fvideo_token(self, length):

        characters = string.ascii_letters + string.digits + "+/"
        digits = string.digits
        characters1 = string.ascii_letters + digits

        random_string = ''.join(choice(characters) for _ in range(length - 3))

        random_string += '='
        random_string += choice(digits)
        random_string += choice(characters1)

        return random_string

    fake = Faker()

    def get_random_resolution(self):
        width = randint(720, 1920)
        height = randint(720, 1080)
        return f"{width},{height}"

    def get_random_timezone(self):
        timezones = [
            "GMT+07:00", "GMT+05:30", "GMT-08:00", "GMT+00:00", "GMT+03:00"
        ]
        return choice(timezones)

    def get_random_timezone_offset(self, timezone):
        # Extract the offset from the timezone format "GMT+07:00"
        sign = 1 if "+" in timezone else -1
        hours = int(timezone.split("GMT")[1].split(":")[0])
        return sign * hours * 60

    def get_random_plugins(self):
        plugins = [
            "PDF Viewer,Chrome PDF Viewer,Chromium PDF Viewer,Microsoft Edge PDF Viewer,WebKit built-in PDF",
            "Flash,Java,Silverlight,QuickTime",
            "Chrome PDF Viewer,Widevine Content Decryption Module",
        ]
        return choice(plugins)

    def get_random_canvas_code(self):
        return ''.join(choices(lower(string.hexdigits), k=8))

    def get_random_fingerprint(self):
        return ''.join(choices(lower(string.hexdigits), k=32))

    def generate_random_data(self, user_agent):
        timezone = self.get_random_timezone()
        sol = self.get_random_resolution()
        data = {
            "screen_resolution": sol,
            "available_screen_resolution": sol,
            "system_version": fake.random_element(["Windows 10", "Windows 11", "macOS Big Sur", "Ubuntu 20.04"]),
            "brand_model": fake.random_element(["unknown", "Dell XPS 13", "MacBook Pro", "HP Spectre"]),
            "system_lang": "en-EN",
            "timezone": timezone,
            "timezoneOffset": self.get_random_timezone_offset(timezone),
            "user_agent": user_agent,
            "list_plugin": self.get_random_plugins(),
            "canvas_code": self.get_random_canvas_code(),
            "webgl_vendor": fake.company(),
            "webgl_renderer": f"ANGLE ({fake.company()}, {fake.company()} Graphics)",
            "audio": str(uniform(100, 130)),
            "platform": fake.random_element(["Win32", "Win64"]),
            "web_timezone": fake.timezone(),
            "device_name": f"{fake.user_agent()} ({fake.random_element(['Windows'])})",
            "fingerprint": self.get_random_fingerprint(),
            "device_id": "",
            "related_device_ids": ""
        }
        return data


    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy):
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")
            return False

    def setup_session(self, session: cloudscraper.CloudScraper):
        payload = {
            "queryString": self.auth_token,
            "socialType": "telegram"
        }
        response = session.post("https://www.binance.com/bapi/growth/v1/friendly/growth-paas/third-party/access/accessToken", headers=headers, json=payload)
        data_ = response.json()
        if data_['code'] == '000000':
            logger.success(f"{self.session_name} | <green>Get access token sucessfully</green>")
            self.access_token = data_['data']['accessToken']
        else:
            logger.warning(f"{self.session_name} | <red>Get access token failed: {data_}</red>")

    def get_game_data(self, session: cloudscraper.CloudScraper):
        try:
            url = 'https://vemid42929.pythonanywhere.com/api/v1/moonbix/play'
            response = session.post(url, json=self.game_response)

            if response.json().get('message') == 'success':
                self.game = response.json().get('game')
                logger.info(f"{self.session_name} | <green> Get game data succesfully!</green>")
                return True

            logger.warning(f"{self.session_name} | <yellow>Failed to get game data, Msg: {response.json().get('message')}</yellow>")
            return False
        except Exception as error:
            logger.error(f"{self.session_name} | <red>Unknown error while trying to get game data: {str(error)}</red>")
            return False

    def setup_account(self, session: cloudscraper.CloudScraper):
        ref_id = settings.REF_LINK.split("=")[1].split('&')[0].split('_')[1]
        payload = {
            "agentId": str(ref_id),
            "resourceId": 2056
        }
        res = session.post("https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/referral", headers=headers,
                           json=payload)
        json_d = res.json()
        if json_d['success']:
            res = session.post("https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/participated",
                               headers=headers, json=payload)
            json_d = res.json()
            if json_d['success']:
                logger.success(f"{self.session_name} | <green>Successfully set up account !</green>")
                login_task = {
                    "resourceId": 2057
                }
                complete = self.complete_task(session, login_task)
                if complete == "done":
                    logger.success(f"{self.session_name} | <green>Successfully checkin for the first time !</green>")

        else:
            logger.warning(f"{self.session_name} | <yellow>Unknown error while tryng to init account: {json_d}</yellow>")
    async def get_user_info(self, session: cloudscraper.CloudScraper):
        payload = {
            "resourceId": 2056
        }
        response = session.post("https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info", headers=headers, json=payload)
        data_ = response.json()
        # print(data_)
        if data_['code'] == '000000':
            # print(data_)
            data__ = data_['data']
            if data__['participated'] is False:
                logger.info(f"{self.session_name} | Attempt to set up account...")
                self.setup_account(session)
                await asyncio.sleep(uniform(3,5))
                await self.get_user_info(session)
            else:
                logger.info(f"{self.session_name} | <cyan>Logged in</cyan>")
                logger.info(f"{self.session_name} | Total point: <yellow>{data__['metaInfo']['totalGrade']}</yellow> | <white>Risk Passed: <red>{data__['riskPassed']}</red> | Qualified: <red>{data__['qualified']}</red></white>")

        else:
            logger.warning(f"{self.session_name} | <red>Get user data failed: {data_}</red>")

    def get_user_info1(self, session: cloudscraper.CloudScraper):
        payload = {
            "resourceId": 2056
        }
        response = session.post(
            "https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/user/user-info",
            headers=headers, json=payload)
        data_ = response.json()
        if data_['code'] == '000000':
            # print(data_)
            data__ = data_['data']
            return data__
        else:
            logger.warning(f"{self.session_name} | <red>Get ticket data failed: {data_}</red>")

    def get_task_list(self, session: cloudscraper.CloudScraper):
        payload = {
            "resourceId": 2056
        }
        response = session.post("https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/list", headers=headers, json=payload)
        data_ = response.json()
        # print(data_)
        if data_['code'] == '000000':
            task_list = data_['data']['data'][0]['taskList']['data'] # bruh what are they doing ????
            tasks = []
            for task in task_list:
                # print(task)
                if task['type'] == "THIRD_PARTY_BIND":
                    continue
                elif task['status'] == "COMPLETED":
                    continue
                elif task['status'] == "IN_PROGRESS":
                    tasks.append(task)
            return tasks
        else:
            logger.warning(f"{self.session_name} | <red>Get tasks list failed: {data_}</red>")
            return None

    def complete_task(self, session: cloudscraper.CloudScraper, task: dict):
        task_ids = [task['resourceId']]
        payload = {
            "referralCode": "null",
            "resourceIdList": task_ids
        }
        response = session.post("https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/task/complete", headers=headers, json=payload)
        data_ = response.json()
        # print(data_)
        if data_['success']:
            return "done"
        else:
            return data_['messageDetail']


    def complete_game(self, session: cloudscraper.CloudScraper):
        string_payload = self.game['payload']
        payload = {
            "log": self.game['log'],
            "payload": string_payload,
            "resourceId": 2056
        }
        # print(payload)
        response = session.post("https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/complete",
                                headers=headers, json=payload)
        data_ = response.json()

        if data_['success']:
            logger.success(f"{self.session_name} | <green>Sucessfully earned: <yellow>{self.game['log']}</yellow> from game !</green>")
        else:
            logger.warning(f"{self.session_name} | <yellow>Failed to complete game: {data_}</yellow>")

    def auto_update_ticket(self, session: cloudscraper.CloudScraper):
        ticket_data = self.get_user_info1(session)
        return ticket_data['metaInfo']['totalAttempts'] - ticket_data['metaInfo']['consumedAttempts']
    async def play_game(self, session: cloudscraper.CloudScraper):
        ticket_data = self.get_user_info1(session)
        if ticket_data['metaInfo']['totalAttempts'] == ticket_data['metaInfo']['consumedAttempts']:
            logger.warning(f"{self.session_name} | No Attempt left to play game...")
            return
        attempt_left = ticket_data['metaInfo']['totalAttempts'] - ticket_data['metaInfo']['consumedAttempts']
        logger.info(f"{self.session_name} | Starting to play game...")
        while attempt_left > 0:
            logger.info(f"{self.session_name} | Attempts left: <cyan>{attempt_left}</cyan>")
            payload = {
                "resourceId": 2056
            }
            response = session.post("https://www.binance.com/bapi/growth/v1/friendly/growth-paas/mini-app-activity/third-party/game/start",
                                    headers=headers, json=payload)
            data_ = response.json()
            if data_['success']:
                logger.success(f"{self.session_name} | <green>Game <cyan>{data_['data']['gameTag']}</cyan> started successful</green>")

                self.game_response = data_
                sleep_ = uniform(45, 45.05)
                logger.info(f"{self.session_name} | Wait <white>{sleep_}s</white> to complete the game...")
                await asyncio.sleep(sleep_)
                check = self.get_game_data(session)
                if check:
                    self.complete_game(session)
                    attempt_left = self.auto_update_ticket(session)

            else:
                logger.warning(f"{self.session_name} | <yellow>Failed to start game, msg: {data_}</yellow>")
                return

            sleep_ = uniform(5, 10)

            logger.info(f"{self.session_name} | Sleep {sleep_}s...")

            await asyncio.sleep(sleep_)


    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        headers["User-Agent"] = generate_random_user_agent(device_type='android', browser_type='chrome')
        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)
        session = cloudscraper.create_scraper()

        if proxy:
            proxy_check = await self.check_proxy(http_client=http_client, proxy=proxy)
            if proxy_check:
                proxy_type = proxy.split(':')[0]
                proxies = {
                    proxy_type: proxy
                }
                session.proxies.update(proxies)
                logger.info(f"{self.session_name} | bind with proxy ip: {proxy}")

        token_live_time = randint(28700, 28800)
        while True:
            try:
                if time() - access_token_created_time >= token_live_time:
                    tg_web_data = await self.get_tg_web_data(proxy=proxy)
                    self.auth_token = tg_web_data
                    data = self.generate_random_data(headers['User-Agent'])
                    json_data = json.dumps(data)
                    encoded_data = base64.b64encode(json_data.encode()).decode()
                    headers['Device-Info'] = encoded_data
                    # print(encoded_data)
                    fvideo_token = self.generate_Fvideo_token(196)
                    headers['Fvideo-Id'] = secrets.token_hex(20)
                    headers['Fvideo-Token'] = fvideo_token
                    headers['Bnc-Uuid'] = str(uuid.uuid4())
                    headers['Cookie'] = f"theme=dark; bnc-uuid={headers['Bnc-Uuid']};"
                    # print(fvideo_token)
                    self.setup_session(session)
                    access_token_created_time = time()
                    token_live_time = randint(3500, 3600)

                if self.access_token:
                    headers['X-Growth-Token'] = self.access_token
                    await self.get_user_info(session)
                    if settings.AUTO_TASK:
                        task_list = self.get_task_list(session)
                        for task in task_list:
                            check = self.complete_task(session, task)
                            if check == "done":
                                logger.success(f"{self.session_name} | <green>Successfully completed task <cyan>{task['type']}</cyan> | Reward: <yellow>{task['rewardList'][0]['amount']}</yellow></green>")
                            else:
                                logger.warning(f"{self.session_name} | <light-yellow> Failed to complete task: {task['type']}, msg: {check}</light-yellow>")
                            await asyncio.sleep(uniform(3,5))

                if settings.AUTO_PLAY_GAME:
                    await self.play_game(session)

                sleep_ = randint(2500, 3600)
                logger.info(f"{self.session_name} | Sleep {sleep_}s...")
                await asyncio.sleep(sleep_)

            except InvalidSession as error:
                raise error

            except Exception as error:
                traceback.print_exc()
                logger.error(f"{self.session_name} | Unknown error: {error}")
                await asyncio.sleep(delay=randint(60, 120))

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        sleep_ = randint(1, 15)
        logger.info(f"{tg_client.name} | start after {sleep_}s")
        await asyncio.sleep(sleep_)
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
