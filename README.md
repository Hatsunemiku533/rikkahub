# RikkaHub 魔改：电脑端工作区与构建交接

本目录从 `C:\Users\ATRI\Desktop\rikkahub_workspace\rikka魔改` 迁出，保留了旧 patch 与排查记录。**今后主要在电脑端读码、修改和维护 patch，本目录是开发工作区，不再是只读副本。** 新 patch 不需要同步回 `rikkahub_workspace`，也不套用该手机工作区的 sync / backup 流程。

手机仍是魔改 App 的使用与实机验收端；APK 构建沿用 GitHub fork + Actions 链路。**本目录现已是 `Hatsunemiku533/rikkahub` 的 Git 克隆，分支 `master`，保留原仓库历史、签名和 ntfy 配置。** 本地改动经验证、提交和推送后才会生效；不需要新建仓库或另配通知通道。

**重要：CI 构建的是上游 release + `patch/*.patch`，不是本仓库根目录的 App 源码。** 实际改码使用 `upstream/`；只改根目录 `app/`、`ai/` 等文件，或只改 `upstream/` 而不更新 patch，都不会改变发布 APK。具体补丁边界与验证说明见 [`patch/README.md`](patch/README.md)。

## 目录

| 路径 | 内容 |
|---|---|
| `.git/` | 原 fork 的 Git 历史；`origin` 为 `Hatsunemiku533/rikkahub`，工作分支为 `master` |
| `upstream/` | 真正的上游 Git 克隆，基于 `2.5.6` / `447bb7e89710d31f1204d7a2973baa19fdbd5b28`，已按 CI 顺序应用三份当前 patch；实际改码目录，不入外层仓库 |
| `patch/` | 从 fork 更新的现行 `2.5.6` 补丁及说明；修改这些文件并推送 `master` 会触发构建 |
| `.github/workflows/` | 自动构建、验证构建和补丁验证工作流 |
| `scripts/` | 顺序打 patch 与构建指纹检查脚本 |
| `backup/` | 旧 `rikkahub-master/` 源码副本，以及 `migration-20261006/` 内的旧 patch 和两处旧 README；仅本地保存，不入库 |
| 根目录 `app/`、`ai/` 等 | fork 保留的历史源码，不是当前发布构建输入 |
| `README.md` | 当前工作方式、构建交接及历史排查记录 |

旧 `2.5.2` patch 已归档，不再作为开发或发布输入。`rikkahub_workspace/rikka魔改` 已退出开发链路。

## 发布链路

```text
上游 rikkahub/rikkahub 发 release (tag x.y.z)
   ↓  每天 UTC 16:05（北京次日 00:05）auto-build.yml 检查
fork Hatsunemiku533/rikkahub（public，Issues 已关闭）
   ├─ check job：定时 heartbeat + 比较上游 tag 与 patch/脚本/CI 指纹
   ├─ build job：clone 上游 tag → 顺序打 patch → 回归测试 → 签名 assembleRelease
   ├─ 成功 → release auto-<tag>（arm64 APK）→ 原 ntfy topic 通知 → 更新构建状态
   └─ 失败 → Actions 日志；尝试发 issue，但 Issues 关闭时该步骤也会失败
```

- **生效位置**：fork 仓库 `patch/` 目录（CI 从那里 apply）。电脑上修改并验证后，获准发布时再更新 fork；不需要先同步到手机工作区。
- **触发方式**：`master` 上的 `patch/**`、`scripts/**`、`auto-build.yml` 变更自动触发；手动运行 `auto-build.yml` 强制重建；定时检查在上游版本或构建指纹变化时构建。只改本 README 不触发打包。
- **签名与通知**：沿用现有仓库 secrets：`KEYSTORE_BASE64`、`KEY_PASSWORD`、`KEY_ALIAS`、`NTFY_TOPIC`。它们保存在 GitHub，不是本地文件；改电脑目录无需更换 secrets。通知由 CI 请求 `ntfy.sh`，包含本仓库 Release 下载链接。
- **电脑端 GitHub 操作**：使用已登录的 GitHub CLI，PowerShell 中调用全路径 `& "C:\Program Files\GitHub CLI\gh.exe"`；2026-10-06 已确认登录账号为 `Hatsunemiku533`，具备 `repo` / `workflow` scope。无需沿用手机端 `~/.git-credentials` 或手工读取、复制 token。
- 手机 proot 的 GitHub TLS 中断是旧环境记录，不作为当前电脑端故障的默认解释。

## 魔改功能（当前 patch）

| # | 功能 | 主要文件 |
|---|---|---|
| 1 | 可配置图片压缩：设置→通用「发送图片压缩」开关（**默认关**）+ KB 数字输入框（默认 500，收敛 100–5000）；开启时最长边 1600px/400 万像素 + 循环降质量缩尺寸到目标 KB；等比缩放不裁剪，GIF 不动。移植自上游 PR #1710（closed 未合并，2026-09-24 适配 2.5.2 + 滑杆改输入框） | `ai/.../util/FileEncoder.kt`、`PreferencesStore.kt`、`SettingPreferencesGeneralPage.kt`、6 语言 strings（image-compress.patch） |
| 2 | 压缩对话目标大小可填 0 = 不限 | `ChatService.kt` compressConversation + `CompressContextDialog.kt` |
| 3 | 压缩后原始消息保留可见（`compressed`/`isSummary` 字段 + UI 标签），只发摘要+最近消息；**roll/编辑重发路径同样过滤 compressed（2026-09-24 修复暴涨 bug）** | `ChatService.kt`、`MessageNodeEntity.kt`、`ConversationRepository.kt`、`ChatMessage.kt`、DB 迁移 |
| 4 | 模式注入新增 `{{time}}` 变量 | `PlaceholderTransformer.kt` |
| 5 | Markdown 后台流式导出，支持选择是否保留思考内容；消息图片和工具返回图片仅保留占位符，不嵌入 Base64 或图片链接（长图导出不变） | `ConversationExport.kt`、`MarkdownExport.kt` 及回归测试 |

