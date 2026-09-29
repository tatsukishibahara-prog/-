#!/usr/bin/env python3
"""毎週月曜の定例アジェンダを Chatwork に投稿する。

月曜の日付が 1〜21 日なら第1〜3週用、22 日以降なら第4〜5週（月末最終週）用のアジェンダを送る。
API トークンは環境変数 CHATWORK_API_TOKEN から読む。

使い方:
  python3 send_weekly_agenda.py            # 今日（日本時間）の日付で送信
  python3 send_weekly_agenda.py --dry-run  # 送信せず本文を表示
  python3 send_weekly_agenda.py --date 2026-10-26 --dry-run
"""
import argparse
import datetime
import os
import sys
import urllib.parse
import urllib.request

ROOM_ID = "321757507"
MENTIONS = "[To:9250811]坂本景都さん\n[To:11229029]原崎寛也さん"

AGENDA_WEEK_1_3 = """\
- 先週決定した動きの報告
- 今週の具体的な行動報告
- 翌週の具体的な行動計画
- 当月・翌月・翌々月の売上進捗
- アポ/アプローチ状況（月間商談KPI進捗）※結果
- 重点クライアント"""

AGENDA_WEEK_4_5 = """\
ゴール：当月の学びを翌月の行動に変える
1. 先週決定した動きの報告
2. 当月の着地と商談KPI結果
3. 成功事例・失注事例の共有
4. 翌月・翌々月の売上見通しと打ち手
5. 重点クライアントの翌月方針"""

JST = datetime.timezone(datetime.timedelta(hours=9))


def build_message(date: datetime.date) -> str:
    if date.day >= 22:
        label, agenda = "第4-5週目（月末最終週）", AGENDA_WEEK_4_5
    else:
        label, agenda = "第1-3週目", AGENDA_WEEK_1_3
    title = f"{date.month}/{date.day} 定例のアジェンダ（{label}）"
    return f"{MENTIONS}\n[info][title]{title}[/title]{agenda}[/info]"


def post(body: str, token: str) -> None:
    req = urllib.request.Request(
        f"https://api.chatwork.com/v2/rooms/{ROOM_ID}/messages",
        data=urllib.parse.urlencode({"body": body}).encode(),
        headers={"X-ChatWorkToken": token},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        print(res.status, res.read().decode())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD（省略時は日本時間の今日）")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    date = (datetime.date.fromisoformat(args.date) if args.date
            else datetime.datetime.now(JST).date())
    body = build_message(date)
    if args.dry_run:
        print(body)
        return 0

    token = os.environ.get("CHATWORK_API_TOKEN")
    if not token:
        print("CHATWORK_API_TOKEN が設定されていません", file=sys.stderr)
        return 1
    post(body, token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
