# session-name

[English README](../README.md)

给当前 Agent 会话起一个简短、方便检索的名字。技能根据整段会话的主线选择分类，默认格式为 `[类型] 主题`：

- `[bugfix] 修复登录超时`
- `[feat] 支持自定义会话前缀`
- `[discuss] 比较会话存储方案`
- `[learn] 了解 Codex App Server`

## 安装

**Hermes Agent、OpenClaw、Claude Code、Codex**：克隆或下载本仓库，在仓库根目录使用 [Skills CLI](https://github.com/vercel-labs/skills) 安装。推荐 Node.js 22 或更新版本：

```sh
npx skills@1.7.4 add . --skill session-name -g -a hermes-agent openclaw claude-code codex -y
```

不使用的 Agent 可以从命令中去掉。CLI 安装的是完整的 `skills/session-name/` 目录，`-a` 只选择安装位置，不裁剪适配器，也不会执行脚本或安装其依赖。使用 Hermes 自定义 Profile 时，可将技能复制到该 Profile 的 `$HERMES_HOME/skills/`；如果已在分类目录下安装过，建议原位更新，避免重复安装。

### DeepSeek Harness（DSH）

将完整的 `skills/session-name/` 复制到 `$DSH_HOME/skills/`（默认 `~/.dsh/skills/`），或项目的 `.dsh/skills/` 下。DSH 也[会发现共享目录里的技能](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/skills.md)。在仓库根目录执行：

```sh
npx skills@1.7.4 add . --skill session-name -g -a universal -y
```

如果共享目录 `~/.agents/skills/session-name/` 已经有一份，不用重复安装。在 DSH 中输入 `/session-name` 即可调用。

### 腾讯 WorkBuddy

从 [v0.0.1 发布页](https://github.com/BorisZhangYYY/session-name/releases/tag/v0.0.1) 下载 `session-name-v0.0.1-workbuddy.zip`。打开桌面端的 **专家·技能·连接器 → 技能 → 添加技能 → 上传技能**，导入 ZIP。只在当前项目使用时，也可放入[官方项目技能目录](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Project) `.codebuddy/skills/session-name/`。

也可以在本地生成 ZIP；它不包含其他宿主的改名脚本和个人配置：

```sh
python3 tools/package_workbuddy.py session-name-workbuddy.zip
```

## 使用

对 Agent 说「给当前会话起个名字」，或在支持的宿主中输入 `/session-name`。说「只推荐，先别改」只会得到建议；指定完整标题则不套模板。能验证写入结果时，技能会报告已应用的标题，并给出 1～2 个未应用的备选名。

| Agent | 改名方式 |
| --- | --- |
| Hermes Agent | 通过官方 `hermes sessions rename` 命令写入，再读回同一会话。 |
| OpenClaw | 在权限允许时，通过原生会话工具修改并读回当前会话标签。 |
| Claude Code | 通过 Claude Agent SDK 改名并读回本地会话；需在适配器使用的 Python 环境中另装 SDK（`python -m pip install claude-agent-sdk==0.2.189`）。 |
| Codex | 通过本地 Codex App Server 改名并读回当前线程。 |
| DeepSeek Harness | 默认给建议；已有可信的当前会话工具（如可选的 `set_session_title`）时才尝试应用。 |
| 腾讯 WorkBuddy | 生成标题，由用户在当前任务的「重命名」菜单中应用。 |

依赖和读回条件详见[宿主说明](../skills/session-name/references/hosts.md)。Hermes、Claude Code、Codex 已对隔离会话实测；OpenClaw 已验证网关层，DSH 桌面端加载和 WorkBuddy 桌面端导入未做端到端验证。

## 自定义

在已安装的技能目录中创建 `references/config.json`，可新增或禁用分类、选择回退分类，以及修改标题模板。比如设为 `"template": "{date}-{topic}"` 可恢复日期格式。没有配置时使用[内置默认值](../skills/session-name/references/prefixes.json)。如安装器会替换整个技能目录，请在升级前备份配置。具体示例见[配置指南](../skills/session-name/references/configuration.md)。

## 仓库结构

- [`skills/session-name/`](../skills/session-name/)：真正安装的技能，包含命名流程、参考资料和脚本。
- [`tools/`](../tools/)：WorkBuddy 打包工具，不随技能安装。
- [`tests/`](../tests/)：在仓库根目录运行 `node --test tests/*.test.mjs` 和 `python3 -m unittest discover -s tests`。

[更新日志](../CHANGELOG.md) · [MIT 许可证](../LICENSE)
