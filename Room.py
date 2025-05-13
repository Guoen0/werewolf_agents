from Player import Player, Vote, Speech, Witch
from agents import Runner, Agent
import config
from prompts import prompts

class Room:
    def __init__(self, players):
        self.players = players
        self.does_witch_have_potion = True
        self.speech_history = []
        self.all_history = []
    
    def get_player_by_role(self, role) -> Player:
        for player in self.players:
            if player.role == role:
                return player
    
    def get_player_by_name(self, name) -> Player:
        for player in self.players:
            if player.name == name:
                return player
            
    def get_role_by_name(self, name) -> str:
        for player in self.players:
            if player.name == name:
                return player.role

    def check_player_role(self, result) -> str:
        if isinstance(result.final_output, Vote):
            role = self.get_role_by_name(result.final_output.target_player_name)
            text = f"{result.final_output.target_player_name} 的身份是 {role}"
            return text
        else:
            return "check_player_role输入错误"
    
    def eliminate_player_by_votes(self, names: list[str]) -> str:
        # 统计票数
        vote_count = {}
        for name in names:
            vote_count[name] = vote_count.get(name, 0) + 1 # 计票
        
        max_vote_count = max(vote_count.values()) # 最高票数
        max_voted_players = [name for name, count in vote_count.items() if count == max_vote_count] # 最高票数玩家
        
        if len(max_voted_players) == 1:
            p = self.get_player_by_name(max_voted_players[0])
            if p:
                self.players.remove(p)
                return f"{p.name} 被投票淘汰了"
            else:
                return "无人被淘汰"
        else:
            return "平票，无人被淘汰"

    async def night_action(self):
        # 预言家夜晚行动
        user_message = f"预言家请睁眼，请选择1个你要查验的玩家。目前在场的玩家有：{[player.name for player in self.players]}。"
        player = self.get_player_by_role("预言家")
        if player:
            result = await player.action("Vote", user_message, self.speech_history, self.all_history)
            check_message = self.check_player_role(result)
            self.judge_speech_to_players(check_message + f"\n这条消息只有你和法官能看到。其他普通玩家并不知道查验结果。", [player])

        # 狼人夜晚行动
        kill_names = []
        player = self.get_player_by_role("狼人")
        if player:
            user_message = f"狼人请睁眼，请选择1个你要杀死的玩家。目前在场的玩家有：{[player.name for player in self.players]}。"
            result = await player.action("Vote", user_message, self.speech_history, self.all_history)
            kill_names.append(result.final_output.target_player_name)
            kill_message = f"狼人准备杀死 {kill_names}。"
            self.judge_speech_to_players(kill_message, []) 

        # 女巫夜晚行动
        save_names = []
        if self.does_witch_have_potion:
            user_message = f"女巫请睁眼，请选择1个你要救或杀的玩家。目前在场的玩家有：{[player.name for player in self.players]}。"
            player = self.get_player_by_role("女巫")
            if player:
                result = await player.action("Witch", user_message, self.speech_history, self.all_history)
                is_save = result.final_output.is_save_someone
                is_kill = result.final_output.is_kill_someone
                name = result.final_output.target_player_name

                if is_kill:
                    kill_names.append(name)
                if is_save:
                    save_names.append(name)

                if is_kill or is_save:
                    self.does_witch_have_potion = False
        
        # 结算
        night_message = ""
        if save_names == kill_names:
            night_message = f"没有人被杀。"
        else:
            kill_names = list(set(kill_names))  # 去重
            for name in kill_names:
                self.eliminate_player_by_votes([name])
            night_message = f"{kill_names}被杀了。"

        self.judge_speech_to_players(f"昨晚。{night_message}", self.players)

    async def day_action(self):
        # 发言
        for player in self.players:
            result = await player.action("Speech", "", self.speech_history, self.all_history)
        
        # 投票
        self.judge_speech_to_players(f"现在请投票淘汰1个玩家。目前在场的玩家有：{[player.name for player in self.players]}。", self.players)
        
        results = []
        for player in self.players:
            result = await player.action("Vote", "", self.speech_history, self.all_history)
            results.append(result)

        # 淘汰
        names = [result.final_output.target_player_name for result in results]
        eliminate_message = self.eliminate_player_by_votes(names)
        self.judge_speech_to_players(f"{eliminate_message}。目前在场的玩家有：{[player.name for player in self.players]}。", self.players)
    
    def judge_speech_to_players(self, message, speech_to_players: list[Player]):
        text = f"法官说：{message}"
        print(text)
        names = [player.name for player in speech_to_players]
        self.all_history.append({"player":"user", "role":"法官", "think":"", "speech":message, "vote": names, "decision": ""})
        for player in speech_to_players:
            player.history.append({"role": "user","content": text})
    
    def is_game_over(self):
        is_wolf_alive = False
        for player in self.players:
            if player.role == "狼人":
                is_wolf_alive = True
                break

        if is_wolf_alive and len(self.players) > 3:
            return False, "游戏继续"
        else:
            if is_wolf_alive:
                return True, "狼人胜利"
            else:
                return True, "好人胜利"