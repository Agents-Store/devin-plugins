# Scenario: Echo bot

The smallest useful grammY bot. Long polling, replies any message back to the sender.

## Files

```
echo-bot/
├── package.json
├── tsconfig.json
├── .env.example
└── src/bot.ts
```

## package.json

```json
{
  "name": "echo-bot",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "tsx watch src/bot.ts",
    "start": "node --import tsx src/bot.ts"
  },
  "dependencies": {
    "grammy": "^1.42.0",
    "dotenv": "^16.4.5"
  },
  "devDependencies": {
    "tsx": "^4.19.0",
    "typescript": "^5.6.0",
    "@types/node": "^22.0.0"
  }
}
```

## tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "moduleResolution": "Bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"]
}
```

## .env.example

```text
BOT_TOKEN=123456:ABC-replace-me
```

## src/bot.ts

```typescript
import "dotenv/config";
import { Bot, GrammyError, HttpError } from "grammy";

const bot = new Bot(process.env.BOT_TOKEN!);

bot.command("start", (ctx) =>
  ctx.reply("Hi! I echo whatever you send me."));

bot.on("message:text", (ctx) => ctx.reply(`You said: ${ctx.message.text}`));

bot.on(":file", async (ctx) => {
  const file = await ctx.getFile();
  await ctx.reply(`Got a file. file_path=${file.file_path}, size=${file.file_size} bytes`);
});

bot.catch((err) => {
  const e = err.error;
  if (e instanceof GrammyError)       console.error("Bot API rejected:", e.description);
  else if (e instanceof HttpError)    console.error("Network problem:", e);
  else                                console.error("Unknown:", e);
});

bot.start();
```

## Run

```bash
cp .env.example .env  # paste your token
npm install
npm run dev
```

Send `/start` to your bot in Telegram. It should reply within a second.
