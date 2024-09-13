# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import time
from datetime import datetime
from http.client import HTTPSConnection



def sign(secret_key, date, service, string_to_sign):
    """计算签名的函数"""
    secret_date = hmac.new(("TC3" + secret_key).encode("utf-8"), date.encode("utf-8"), hashlib.sha256).digest()
    secret_service = hmac.new(secret_date, service.encode("utf-8"), hashlib.sha256).digest()
    secret_signing = hmac.new(secret_service, "tc3_request".encode("utf-8"), hashlib.sha256).digest()
    return hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()


def construct_request(secret_id, secret_key, token, service, host, region, version, action, payload):
    """构造请求的函数"""
    timestamp = int(time.time())
    date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

    # 步骤 1：拼接规范请求串
    http_request_method = "POST"
    canonical_uri = "/"
    canonical_querystring = ""
    ct = "application/json; charset=utf-8"
    canonical_headers = f"content-type:{ct}\nhost:{host}\nx-tc-action:{action.lower()}\n"
    signed_headers = "content-type;host;x-tc-action"
    hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    canonical_request = f"{http_request_method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{hashed_request_payload}"

    # 步骤 2：拼接待签名字符串
    credential_scope = f"{date}/{service}/tc3_request"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    string_to_sign = f"TC3-HMAC-SHA256\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"

    # 步骤 3：计算签名
    signature = sign(secret_key, date, service, string_to_sign)

    # 步骤 4：拼接 Authorization
    authorization = f"TC3-HMAC-SHA256 Credential={secret_id}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json; charset=utf-8",
        "Host": host,
        "X-TC-Action": action,
        "X-TC-Timestamp": timestamp,
        "X-TC-Version": version
    }
    if region:
        headers["X-TC-Region"] = region
    if token:
        headers["X-TC-Token"] = token

    try:
        req = HTTPSConnection(host)
        req.request("POST", "/", headers=headers, body=payload.encode("utf-8"))
        resp = req.getresponse()
        return resp.read()
    except Exception as err:
        return str(err)


secret_id = "AKIDgHpIauKpAbBfzxwnYCjAXq13ykUK7qRv"
secret_key = "TK3fDjDYmtwvrkZHtNjw1zoV6Z7Wmwyt"
token = ""
service = "tmt"
host = "tmt.tencentcloudapi.com"
region = "ap-shanghai"
version = "2018-03-21"
action = "TextTranslateBatch"

# 示例调用，将待翻译文本列表作为参数传入
text_list = ["测试", "方案"]
payload = json.dumps({
    "Source": "zh",
    "Target": "en",
    "ProjectId": 0,
    "SourceTextList": text_list
})

response = construct_request(secret_id, secret_key, token, service, host, region, version, action, payload) ['']
print(response)