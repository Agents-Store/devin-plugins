---
name: api-reference
description: This skill should be used when the user asks for "grammY API reference", "Bot API method", "ctx.api signature", "sendMessage parameters", "answerCallbackQuery", "editMessageText", "getChat", "specific Telegram Bot API endpoint", or needs precise method signatures and parameter details for the grammY Bot API client.
disable-model-invocation: true
---

# grammY — Bot API Reference

Curated reference of the most-used Bot API methods as called via `bot.api.*` / `ctx.api.*`. For exhaustive low-traffic methods, open `references/advanced-api.md`.

All methods return Promises. Signatures show the grammY shape: required Bot API parameters are positional, in the order of the Bot API docs, and the trailing `other` object holds the optional ones. Verified against grammY 1.46 / `@grammyjs/types` 5.0 (Bot API 10.3). The types package took two major bumps with Bot API 10.x (4.0 on 2026-07-15, 5.0 on 2026-08-25); code that imports from `grammy/types` may need adjustments after upgrading.

## Messages

```typescript
bot.api.sendMessage(chatId, text, other?, signal?);
bot.api.forwardMessage(chatId, fromChatId, messageId, other?);
bot.api.forwardMessages(chatId, fromChatId, messageIds[], other?);
bot.api.copyMessage(chatId, fromChatId, messageId, other?);
bot.api.copyMessages(chatId, fromChatId, messageIds[], other?);
bot.api.editMessageText(chatId, messageId, textOrRichMessage, other?);
bot.api.editMessageCaption(chatId, messageId, other?);   // caption inside other
bot.api.editMessageMedia(chatId, messageId, media, other?);
bot.api.editMessageReplyMarkup(chatId, messageId, other?);
bot.api.editMessageLiveLocation(chatId, messageId, latitude, longitude, other?);
bot.api.stopMessageLiveLocation(chatId, messageId, other?);
bot.api.deleteMessage(chatId, messageId);
bot.api.deleteMessages(chatId, messageIds[]);
bot.api.setMessageReaction(chatId, messageId, reaction[], other?);   // ReactionType[]; [] clears
bot.api.pinChatMessage(chatId, messageId, other?);
bot.api.unpinChatMessage(chatId, messageId?, other?);                // messageId optional → unpin last
bot.api.unpinAllChatMessages(chatId);
```

Common `other` keys for text messages: `parse_mode`, `entities`, `link_preview_options`, `disable_notification`, `protect_content`, `reply_parameters`, `reply_markup`, `message_thread_id`, `business_connection_id`.

## Media send

```typescript
bot.api.sendPhoto(chatId, photo, other?, signal?);
bot.api.sendDocument(chatId, document, other?, signal?);
bot.api.sendVideo(chatId, video, other?, signal?);
bot.api.sendAudio(chatId, audio, other?, signal?);
bot.api.sendVoice(chatId, voice, other?, signal?);
bot.api.sendVideoNote(chatId, video_note, other?);
bot.api.sendSticker(chatId, sticker, other?);
bot.api.sendAnimation(chatId, animation, other?, signal?);
bot.api.sendMediaGroup(chatId, media[], other?);
bot.api.sendLocation(chatId, latitude, longitude, other?);
bot.api.sendVenue(chatId, latitude, longitude, title, address, other?);
bot.api.sendContact(chatId, phone_number, first_name, other?);
bot.api.sendDice(chatId, emoji, other?);                  // "🎲"|"🎯"|"🏀"|"⚽"|"🎳"|"🎰"
bot.api.sendPoll(chatId, question, options[], other?);
bot.api.sendChatAction(chatId, action);    // "typing"|"upload_photo"|"record_video"|...
```

`photo` / `document` / `video` accept `string` (file_id or URL) or `InputFile`. See `files-and-media`.

## Inline & callback

