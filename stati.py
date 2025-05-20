import json
import os
import matplotlib.pyplot as plt

# 配置模型信息，(模型原名, 在图像里的显示名)
MODEL_CONFIG = [
    ("gpt-4.1-nano", "gpt-4.1-nano"),
    ("gpt-4.1-mini", "gpt-4.1-mini"),
    ("gpt-4.1", "gpt-4.1"),
    ("meta-llama/llama-4-maverick", "llama-4-maverick"),
    ("google/gemini-2.5-flash-preview", "gemini-2.5-flash"),
    ("google/gemini-2.5-pro-preview", "gemini-2.5-pro"),
    ("mistralai/mistral-medium-3", "mistral-medium-3"),
    ("all", "all"),
]

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
plt.rcParams['font.sans-serif'] = ['Heiti TC']  # 设置中文字体为黑体
plt.rcParams['axes.unicode_minus'] = False    # 正常显示负号

########################################################
# 统计数据
########################################################

# 自动生成必要的变量
model_names = [item[0] for item in MODEL_CONFIG]
model_names_display = [item[1] for item in MODEL_CONFIG]

# 创建字典存储每个模型的数据
model_data = {}
model_chat_data = {}

# 初始化每个模型的数据列表
for model_name, _ in MODEL_CONFIG:
    if model_name != "all":  # 排除"all"
        model_data[model_name] = []
        model_chat_data[model_name] = []

# 按模型分类数据
for item in data_win:
    for i in item:
        model_name = i["model"]
        if model_name in model_data:
            model_data[model_name].append(i)

# 1. 统计每个模型的胜率和数量
win_rates = []
win_counts = []
total_counts = []

for model_name, _ in MODEL_CONFIG:
    if model_name == "all":
        # 全部模型的总和
        all_win_count = sum(i["win"] for game in data_win for i in game)
        all_total_count = sum(len(game) for game in data_win)
        all_win_rate = all_win_count / all_total_count if all_total_count > 0 else 0
        win_rates.append(all_win_rate)
        win_counts.append(all_win_count)
        total_counts.append(all_total_count)
    else:
        # 当前模型
        model_items = model_data[model_name]
        if model_items:
            win_count = sum(i["win"] for i in model_items)
            total_count = len(model_items)
            win_rate = win_count / total_count
        else:
            win_count = 0
            total_count = 0
            win_rate = 0
        win_rates.append(win_rate)
        win_counts.append(win_count)
        total_counts.append(total_count)

# 1.1. 作图：模型胜率
plt.figure(figsize=(12, 6))
bars = plt.bar(model_names_display, win_rates)
plt.title("不同模型的胜率对比")
plt.ylim(0.4, max(win_rates) * 1.05 if win_rates else 1)

# 添加"胜率(胜利数/总次数)"标记
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
plt.savefig("assets/model_win_rate.png")
plt.show()

# 2. 按模型和角色统计胜率
roles = ["狼人", "预言家", "女巫", "平民"]

fig, axes = plt.subplots(2, 4, figsize=(16, 8))
fig.suptitle('不同模型于各角色的胜率对比')

for idx, (model_name, model_display) in enumerate(MODEL_CONFIG):
    # 计算当前子图位置
    row = idx // 4
    col = idx % 4
    ax = axes[row, col]
    
    # 获取该模型的数据
    if model_name == "all":
        model_items = [i for game in data_win for i in game]
    else:
        model_items = model_data[model_name]
    
    # 按角色统计胜率
    role_win_rates = []
    for role in roles:
        role_items = [i for i in model_items if i["role"] == role]
        if role_items:
            role_win_rate = sum(i["win"] for i in role_items) / len(role_items)
        else:
            role_win_rate = 0
        role_win_rates.append(role_win_rate)
    
    # 绘制条形图
    ax.bar(roles, role_win_rates)
    ax.set_title(f'{model_display} 胜率')
    ax.set_ylim(0, 1)
    ax.set_xticks(range(len(roles)))
    ax.set_xticklabels(roles, rotation=45)
    
    # 添加数值标签
    for i, v in enumerate(role_win_rates):
        ax.text(i, v + 0.02, f'{v:.2f}', ha='center')

