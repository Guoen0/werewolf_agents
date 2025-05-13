from agents import Agent, Runner, set_default_openai_key
import asyncio
from Player import Player, Vote
from Room import Room
from prompts import prompts
import config
import os
import json
########################################################
# 配置
########################################################
set_default_openai_key(config.api_key)
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1" # no tracing

########################################################
# 初始化
########################################################
players = [
    Player("王大", "平民"),
    Player("刘二", "平民"),
    Player("张三", "预言家"),
    Player("赵四", "平民"),
    Player("孙五", "狼人"),
    Player("周六", "平民"),
    Player("吴七", "平民"),
    Player("郑八", "女巫"),
]

room = Room(players)
########################################################
# Run
########################################################
def game_over(winner_message):
    over_message = f"游戏结束，{winner_message}。"
    print(over_message)
    room.judge_speech_to_players(over_message, [])

    # 保存历史
    with open(f"history_{config.model}.json", "w", encoding="utf-8") as f:
        json.dump(room.all_history, f, ensure_ascii=False, indent=2)

    # 查看单个玩家的记忆
    #player = room.players[0]
    #print(f"###### 查看 {player.name} 的记忆 ######")
    #print(player.history)
    exit()

async def main():

    day_count = 0
    while True:
        day_count += 1

        room.judge_speech_to_players(f"第{day_count}天夜晚。天黑，请闭眼。", room.players)
        await room.night_action()

        room.judge_speech_to_players(f"现在是白天，请睁眼。目前在场的玩家有：{[player.name for player in players]}。请发言。", room.players)
        await room.day_action()

        is_game_over, winner_message = room.is_game_over()
        if is_game_over: 
            game_over(winner_message)
            break

if __name__ == "__main__":
    asyncio.run(main())