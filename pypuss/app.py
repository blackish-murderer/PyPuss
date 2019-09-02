import asyncio
import time as _time

import pypuss.base as base
import pypuss.utils as utils

class Master(base.Root):
    def __init__(self):
        base.Root.__init__(self)
        self.start_time = _time.time()
        self.muted_uuids = []
        self.should_block_blueheads = False

    async def on_self_context(self, uuid, name, is_guest, is_online, is_deleted):
        print("[debug]", "on_self_context")

    async def on_text_add(self, uuid, name, body, time, is_mine):
        if is_mine:
            return
        if uuid in self.muted_uuids:
            await self.remove_text(uuid)

    async def on_pv_add(self, uuid, body, time, is_mine):
        if is_mine:
            pass
        elif utils.startswith(body, "ban"):
            await self.ban(uuid, body)
        elif utils.startswith(body, "unban"):
            await self.unban(uuid, body)
        elif utils.startswith(body, "mute"):
            await self.mute(uuid, body)
        elif utils.startswith(body, "unmute"):
            await self.unmute(uuid, body)
        elif utils.startswith(body, "stalk"):
            await self.stalk(uuid, body)
        elif utils.startswith(body, "unstalk"):
            await self.unstalk(uuid, body)
        elif utils.startswith(body, "shield"):
            await self.shield(uuid, body)
        elif utils.startswith(body, "quote"):
            await self.quote(uuid, body)
        elif utils.startswith(body, "clear"):
            await self.clear(uuid, body)
        elif utils.startswith(body, "remove"):
            await self.remove(uuid, body)
        elif utils.startswith(body, "notrace"):
            await self.notrace(uuid, body)
        elif utils.startswith(body, "uptime"):
            await self.uptime(uuid, body)
        elif utils.startswith(body, "refresh"):
            await self.refresh(uuid, body)
        elif utils.startswith(body, "freeall"):
            await self.freeall(uuid, body)
        elif utils.startswith(body, "help"):
            await self.help(uuid, body)
        else:
            await self.nocommand(uuid, body)

    async def ban(self, uuid, body):
        args = utils.strip(body, "ban")

        if len(args) <= 0:
            await self.add_pv(uuid, "Just give me their nickname, I'll do my best to bust them.")
            await self.add_pv(uuid, "Some are tricky and slippery though, which require a UUID.")
            await self.add_pv(uuid, "more on UUIDs later or never!")
            return

        if utils.isuuid(args):
            await self.add_ban(args)
            await self.add_pv(uuid, "Such an easy task, sqaushed the scum in a jiffy.")
            return

        users = self.storage["chatroomContext"]["data"]["users"].values()
        user = utils.best_match(users, "username", args)
        if user is not None:
            await self.add_ban(user["userUuid"])
            await self.add_pv(uuid, "I found a match and banned this scum: " + user["username"])
            return

        await self.add_pv(uuid, "They seem not to be around, I might ban them once they are back.")

    async def unban(self, uuid, body):
        args = utils.strip(body, "unban")

        if len(args) <= 0:
            await self.add_pv(uuid, "Just give me their nickname, I'll do my best to free them.")
            await self.add_pv(uuid, "Some are tricky and slippery though, which require a UUID.")
            await self.add_pv(uuid, "more on UUIDs later or never!")
            return

        if utils.isuuid(args):
            await self.remove_ban(args)
            await self.add_pv(uuid, "Not sure if it was the correct decision.")
            return

        users = await self.batch_context_users(self.storage["chatroomBannedUuids"])
        user = utils.best_match(users, "username", args)
        if user is not None:
            await self.remove_ban(user["userUuid"])
            await self.add_pv(uuid, "I found a match and unbanned this once-a-scum prick: " + user["username"])
            return

        await self.add_pv(uuid, "I can't recall if I banned this user before.")

    async def mute(self, uuid, body):
        print('[debug]', 'before execution mute')
        print(self.muted_uuids)
        args = utils.strip(body, "mute")

        if len(args) <= 0:
            await self.add_pv(uuid, "Toss me a nickname and you'll see no more of their gibberish words.")
            await self.add_pv(uuid, "Some are tricky and slippery though, which require a UUID.")
            await self.add_pv(uuid, "more on UUIDs later or never!")
            return

        if utils.isuuid(args):
            utils.append_to(self.muted_uuids, args)
            await self.add_pv(uuid, "Taped their mouth, till they suffocate.")
            print('[debug]', 'after execution of mute')
            print(self.muted_uuids)
            return

        users = self.storage["chatroomContext"]["data"]["users"].values()
        user = utils.best_match(users, "username", args)
        if user is not None:
            utils.append_to(self.muted_uuids, user["userUuid"])
            await self.add_pv(uuid, "I found a match and taped this prick: " + user["username"])
            print('[debug]', 'after execution of mute')
            print(self.muted_uuids)
            return

        await self.add_pv(uuid, "I don't think they are around anymore.")
        print('[debug]', 'after execution of mute')
        print(self.muted_uuids)

    async def unmute(self, uuid, body):
        print('[debug]', 'before execution of unmute')
        print(self.muted_uuids)
        args = utils.strip(body, "unmute")

        if len(args) <= 0:
            await self.add_pv(uuid, "Want to remove the tape on someone's mouth? Give me their nickname!")
            await self.add_pv(uuid, "Some are tricky and slippery though, which require a UUID.")
            await self.add_pv(uuid, "more on UUIDs later or never!")
            return

        if utils.isuuid(args):
            self.muted_uuids.remove(args)
            await self.add_pv(uuid, "Not sure if it was the correct decision.")
            print('[debug]', 'after execution of unmute')
            print(self.muted_uuids)
            return

        users = await self.batch_context_users(self.muted_uuids)
        user = utils.best_match(users, "username", args)
        if user is not None:
            self.muted_uuids.remove(user["userUuid"])
            await self.add_pv(uuid, "I found a match and untaped this once-a-scum prick: " + user["username"])
            print('[debug]', 'after execution of unmute')
            print(self.muted_uuids)
            return

        await self.add_pv(uuid, "I don't recall taping their mouth before.")
        print('[debug]', 'after execution of unmute')
        print(self.muted_uuids)

    async def stalk(self, uuid, body):
        args = utils.strip(body, "stalk")

        if len(args) <= 0:
            await self.add_pv(uuid, "This is a tricky feature I hesitate to equip myself with.")
            await self.add_pv(uuid, "It involves colleting information on a user's activity, like their login pattern and whatnots.")
            await self.add_pv(uuid, "If you like this feature to be enabled, let me know.")
            return

        await self.add_pv(uuid, "Dunno what to do with that, I think they patched it for decorations!")

    async def unstalk(self, uuid, body):
        args = utils.strip(body, "unstalk")

        if len(args) <= 0:
            await self.add_pv(uuid, "Well, this stops me from stalking someone I was asked to stalk before.")
            await self.add_pv(uuid, "It's disabled for now, just saying!")
            return

        await self.add_pv(uuid, "Dunno what to do with that, I think they patched it for decorations!")

    async def shield(self, uuid, body):
        args = utils.strip(body, "shield")

        if len(args) <= 0:
            await self.add_pv(uuid, "This will block blueheads from accessing the room.")
            await self.add_pv(uuid, "Should I put my shield \"on\" or \"off\"?")
            return

        if utils.ismatch(args, "on"):
            self.should_block_blueheads = True
            await self.add_pv(uuid, "I'll fend them off as long as I live")
            return

        if utils.ismatch(args, "off"):
            self.should_block_blueheads = False
            await self.add_pv(uuid, "I could keep them away for years")
            return

        await self.add_pv(uuid, "What with my shield? Put it \"on\" or \"off\"?")

    async def quote(self, uuid, body):
        args = utils.strip(body, "quote")

        if len(args) <= 0:
            await self.add_pv(uuid, "Everyone likes to fool the others.")
            await self.add_pv(uuid, "Give me a text and I will post it right away.")
            return

        if len(args) > 0:
            await self.add_text(args)
            await self.add_pv(uuid, "It's fun fooling people!")
            return

        await self.add_pv(uuid, "Did this really happen? that's strange.")

    async def clear(self, uuid, body):
        args = utils.strip(body, "clear")

        if len(args) > 0:
            await self.add_pv(uuid, "As the name suggests this will clear every text in the chatroom.")
            return

        uuids = utils.seek_unique_values(self.storage["chatroomContext"]["data"]["messages"], "userUuid")
        for _uuid in uuids:
            await self.remove_text(_uuid)

        await self.add_pv(uuid, "I suppose the room is plain white now.")

    async def remove(self, uuid, body):
        args = utils.strip(body, "remove")

        if len(args) <= 0:
            await self.add_pv(uuid, "Just give me their nickname, I'll do my best to wipe them.")
            await self.add_pv(uuid, "Some are tricky and slippery though, which require a UUID.")
            await self.add_pv(uuid, "more on UUIDs later or never!")
            return

        if utils.isuuid(args):
            await self.remove_text(args)
            await self.add_pv(uuid, "I've just removed some text.")
            return

        users = self.storage["chatroomContext"]["data"]["messages"]
        user = utils.best_match(users, "username", args)
        if user is not None:
            await self.remove_text(user["userUuid"])
            await self.add_pv(uuid, "I wiped some texts written by this fellow: " + user["username"])
            return

        await self.add_pv(uuid, "They have no texts here.")

    async def notrace(self, uuid, body):
        args = utils.strip(body, "notrace")

        if len(args) <= 0:
            await self.add_pv(uuid, "With this flag set, I will wipe your texts once you leave the room.")
            await self.add_pv(uuid, "If you use it a lot, it becomes a default routine.")
            await self.add_pv(uuid, "However, it's disabled for now")
            return

        await self.add_pv(uuid, "Dunno what to do with that, I think they patched it for decorations!")

    async def uptime(self, uuid, body):
        args = utils.strip(body, "uptime")

        if len(args) > 0:
            await self.add_pv(uuid, "Curious how long I've been watching here?")
            await self.add_pv(uuid, "Ask me for uptime.")
            return

        current_time = _time.time()
        uptime_string = utils.format_period(current_time - self.start_time)
        await self.add_pv(uuid, "Here is my uptime: " + uptime_string)

    async def refresh(self, uuid, body):
        args = utils.strip(body, "refresh")

        if len(args) > 0:
            await self.add_pv(uuid, "I am such a flimsy craft and brimful of bugs!")
            await self.add_pv(uuid, "If I go buggy, a refresh might patch me up.")
            return

        await self.context_self()
        await self.add_pv(uuid, "I feel so lively now.")

    async def freeall(self, uuid, body):
        args = utils.strip(body, "freeall")

        if len(args) > 0:
            await self.add_pv(uuid, "This will unban everyone in my list")
            return

        uuids = self.storage["chatroomBannedUuids"]
        for _uuid in uuids:
            await self.remove_ban(_uuid)

        await self.add_pv(uuid, "I freed them all!")

    async def help(self, uuid, body):
        await self.add_pv(uuid, "Here is the list of commands you may use to interact with me.")
        await self.add_pv(uuid, "Ban, Unban, Mute, Unmute, Stalk, Unstalk, Shield, Quote, Clear, Remove, Notrace, Uptime, Refresh")
        await self.add_pv(uuid, "Just try them out, I'll help you with their usage, bear in mind case don't matter.")

    async def nocommand(self, uuid, body):
        commands = ["ban", "unban", "mute", "unmute", "stalk", "unstalk", "shield", "quote", "clear", "remove", "notrace", "uptime", "refresh"]

        words = body.split()
        if len(words) > 0:
            guess = utils.best_match(commands, None, words[0], 0.1)
            if isinstance(guess, str):
                await self.add_pv(uuid, "Did you mean \"" + guess + "\"? Do try again!")
                return

        await self.add_pv(uuid, "I'm supposed to talk you, but you are boring me already.")
        await self.add_pv(uuid, "Or it's me boring you, either way, BUGGER OFF!")

    async def on_user_add(self, uuid, name, is_guest, is_online, is_deleted):
        print("[debug]", "on_user_add")
        print(uuid, name, is_guest, is_online, is_deleted)

        if (self.should_block_blueheads and (is_guest or await utils.isbluehead(uuid))):
            await self.add_ban(uuid)

#    async def greet(self):
#        last_time = 0
#        while True:
#            _body = "let's find a reasonable spam threshold"
#            _uuid = "3f9d8b29-cce3-4be8-b23b-bdfebaf4b941"
#            await asyncio.sleep(1)
#            uuid, body, time, is_mine = await self.add_pv(_uuid, _body)
#            try:
#                assert last_time == 0
#            except AssertionError:
#               print("[debug]", "it took", time - last_time, "ticks to post another text")
#            finally:
#                last_time = time

#TODO: handle SIGTERM and SIGINT
#TODO: move context storage to a seperate module [Done]
#TODO: modify Adaptor extention so that it works with async/await [Done]