plt.tight_layout()
plt.subplots_adjust(top=0.9)
plt.savefig("assets/model_role_win_rate.png")
plt.show()

# 3. 统计模型做女巫时使用「救」或者「杀」的次数
# 统计结构：{model: {'save': n, 'poison': n, 'total': n, 'self_save': n, 'save_seer': n, 'poison_wolf': n}}
witch_action_stats = {model: {'save': 0, 'poison': 0, 'total': 0, 'self_save': 0, 'save_seer': 0, 'poison_wolf': 0} for model in model_data}

for game in data_game:
    # 先建立该局玩家名到角色的映射
    name2role = {item['player']: item['role'] for item in game if 'player' in item and 'role' in item}
    for record in game:
        if record.get('role') == '女巫':
            model = record.get('model')
            vote = str(record.get('vote', ''))
            player_name = record.get('player', '')
            if model in witch_action_stats:
                if '救' in vote:
                    witch_action_stats[model]['save'] += 1
                    # 判断是否自救
                    if f'救{player_name}' in vote:
                        witch_action_stats[model]['self_save'] += 1
                    # 判断是否救预言家
                    for name in name2role:
                        if f'救{name}' in vote and name2role.get(name) == '预言家':
                            witch_action_stats[model]['save_seer'] += 1
                if '毒' in vote or '杀' in vote:
                    witch_action_stats[model]['poison'] += 1
                    # 判断杀死的是不是狼人
                    # 假设vote格式为"毒张三"或"杀张三"，提取被杀玩家名
                    for name in name2role:
                        if (f'毒{name}' in vote or f'杀{name}' in vote) and name2role.get(name) == '狼人':
                            witch_action_stats[model]['poison_wolf'] += 1
                if ('救' in vote) or ('毒' in vote) or ('杀' in vote):
                    witch_action_stats[model]['total'] += 1

# 汇总all
witch_action_stats['all'] = {
    'save': sum(witch_action_stats[m]['save'] for m in model_data),
    'poison': sum(witch_action_stats[m]['poison'] for m in model_data),
    'total': sum(witch_action_stats[m]['total'] for m in model_data),
    'self_save': sum(witch_action_stats[m]['self_save'] for m in model_data),
    'save_seer': sum(witch_action_stats[m]['save_seer'] for m in model_data),
    'poison_wolf': sum(witch_action_stats[m]['poison_wolf'] for m in model_data),
}

# 计算堆叠数据
save_counts = [witch_action_stats[m]['save'] for m, _ in MODEL_CONFIG]
poison_counts = [witch_action_stats[m]['poison'] for m, _ in MODEL_CONFIG]
self_save_counts = [witch_action_stats[m]['self_save'] for m, _ in MODEL_CONFIG]
save_seer_counts = [witch_action_stats[m]['save_seer'] for m, _ in MODEL_CONFIG]
# 其他救人 = 总救人 - 自救 - 救预言家
other_save_counts = [max(0, s - ss - seer) for s, ss, seer in zip(save_counts, self_save_counts, save_seer_counts)]
total_counts = [witch_action_stats[m]['total'] for m, _ in MODEL_CONFIG]
# 新增：杀死狼人和杀死非狼人的数量
poison_wolf_counts = [witch_action_stats[m]['poison_wolf'] for m, _ in MODEL_CONFIG]
poison_nonwolf_counts = [max(0, p - w) for p, w in zip(poison_counts, poison_wolf_counts)]

plt.figure(figsize=(16, 6))
bar_width = 0.35
x = range(len(model_names_display))

# 左侧堆叠救人
plt.bar(x, self_save_counts, width=bar_width, label='自救', color='#2196F3')
plt.bar(x, save_seer_counts, width=bar_width, bottom=self_save_counts, label='救预言家', color='#FFD600')
plt.bar(x, other_save_counts, width=bar_width, bottom=[a+b for a,b in zip(self_save_counts, save_seer_counts)], label='救其他', color='#4CAF50')

