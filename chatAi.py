import asyncio
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
        """Initialize the client and find the friend"""
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
        """Send message to bot"""
        await self.client.send_message(self.friend, text)
        print(f"You: {text}")
        self.waiting_for_reply = True

    async def handle_incoming_messages(self):
        """Set up handler for incoming messages from bot"""
        @self.client.on(events.NewMessage(from_users=self.friend))
        async def handler(event):
            # Add bot message to queue
            await self.message_queue.put(f"Kyra: {event.message.text}")
            self.waiting_for_reply = False
        
        print("👂 Listening for messages...")
        await self.client.run_until_disconnected()

    async def process_message_queue(self):
        """Process messages from queue and display them"""
        while True:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(self.message_queue.get(), timeout=0.1)
                print(f"\n{message}")
                if not self.waiting_for_reply:
                    print("You: ", end="", flush=True)
            except asyncio.TimeoutError:
                # No message in queue, continue
                continue

async def main():
    chat = TelegramChat()
    
    if not await chat.setup():
        return

    print(f"\n💬 Starting chat with {chat.friend.first_name}")
    print("Type your messages and press Enter to send")
    print("Press Ctrl+C to exit\n")
    print("You: ", end="", flush=True)

    # Start message handler and queue processor
    message_task = asyncio.create_task(chat.handle_incoming_messages())
    queue_task = asyncio.create_task(chat.process_message_queue())
    
    try:
        while True:
            # Async input without blocking
            message = await asyncio.get_event_loop().run_in_executor(
                None, input, ""
            )
            if message.strip():
                await chat.send_message(message)
                # Print "You:" prompt only if not waiting for reply
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
