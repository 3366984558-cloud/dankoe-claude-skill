# Dan Koe Skill for Claude Code

把 [Dan Koe](https://thedankoe.com) 蒸馏进 Claude Code，让他变成你的 24/7 第一人称顾问。

聊到**个人 IP / 一人公司 / 内容创作 / 数字杠杆 / 产品定价 / 人生方向**时自动触发，或者手动 `/dankoe`。

## 这是什么

- **全套语料**：thedankoe.com 上 178 篇 letters 全部抓下来存成 markdown
- **5 个核心思想框架**：一人公司、数字杠杆、purpose-driven life、写作公式、个人品牌
- **金句库**：60+ 句 Dan Koe 真实金句，分类索引
- **语气复刻指南** (`voice.md`)：完整的口头禅清单 / 句式模板 / 修辞模式 / 中英夛金混合规则
- **BM25 本地检索**：纯 Python，无 embedding API 依赖，毫秒级响应

不是套个 prompt 喊"你是 Dan Koe"，是把他真正写过的每一段话都存下来、按需检索、按他的节奏回答。

## 安装

```bash
# 1. clone 到 Claude Code skills 目录
git clone https://github.com/3366984558-cloud/DanKoe.skill ~/.claude/skills/DanKoe.skill

# 2. 装 Python 依赖
pip install requests beautifulsoup4 markdownify lxml

# 3. 抓全部 essay (~2 分钟)
python ~/.claude/skills/DanKoe.skill/scripts/fetch_all.py

# 4. 建索引
python ~/.claude/skills/DanKoe.skill/scripts/build_index.py
```

## 用法

**手动调用**：
```
/DanKoe.skill 我做一人公司,要不要 niche down?
```

**自动触发**：聊到一人公司 / 个人 IP / 内容 / 杠杆 / 定价 / discipline / purpose 时 Claude 会自己 surface。

**输出示例**：
> Dude, niche down is dead advice. 你不需要 niche, 你需要 point of view。
>
> The most profitable niche is you — 你的兴趣交集、你的故事、你的视角。Niche of one.
>
> 别去抢"健身 / 理财 / 学习"这种红海赛道。把你独有的 3-5 个 interest stack 起来,那块土地全世界只有你站着。
>
> Stop optimizing for the algorithm. Start optimizing for your higher self.

## 文件结构

```
DanKoe.skill/
├── SKILL.md              skill 入口 + 人格指令 + 触发规则
├── voice.md              语气复刻指南(口头禅 / 句式 / 修辞 / 中英夛金)
├── frameworks/           5 个核心思想框架(浓缩版)
├── essays/               thedankoe.com 全部 letters(原文 markdown)
├── transcripts/          YouTube 转录(可选)
├── quotes.md             60+ 金句库
├── index.json            BM25 检索索引(脚本生成)
└── scripts/
    ├── fetch_all.py      抓 thedankoe.com 全站
    ├── build_index.py    建关键词索引
    └── search.py         查询接口
```

## 重新抓取 / 更新

Dan Koe 每周更新一篇。想拉最新：

```bash
python ~/.claude/skills/DanKoe.skill/scripts/fetch_all.py    # 增量抓,跳过已存在
python ~/.claude/skills/DanKoe.skill/scripts/build_index.py  # 重建索引
```

## 免责声明

本 skill 的 essay 内容版权归 [Dan Koe](https://thedankoe.com) 本人。本仓库**不再发布**他的原文，只发布抓取脚本和框架/语气/金句的二次创作。安装时由用户本地脚本从官网抓取，相当于个人收藏夹。商用请联系 Dan Koe 本人。

## License

MIT for the skill code (scripts / SKILL.md / frameworks / voice.md).
Essay content (essays/) belongs to Dan Koe — fetched on-demand by the user.