```typescript
bot.api.answerInlineQuery(inlineQueryId, results[], other?);
bot.api.answerCallbackQuery(callbackQueryId, other?);
bot.api.answerWebAppQuery(webAppQueryId, result);
bot.api.answerShippingQuery(shippingQueryId, ok, other?);
bot.api.answerPreCheckoutQuery(preCheckoutQueryId, ok, other?);
```

## Chats and members

```typescript
bot.api.getChat(chatId);
bot.api.getChatAdministrators(chatId);
bot.api.getChatMemberCount(chatId);
bot.api.getChatMember(chatId, userId);
bot.api.setChatTitle(chatId, title);
bot.api.setChatDescription(chatId, description);
bot.api.setChatPhoto(chatId, photo);              // InputFile
bot.api.deleteChatPhoto(chatId);
bot.api.setChatPermissions(chatId, permissions, other?);
bot.api.setChatStickerSet(chatId, stickerSetName);
bot.api.deleteChatStickerSet(chatId);
bot.api.exportChatInviteLink(chatId);
bot.api.createChatInviteLink(chatId, other?);
bot.api.editChatInviteLink(chatId, inviteLink, other?);
bot.api.revokeChatInviteLink(chatId, inviteLink);
bot.api.approveChatJoinRequest(chatId, userId);
bot.api.declineChatJoinRequest(chatId, userId);
bot.api.banChatMember(chatId, userId, other?);
bot.api.unbanChatMember(chatId, userId, other?);
bot.api.restrictChatMember(chatId, userId, permissions, other?);
bot.api.promoteChatMember(chatId, userId, other?);
bot.api.setChatAdministratorCustomTitle(chatId, userId, customTitle);
bot.api.leaveChat(chatId);
```

## Bot metadata

```typescript
bot.api.getMe();
bot.api.logOut();
bot.api.close();
bot.api.setMyName(name, other?);           // language_code in other
bot.api.getMyName(other?);
bot.api.setMyDescription(description, other?);
bot.api.getMyDescription(other?);
bot.api.setMyShortDescription(shortDescription, other?);
bot.api.getMyShortDescription(other?);
bot.api.setMyCommands(commands[], other?); // scope + language_code in other
bot.api.deleteMyCommands(other?);
bot.api.getMyCommands(other?);
bot.api.setChatMenuButton(other?);
bot.api.getChatMenuButton(other?);
bot.api.setMyDefaultAdministratorRights(other?);
bot.api.getMyDefaultAdministratorRights(other?);
```

## Files

```typescript
bot.api.getFile(fileId);                   // → File obj with file_path
// Download via: https://api.telegram.org/file/bot<TOKEN>/<file_path>
```

## Payments

```typescript
bot.api.sendInvoice(chatId, title, description, payload, currency, prices[], other?);
bot.api.createInvoiceLink(title, description, payload, providerToken, currency, prices[], other?);   // Stars: providerToken = "", currency "XTR"
bot.api.answerShippingQuery(shippingQueryId, ok, other?);
bot.api.answerPreCheckoutQuery(preCheckoutQueryId, ok, other?);
bot.api.refundStarPayment(userId, telegramPaymentChargeId);
bot.api.getMyStarBalance();
bot.api.getStarTransactions(other?);
```

## Webhooks

```typescript
bot.api.setWebhook(url, other?);           // certificate, allowed_updates, secret_token in other
bot.api.deleteWebhook(other?);             // drop_pending_updates in other
bot.api.getWebhookInfo();
```

## Stickers

```typescript
bot.api.getStickerSet(name);
bot.api.uploadStickerFile(userId, stickerFormat, sticker);
bot.api.createNewStickerSet(userId, name, title, stickers[], other?);
bot.api.addStickerToSet(userId, name, sticker);
bot.api.setStickerPositionInSet(sticker, position);
bot.api.deleteStickerFromSet(sticker);
bot.api.replaceStickerInSet(userId, name, oldSticker, sticker);
bot.api.setStickerEmojiList(sticker, emojiList[]);
bot.api.setStickerKeywords(sticker, keywords[]);
bot.api.setStickerMaskPosition(sticker, maskPosition?);
bot.api.setStickerSetTitle(name, title);
bot.api.setStickerSetThumbnail(name, userId, thumbnail, format);
bot.api.deleteStickerSet(name);
bot.api.setCustomEmojiStickerSetThumbnail(name, customEmojiId);
bot.api.getCustomEmojiStickers(customEmojiIds[]);
```

