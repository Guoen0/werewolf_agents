import json
import os
import matplotlib.pyplot as plt
from collections import Counter

########################################################
# 加载历史数据
########################################################
data_win = []
data_game = []
files = os.listdir("history")
for file in files:
    with open(f"history/{file}", "r", encoding="utf-8") as f:
        history = json.load(f)

        # 胜利信息
        winner_message = history[-1]["speech"]
        if "狼人胜利" in winner_message:
            is_wolf_win = True
        else:
            is_wolf_win = False

        # 找到不同的角色并去掉user
        players_name = []
        for item in history:
            if item["player"] not in players_name:
                players_name.append(item["player"])
        players_name = [player for player in players_name if player != "user"]

        # 名字对应的角色和模型
        list = [{"name": name, "role": "", "model": "", "win": False} for name in players_name]
        for name in players_name:
            for item in history:
                if item["player"] == name:
                    list[players_name.index(name)]["role"] = item["role"]
                    list[players_name.index(name)]["model"] = item["model"]
                    
                    if is_wolf_win and item["role"] == "狼人":
                        list[players_name.index(name)]["win"] = True

                    if not is_wolf_win and item["role"] != "狼人":
                        list[players_name.index(name)]["win"] = True
                    break

        data_win.append(list)

        # 聊天记录
        data_game.append(history)

########################################################
# 统计数据
########################################################
plt.rcParams['font.sans-serif'] = ['Heiti TC']  # 设置中文字体为黑体
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

gpt_4_1 = []
gpt_4_1_mini = []
gpt_4_1_nano = []
for item in data_win:
    for i in item:
        if i["model"] == "gpt-4.1":
            gpt_4_1.append(i)
        elif i["model"] == "gpt-4.1-mini":
            gpt_4_1_mini.append(i)
        elif i["model"] == "gpt-4.1-nano":
            gpt_4_1_nano.append(i)

# 1 统计每个模型的胜率以及平均胜率
gpt_4_1_win_rate = sum([i["win"] for i in gpt_4_1]) / len(gpt_4_1)
gpt_4_1_mini_win_rate = sum([i["win"] for i in gpt_4_1_mini]) / len(gpt_4_1_mini)
gpt_4_1_nano_win_rate = sum([i["win"] for i in gpt_4_1_nano]) / len(gpt_4_1_nano)
all_win_rate = sum([i["win"] for game in data_win for i in game]) / sum([len(game) for game in data_win])

# 作图：模型胜率
model_names = ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "all"]
win_rates = [gpt_4_1_win_rate, gpt_4_1_mini_win_rate, gpt_4_1_nano_win_rate, all_win_rate]
# 统计胜利次数和总次数
win_counts = [sum([i["win"] for i in gpt_4_1]), sum([i["win"] for i in gpt_4_1_mini]), sum([i["win"] for i in gpt_4_1_nano]), sum([i["win"] for game in data_win for i in game])]
total_counts = [len(gpt_4_1), len(gpt_4_1_mini), len(gpt_4_1_nano), sum([len(game) for game in data_win])]

bars = plt.bar(model_names, win_rates)
plt.title("不同模型的胜率对比")
plt.ylim(0, max(win_rates) * 1.1)  # 让y轴上限高于最高柱子，给标签留空间


# 添加"胜率(胜利数/总次数)"标记，减小字体并加粗
for bar, win, total, rate in zip(bars, win_counts, total_counts, win_rates):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{rate:.2f}({win}/{total})",
        ha='center',
        va='bottom',
        fontsize=10,
        fontweight='bold',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.2')
    )

plt.tight_layout()
# 保存图片
plt.savefig("assets/model_win_rate.png")
plt.show()


# 2 按模型和角色统计胜率
models = ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "all"]
roles = ["狼人", "预言家", "女巫", "平民"]

# 创建子图
fig, axes = plt.subplots(1, 4, figsize=(12, 5))  # 宽度由20缩小为10
fig.suptitle('不同模型于各角色的胜率对比')

