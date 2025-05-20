from prompts import prompts
from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from pydantic import BaseModel
import config

# 输出类型
class Speech(BaseModel):
    think: str
    speech: str

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
    def __init__(self, name, role, model):
        self.name = name
        self.role = role
        self.model_name = model
        self.model = None
        self.history = []
        self.instructions = prompts["GAME_RULE"] + f"\n你是 {name}。" + f"\n你是{role}。"

        if "gpt" in model or "o4" in model:
            self.model = model
        else:
            self.model = OpenAIChatCompletionsModel(
                model=model, 
                openai_client=AsyncOpenAI(api_key=config.openrouter_api_key, base_url=config.openrouter_url)
            )
            
        self.agent = Agent(
            name=name,
            instructions=self.instructions,
            model=self.model,
        )
    
    async def action(self, output_type, user_message, speech_history, all_history):

        if user_message:
            self.history.append({
                "role": "user",
                "content": user_message 
            })

        # 更新对话记录（删除旧的，减少重复）
        self.history = [
            item for item in self.history
            if isinstance(item, dict) and "content" in item and f"\n当前房间的对话记录是：" not in item["content"]
        ]
        self.history.append({
            "role": "user",
            "content": f"\n当前房间的对话记录是：{speech_history}"
        })

        # output type
        if output_type == "Vote": 
            self.agent.output_type = Vote
        elif output_type == "Speech": 
            self.agent.output_type = Speech
        elif output_type == "Witch": 
            self.agent.output_type = Witch
            
        result = await Runner.run(self.agent, self.history)
        self.history = result.to_input_list()
        
        # 更新历史
        if output_type == "Speech":
            speech_history.append({"player":self.name, "speech":result.final_output.speech})
            all_history.append({"player":self.name, "role":self.role, "think":result.final_output.think, "speech":result.final_output.speech, "vote": "", "model": self.model_name })
        elif output_type == "Vote":
            all_history.append({"player":self.name, "role":self.role, "think":result.final_output.think, "speech":"", "vote": result.final_output.target_player_name, "model": self.model_name })
        elif output_type == "Witch":
            text = ""
            if result.final_output.is_save_someone: text = "救"
            if result.final_output.is_kill_someone: text = "杀"
            text = f"{text}{result.final_output.target_player_name}"
            all_history.append({"player":self.name, "role":self.role, "think":result.final_output.think, "speech":"", "vote": text, "model": self.model_name })
        
        print(self.name)
        print(result.final_output)
        return result