## Forum topics

```typescript
bot.api.createForumTopic(chatId, name, other?);
bot.api.editForumTopic(chatId, messageThreadId, other?);
bot.api.closeForumTopic(chatId, messageThreadId);
bot.api.reopenForumTopic(chatId, messageThreadId);
bot.api.deleteForumTopic(chatId, messageThreadId);
bot.api.unpinAllForumTopicMessages(chatId, messageThreadId);
bot.api.editGeneralForumTopic(chatId, name);
bot.api.closeGeneralForumTopic(chatId);
bot.api.reopenGeneralForumTopic(chatId);
bot.api.hideGeneralForumTopic(chatId);
bot.api.unhideGeneralForumTopic(chatId);
bot.api.unpinAllGeneralForumTopicMessages(chatId);
bot.api.getForumTopicIconStickers();
```

## Newer surface (Bot API 9.1 – 10.3)

### Streaming drafts and rich messages

```typescript
bot.api.sendMessageDraft(chatId, draftId, text, other?);          // private chats; show a reply while it is generated (9.3; every bot since 9.5)
bot.api.sendRichMessage(chatId, richMessage, other?);             // structured message: markdown, html or blocks (10.1+)
bot.api.sendRichMessageDraft(chatId, draftId, richMessage, other?);
bot.api.editMessageText(chatId, messageId, richMessage, other?);  // the text argument also accepts a rich message
bot.api.sendChecklist(businessConnectionId, chatId, checklist, other?);   // 9.1, Business
bot.api.editMessageChecklist(businessConnectionId, chatId, messageId, checklist, other?);
```

`richMessage` is an `InputRichMessage`: `{ markdown }`, `{ html }` or `{ blocks: [...] }`, plus an optional `media` list that the `tg://photo?id=` style links in markdown/html point to. 10.2 added the block types, 10.3 added buttons inside blocks, document blocks and expandable quotes. Both draft methods take `can_stop` / `keep_on_stop` (10.3): the user gets a stop button and the bot receives a `stopped_message_generation` update. Do not hand-roll the draft loop — `@grammyjs/stream` wraps it (see `plugins-catalog`).

### Ephemeral messages (10.2, reshaped in 10.3)

Messages — and commands — visible only to one user and the bot, mostly for group chats. Since 10.3 every send method takes one `ephemeral_message_parameters` object; the 10.2 pair `receiver_user_id` + `callback_query_id` at the top level no longer exists, so code copied from the 10.2 announcement fails type-checking on 1.46:

```typescript
await ctx.reply("Only you can see this", {
  ephemeral_message_parameters: {
    receiver_user_id: ctx.from!.id,
    callback_query_id: ctx.callbackQuery?.id,   // optional: answer a button press
    replace_callback_query_message: false,        // true: show it in place of the original message
  },
});
```

```typescript
bot.api.editEphemeralMessageText(chatId, receiverUserId, ephemeralMessageId, textOrRichMessage, other?);
bot.api.editEphemeralMessageMedia(chatId, receiverUserId, ephemeralMessageId, media, other?);
bot.api.editEphemeralMessageCaption(chatId, receiverUserId, ephemeralMessageId, caption, other?);
bot.api.editEphemeralMessageReplyMarkup(chatId, receiverUserId, ephemeralMessageId, other?);
bot.api.deleteEphemeralMessage(chatId, receiverUserId, ephemeralMessageId);
```

The sent `Message` carries `receiver_user` and `ephemeral_message_id`; `BotCommand.is_ephemeral` marks ephemeral commands (`@grammyjs/commands` 1.4 has `.ephemeral()`). Delivery is not guaranteed — the user may be offline.

### Managed bots (9.6)

The official way to create bots for users programmatically:

