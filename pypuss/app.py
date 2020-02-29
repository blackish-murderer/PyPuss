import asyncio
import time as _time

import pypuss.base as base
import pypuss.utils as utils
import pypuss.constants as constants

class Master(base.Root):
    def __init__(self):
        base.Root.__init__(self)
        self.start_time = _time.time()
        self.muted = {}
        self.stalked_users = {}
        self.should_block_blues = False


    async def on_account_get_self(self, context):
        print("[info]" , "on_account_get_self")
        print("[info]" , "joined chatroom")

    async def on_chatroom_message_add(self, message):
        uuid = message.get("uuid")
        text = message.get("text")
        is_mine = uuid == self.myself["uuid"]

        print("[info]", "on_chatroom_message_add")
        print("[info]", uuid, text)

        text = text.replace(constants.PROFILE_URL, "")
        text = text.replace(constants.PROFILE_PATH, "")

        if is_mine:
            pass
        elif uuid in self.muted.keys():
            await self.moderator_remove_messages(uuid)
        elif utils.isuuid(text):
            await self.moderator_remove_messages(uuid)
            await self.moderator_remove_messages(text)

    async def on_chatroom_user_joined(self, user):
        uuid = user.get("uuid")
        name = user.get("name")

        print("[info]", "on_chatroom_user_joined")
        print("[info]", uuid, name)

        if self.should_block_blues and await utils.isblue(uuid):
            await self.moderator_ban_account(uuid)

    async def on_chatroom_user_left(self, user):
        uuid = user.get("uuid")
        name = user.get("name")

        print("[info]", "on_chatroom_user_left")
        print("[info]", uuid, name)

    async def on_conversation_message(self, message):
        uuid = message.get("uuid")
        text = message.get("text")
        is_mine = uuid == self.myself["uuid"]

        # print("[info]", "on_conversation_message")
        # print("[info]", uuid, text)

        text = text.replace(constants.PROFILE_URL, "")
        text = text.replace(constants.PROFILE_PATH, "")

        if is_mine:
            pass
        elif utils.startswith(text, "ban"):
            await self.ban(uuid, text)
        elif utils.startswith(text, "unban"):
            await self.unban(uuid, text)
        elif utils.startswith(text, "mute"):
            await self.mute(uuid, text)
        elif utils.startswith(text, "unmute"):
            await self.unmute(uuid, text)
        elif utils.startswith(text, "shield"):
            await self.shield(uuid, text)
        elif utils.startswith(text, "quote"):
            await self.quote(uuid, text)
        elif utils.startswith(text, "clear"):
            await self.clear(uuid, text)
        elif utils.startswith(text, "remove"):
            await self.remove(uuid, text)
        elif utils.startswith(text, "uptime"):
            await self.uptime(uuid, text)
        elif utils.startswith(text, "refresh"):
            await self.refresh(uuid, text)
        elif utils.startswith(text, "uuid"):
            await self.uuid(uuid, text)
        elif utils.startswith(text, "freeall"):
            await self.freeall(uuid, text)
        elif utils.startswith(text, "help"):
            await self.help(uuid, text)
        elif utils.isuuid(text):
            await self.uuid(uuid, text)
        else:
            await self.nocommand(uuid, text)

    async def ban(self, uuid, text):
        args = utils.strip(text, "ban")

        if len(args) <= 0:
            await self.conversation_message(uuid, "Just give me their nickname, I'll do my best to bust them.")
            await self.conversation_message(uuid, "Some are tricky and slippery though, which require a UUID.")
            await self.conversation_message(uuid, "more on UUIDs later or never!")
            return

        if utils.isuuid(args):
            await self.moderator_ban_account(args)
            await self.conversation_message(uuid, "Such an easy task, sqaushed the scum in a jiffy.")
            return

        users = self.users.values()
        user = utils.find_best_match(users, "name", args)
        if user is not None:
            await self.moderator_ban_account(user["uuid"])
            await self.conversation_message(uuid, "I found a match and banned this scum: " + user["name"])
            return

        await self.conversation_message(uuid, "They seem not to be around, I might ban them once they are back.")

    async def unban(self, uuid, text):
        args = utils.strip(text, "unban")

        if len(args) <= 0:
            await self.conversation_message(uuid, "Just give me their nickname, I'll do my best to free them.")
            await self.conversation_message(uuid, "Some are tricky and slippery though, which require a UUID.")
            await self.conversation_message(uuid, "more on UUIDs later or never!")
            return

        if utils.isuuid(args):
            await self.moderator_unban_account(args)
            await self.conversation_message(uuid, "Not sure if it was the correct decision.")
            return

        users = self.banned.values()
        user = utils.find_best_match(users, "name", args)
        if user is not None:
            await self.moderator_unban_account(user["uuid"])
            await self.conversation_message(uuid, "I found a match and unbanned this once-a-scum prick: " + user["name"])
            return

        await self.conversation_message(uuid, "I can't recall if I banned this user before.")

    async def mute(self, uuid, text):
        args = utils.strip(text, "mute")

        if len(args) <= 0:
            await self.conversation_message(uuid, "Toss me a nickname and you'll see no more of their gibberish words.")
            await self.conversation_message(uuid, "Some are tricky and slippery though, which require a UUID.")
            await self.conversation_message(uuid, "more on UUIDs later or never!")
            return

        if utils.isuuid(args):
            user = await self.account_get_target(args)
            user = { "name": user["name"], "uuid": user["uuid"] }
            self.muted[args] = user
            await self.conversation_message(uuid, "Taped their mouth, till they suffocate.")
            return

        users = self.users.values()
        user = utils.find_best_match(users, "name", args)
        if user is not None:
            self.muted[user["uuid"]] = user
            await self.conversation_message(uuid, "I found a match and taped this prick's mouth: " + user["name"])
            return

        await self.conversation_message(uuid, "I don't think they are around anymore.")

    async def unmute(self, uuid, text):
        args = utils.strip(text, "unmute")

        if len(args) <= 0:
            await self.conversation_message(uuid, "Want to remove the tape on someone's mouth? Give me their nickname!")
            await self.conversation_message(uuid, "Some are tricky and slippery though, which require a UUID.")
            await self.conversation_message(uuid, "more on UUIDs later or never!")
            return

        if utils.isuuid(args):
            self.muted.pop(args, None)
            await self.conversation_message(uuid, "I think they can move their jaws now.")
            return

        users = self.muted.values()
        user = utils.find_best_match(users, "name", args)
        if user is not None:
            self.muted.pop(user["uuid"])
            await self.conversation_message(uuid, "I found a match and untaped this prick's mouth: " + user["name"])
            return

        await self.conversation_message(uuid, "I don't recall taping their mouth before.")

    async def shield(self, uuid, text):
        args = utils.strip(text, "shield")

        if len(args) <= 0:
            await self.conversation_message(uuid, "This will block blueheads from accessing the room.")
            await self.conversation_message(uuid, "Should I put my shield \"on\" or \"off\"?")
            return

        if utils.ismatch(args, "on"):
            self.should_block_blues = True
            await self.conversation_message(uuid, "I'll fend them off as long as I live")
            return

        if utils.ismatch(args, "off"):
            self.should_block_blues = False
            await self.conversation_message(uuid, "I could keep them away for years")
            return

        await self.conversation_message(uuid, "What with my shield? Put it \"on\" or \"off\"?")

    async def quote(self, uuid, text):
        args = utils.strip(text, "quote")

        if len(args) <= 0:
            await self.conversation_message(uuid, "Everyone likes to fool the others.")
            await self.conversation_message(uuid, "Give me a text and I will post it right away.")
            return

        if len(args) > 0:
            await self.chatroom_message(args)
            await self.conversation_message(uuid, "It's fun fooling people!")
            return

        await self.conversation_message(uuid, "Did this really happen? that's strange.")

    async def clear(self, uuid, text):
        args = utils.strip(text, "clear")

        if len(args) > 0:
            await self.conversation_message(uuid, "As the name suggests this will clear every text in the chatroom.")
            return

        uuids = self.texts.keys()
        for _uuid in uuids:
            await self.moderator_remove_messages(_uuid)

        await self.conversation_message(uuid, "I suppose the room is plain white now.")

    async def remove(self, uuid, text):
        args = utils.strip(text, "remove")

        if len(args) <= 0:
            await self.conversation_message(uuid, "Just give me their nickname, I'll do my best to wipe them.")
            await self.conversation_message(uuid, "Some are tricky and slippery though, which require a UUID.")
            await self.conversation_message(uuid, "more on UUIDs later or never!")
            return

        if utils.isuuid(args):
            await self.moderator_remove_messages(args)
            await self.conversation_message(uuid, "I've just removed some text.")
            return

        users = self.texts.values()
        user = utils.find_best_match(users, "name", args)
        if user is not None:
            await self.moderator_remove_messages(user["uuid"])
            await self.conversation_message(uuid, "I wiped some texts written by this fellow: " + user["name"])
            return

        await self.conversation_message(uuid, "They have no texts here.")

    async def uptime(self, uuid, text):
        args = utils.strip(text, "uptime")

        if len(args) > 0:
            await self.conversation_message(uuid, "Curious how long I've been watching here?")
            await self.conversation_message(uuid, "Ask me for uptime.")
            return

        current_time = _time.time()
        uptime_string = utils.format_period(current_time - self.start_time)
        await self.conversation_message(uuid, "Here is my uptime: " + uptime_string)

    async def refresh(self, uuid, text):
        args = utils.strip(text, "refresh")

        if len(args) > 0:
            await self.conversation_message(uuid, "I am such a flimsy craft and brimful of bugs!")
            await self.conversation_message(uuid, "If I go buggy, a refresh might patch me up.")
            return

        await self.account_get_self()
        await self.conversation_message(uuid, "I feel so lively now.")

    async def uuid(self, uuid, text):
        args = text if utils.isuuid(text) else utils.strip(text, "uuid")

        if utils.isuuid(args):
            await self.conversation_message(uuid, "Yes! Here is the UUID of the user you asked for!")
            await self.conversation_message(uuid, args)
            return

        await self.conversation_message(uuid, "Speaking of UUIDs, they are unique IDs for each user.")
        await self.conversation_message(uuid, "If you are looking for someone's UUID, just drag and drop their avatar in the textbox below.")
        await self.conversation_message(uuid, "Posting the link in chatroom will wipe your texts in addition to the texts from the owner of the avatar you dropped.")

    async def freeall(self, uuid, text):
        args = utils.strip(text, "freeall")

        if len(args) > 0:
            await self.conversation_message(uuid, "This will unban everyone in my list")
            return

        uuids = self.banned.keys()
        for _uuid in uuids:
            await self.moderator_unban_account(_uuid)

        await self.conversation_message(uuid, "I freed them all!")

    async def help(self, uuid, text):
        await self.conversation_message(uuid, "Here is the list of commands you may use to interact with me.")
        await self.conversation_message(uuid, "Ban, Unban, Mute, Unmute, Shield, Quote, Clear, Remove, Uptime, Refresh, UUID")
        await self.conversation_message(uuid, "Just try them out, I'll help you with their usage, bear in mind case don't matter.")

    async def nocommand(self, uuid, text):
        commands = [{"name": "ban"}, {"name": "unban"}, {"name": "mute"}, {"name": "unmute"}, {"name": "shield"}, {"name": "quote"}, {"name": "clear"}, {"name": "remove"}, {"name": "uptime"}, {"name": "refresh"}, {"name": "uuid"}]

        words = text.split()
        if len(words) > 0:
            guess = utils.find_best_match(commands, "name", words[0], 0.1)
            if guess is not None:
                await self.conversation_message(uuid, "Did you mean \"" + guess["name"] + "\"? Do try again!")
                return

        await self.conversation_message(uuid, "I'm supposed to talk you, but you are boring me already.")
        await self.conversation_message(uuid, "Or it's me boring you, either way, BUGGER OFF!")
