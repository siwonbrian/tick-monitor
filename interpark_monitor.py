"""
인터파크(NOL 티켓) 옥토버페스트 서울 2026 - 9/17 2부(playSeq 012) 잔여석 모니터링

REMAINSEAT API로 잔여석을 확인해서, 0석(매진) -> 1석 이상으로 바뀌는 순간
디스코드 봇 DM으로 알림을 보낸다.

필요한 환경변수: DISCORD_BOT_TOKEN, DISCORD_USER_ID
"""

import json
import os
import sys
import urllib.request

from discord_bot import send_discord_dm

GOODS_CODE = "26010333"
PLAY_SEQ = "012"  # 9/17 2부 (17:30)

REMAINSEAT_URL = (
    f"https://api-ticketfront.interpark.com/v1/goods/{GOODS_CODE}"
    f"/playSeq/PlaySeq/{PLAY_SEQ}/REMAINSEAT"
)
GOODS_LINK = f"https://tickets.interpark.com/goods/{GOODS_CODE}"

STATE_FILE = "state_interpark.json"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://tickets.interpark.com",
    "Referer": "https://tickets.interpark.com/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
    ),
}


def fetch_remain_seat() -> int:
    req = urllib.request.Request(REMAINSEAT_URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    remain_list = data.get("data", {}).get("remainSeat", [])
    if not remain_list:
        raise ValueError("remainSeat 필드가 비어있습니다 - API 응답 구조 확인 필요")
    return remain_list[0].get("remainCnt", 0)


def load_previous_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def main():
    bot_token = os.environ.get("DISCORD_BOT_TOKEN")
    user_id = os.environ.get("DISCORD_USER_ID")
    if not bot_token or not user_id:
        print("경고: DISCORD_BOT_TOKEN 또는 DISCORD_USER_ID 환경변수가 없습니다.", file=sys.stderr)

    old_state = load_previous_state()
    old_remain = old_state.get("remainCnt")

    new_remain = fetch_remain_seat()

    if old_remain is not None and old_remain == 0 and new_remain > 0:
        content = (
            "🎫 **인터파크 티켓 재입고!**\n"
            "옥토버페스트 서울 2026 - 9/17 2부(17:30)\n"
            f"잔여석: {new_remain}석\n"
            f"{GOODS_LINK}"
        )
        print(content)
        if bot_token and user_id:
            send_discord_dm(bot_token, user_id, content)
    else:
        print(f"변경 사항 없음. 현재 잔여석: {new_remain}")

    save_state({"remainCnt": new_remain})


if __name__ == "__main__":
    main()
