import time
from typing import List

from audiobot.command import CommandExecutor
from audiobot import Global_Command_Manager
from config import Config
from liveroom.message import DanmakuMessage
from audiobot.user import DanmakuUser
from sources.audio import BiliAudioSource, NeteaseMusicSource
from sources.audio.kuwo import KuwoMusicSource
from audiobot.audio import AudioItem


@Global_Command_Manager.register("diange")
class DiangeCommand(CommandExecutor):
    def __init__(self, audiobot):
        super().__init__(audiobot, ["点歌", "点b歌", "点w歌", "点k歌"])
        self.cooldowns = {}

    def process(self, command, dmkMsg: DanmakuMessage):
        msg: List[str] = dmkMsg.message.split(" ")
        if len(msg) < 2:
            return
        val = " ".join(msg[1::])
        if not (self.__hasPermission(dmkMsg) and self.__inCooldown(dmkMsg) and self.__notArriveLimit(dmkMsg.user) and self.__notReachMax()):
            return
        if (command == "点歌"):
            self.audiobot.addAudioByUrl(val, dmkMsg.user)
        elif command == "点b歌":
            self.audiobot.addAudioByUrl(val, dmkMsg.user, source_class=BiliAudioSource)
        elif command == "点w歌":
            self.audiobot.addAudioByUrl(val, dmkMsg.user, source_class=NeteaseMusicSource)
        elif command == "点k歌":
            self.audiobot.addAudioByUrl(val, dmkMsg.user, source_class=KuwoMusicSource)

    def __hasPermission(self, dmkMsg: DanmakuMessage):
        config = Config.commands["diange"]
        try:
            if config["visitor"]:
                return True
            if config["admin"] and dmkMsg.admin:
                return True
            if config["guard"] and dmkMsg.privilege_level > 0:
                return True
            # if config["fan"] is not None:
            #     if (str(config["fan"]["room_id"]) == str(dmkMsg.room_id)
            #             and int(dmkMsg.medal_level) >= int(config["fan"]["level"])):
            #         return True
            return False
        except:
            return False

    def __inCooldown(self, dmkMsg: DanmakuMessage):
        uid = str(dmkMsg.user.identifier)
        if self.cooldowns.get(uid) is None:
            self.cooldowns[uid] = int(time.time())
            return True
        if int(time.time()) - self.cooldowns[uid] >= Config.commands["diange"]["cooldown"]:
            self.cooldowns[uid] = int(time.time())
            return True
        return False

    def __notArriveLimit(self, dmkUser: DanmakuUser):
        playlist: List[AudioItem] = self.audiobot.user_playlist.playlist
        count: int = 0
        for x in playlist:
            user = x.user
            if isinstance(user, DanmakuUser) and dmkUser.username == user.username:
                count = count + 1
        if count < Config.commands["diange"]["limit_per_user"]:
            return True
        return False

    def __notReachMax(self):
        return self.audiobot.user_playlist.size() < Config.commands["diange"]["limit"]