---
name: api-reference
description: This skill should be used when the user asks for "grammY API reference", "Bot API method", "ctx.api signature", "sendMessage parameters", "answerCallbackQuery", "editMessageText", "getChat", "specific Telegram Bot API endpoint", or needs precise method signatures and parameter details for the grammY Bot API client.
disable-model-invocation: true
---

# grammY — Bot API Reference

Curated reference of the most-used Bot API methods as called via `bot.api.*` / `ctx.api.*`. For exhaustive low-traffic methods, open `references/advanced-api.md`.

All methods return Promises. Signatures show the grammY shape — the third positional argument (`other`) holds optional Bot API parameters.

## Messages

```typescript
bot.api.sendMessage(chatId, text, other?, signal?);
bot.api.forwardMessage(chatId, fromChatId, messageId, other?);
bot.api.forwardMessages(chatId, fromChatId, messageIds[], other?);
bot.api.copyMessage(chatId, fromChatId, messageId, other?);
bot.api.copyMessages(chatId, fromChatId, messageIds[], other?);
bot.api.editMessageText(chatId, messageId, text, other?);
bot.api.editMessageCaption(chatId, messageId, other?);   // caption inside other
bot.api.editMessageMedia(chatId, messageId, media, other?);
bot.api.editMessageReplyMarkup(chatId, messageId, other?);
bot.api.editMessageLiveLocation(chatId, messageId, latitude, longitude, other?);
bot.api.stopMessageLiveLocation(chatId, messageId, other?);
bot.api.deleteMessage(chatId, messageId);
bot.api.deleteMessages(chatId, messageIds[]);
bot.api.setMessageReaction(chatId, messageId, other?);   // reactions in other
bot.api.pinChatMessage(chatId, messageId, other?);
bot.api.unpinChatMessage(chatId, other?);                // messageId optional → unpin last
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
bot.api.sendDice(chatId, other?);
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
bot.api.getChatMembersCount(chatId);
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
bot.api.setMyName(other?);                 // name + language_code in other
bot.api.getMyName(other?);
bot.api.setMyDescription(other?);
bot.api.getMyDescription(other?);
bot.api.setMyShortDescription(other?);
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
bot.api.createInvoiceLink(title, description, payload, currency, prices[], other?);
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
bot.api.uploadStickerFile(userId, sticker, stickerFormat);
bot.api.createNewStickerSet(userId, name, title, stickers[], other?);
bot.api.addStickerToSet(userId, name, sticker);
bot.api.setStickerPositionInSet(sticker, position);
bot.api.deleteStickerFromSet(sticker);
bot.api.replaceStickerInSet(userId, name, oldSticker, sticker);
bot.api.setStickerEmojiList(sticker, emojiList[]);
bot.api.setStickerKeywords(sticker, other?);
bot.api.setStickerMaskPosition(sticker, other?);
bot.api.setStickerSetTitle(name, title);
bot.api.setStickerSetThumbnail(name, userId, other?);
bot.api.deleteStickerSet(name);
bot.api.setCustomEmojiStickerSetThumbnail(name, other?);
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

## Telegram Business

```typescript
bot.api.getBusinessConnection(businessConnectionId);
bot.api.sendMessage(chatId, text, { business_connection_id, ... });
bot.api.readBusinessMessage(businessConnectionId, chatId, messageId);
bot.api.deleteBusinessMessages(businessConnectionId, messageIds[]);
bot.api.setBusinessAccountName(businessConnectionId, firstName, other?);
bot.api.setBusinessAccountBio(businessConnectionId, other?);
bot.api.setBusinessAccountUsername(businessConnectionId, other?);
bot.api.setBusinessAccountProfilePhoto(businessConnectionId, photo, other?);
bot.api.removeBusinessAccountProfilePhoto(businessConnectionId, other?);
bot.api.transferBusinessAccountStars(businessConnectionId, starCount);
bot.api.getBusinessAccountStarBalance(businessConnectionId);
bot.api.getBusinessAccountGifts(businessConnectionId, other?);
bot.api.convertGiftToStars(businessConnectionId, ownedGiftId);
bot.api.upgradeGift(businessConnectionId, ownedGiftId, other?);
bot.api.transferGift(businessConnectionId, ownedGiftId, newOwnerChatId, other?);
bot.api.postStory(businessConnectionId, content, activePeriod, other?);
bot.api.editStory(businessConnectionId, storyId, content, other?);
bot.api.deleteStory(businessConnectionId, storyId);
```

For full advanced API (web_apps, mini-apps, passports, gift links, paid media, etc.) open `references/advanced-api.md`.