for idx, model in enumerate(models):
    # 获取当前模型的数据
    if model == "gpt-4.1":
        model_data_win = gpt_4_1
    elif model == "gpt-4.1-mini":
        model_data_win = gpt_4_1_mini
    elif model == "gpt-4.1-nano":
        model_data_win = gpt_4_1_nano
    elif model == "all":
        model_data_win = [i for game in data_win for i in game]
    
    # 计算每个角色的胜率
    win_rates = []
    for role in roles:
        role_data_win = [i for i in model_data_win if i["role"] == role]
        if role_data_win:  # 检查列表是否为空
            win_rate = sum(i["win"] for i in role_data_win) / len(role_data_win)
        else:
            win_rate = 0
        win_rates.append(win_rate)
    
    # 绘制条形图
    axes[idx].bar(roles, win_rates)
    axes[idx].set_title(f'{model} 胜率')
    axes[idx].set_ylim(0, 1)
    # 先设置刻度再旋转标签
    axes[idx].set_xticks(range(len(roles)))
    axes[idx].set_xticklabels(roles, rotation=45)
    # 添加数值标签
    for i, v in enumerate(win_rates):
        axes[idx].text(i, v + 0.02, f'{v:.2f}', ha='center')

plt.tight_layout()
plt.subplots_adjust(top=0.85)  # 为标题留出空间
# 保存图片
plt.savefig("assets/model_role_win_rate.png")
plt.show()

# 3 按模型的发言次数（存活时长）统计
gpt_4_1_chat = []
gpt_4_1_mini_chat = []
gpt_4_1_nano_chat = []

players_name = ["王大", "刘二", "张三", "赵四", "孙五", "周六", "李七", "郑八"]
for game in data_game:
    # 统计本局每个玩家的发言次数和模型

    # 初始化两个字典：
    # player_chat_count 用于记录每个玩家的发言次数，初始值为0
    # player_model 用于记录每个玩家使用的模型，初始值为None
    player_chat_count = {name: 0 for name in players_name}
    player_model = {name: None for name in players_name}
    for chat in game:
        name = chat["player"]
        if name in players_name:
            player_chat_count[name] += 1
            player_model[name] = chat["model"]
    # 按模型分类
    for name in players_name:
        if player_model[name] == "gpt-4.1":
            gpt_4_1_chat.append(player_chat_count[name])
        elif player_model[name] == "gpt-4.1-mini":
            gpt_4_1_mini_chat.append(player_chat_count[name])
        elif player_model[name] == "gpt-4.1-nano":
            gpt_4_1_nano_chat.append(player_chat_count[name])

# 计算平均发言次数
def avg(lst):
    return sum(lst) / len(lst) if lst else 0

gpt_4_1_chat_avg = avg(gpt_4_1_chat)
gpt_4_1_mini_chat_avg = avg(gpt_4_1_mini_chat)
gpt_4_1_nano_chat_avg = avg(gpt_4_1_nano_chat)
all_chat_avg = avg(gpt_4_1_chat + gpt_4_1_mini_chat + gpt_4_1_nano_chat)

# 作图
bars = plt.bar(
    ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "all"],
    [gpt_4_1_chat_avg, gpt_4_1_mini_chat_avg, gpt_4_1_nano_chat_avg, all_chat_avg]
)
plt.title("不同模型的平均存活时长（发言次数）对比")
plt.ylabel("每局平均发言次数（投票也算1次）")
plt.ylim(0, max([gpt_4_1_chat_avg, gpt_4_1_mini_chat_avg, gpt_4_1_nano_chat_avg, all_chat_avg]) * 1.1)
# 添加数值标签
for bar, value in zip(bars, [gpt_4_1_chat_avg, gpt_4_1_mini_chat_avg, gpt_4_1_nano_chat_avg, all_chat_avg]):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{value:.2f}",
        ha='center',
        va='bottom',
        fontsize=10,
        fontweight='bold',
        bbox=dict(facecolor='white', alpha=0, edgecolor='none', boxstyle='round,pad=0.2')
    )
plt.tight_layout()
# 保存图片
plt.savefig("assets/model_num_of_chat.png")
plt.show()
