import config
from prompts import prompts
from agents import Agent, Runner
from pydantic import BaseModel

# 输出类型
class Speech(BaseModel):
    think: str
    speach: str

class Vote(BaseModel):
    think: str
    target_player_name: str

class Witch(BaseModel):
    think: str
    is_save_someone: bool
    is_kill_someone: bool
    target_player_name: str

# 玩家定义
class Player:
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.agent = Agent(
            name=name,
            instructions=prompts["GAME_RULE"] + f"\n你是 {name}。" + f"\n你是{role}。",
            model=config.model,
        )
        self.history = []
    
    async def action(self, output_type, user_message, speech_history, all_history):

        if user_message:
            self.history.append({
                "role": "user",
                "content": user_message 
            })

        # 更新对话记录（删除旧的，减少重复）
        self.history = [item for item in self.history if item["role"] != "developer"]
        self.history.append({
            "role": "developer",
            "content": f"\n当前房间的对话记录是：{speech_history}"
        })

        # Run
        if output_type == "Vote": self.agent.output_type = Vote
        elif output_type == "Speech": self.agent.output_type = Speech
        elif output_type == "Witch": self.agent.output_type = Witch
            
        result = await Runner.run(self.agent, self.history)
        self.history = result.to_input_list()
        
        # 更新历史
        if output_type == "Speech":
            speech_history.append({"player":self.name, "speech":result.final_output.speach})
            all_history.append({"player":self.name, "role":self.role, "think":result.final_output.think, "speech":result.final_output.speach, "vote": "", "decision": ""})
        elif output_type == "Vote":
            all_history.append({"player":self.name, "role":self.role, "think":result.final_output.think, "speech":"", "vote": result.final_output.target_player_name, "decision": ""})
        elif output_type == "Witch":
            text = ""
            if result.final_output.is_save_someone: text = "救"
            if result.final_output.is_kill_someone: text = "杀"
            all_history.append({"player":self.name, "role":self.role, "think":result.final_output.think, "speech":"", "vote": result.final_output.target_player_name, "decision": text})
        
        print(self.name)
        print(result.final_output)
        return result