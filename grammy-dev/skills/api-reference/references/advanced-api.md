# grammY — Advanced API Reference

Less-common Bot API methods, grouped. Open the full method docs at https://grammy.dev/ref/core/api for parameter details.

## Web Apps & Mini Apps

```typescript
bot.api.setChatMenuButton(other?);
bot.api.getChatMenuButton(other?);
bot.api.answerWebAppQuery(webAppQueryId, result);
bot.api.setMyDefaultAdministratorRights(other?);
bot.api.getMyDefaultAdministratorRights(other?);
```

`reply_markup: { web_app: { url } }` on any keyboard button launches a Mini App. Use `Telegram.WebApp.sendData(...)` from the web app side to post back data — your bot receives it as `web_app_data` on a message.

## Passport (legacy KYC)

```typescript
bot.api.setPassportDataErrors(userId, errors[]);
```

Now largely superseded by Mini Apps + Telegram Login.

## Gift transactions

```typescript
bot.api.sendGift(userId, giftId, other?);
bot.api.giftPremiumSubscription(userId, monthCount, starCount, other?);
bot.api.verifyUser(userId, other?);
bot.api.verifyChat(chatId, other?);
bot.api.removeUserVerification(userId);
bot.api.removeChatVerification(chatId);
```

## Paid media (channels)

```typescript
bot.api.sendPaidMedia(chatId, starCount, media[], other?);
```

Channels can attach a Star price to media — viewers unlock by paying.

## Chat backgrounds

```typescript
bot.api.setChatPhoto(chatId, photo);
bot.api.deleteChatPhoto(chatId);
```

## Boosts

```typescript
bot.api.getUserChatBoosts(chatId, userId);
```

## Available reactions

```typescript
bot.api.setMessageReaction(chatId, messageId, other?);  // reactions: ReactionType[]
```

`ReactionType` is `{ type: "emoji", emoji }` or `{ type: "custom_emoji", custom_emoji_id }`.

## Logging out of cloud Bot API server

Required before switching to a self-hosted Bot API server:

```typescript
await bot.api.logOut();
await bot.api.close();
```

## Bulk admin actions

```typescript
bot.api.forwardMessages(chatId, fromChatId, messageIds[], other?);
bot.api.copyMessages(chatId, fromChatId, messageIds[], other?);
bot.api.deleteMessages(chatId, messageIds[]);
bot.api.editGeneralForumTopic(chatId, name);
```

## Telegram Business advanced

```typescript
bot.api.setBusinessAccountGiftSettings(businessConnectionId, other?);
bot.api.getOwnedStickerSets(businessConnectionId);
```

## Edited content

```typescript
bot.api.editMessageLiveLocation(chatId, messageId, latitude, longitude, other?);
bot.api.stopMessageLiveLocation(chatId, messageId, other?);
```

## Chat boost (channel growth)

```typescript
bot.api.getUserChatBoosts(chatId, userId);
```

For the canonical source, always cross-check https://core.telegram.org/bots/api — the grammY TS client tracks Bot API changes within days.
