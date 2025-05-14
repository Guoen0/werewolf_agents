from agents import set_default_openai_key, trace, set_tracing_disabled
import asyncio
from Player import Player
from Room import Room
import config
import json
import random
from datetime import datetime
########################################################
# 配置
########################################################
set_default_openai_key(config.api_key)
set_tracing_disabled(True) # no tracing

players_name = ["王大", "刘二", "张三", "赵四", "孙五", "周六", "李七", "郑八"]
players_role = ["狼人", "预言家", "女巫", "平民", "平民", "平民", "平民", "平民"]
models = ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano"]

arena_runs = 10

########################################################
# Arena
########################################################
def game_over(winner_message, room:Room):
    over_message = f"游戏结束，{winner_message}。"
    print(over_message)
    room.judge_speech_to_players(over_message, [])

    # 保存历史
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"history/history_{timestamp}.json", "w", encoding="utf-8") as f:
        json.dump(room.all_history, f, ensure_ascii=False, indent=2)

async def arena(players_name, players_role, model_list):

    players = []
    for i in range(len(players_name)):
        players.append(Player(players_name[i], players_role[i], model_list[i]))

    room = Room(players)

    day_count = 0
    while True:
        day_count += 1

        room.judge_speech_to_players(f"第{day_count}天夜晚。天黑，请闭眼。", room.players)
        await room.night_action()
        is_game_over, winner_message = room.is_game_over_when("night")  
        if is_game_over: 
            game_over(winner_message, room)
            break

        room.judge_speech_to_players(f"现在是白天，请睁眼。目前在场的玩家有：{[player.name for player in players]}。请发言。", room.players)
        await room.day_action()
        is_game_over, winner_message = room.is_game_over_when("day")
        if is_game_over: 
            game_over(winner_message, room)
            break

async def main():

    for _ in range(arena_runs):
        
        # 打乱顺序
        random.shuffle(players_name)
        random.shuffle(players_role)
        model_list = random.choices(models, k=len(players_name))
        matching = list(zip(players_name, players_role, model_list))
        print(matching)

        await arena(players_name, players_role, model_list)

if __name__ == "__main__":
    asyncio.run(main())