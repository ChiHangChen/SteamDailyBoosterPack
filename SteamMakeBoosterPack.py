import configparser
import os
import sys
import steam
import steam.webauth
import steamfront
import json
import logging
import re
import time
import datetime
from requests import Session
from base64 import b64encode
from steam.core.crypto import rsa_publickey, pkcs1v15_encrypt
from steam.utils.web import generate_session_id


class get_info():
    def __init__(self):
        # Load config
        if os.path.exists('config.ini'):
            self.config_found = True
            config = configparser.ConfigParser()
            config.read('config.ini')
            self.username = config['ACCOUNT INFO']['username']
            self.password = config['ACCOUNT INFO']['password']
            self.inventory_id = config['ACCOUNT INFO']['inventory_id']
            self.game_id = json.loads(config['APP LIST']['game_id'])
            self.client = steamfront.Client()
            logging.warning("Load config success!")
            self.make_url = 'https://steamcommunity.com/tradingcards/ajaxcreatebooster'
            self.unpack_url = 'https://steamcommunity.com/id/{}/ajaxunpackbooster/'.format(self.inventory_id)
            self.headers = {
                "Referer": "https://steamcommunity.com/tradingcards/boostercreator/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
            }
        else:
            self.config_found = False
            self.game_id = []
            logging.warning("Config file not detected, please create a new config file.")

    # Start make booster pack
    def login(self):
        logging.warning("Getting login information...")
        # self.account = steam.webauth.WebAuth(self.username, self.password)
        # logging.warning("Enter steam mobile authenticator:")
        twofactor_code_inp = sys.argv[1]
        try:
            logging.warning(f"Logging in as {self.username} using 2FA: {twofactor_code_inp}...")
            # self.account_session = self.account.login(twofactor_code=str(twofactor_code_inp))
            self.account_session = Session()
            ua = "python-steam/{0} {1}".format("jimchen", self.account_session.headers['User-Agent'])
            self.account_session.headers['User-Agent'] = ua
            resp = self.account_session.post(
                'https://steamcommunity.com/login/getrsakey/',
                timeout=15,
                data={
                    'username': self.username,
                    'donotcache': int(time.time() * 1000),
                }
            ).json()
            key = rsa_publickey(
                int(resp['publickey_mod'], 16),
                int(resp['publickey_exp'], 16)
            )
            timestamp = resp['timestamp']
            data = {
                'username': self.username,
                "password": b64encode(pkcs1v15_encrypt(key, self.password.encode('ascii'))),
                "emailauth": "",
                "emailsteamid": "",
                "twofactorcode": twofactor_code_inp,
                "captchagid": -1,
                "captcha_text": "",
                "loginfriendlyname": "python-steam webauth",
                "rsatimestamp": timestamp,
                "remember_login": 'true',
                "donotcache": int(time.time() * 100000),
            }
            resp = self.account_session.post('https://steamcommunity.com/login/dologin/', data=data, timeout=15)
            if resp.json() is None or resp.json()['success'] is not True:
                logging.error(f"Login failed with resp: {resp.text}, please check account info or authenticator code.")
                sys.exit(1)
            logging.warning(f"Login response: {resp.json()}")
            domains = ['store.steampowered.com', 'help.steampowered.com', 'steamcommunity.com']
            for cookie in list(self.account_session.cookies):
                for domain in domains:
                    self.account_session.cookies.set(cookie.name, cookie.value, domain=domain, secure=cookie.secure)

            session_id = generate_session_id()
            self.account_session.session_id = session_id
            language = 'english'
            for domain in domains:
                self.account_session.cookies.set('Steam_Language', language, domain=domain)
                self.account_session.cookies.set('birthtime', '-3333', domain=domain)
                self.account_session.cookies.set('sessionid', session_id, domain=domain)
            return True
        except Exception as e:
            logging.exception("Login failed, please check account info or authenticator code, error {}".format(e))
            return False
            # Set main work

    def run(self):
        login_status = self.login()
        if not login_status:
            return
        while True:
            params = {
                "sessionid" : self.account_session.session_id,
                "appid": -1,
                "series": 1,
                "tradability_preference" : 2
            }
            response = self.account_session.post(self.make_url, headers=self.headers, data=params)
            try:
                goo_amount = int(re.search(r'"goo_amount":"([^"]+)"', response.text).group(1))
            except:
                goo_amount = -1
            logging.warning(f"Steam gems stock right now : {goo_amount}")
            if goo_amount <= 1000:
                logging.warning("Steam gems stock low, please re-fill.")
                logging.warning(f"Current time : {str(datetime.datetime.now())[:19]}")
                time.sleep(60 * 60 * 12)
            else:
                for gi in self.game_id:
                    time.sleep(0.1)
                    params = {
                        "sessionid" : self.account_session.session_id,
                        "appid": gi,
                        "series": 1,
                        "tradability_preference" : 2
                    }
                    response = self.account_session.post(self.make_url, headers=self.headers, data=params)
                    if response.text[2:18] != 'purchase_eresult':
                        logging.warning("Puchase booster pack SUCCESS on game : %s-%s" % (gi, self.client.getApp(appid=gi).name))
                        search_result = re.search(r'"communityitemid":"([^"]+)"', response.text)
                        if search_result is None:
                            logging.error(f"Can't find communityitemid on game : {gi}-{self.client.getApp(appid=gi).name}")
                            continue
                        item_id = search_result.group(1)
                        params = {
                            "appid": gi,
                            "communityitemid": item_id,
                            "sessionid" : self.account_session.session_id
                        }
                        self.account_session.post(self.unpack_url, headers=self.headers, data=params)
                    else:
                        try:
                            game_name = self.client.getApp(appid=gi).name
                        except:
                            game_name = "Unknown game"
                        logging.warning("Purchase booster pack FAILED on game : %s-%s" % (gi, game_name))
                logging.warning("Current time : " + str(datetime.datetime.now())[:19])
                time.sleep(60 * 60 * 6 + 60 * 5)  # Retry after 4 hours and 5 minutes


if __name__ == "__main__":
    main = get_info()
    main.run()
