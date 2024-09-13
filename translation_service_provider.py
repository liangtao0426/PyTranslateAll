import configparser
import time
from datetime import datetime
import hashlib
import hmac
import json
from http.client import HTTPSConnection
from volcengine.ApiInfo import ApiInfo
from volcengine.Credentials import Credentials
from volcengine.ServiceInfo import ServiceInfo
from volcengine.base.Service import Service

class TranslationServiceProvider(Service):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def get_service_info(self, config_name):
        if "hs_api" in config_name:
            return self.get_volcengine_translation_service(config_name)
        elif "tx_api" in config_name:
            return self.get_tencent_translation_service(config_name)

    # 火山翻译的api服务
    def get_volcengine_translation_service(self, config_name):
        # 火山翻译相关设置
        access_key = self.config.get(config_name, 'access_key')
        secret_key = self.config.get(config_name, 'secret_key')
        service_info = self.config.get(config_name, 'service_info')
        content_type = self.config.get(config_name, 'content_type')
        credentials_name = self.config.get(config_name, 'credentials_name')
        region = self.config.get(config_name, 'region')
        api_action = self.config.get(config_name, 'api_action')
        api_version = self.config.get(config_name, 'api_version')

        service_info_obj = ServiceInfo(service_info, {'content-type': content_type},
                                       Credentials(access_key, secret_key, 'translate', 'cn-north-1'),
                                       300,
                                       300)
        query = {
            'Action': api_action,
            'Version': api_version
        }
        api_info = {
            'translate': ApiInfo('POST', '/', query, {}, {})
        }

        return Service(service_info_obj, api_info)

    # 腾讯翻译的api服务
    def get_tencent_translation_service(self, config_name):
        """
        返回一个类实例
        :param config_name:
        :return:
        """
        return TC3Client(self.config, config_name)

class TC3Client:
    def __init__(self, config, config_name):
        self.config = config[config_name]
        self.secret_id = self.config['secret_id']
        self.secret_key = self.config['secret_key']
        self.token = self.config.get('token', '')  # 提供默认值
        self.service = self.config['service']
        self.host = self.config['host']
        self.region = self.config['region']
        self.version = self.config['version']
        self.action = self.config['action']

    def sign(self, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def construct_request(self, text_list):
        # 获取当前时间戳
        timestamp = int(time.time())
        # 转换为 UTC 日期格式
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

        # 构造请求体
        payload = json.dumps({
            "Source": "zh",
            "Target": "en",
            "ProjectId": 0,
            "SourceTextList": text_list
        })

        # 组建请求头
        canonical_uri = "/"
        canonical_querystring = ""
        ct = "application/json; charset=utf-8"
        canonical_headers = f"content-type:{ct}\nhost:{self.host}\nx-tc-action:{self.action.lower()}\n"
        signed_headers = "content-type;host;x-tc-action"
        hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        canonical_request = (f"POST\n{canonical_uri}\n{canonical_querystring}\n"
                             f"{canonical_headers}\n{signed_headers}\n{hashed_request_payload}")

        # 签名字段
        credential_scope = f"{date}/{self.service}/tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = (f"TC3-HMAC-SHA256\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}")

        # 签名
        secret_date = self.sign(("TC3" + self.secret_key).encode("utf-8"), date)
        secret_service = self.sign(secret_date, self.service)
        secret_signing = self.sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        # 获取authorization
        authorization = (f"TC3-HMAC-SHA256 Credential={self.secret_id}/{credential_scope}, "
                         f"SignedHeaders={signed_headers}, Signature={signature}")

        # 请求头
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json; charset=utf-8",
            "Host": self.host,
            "X-TC-Action": self.action,
            "X-TC-Timestamp": str(timestamp),
            "X-TC-Version": self.version,
        }
        if self.region:
            headers["X-TC-Region"] = self.region
        if self.token:
            headers["X-TC-Token"] = self.token

        # 发送请求
        try:
            req = HTTPSConnection(self.host)
            req.request("POST", "/", headers=headers, body=payload.encode("utf-8"))
            resp = req.getresponse()
            return resp.read()  # 返回原始响应内容
        except Exception as err:
            return str(err)
