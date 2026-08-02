# 01 · 需求 / 活 PRD 〔本项目活记忆 · AI 维护〕

> **作用**:这是本项目唯一的需求文档。所有新功能、缺陷、技术债都追加到这里,不要另起多个 PRD 文件。
> **更新时机**:每次有新需求、需求变更、验收标准变化时更新。

---

## 1. 需求来源

| 类型 | 来源 | 进入方式 |
|---|---|---|
| 功能需求 Feature | 用户 / 老师 / 产品 / 客户 | 写成用户故事 |
| 缺陷 Bug | 测试 / 线上日志 / 用户反馈 | 写复现步骤和期望结果 |
| 技术债 Tech Debt | 开发 / Review / CI/CD 故障 | 写影响和修复目标 |

---

## 2. Issue 生命周期

| 阶段 | 状态 | 动作 |
|---|---|---|
| 提出 | Open | 写清场景、目标、验收标准 |
| 排期 | Backlog / Todo | 决定优先级和负责人 |
| 开发 | In Progress | 从 main 开 feature 分支 |
| 评审 | In Review | 提 PR,等待 CI 和 Review |
| 合并 | Done | PR 合并 main,自动关闭 Issue |
| 验收 | Verified | 按验收标准确认 |

**追踪规则**:分支名带 Issue 号,PR 描述写 `closes #<编号>`。

---

## 3. 用户故事模板

```text
### US-<编号> <一句话标题> · 状态: Backlog
作为 <角色>,
我想要 <能力>,
以便 <价值>。

验收标准:
- AC1: Given <前提>,When <动作>,Then <可验证结果>。
- AC2: <补充标准>

技术备注:
- <可选:约束、边界、风险>
```

---

## 4. 需求清单

### US-1 初始化项目工程化与 CI/CD · 状态: Backlog

作为 **项目开发者**,
我想要 项目具备基础工程结构、测试、CI 与 CD,
以便 后续每次开发都能自动检查并自动部署。

验收标准:
- AC1: Given 项目已确认需求,When 初始化仓库与工程结构,Then 项目包含 `requirements.txt`、`requirements-dev.txt`、`Dockerfile`、`.github/workflows/ci.yml`、`.github/workflows/cd.yml`、`README.md`、`tests/` 等必要文件。
- AC2: Given 开发从 `main` 开始,When 开始第一项功能,Then 必须从 `main` 创建 feature 分支,不直接在 `main` 开发。
- AC3: Given PR 被创建或分支被推送,When GitHub Actions CI 运行,Then 至少执行 `ruff format --check .`、`ruff check .`、`pytest --cov --cov-fail-under=80` 与 `docker build`。
- AC4: Given CI 全绿且人工合并到 `main`,When CD 触发,Then 服务器使用 Docker 部署 `banksys_sy_qiuyu` 容器并监听 8888 或预留回退端口。
- AC5: Given CD 完成,When 访问健康检查地址,Then Streamlit 应用页面可访问且 Actions 日志打印最终端口。
- AC6: Given 任一阶段完成,When 会话结束或进入确认门,Then 更新 `standards/PROGRESS.md`。

技术备注:
- 仓库名称、Docker 镜像名、容器名统一为 `banksys_sy_qiuyu`。
- 服务器 Secrets 由人类配置:`SSH_PRIVATE_KEY`、`SSH_HOST`、`SSH_USER`。

### US-2 数据分析交互页面 · 状态: Backlog

作为 **银行营销业务分析人员**,
我想要 在 Web 页面中交互式查看银行营销数据,
以便 快速理解客户特征、营销触达特征与认购结果之间的关系。

验收标准:
- AC1: Given 应用已启动,When 用户打开数据分析页面,Then 页面展示数据集基本信息,包括行数、列数、字段列表与缺失值概览。
- AC2: Given 数据包含 `subscribe` 标签,When 用户查看目标变量分析,Then 页面展示认购/未认购数量与比例。
- AC3: Given 用户选择一个类别字段,When 页面刷新图表,Then 展示该字段的类别分布,并能按 `subscribe` 分组对比。
- AC4: Given 用户选择一个数值字段,When 页面刷新图表,Then 展示该字段的基础统计与分布情况。
- AC5: Given 用户设置筛选条件,When 条件生效,Then 表格与统计结果只基于筛选后的数据计算。
- AC6: Given 数据文件缺少目标标签或字段不一致,When 页面加载,Then 应用给出清晰提示,不中断整个应用。

