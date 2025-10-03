import asyncio
import subprocess
from telethon import TelegramClient, events

# ===== CONFIGURATION =====
API_ID = "28880964"
API_HASH = "a4e2146bceb7aa5c60f77756355d5b83"
FRIEND_USERNAME = "@Kyra_AIbot"
SESSION_FILE = "telegram_chat.session"
# =========================

class TelegramChat:
    def __init__(self):
        self.client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        self.friend = None
        self.message_queue = asyncio.Queue()
        self.waiting_for_reply = False

    async def setup(self):
        await self.client.start()
        print("🔐 Logging into Telegram...")

        me = await self.client.get_me()
        print(f"✅ Logged in as: {me.first_name} (@{me.username})")

        try:
            self.friend = await self.client.get_entity(FRIEND_USERNAME)
            print(f"✅ Found bot: {self.friend.first_name}")
        except Exception as e:
            print(f"❌ Could not find bot: {e}")
            return False
        return True

    async def send_message(self, text):
        await self.client.send_message(self.friend, text)
        print(f"You: {text}")
        self.waiting_for_reply = True

    async def handle_incoming_messages(self):
        @self.client.on(events.NewMessage(from_users=self.friend))
        async def handler(event):
            await self.message_queue.put(f"Kyra: {event.message.text}")
            self.waiting_for_reply = False

        print("👂 Listening for messages...")
        await self.client.run_until_disconnected()

    async def process_message_queue(self):
        while True:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=0.1)
                print(f"\n{message}")

                # Kyra चा reply आवाजात वाचवा
                if message.startswith("Kyra: "):
                    text_to_speak = message.replace("Kyra: ", "")
                    subprocess.run(["termux-tts-speak", text_to_speak])

                if not self.waiting_for_reply:
                    print("You: ", end="", flush=True)
            except asyncio.TimeoutError:
                continue

async def main():
    chat = TelegramChat()

    if not await chat.setup():
        return

    print(f"\n💬 Starting chat with {chat.friend.first_name}")
    print("Type your messages and press Enter to send")
    print("Press Ctrl+C to exit\n")
    print("You: ", end="", flush=True)

    message_task = asyncio.create_task(chat.handle_incoming_messages())
    queue_task = asyncio.create_task(chat.process_message_queue())

    try:
        while True:
            message = await asyncio.get_event_loop().run_in_executor(None, input, "")
            if message.strip():
                await chat.send_message(message)
                if not chat.waiting_for_reply:
                    print("You: ", end="", flush=True)
    except KeyboardInterrupt:
        print("\n👋 Disconnecting...")
    finally:
        message_task.cancel()
        queue_task.cancel()
        await chat.client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
