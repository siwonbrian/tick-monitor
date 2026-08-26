"""
디스코드 '봇'을 이용해 특정 유저에게 DM(개인 메시지)을 보내는 헬퍼.

웹훅과 다르게, 봇 토큰(DISCORD_BOT_TOKEN)과 받는 사람의 유저 ID(DISCORD_USER_ID)가 필요하다.
동작 순서:
  1. 봇이 그 유저와의 DM 채널을 연다 (이미 있으면 기존 채널을 그대로 돌려줌)
  2. 그 채널에 메시지를 보낸다
둘 다 REST API 호출 한 번씩이라, 봇을 "계속 켜둘" 필요 없이 GitHub Actions처럼
가끔 실행되는 스크립트에서도 그대로 쓸 수 있다.
"""

import json
import sys
import urllib.error
import urllib.request

DISCORD_API = "https://discord.com/api/v10"


def send_discord_dm(bot_token: str, user_id: str, content: str) -> None:
    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json",
    }

    try:
        # 1. DM 채널 열기
        open_dm_req = urllib.request.Request(
            f"{DISCORD_API}/users/@me/channels",
            data=json.dumps({"recipient_id": user_id}).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(open_dm_req, timeout=15) as resp:
            channel = json.loads(resp.read().decode("utf-8"))
        channel_id = channel["id"]

        # 2. 메시지 전송
        send_req = urllib.request.Request(
            f"{DISCORD_API}/channels/{channel_id}/messages",
            data=json.dumps({"content": content}).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(send_req, timeout=15) as resp:
            resp.read()

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        print(f"경고: 디스코드 DM 전송 실패 ({e.code} {e.reason}) - {body}", file=sys.stderr)