技术备注:
- 图表实现需遵循后续数据可视化设计规范;在真正写图表代码前需先读取 `dataviz` 技能。
- 当前 `data/test.csv` 有 `subscribe` 标签,`data/train.csv` 表头未发现该标签,实现前需确认训练/测试文件语义。

### US-3 离线训练认购预测模型 · 状态: Backlog

作为 **项目开发者**,
我想要 基于银行营销历史数据离线训练一个可复现的分类模型,
以便 在线预测页面可以稳定判断用户是否可能认购。

验收标准:
- AC1: Given 可用训练数据已确认,When 运行训练入口,Then 程序完成数据加载、特征预处理、模型训练、评估与模型保存。
- AC2: Given 数据包含类别字段和数值字段,When 训练 pipeline 构建,Then 类别字段使用可处理未知类别的编码方式,数值字段按模型需要进行适当处理。
- AC3: Given 训练完成,When 查看输出日志或报告,Then 至少记录 accuracy、precision、recall、F1 或 ROC-AUC 中的适用指标,并说明主指标。
- AC4: Given 模型产物已保存,When 在线预测模块加载模型,Then 能使用同一套预处理逻辑完成推理,避免训练/预测特征不一致。
- AC5: Given CI 环境运行测试,When 执行模型相关测试,Then 测试使用小样本或固定随机种子,不依赖外部网络且结果可重复。
- AC6: Given 训练数据标签缺失,When 用户或 CI 运行训练,Then 程序失败时给出明确错误,说明缺少 `subscribe` 标签或需指定标签来源。

技术备注:
- 优先使用 scikit-learn `Pipeline` / `ColumnTransformer` 持久化完整预处理与模型。
- 大型模型产物默认不进 Git;小型课程演示产物是否提交需在 PR 中说明。

### US-4 在线预测系统 · 状态: Backlog

作为 **银行营销业务人员**,
我想要 通过点选和少量数值输入录入客户与营销特征,
以便 快速得到该客户是否会认购的预测结果。

验收标准:
- AC1: Given 离线模型已训练并可加载,When 用户打开在线预测页面,Then 页面显示与模型特征一致的输入控件。
- AC2: Given 字段为有限类别,When 用户录入信息,Then 页面使用下拉框、单选或点选形式输入,避免自由文本导致非法类别。
- AC3: Given 字段为数值字段,When 用户录入信息,Then 页面使用数值输入控件并提供合理默认值或范围。
- AC4: Given 用户点击预测,When 输入合法,Then 页面显示“会认购”或“不会认购”,并展示概率或置信度。
- AC5: Given 模型文件不存在或加载失败,When 页面进入预测功能,Then 应用提示需要先训练模型,并且其他页面仍可使用。
- AC6: Given 用户提交异常输入,When 预测执行,Then 应用给出可理解错误提示,不显示 Python 堆栈给最终用户。

技术备注:
- 预测表单字段必须来自训练 pipeline 的特征定义,避免手工散落配置。

### US-5 Streamlit 应用运行与 Docker 部署 · 状态: Backlog

作为 **项目使用者**,
我想要 能用本地命令和 Docker 方式启动应用,
以便 在开发机、CI 和服务器上都能复现运行。

验收标准:
- AC1: Given 本地已安装依赖,When 执行 `streamlit run app.py --server.port 8888`,Then 应用在 8888 端口可访问。
- AC2: Given Docker 镜像构建完成,When 运行容器,Then 容器内 Streamlit 服务监听固定端口并映射到主机 8888 或 CD 回退端口。
- AC3: Given 应用启动,When 访问 `/`,Then 返回 Streamlit 页面而不是连接失败。
- AC4: Given README 被查看,When 用户按文档操作,Then 能找到本地运行、测试、训练、Docker、CI/CD 的最小命令。

技术备注:
- Streamlit 默认健康检查可先使用首页 `/`;若后续增加更明确的健康检查,同步更新 `00-project-context.md`。

---

## 5. 非功能需求

- **安全**:密钥只进 Secrets,不进 Git;应用不展示敏感环境变量。
- **可维护**:一需求一小 PR,避免大爆炸式提交;业务逻辑与 Streamlit UI 分离。
- **可测试**:核心数据加载、特征处理、训练、预测逻辑必须有单元测试;UI 层保持薄。
- **可复现**:训练流程固定随机种子;CI 测试不依赖外部网络。
- **可部署**:部署后必须有健康检查或等价验证;端口采用 8888,必要时按标准回退。
- **开源合规**:仓库为开源仓库;README 需说明数据来源、运行方式和许可证/使用限制。
