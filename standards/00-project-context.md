# 00 · 项目上下文 〔本项目活记忆 · AI 维护〕

> **作用**:这是项目的“身份档案”。AI 接管项目时先读这里,了解项目目标、技术栈、目录、部署取值。
> **更新时机**:架构、技术栈、目录结构、端口、部署目录、重要约束变化时更新。

---

## 1. 项目是什么

- **项目名称**:`banksys_sy_qiuyu`
- **仓库名称**:`banksys_sy_qiuyu`
- **Docker 镜像/容器名称**:`banksys_sy_qiuyu`
- **一句话目标**:基于银行营销数据构建一个 Streamlit Web 应用,提供交互式数据分析与在线认购预测。
- **使用者/受益者**:课程评审者、项目开发者、银行营销业务分析人员。
- **核心功能**:
  - 数据分析交互页面:浏览银行营销数据,查看字段分布、目标变量分布、筛选结果与基础统计。
  - 在线预测系统:基于离线训练模型,通过点选/输入客户特征,预测客户是否会认购。
  - 工程化交付:Python 3.11、Streamlit、pytest、ruff、Docker、GitHub Actions CI/CD 全链路跑通。
- **输入/数据**:`data/` 目录下银行营销 CSV 数据。
  - `data/test.csv`:包含特征列与 `subscribe` 标签,可用于训练/验证或样本检查。
  - `data/train.csv`:当前表头未发现 `subscribe` 标签,需要在建模前确认该文件是否为待预测集、是否另有标签文件,或是否文件命名与常规 train/test 语义相反。
  - 数据属于课程/公开项目数据;如确认无敏感个人身份信息,可随开源仓库保留。若后续发现敏感字段,必须从 Git 中移除并改为下载或样本化。

## 2. 技术栈

| 层 | 选型 | 理由 |
|---|---|---|
| 语言/运行时 | Python 3.11 | 数据分析、机器学习与 Streamlit 生态成熟,符合项目约束 |
| Web/API 框架 | Streamlit | 快速构建数据分析与表单预测页面,适合教学演示 |
| 数据处理/建模 | pandas + scikit-learn | 适合 CSV 清洗、特征工程、分类模型训练与可复现 pipeline |
| 测试 | pytest | Python 项目通用测试框架,易接入 CI |
| 格式/静态检查 | ruff | 同时覆盖格式与 lint,速度快,配置简单 |
| 打包/运行 | Docker | 统一运行环境,便于 CD 部署 |
| CI/CD | GitHub Actions | 通用、可视化、适合教学与团队协作 |

## 3. 目录地图

```text
banksys_sy_qiuyu/
├── standards/                 # AI 项目记忆与通用规范
├── data/                      # 银行营销 CSV 数据
│   ├── train.csv
│   └── test.csv
├── src/                       # 计划放置可测试业务逻辑:数据加载、特征工程、训练、预测
├── app.py                     # 计划 Streamlit 应用入口
├── tests/                     # 计划 pytest 测试
├── models/                    # 计划本地模型产物目录;默认不提交大型二进制产物
├── requirements.txt           # 生产运行依赖
├── requirements-dev.txt       # 本地/CI 检查依赖
├── Dockerfile                 # 容器构建
├── .github/workflows/
│   ├── ci.yml                 # PR/push CI
│   └── cd.yml                 # main 合并后 CD
└── README.md                  # 项目说明、运行与部署说明
```

> 新增目录前先更新本节,避免项目越做越散。

## 4. 质量门槛

| 类型 | 本项目标准 |
|---|---|
| 格式检查 | `ruff format --check .` |
| 静态检查 | `ruff check .` |
| 单元测试 | `pytest --cov --cov-fail-under=80` |
| 覆盖率 | 核心逻辑覆盖率 >= 80% |
| 构建 | CI 中 `docker build` 成功 |
| 业务/模型指标 | 离线训练流程输出可复现评估指标;分类模型至少记录 accuracy、precision、recall、F1 或 ROC-AUC 中的适用指标,并在 PR 中说明选择理由 |
| 应用验证 | Streamlit 应用可在 8888 端口启动;预测页输入完整特征后返回“会认购/不会认购”及概率或置信度 |
| 健康检查 | 容器部署后可通过 Streamlit HTTP 首页或约定健康检查地址验证服务可访问 |

## 5. 不变约束

- 密钥、密码、私钥、Token **绝不写进代码或文档**,只进 GitHub Secrets / 环境变量。
- 开源仓库默认不提交大体积模型产物;若模型文件较小且为演示必需,需在 PR 中说明并更新本节。
- 数据集默认保留在 `data/`;如后续确认数据敏感或体积不适合 Git,改为 `.gitignore` 排除并在 CI 中生成/下载样本数据。
- `main` 分支受保护,日常开发必须走 feature 分支 + PR。
- CI 红灯不合并。
- 第一阶段只填写标准文档并等待人工确认,不开始写应用代码。

## 6. 部署/CI 占位符取值

> `guides/` 和 workflow 里的通用占位符,在本项目里的真实值只写这里。

| 占位符 | 本项目取值 | 说明 |
|---|---|---|
| `<APP>` | `banksys_sy_qiuyu` | 应用名、镜像名、容器名统一取值 |
| `<DEPLOY_DIR>` | `/opt/banksys_sy_qiuyu` | 服务器部署目录;如服务器有课程统一路径,以后再改 |
| `<PORT>` | `8888` | 对外服务端口 |
| `<PORT_MAX>` | `8898` | CD 端口回退预留区间上限 |
| `<PYVER>` | `3.11` | Python 版本 |
| `<HEALTHCHECK>` | `/` | Streamlit 默认首页可作为最小可访问性检查;若后续增加健康检查端点再改 |
| `<SSH_USER>` | `待配置` | 由人类在 GitHub Secrets 中配置 |
| `<SSH_HOST>` | `待配置` | 由人类在 GitHub Secrets 中配置 |