# 右侧杀人柱，分为杀死狼人和杀死非狼人
x2 = [i + bar_width + 0.1 for i in x]
plt.bar(x2, poison_wolf_counts, width=bar_width, label='杀死狼人', color='#8D6E63')
plt.bar(x2, poison_nonwolf_counts, width=bar_width, bottom=poison_wolf_counts, label='杀死非狼人', color='#F44336')

# 添加数值标签
for i, (self_save, save_seer, other_save, wolf, nonwolf) in enumerate(zip(self_save_counts, save_seer_counts, other_save_counts, poison_wolf_counts, poison_nonwolf_counts)):
    plt.text(i, self_save/2, f'{self_save}', ha='center', va='center', fontsize=10, color='#fff' if self_save else '#2196F3')
    plt.text(i, self_save + save_seer/2, f'{save_seer}', ha='center', va='center', fontsize=10, color='#333' if save_seer else '#FFD600')
    plt.text(i, self_save + save_seer + other_save/2, f'{other_save}', ha='center', va='center', fontsize=10, color='#fff' if other_save else '#4CAF50')
    plt.text(x2[i], wolf/2, f'{wolf}', ha='center', va='center', fontsize=10, color='#fff' if wolf else '#8D6E63')
    plt.text(x2[i], wolf + nonwolf/2, f'{nonwolf}', ha='center', va='center', fontsize=10, color='#fff' if nonwolf else '#F44336')

plt.xticks([i + bar_width/2 for i in x], model_names_display, rotation=30)
plt.title('不同模型担任女巫时救人（分类型堆叠）与杀人（分狼人/非狼人）次数对比')
plt.ylabel('次数')
plt.legend()

# 为每个模型分别添加『救人』『杀人』标签
for i in range(len(model_names_display)):
    # 救人柱顶端高度
    save_top = self_save_counts[i] + save_seer_counts[i] + other_save_counts[i]
    plt.text(i, save_top + 0.5, '救人', ha='center', va='bottom', fontsize=12, fontweight='bold', color='#1976D2')
    # 杀人柱顶端高度
    poison_top = poison_wolf_counts[i] + poison_nonwolf_counts[i]
    plt.text(x2[i], poison_top + 0.5, '杀人', ha='center', va='bottom', fontsize=12, fontweight='bold', color='#B71C1C')

plt.tight_layout()
plt.savefig('assets/model_witch_action.png')
plt.show()

# 4. 按模型的发言次数（存活时长）统计
players_name = ["王大", "刘二", "张三", "赵四", "孙五", "周六", "李七", "郑八"]

# 统计每局玩家的发言次数和模型
for game in data_game:
    player_chat_count = {name: 0 for name in players_name}
    player_model = {name: None for name in players_name}
    
    # 统计发言次数和记录模型
    for chat in game:
        name = chat["player"]
        if name in players_name:
            player_chat_count[name] += 1
            player_model[name] = chat["model"]
    
    # 按模型汇总数据
    for name in players_name:
        model_name = player_model[name]
        if model_name in model_chat_data:
            model_chat_data[model_name].append(player_chat_count[name])

# 计算平均值函数
def avg(lst):
    return sum(lst) / len(lst) if lst else 0

# 统计每个模型的平均发言次数
chat_avgs = []
for model_name, _ in MODEL_CONFIG:
    if model_name == "all":
        # 所有模型的平均
        all_chats = []
        for m_name in model_chat_data:
            all_chats.extend(model_chat_data[m_name])
        chat_avgs.append(avg(all_chats))
    else:
        # 当前模型的平均
        chat_avgs.append(avg(model_chat_data.get(model_name, [])))

# 作图：模型平均发言次数
plt.figure(figsize=(12, 6))
bars = plt.bar(model_names_display, chat_avgs)
plt.title("不同模型的平均存活时长（发言次数）对比")
plt.ylabel("每局平均发言次数（投票也算1次）")
plt.ylim(0, max(chat_avgs) * 1.1 if chat_avgs else 1)

# 添加数值标签
for bar, value in zip(bars, chat_avgs):
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
plt.savefig("assets/model_num_of_chat.png")
plt.show()