```typescript
new Keyboard().requestManagedBot("Create my bot", 1, { suggested_name: "My helper" });
// or a link: https://t.me/newbot/<manager_bot_username>/<suggested_bot_username>?name=<name>

bot.on("managed_bot", async (ctx) => { /* update: a managed bot was created or its token changed */ });
const token = await bot.api.getManagedBotToken(managedBotUserId);          // string
const next  = await bot.api.replaceManagedBotToken(managedBotUserId);      // revokes the old token
```

`getMe().can_manage_bots` tells you whether the bot may create other bots. Treat the returned tokens like any other secret — never log them or commit them.

### Polls (9.6, 10.0)

```typescript
await bot.api.sendPoll(chatId, "Which are fruits?", ["Apple", "Carrot", "Pear"], {
  type: "quiz",
  allows_multiple_answers: true,   // quizzes may have several correct answers since 9.6
  correct_option_ids: [0, 2],      // an array — it replaced the old single correct_option_id
  allows_revoting: false,
  shuffle_options: true,
});
```

`Poll.correct_option_id` is now `Poll.correct_option_ids`. 10.0 added media in polls and options and lowered the minimum to one option.

### Other additions worth knowing

```typescript
bot.api.getUserGifts(userId, other?);                // 9.3
bot.api.getChatGifts(chatId, other?);                // 9.3
bot.api.answerGuestQuery(guestQueryId, result);      // 10.0 guest mode: answer a `guest_message` update from a chat the bot is not in
bot.api.sendLivePhoto(chatId, livePhoto, photo, other?);   // 10.0
bot.api.setChatMemberTag(chatId, userId, tag);       // 9.5
bot.api.answerChatJoinRequestQuery(queryId, "approve" | "decline" | "queue");   // 10.1 join request queries
```

Other features worth knowing: the `date_time` message entity (9.5, `time()` in `@grammyjs/parse-mode`), payment subscription updates (`ctx.subscription`, 10.2) and the Mini App origin check — since 2026-07-20 Mini App methods only work from the Mini App's own origin unless the bot opted out in the BotFather Mini App.

## Telegram Business

```typescript
bot.api.getBusinessConnection(businessConnectionId);
bot.api.sendMessage(chatId, text, { business_connection_id, ... });
bot.api.readBusinessMessage(businessConnectionId, chatId, messageId);
bot.api.deleteBusinessMessages(businessConnectionId, messageIds[]);
bot.api.setBusinessAccountName(businessConnectionId, firstName, other?);
bot.api.setBusinessAccountBio(businessConnectionId, bio);
bot.api.setBusinessAccountUsername(businessConnectionId, username);
bot.api.setBusinessAccountProfilePhoto(businessConnectionId, photo, other?);
bot.api.removeBusinessAccountProfilePhoto(businessConnectionId, other?);
bot.api.transferBusinessAccountStars(businessConnectionId, starCount);
bot.api.getBusinessAccountStarBalance(businessConnectionId);
bot.api.getBusinessAccountGifts(businessConnectionId, other);   // other: exclude_unsaved, exclude_saved, exclude_unlimited, exclude_limited_upgradable, exclude_limited_non_upgradable (9.3 — replaced exclude_limited), exclude_from_blockchain, exclude_unique, sort_by_price, offset, limit
bot.api.convertGiftToStars(businessConnectionId, ownedGiftId);
bot.api.upgradeGift(businessConnectionId, ownedGiftId, other);
bot.api.transferGift(businessConnectionId, ownedGiftId, newOwnerChatId, starCount);
// Gift objects (9.3): UniqueGiftInfo.last_resale_star_count became last_resale_currency + last_resale_amount
bot.api.postStory(businessConnectionId, content, activePeriod, other);
bot.api.editStory(businessConnectionId, storyId, content, other);
bot.api.deleteStory(businessConnectionId, storyId);
```

For full advanced API (web_apps, mini-apps, passports, gift links, paid media, etc.) open `references/advanced-api.md`.
