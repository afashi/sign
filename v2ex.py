# -*- coding: utf-8 -*-
"""
cron: 1 0 0 * * *
new Env('V2EX');
"""
import os
import re

import requests
import urllib3

from notify import send

urllib3.disable_warnings()


def sign(headers):
    msg = []
    response = requests.get(url="https://www.v2ex.com/mission/daily", headers=headers, verify=False)
    pattern = (
        r"<input type=\"button\" class=\"super normal button\""
        r" value=\".*?\" onclick=\"location\.href = \'(.*?)\';\" />"
    )
    urls = re.findall(pattern=pattern, string=response.text)
    url = urls[0] if urls else None
    if url is None:
        return [{"name": "签到失败", "value": "cookie 可能过期"}]
    elif url != "/balance":
        headers.update({"Referer": "https://www.v2ex.com/mission/daily"})
        data = {"once": url.split("=")[-1]}
        _ = requests.get(
            url="https://www.v2ex.com" + url,
            verify=False,
            headers=headers,
            params=data,
        )
    response = requests.get(url="https://www.v2ex.com/balance", headers=headers, verify=False)
    total = re.findall(
        pattern=r"<td class=\"d\" style=\"text-align: right;\">(\d+\.\d+)</td>",
        string=response.text,
    )
    total = total[0] if total else "签到失败"
    today = re.findall(
        pattern=r'<td class="d"><span class="gray">(.*?)</span></td>',
        string=response.text,
    )
    today = today[0] if today else "签到失败"
    username = re.findall(
        pattern=r"<a href=\"/member/.*?\" class=\"top\">(.*?)</a>",
        string=response.text,
    )
    username = username[0] if username else "用户名获取失败"
    msg += [
        {"name": "帐号信息", "value": username},
        {"name": "今日签到", "value": today},
        {"name": "帐号余额", "value": total},
    ]
    response = requests.get(url="https://www.v2ex.com/mission/daily", headers=headers, verify=False)
    data = re.findall(
        pattern=r"<div class=\"cell\">(.*?)天</div>", string=response.text
    )
    data = data[0] + "天" if data else "获取连续签到天数失败"
    msg += [
        {"name": "签到天数", "value": data},
    ]
    return msg


def start(cookie_str):
    max_retries = 3
    retries = 0
    msg = ""
    headers = {
        "cookie": cookie_str,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    msg += "第{}次执行签到\n".format(str(retries + 1))
    msg1 = sign(headers=headers)
    msg = "\n".join([f"{one.get('name')}: {one.get('value')}" for one in msg1])
    send("V2EX 签到结果", msg)
    return msg


if __name__ == "__main__":
    cookie = os.getenv("V2EX_COOKIE")
    start(cookie)