现行 `2.5.6` patch 还修复了压缩保留区的分支/收藏丢失、旧快照覆盖，以及图片压缩质量搜索结束后未达到大小上限的问题。压缩期间消息发生变化会中止写回，详细边界见 `patch/README.md`；旧排查记录保留在本地 `backup/migration-20261006/`，不随公开仓库发布。

上游 2.5.1 与魔改的重合情况（2026-09-13 核查）：ask_user 原生支持每题自由输入（模式注入里旧的 ask_user workaround 可删）；`{{time}}` 与上游 TimeReminderTransformer 机制不同（间隔提醒 vs 每次注入），保留；其余无重合。

## DB 迁移史（重要，别再踩）

- 魔改原设计：`AutoMigration(24,25)` 给 `message_node` 加 `compressed`/`is_summary` 列。
- **2.5.1 撞车**：上游自己也升到 version 25（workspace 表加 `shell_compatibility_mode`）。
- 2026-09-13 事故：我改成 `AutoMigration(25,26)` 顺延 → 已装用户的真实 DB 是"魔改25"（已有 compressed 列），与上游 25.json 不符 → `duplicate column name: compressed` 崩溃，App 能开但进对话就崩。
- **现行方案（opencode 修复，commit `9913f1c2`）**：删掉撞车的 AutoMigration，改**手工迁移** `PatchMigration_24_25` / `PatchMigration_25_26`（列已存在就跳过），上游 workspace 新列同样"有则跳过"。以后上游再升版本号，魔改迁移照此模式顺延，**永远用手工迁移判断列是否存在，不要用 AutoMigration 加自定义列**。
- **当前方案（2.5.6）**：现行 patch 仍使用魔改 schema 26 和带列存在检查的 24→25、25→26 迁移；已从原 fork 取回适配版。以后上游 schema 变化仍需重新核对迁移路径，不以旧源码副本的版本号推断兼容性。

## 当前电脑端状态（2026-10-06）

- 本目录连接原 fork，Git 历史与远端配置均保留；现行 patch、工作流与构建脚本已落到电脑。
- `upstream/` 已在真正的上游 `2.5.6` 干净基线上按脚本顺序回放当前 patch，并通过 `git diff --check`。
- 最近一次实际发布验证：2026-10-03 的 Actions run `37091498929`，回归测试、Release 构建、发布和 ntfy 请求均成功。之后定时检查因指纹未变而跳过打包；不能把这些跳过的运行当成新构建。
- 本次迁移不修改构建逻辑、签名或 ntfy topic，无需重复发布相同 APK。未验证电脑端 Android 构建环境，也未确认手机实际装机版本或通知是否展示。

## 电脑端常用操作

以下使用 Windows PowerShell。只读查询可直接运行；更新 fork、触发构建等远端操作需有本次明确授权。

```powershell
# 在本项目根目录查看状态、更新电脑入口
git status --short --branch
git pull --ff-only origin master

# 查询 fork 的近期构建（可在任意目录运行）
& "C:\Program Files\GitHub CLI\gh.exe" run list --repo Hatsunemiku533/rikkahub --workflow auto-build.yml --limit 5

# 获准后强制重建当前 patch 基线；手动运行会强制重建，不再只依赖 last_built.txt
& "C:\Program Files\GitHub CLI\gh.exe" workflow run auto-build.yml --repo Hatsunemiku533/rikkahub --ref master -f ref=2.5.6
```

开发时先拉取外层仓库最新状态；`upstream/` 是独立 Git 仓库，外层 pull 不会自动更新它或重打 patch。实际修改 `upstream/` 后，按两阶段流程更新 `patch/`，在另一棵干净基线树回放并验证，再只提交本次相关文件、推送 `master`。不要在已有改动的树上重复打 patch 或直接清空改动。

本地检查必须在**对应上游版本的干净源码树**中进行，按实际 CI 顺序逐份应用并验证。在项目根目录使用 Git Bash 的脚本入口如下；当前 `upstream/` 已应用 patch，不能重复执行：

```powershell
# 仅对新准备的干净上游目录执行；将路径改为该目录
& "C:\Program Files\Git\bin\bash.exe" scripts/apply-patches.sh "干净上游目录的完整路径"
```

`git apply --check` 只检查、不修改文件；两份 patch 共用字符串资源，分别对同一棵未应用任何 patch 的树检查，不能代替顺序回放验证。**重制 patch 用两阶段方法**：干净基线只实现图片压缩，生成 `image-compress.patch`；在其上叠加 UX 改动，生成相对第一阶段的 `user-experience.patch`。不要把共享文件的改动重复打包，最后必须按 CI 顺序在干净基线上回放。

电脑端本地构建使用 `upstream/gradlew.bat`，须先确认 JDK、Android SDK 与构建配置；发布默认仍走 Actions。

## 上游与许可

上游项目介绍见 [`README_ZH_CN.md`](README_ZH_CN.md)，许可证为 [AGPL-3.0](LICENSE)。
