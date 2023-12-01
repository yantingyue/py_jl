#!/usr/bin/python3
# -*- coding:utf-8 -*-

import requests
import execjs
import time
import json
from copy import deepcopy
from loguru import logger
from greenlet import greenlet


class Nice:

    def __init__(self):
        self.nft_id = 240063  # 藏品id
        self.token = "R4KPSXOgbJTwJmeqpleWPiS8YeiBKuv_"
        self.tokens = [
            "M5K0-uBomkUYo_UZxlSXP6cM9PUdV1fO",
            "R4KPSXOgbJTwJmeqpleWPiS8YeiBKuv_",
        ]
        self.did = "d5401cf612846e7cd15a2318039d67b8"
        self.seid = ""
        self.dvi = ""
        self.headers = {
            "Host": "api.oneniceapp.com",
            "user-agent": "nice/5.9.33, Android/8.1.0, Google+Pixel+2, OkHttp",
            "content-type": "application/json; charset=utf-8"
        }
        self.params = {
            "token": self.token,
            "did": self.did,
            "osn": "android",
            "osv": "8.1.0",
            "appv": "5.9.33",
            "net": "0-0-wifi",
            "ch": "main",
            "ver": "1",
            "ts": "",
            "sw": "1080",
            "sh": "1920",
            "la": "zh-CN",
            "seid": self.seid,
            "src": "",
            "tpid": "",
            "lm": "",
            "abroad": "no",
            "country": "",
            "dt": "Google Pixel 2",
            "dvi": self.dvi
        }
        self.ctx = self.get_sign()
        self.session = requests.Session()

    def get_sign(self):
        with open("./sign.js", "r", encoding='utf-8') as file:
            js_code = file.read()
        result = execjs.compile(js_code)
        return result

    def priceInfos(self,token):
        ts = int(time.time() * 1000)
        url = "https://api.oneniceapp.com/Sneakerpurchase/priceInfosV3"
        self.params["token"] = token
        params = deepcopy(self.params)
        params["ts"] = ts
        js_result = self.ctx.call("nice_sign_v3", '{"button_type":"purchase","id":"%s","sort":"common"}' % self.nft_id, params["did"])
        js_datas = json.loads(js_result)
        data = js_datas.get("data")
        print(data)
        try:
            response = self.session.post(url, headers=self.headers, params=params, data=data)
            if response.status_code == 200:
                datas = response.json()
                print(datas)
                infos = datas.get("data").get("tab_list")
                if infos:
                    nft_result = list()
                    nft_lst = infos[0].get("list")
                    for i in nft_lst:
                        nft_dict = {}
                        size_id = i.get("size_id")
                        price = i.get("price")
                        stock = i.get("stock")
                        if stock:
                            nft_dict["size_id"] = size_id
                            nft_dict["price"] = price
                            nft_result.append(nft_dict)
                    return nft_result
        except Exception as e:
            logger.error(e)

    def config(self, nft_lst):
        if nft_lst:
            ts = int(time.time() * 1000)
            self.params["token"] = self.token
            params = deepcopy(self.params)
            params["ts"] = ts
            url = "https://api.oneniceapp.com/Sneakerpurchase/config"
            for nft in nft_lst:
                price = nft.get("price")
                size_id = nft.get("size_id")
                js_result = self.ctx.call("nice_sign_v3", '{"price":"%s","size_id":"%s","id":"%s","stock_id":"128"}' % (price, size_id, self.nft_id), params["did"])
                js_datas = json.loads(js_result)
                data = js_datas.get("data")
                try:
                    response = self.session.post(url, headers=self.headers, params=params, data=data)
                    if response.status_code == 200:
                        datas = response.json()
                        self.prepub(datas)
                except Exception as e:
                    logger.error(e)

    def prepub(self, datas):
        info = datas.get("data").get("stock_info")
        unique_token = datas.get("data").get("unique_token")
        size_id = info.get("size_id")
        stock_id = info.get("stock_id")
        price = info.get("price")
        ts = int(time.time() * 1000)
        url = "https://api.oneniceapp.com/Sneakerpurchase/prepub"
        self.params["token"] = self.token
        params = deepcopy(self.params)
        params["ts"] = ts
        args = {
            "id": info.get("id"),
            "size_id": str(size_id),
            "stock_id": str(stock_id),
            "price": str(price),
            "pay_type": "",
            "address_id": "",
            "unique_token": unique_token,
            "sale_id": "",
            "need_storage": "yes",
            "coupon_id": "",
            "stamp_id": "",
            "discount_id": "",
            "order_source": "",
            "params": {},
            "price_list": [
                {
                    "price": str(price),
                    "num": 1
                }
            ],
            "purchase_num": 1
        }
        js_result = self.ctx.call("nice_sign_v3", args, params["did"])
        js_datas = json.loads(js_result)
        data = js_datas.get("data")
        try:
            response = self.session.post(url, headers=self.headers, params=params, data=data)
            if response.status_code == 200:
                datas = response.json()
                code = datas.get("code")
                if code == 0:
                    logger.info(datas)
                    self.pub(args)
        except Exception as e:
            logger.error(e)

    def pub(self, args):
        url = "https://api.oneniceapp.com/Sneakerpurchase/pub"
        self.params["token"] = self.token
        params = deepcopy(self.params)
        ts = int(time.time() * 1000)
        params["ts"] = ts
        js_result = self.ctx.call("nice_sign_v3", args, params["did"])
        js_datas = json.loads(js_result)
        data = js_datas.get("data")
        try:
            response = self.session.post(url, headers=self.headers, params=params, data=data)
            if response.status_code == 200:
                datas = response.json()
                code = datas.get("code")
                if code == 0:
                    self.FeishuNotice()
                    logger.info(datas)
        except Exception as e:
            logger.error(e)
    def Login(self):
        ts = int(time.time() * 1000)
        url = "https://api.oneniceapp.com/account/login"
        params = deepcopy(self.params)
        params["ts"] = ts
        js_result = self.ctx.call("nice_sign_v3", '{"password":"KgAmeyXsfaiEtywPvvg4FX7SbMBQgJke5s9XC+0YNILqJkYOvCVRfYuTir8aUMj5sgwrXBqp4nqV7tvzdkc8N+fQFK5MF\/etpsZQe1lkmrm3NjjyhV1IIhq61JsB\/GMOWa2K84ugjdeVeYmiCqXTTOSzvAWjyQDJDAiyc8LvJ70=","country":"1","mobile":"15601632711","platform":"mobile"}',
                                  params["did"])
        js_datas = json.loads(js_result)
        data = js_datas.get("data")
        try:
            response = self.session.post(url, headers=self.headers, params=params, data=data)
            if response.status_code == 200:
                datas = response.json()
                print(datas)
                code = datas.get("code")
                self.token = datas.get("data").get("token")
                if code == 0:
                    logger.info(datas)
        except Exception as e:
            logger.error(e)

    def FeishuNotice(self):
        data = {"msg_type":"text","content":json.dumps({
            "text": "下单成功"
        })}
        response = self.session.post("https://open.feishu.cn/open-apis/bot/v2/hook/5e243fc2-ab6b-4ed7-8960-6a14e391224f", data=data)
        datas = response.json()
        print(datas)
    def Begin(self,token):
        nft_result = self.priceInfos(token)
        if nft_result:
            self.config(nft_result)
    def main(self):
        while True:
            for token in self.tokens:
                greenlet(self.Begin(token))
                time.sleep(2)


if __name__ == '__main__':
    nc = Nice()
    nc.main()
