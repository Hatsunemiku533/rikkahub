# RikkaHub 魔改：构建与维护

本仓库是 `Hatsunemiku533/rikkahub`，手机工作区仓库 `rikkahub_workspace` 保持独立。
APK 使用 **官方 release 源码＋`patch/*.patch`** 构建；根目录历史 App 源码不参与发布。
实际开发使用被忽略的 `upstream/`，改完必须更新补丁，并在干净源码上按顺序回放。

## 当前功能与基线

基线为官方 **3.0.0 / 55a108a4477fa308d6eacbe22ebf2fb0ceea1420**。

- **对话压缩完全采用官方实现**：移除原有自定义压缩设置、运行逻辑和 UI 标签。
- 保留工作区双栏文件管理、路径显示、跨栏操作、左滑范围多选、底部基本/文件切换。
- 保留发送前图片压缩，默认关闭，支持 100–5000 KB 大小上限（默认 500）。
- 保留 `{{time}}` 时间变量和 Markdown 后台流式导出；图片使用文字占位符。
- 提供旧魔改数据库的升级迁移：保留对话、图片、分支与收藏，旧摘要转成官方检查点。

详细行为、迁移边界与补丁顺序见 [patch/README.md](patch/README.md)。

## 目录和构建链路

| 路径 | 用途 |
|---|---|
| `upstream/` | 实际开发用的独立上游 checkout，不入外层仓库 |
| `patch/` | 发布构建真正应用的补丁 |
| `scripts/` | 严格回放与构建指纹检查 |
| `.github/workflows/patch-validation.yml` | 独立回归测试和 Debug APK，不读取签名/通知 secrets |
| `.github/workflows/auto-build.yml` | 检查版本、回归、签名构建、Release 和原 ntfy 通知 |
| `backup/` | 本地历史资料，不提交 |
| 根目录 `app/`、`ai/` 等 | 历史源码，不能通过只修改这里改变 APK |

CI 从上游 tag 克隆源码，依次应用图片、UX、工作区、迁移四份补丁。
`master` 的 patch/script/auto-build 工作流变化会触发正式构建。
`fix/**` 分支及 PR 的相关变化触发不发布的验证构建。
定时检查比较上游 tag 和补丁/脚本/CI 指纹；手动运行强制重建。

沿用原仓库签名和通知配置，不读取或复制 secrets；手机已有本仓库签名的版本可覆盖升级。
签名构建发布和 ntfy 仍使用既有工作流；开发分支验证不会发布 APK。
电脑端可使用已有登录的 GitHub CLI；不要手工读取或复制 token。

## 维护与升级

1. 拉取本仓库最新状态，再准备对应上游 tag 的干净 checkout。
2. 阅读 `AGENTS.md` 和 `patch/README.md`，在 `upstream/` 实现变更。
3. 分阶段生成补丁，共享资源变更不能重复打包。
4. 在另一棵干净源码上运行 `bash scripts/apply-patches.sh <路径>`，检查严格回放一致。
5. 跑回归测试和 Android 构建后再发布。不能把跳过打包的定时运行当作新构建。

从旧魔改升级时，schema 25/26 与官方同号但字段不同，必须保留迁移补丁。
迁移结束匹配官方 schema 30；不使用清库、破坏性回退或“重新创建空数据库”。
未来上游 schema 变化需重新核对迁移和恢复路径。不要直接把旧自定义列的 AutoMigration
接到官方链路，也不要只通过版本号推断兼容性。

## 上游与许可

上游介绍见 [README_ZH_CN.md](README_ZH_CN.md)，采用 [AGPL-3.0](LICENSE)。
