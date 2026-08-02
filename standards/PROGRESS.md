# PROGRESS · banksys_sy_qiuyu 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的“存档点”。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by AI)

- **阶段**:`引导版完成,PR 已合并,CI/CD 全链路跑通`
- **对应 06 六步流程**:`第②步(引导提交)→ 第③④⑤步(CI 验证、CD 部署)完成;进入第⑥步:迭代功能开发`
- **上一步完成**:`PR #1 合并到 main(merge commit 2122ddf);CI(ruff+pytest+docker build)通过;CD 部署成功,健康检查返回 Streamlit 页面`
- **下一步 (TODO 第一条)**:`实现数据分析 Streamlit 页面,包含基础统计、目标变量分布、字段筛选与分布展示`
- **阻塞项**:`无(模型链路已打通:US-3 训练 pipeline 已实现,models/model.joblib 纳入 git 随 CD 同步,在线预测页已接入真实模型)`

---

## 待办清单 (TODO,按优先级)

- [x] 人工确认 `standards/00-project-context.md`、`standards/01-requirements.md` 与本文件初稿
- [x] 确认 `data/train.csv` / `data/test.csv` 的用途与 `subscribe` 标签来源(train.csv 含标签,test.csv 无)
- [x] 建立或确认 GitHub 开源仓库 `banksys_sy_qiuyu`
- [x] 提醒并等待人类配置 GitHub Actions Secrets:`SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`(已确认配置完成)
- [x] 从 `main` 创建第一条 feature 分支,建议 `feature/1-project-bootstrap`
- [x] 初始化 Python 3.11 + Streamlit 项目结构、依赖文件、README、ruff/pytest 配置
- [x] 实现数据加载与字段校验模块,并添加单元测试
- [x] **已决**:实现 US-3 训练 pipeline,模型纳入 git 随 CD 同步(方案 A);预测页接入真实模型
- [ ] 实现数据分析 Streamlit 页面,包含基础统计、目标变量分布、字段筛选与分布展示
- [x] 实现离线训练 pipeline,包含预处理、模型训练、评估、模型保存与测试
- [x] 实现在线预测页面,使用点选/数值控件输入并返回认购预测
- [x] 配置 Dockerfile,确保 Streamlit 在 8888 端口运行
- [x] 配置 GitHub Actions CI:ruff format、ruff check、pytest coverage、docker build
- [x] 配置 GitHub Actions CD:main 合并后部署容器并健康检查
- [x] 本地自检通过后提交并推送 feature 分支
- [x] 创建 PR,等待 CI 与人工 Review
- [x] 人工合并后跟踪 CD,记录最终端口与健康检查结果
- [x] 会话结束前持续更新本文件

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-08-02 | 技术栈采用 Python 3.11 + Streamlit + pytest + ruff + Docker + GitHub Actions | 用户明确指定,且适合数据分析与教学型 Web 应用 |
| 2026-08-02 | 应用、仓库、Docker 镜像/容器统一命名为 `banksys_sy_qiuyu` | 用户明确指定,减少 CI/CD 占位符混乱 |
| 2026-08-02 | 服务端口采用 `8888`,CD 可在 `8888-8898` 范围回退 | 用户指定主端口;标准 05 建议端口占用时自动回退 |
| 2026-08-02 | 第一阶段只更新标准文档,不开始写代码 | 用户明确要求“先停下让我确认,不要开始写代码” |

---

## 已知坑 (GOTCHAS)

- 文件名与常规语义相反:`data/train.csv` 才是带 `subscribe` 标签的训练集,`data/test.csv` 是无标签待预测集;曾一度误判为相反并写入文档,已在测试与文档中修正;验证方式:读取完整表头并在训练入口对标签列做显式校验。
- 模型文件到达服务器的链路是断的,且有两个隐形坑:(1) `.gitignore` 排除了 `models/*.joblib`,模型不进 git;(2) CD 的 `rsync --delete` 会删除目标端不在 git 内的文件——即使手动 scp 模型到服务器,下次部署也会被清掉。正路是让模型进 git 由 CD 同步,或在 CD 脚本中显式处理模型文件。
- 当前工作目录环境显示“不是 git repository”:进入建仓/分支流程前需先初始化或创建 GitHub 仓库;验证方式:`git status` 能正常识别仓库。

---

## 里程碑 (DONE)

- [x] 2026-08-02:读取项目标准文档与数据表头,完成项目上下文、需求用户故事和第一批 TODO 初稿。
- [x] 2026-08-02:PR #1 合并(commit 2122ddf),CI 通过,CD 部署成功——应用运行于 `http://<SSH_HOST>:8890/`(8888 被占用自动回退),健康检查返回 Streamlit 页面。
- [x] 2026-08-02:实现 US-3 训练 pipeline(LogisticRegression + ColumnTransformer,主指标 ROC-AUC 0.81,产物 8.7KB),`models/model.joblib` 纳入 git;预测页接入真实模型,在线预测可用。
