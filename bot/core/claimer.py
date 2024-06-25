import asyncio
from time import time
from datetime import datetime, timezone
from urllib.parse import unquote

import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw.functions.messages import RequestWebView

from bot.config import settings
from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
import random


class Claimer:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client

    async def get_tg_web_data(self, proxy: str | None) -> str:
        proxy_dict = None
        self.tg_client.proxy = proxy_dict
        
        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)
            web_view = await self.tg_client.invoke(RequestWebView(
                peer=await self.tg_client.resolve_peer('claytoncoinbot'),
                bot=await self.tg_client.resolve_peer('claytoncoinbot'),
                platform='android',
                from_bot_menu=False,
                url='https://tonclayton.fun/api/user/subscribe'
            ))
            auth_url = web_view.url
            tg_web_data = unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])
            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error during Authorization: {error}")
            await asyncio.sleep(delay=3)

    async def get_mining_data(self, http_client: aiohttp.ClientSession) -> dict[str, str]:
        try:
            response = await http_client.post('https://tonclayton.fun/api/user/login')
            response.raise_for_status()
            
            response_json = await response.json()
            mining_data = response_json['user']

            return mining_data
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Profile Data: {error}")
            await asyncio.sleep(delay=3)

    async def send_claim(self, http_client: aiohttp.ClientSession) -> bool:
        try:
            response = await http_client.post('https://tonclayton.fun/api/user/claim', json={})
            response.raise_for_status()
            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when Claiming: {error}")
            await asyncio.sleep(delay=3)

            return False

    async def start_farming(self, http_client: aiohttp.ClientSession) -> bool:
        await asyncio.sleep(delay=6)
        try:
            response = await http_client.post('https://tonclayton.fun/api/user/start', json={})
            response.raise_for_status()

            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when Start Farming: {error}")
            await asyncio.sleep(delay=3)

            return False

    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")

    async def get_mining_data(self, http_client: aiohttp.ClientSession) -> dict[str, str]:
        try:
            response = await http_client.post('https://tonclayton.fun/api/user/login')
            response.raise_for_status()
            
            response_json = await response.json()
            mining_data = response_json['user']

            return mining_data
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when getting Profile Data: {error}")
            await asyncio.sleep(delay=3)
            return {}
    
    async def start_game(self, http_client: aiohttp.ClientSession) -> tuple[bool, dict]:
        # Start a new game
        try:
            response = await http_client.post('https://tonclayton.fun/api/game/start', json={})
            response.raise_for_status()
            logger.info(f"{self.session_name} | Game started successfully.")
        except aiohttp.ClientResponseError as e:
            logger.error(f"{self.session_name} | Error starting game: {e}")
            return False, {}
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when starting game: {error}")
            return False, {}

        await asyncio.sleep(random.uniform(2, 3))  # Wait 2-3 seconds

        # Progress through tile values
        base_url = 'https://tonclayton.fun/api/game/save-max-tile'
        tile_values = [4, 8, 16, 32, 64, 128, 256, 512]
        
        try:
            for tile in tile_values:
                payload = {"maxTile": tile}
                response = await http_client.post(base_url, json=payload)
                response.raise_for_status()
                logger.info(f"{self.session_name} | Successfully saved tile {tile}")
                
                if tile != 512:  # Don't wait after the last tile
                    await asyncio.sleep(random.uniform(5, 15))
            
            # End the game after reaching 512
            await asyncio.sleep(random.uniform(2, 7))  # Wait 2-7 seconds after the last tile
            response = await http_client.post('https://tonclayton.fun/api/game/over', json={})
            response.raise_for_status()
            logger.info(f"{self.session_name} | Game finished successfully")

            # Fetch updated mining data after successful game
            mining_data = await self.get_mining_data(http_client)
            return True, mining_data

        except aiohttp.ClientResponseError as e:
            logger.error(f"{self.session_name} | Error during game play: {e}")
            return False, {}
        except Exception as error:
            logger.error(f"{self.session_name} | Error during game play: {error}")
            return False, {}



    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        claim_time = 0

        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn) as http_client:
            while True:
                try:
                    if time() - access_token_created_time >= 3600:
                        tg_web_data = await self.get_tg_web_data(proxy=proxy)
                        http_client.headers["Init-Data"] = tg_web_data
                        headers["Init-Data"] = tg_web_data
                        access_token_created_time = time()

                    mining_data = await self.get_mining_data(http_client=http_client)

                    active_farm = mining_data['active_farm']
                    daily_attempts = mining_data['daily_attempts']
                    start_time = datetime.fromisoformat(mining_data['start_time'].replace('Z', '+00:00'))
                    current_time = datetime.now(timezone.utc)

                    if daily_attempts > 0:
                        logger.info(f"{self.session_name} | Daily attempts remaining: {daily_attempts}")
                        while daily_attempts > 0:
                            if await self.start_game(http_client=http_client):
                                logger.success(f"{self.session_name} | Game completed successfully.")
                                daily_attempts -= 1
                            else:
                                logger.warning(f"{self.session_name} | Game could not be completed.")
                            await asyncio.sleep(random.uniform(10, 15))  # Wait between games
                        continue
                    if not active_farm:
                        logger.info(f"{self.session_name} | Farm not active. Claiming and starting farming.")
                        if await self.send_claim(http_client=http_client):
                            logger.success(f"{self.session_name} | Claim successful.")
                        if await self.start_farming(http_client=http_client):
                            logger.success(f"{self.session_name} | Farming started successfully.")
                    else:
                        time_elapsed = current_time - start_time
                        time_to_wait = max(0, 6 * 3600 - time_elapsed.total_seconds())
                        
                        if time_to_wait > 0:
                            logger.info(f"{self.session_name} | Farming active. Waiting for {time_to_wait/3600:.2f} hours before claiming and restarting.")
                            await asyncio.sleep(time_to_wait)
                        
                        logger.info(f"{self.session_name} | Time to claim and restart farming.")
                        if await self.send_claim(http_client=http_client):
                            logger.success(f"{self.session_name} | Claim successful.")
                        if await self.start_farming(http_client=http_client):
                            logger.success(f"{self.session_name} | Farming restarted successfully.")

                    # Log current status
                    logger.info(f"{self.session_name} | Balance: {mining_data['tokens']} | "
                                f"Available to claim: {mining_data['storage']} | "
                                f"Multiplier: {mining_data['multiplier']}")
                    
                except InvalidSession as error:
                    raise error
                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error}")
                    await asyncio.sleep(delay=3)
                else:
                    logger.info(f"Sleep 1min")
                    await asyncio.sleep(delay=60)

async def run_claimer(tg_client: Client, proxy: str | None):
    try:
        await Claimer(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
