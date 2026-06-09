import os
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

DATA_FILE = "data.json"


def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(chat_id):
    data = load_data()

    if str(chat_id) not in data:
        data[str(chat_id)] = {
            "salary": 0,
            "tip": 0,
            "history": []
        }

    return data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💰 딜러 정산봇\n\n"
        "입력 예시: 2/7\n\n"
        "설명서 를 입력하면 사용법을 확인할 수 있습니다."
    )


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    text = update.message.text.strip()

    data = get_user(chat_id)

    if text == "설명서":
        await update.message.reply_text(
            "📖 딜러 정산봇 사용법\n\n"
            "입력 형식\n"
            "수익/팁\n\n"
            "예시\n"
            "2/7\n"
            "3/5\n"
            "10/10\n\n"
            "━━━━━━━━━━\n\n"
            "합계\n"
            "현재까지 누적된 시급, 팁, 합계를 확인합니다.\n\n"
            "━━━━━━━━━━\n\n"
            "내역\n"
            "입력한 모든 정산 내역을 확인합니다.\n\n"
            "━━━━━━━━━━\n\n"
            "취소\n"
            "가장 최근 입력한 내역을 삭제합니다.\n\n"
            "━━━━━━━━━━\n\n"
            "종료\n"
            "오늘 정산을 마감하고 데이터를 초기화합니다.\n\n"
            "━━━━━━━━━━\n\n"
            "초기화\n"
            "현재 데이터를 모두 삭제합니다."
        )
        return

    if text == "합계":
        user = data[chat_id]

        await update.message.reply_text(
            f"누적 시급: {user['salary']}\n"
            f"누적 팁: {user['tip']}\n"
            f"누적 합계: {user['salary'] + user['tip']}"
        )
        return

    if text == "내역":
        user = data[chat_id]

        if not user["history"]:
            await update.message.reply_text("내역이 없습니다.")
            return

        msg = []

        for i, item in enumerate(user["history"], start=1):
            msg.append(
                f"{i}. {item['wage']}/{item['tip']} = {item['total']}"
            )

        await update.message.reply_text("\n".join(msg))
        return

    if text == "취소":
        user = data[chat_id]

        if not user["history"]:
            await update.message.reply_text("삭제할 내역이 없습니다.")
            return

        last = user["history"].pop()

        user["salary"] -= last["wage"]
        user["tip"] -= last["tip"]

        save_data(data)

        await update.message.reply_text(
            f"삭제 완료\n\n"
            f"삭제된 내역: {last['wage']}/{last['tip']}"
        )
        return

    if text == "초기화":
        data[chat_id] = {
            "salary": 0,
            "tip": 0,
            "history": []
        }

        save_data(data)

        await update.message.reply_text("초기화 완료")
        return

    if text == "종료":
        user = data[chat_id]

        total = user["salary"] + user["tip"]

        await update.message.reply_text(
            f"오늘의 총 일당\n\n"
            f"총 시급: {user['salary']}\n"
            f"총 팁: {user['tip']}\n"
            f"최종 합계: {total}\n\n"
            f"정산 종료 및 초기화 완료"
        )

        data[chat_id] = {
            "salary": 0,
            "tip": 0,
            "history": []
        }

        save_data(data)
        return

    if "/" in text:
        try:
            wage, tip = map(float, text.split("/"))

            user = data[chat_id]

            user["salary"] += wage
            user["tip"] += tip

            user["history"].append({
                "wage": wage,
                "tip": tip,
                "total": wage + tip
            })

            save_data(data)

            await update.message.reply_text(
                f"추가 완료\n\n"
                f"이번 정산: {wage + tip}\n\n"
                f"누적 시급: {user['salary']}\n"
                f"누적 팁: {user['tip']}\n"
                f"누적 합계: {user['salary'] + user['tip']}"
            )

        except:
            await update.message.reply_text(
                "입력 형식: 2/7"
            )


TOKEN = os.getenv("BOT_TOKEN")

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle
    )
)

app.run_polling()
