import configparser
import os
import sys
import steam
import steam.webauth
import steamfront
import json
import re
import time
import datetime


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
            print("Load config success!")
            self.make_url = 'https://steamcommunity.com//tradingcards/ajaxcreatebooster'
            self.unpack_url = 'https://steamcommunity.com/id/{}/ajaxunpackbooster/'.format(self.inventory_id)
            self.headers = {
                "Referer": "https://steamcommunity.com/tradingcards/boostercreator/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
            }
        else:
            self.config_found = False
            self.game_id = []
            print("Config file not detected, please create a new config file.")

    # Start make booster pack
    def login(self):
        print("Getting login information...")
        self.account = steam.webauth.WebAuth(self.username, self.password)
        # print("Enter steam mobile authenticator:")
        twofactor_code_inp = sys.argv[1]
        try:
            self.account_session = self.account.login(twofactor_code=str(twofactor_code_inp))
            print("Login success!")
            return True
        except Exception as e:
            print("Login failed, please check account info or authenticator code, error {}".format(e))
            return False
            # Set main work

    def run(self):
        login_status = self.login()
        if not login_status:
            return
        while True:
            params = {
                "sessionid" : self.account.session_id,
                "appid": -1,
                "series": 1,
                "tradability_preference" : 1
            }
            response = self.account_session.post(self.make_url, headers=self.headers, data=params)
            try:
                goo_amount = int(re.search(r'"goo_amount":"([^"]+)"', response.text).group(1))
            except:
                goo_amount = -1
            print("Steam gems stock right now : %d" % goo_amount)
            if goo_amount <= 1000:
                print("Steam gems stock low, please re-fill.")
                print("Current time :", str(datetime.datetime.now())[:19])
                time.sleep(60 * 60 * 12)
            else:
                for gi in self.game_id:
                    time.sleep(0.1)
                    params = {
                        "sessionid" : self.account.session_id,
                        "appid": gi,
                        "series": 1,
                        "tradability_preference" : 1
                    }
                    response = self.account_session.post(self.make_url, headers=self.headers, data=params)
                    if response.text[2:18] != 'purchase_eresult':
                        print("Puchase booster pack SUCCESS on game : %s-%s" % (gi, self.client.getApp(appid=gi).name))
                        search_result = re.search(r'"communityitemid":"([^"]+)"', response.text)
                        if search_result is None:
                            continue
                        item_id = search_result.group(1)
                        params = {
                            "appid": gi,
                            "communityitemid": item_id,
                            "sessionid" : self.account.session_id
                        }
                        self.account_session.post(self.unpack_url, headers=self.headers, data=params)
                    else:
                        try:
                            game_name = self.client.getApp(appid=gi).name
                        except:
                            game_name = "Unknown game"
                        print("Purchase booster pack FAILED on game : %s-%s" % (gi, game_name))
                print("Current time : " + str(datetime.datetime.now())[:19])
                time.sleep(60 * 60 * 6 + 60 * 5)  # Retry after 4 hours and 5 minutes


if __name__ == "__main__":
    main = get_info()
    main.run()
