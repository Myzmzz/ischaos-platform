# ISChaos-sub 混沌工程演练平台

基于业务链路的混沌工程演练平台，支持 Train-Ticket 微服务系统的故障注入配置、执行、状态监控与观测数据收集。

## 技术栈

- **后端**: Python 3.12 + Flask 3.1（前后端不分离，Jinja2 模板渲染）
- **前端**: Vue 3 (CDN) + AntV X6 (拓扑图) + ECharts (图表) + TailwindCSS (CDN)
- **数据库**: SQLite
- **故障注入**: Chaos Mesh Workflow API
- **观测平台**: Coroot API
- **集群感知**: Kubernetes Python Client
- **部署**: Docker → Harbor → Kubernetes

## 功能特性

- **链路拓扑可视化**: 15 个核心业务接口的调用链拓扑图（Dagre 分层布局）
- **10 种故障类型**: 网络延迟/丢包/隔离、Pod 故障/终止、CPU/内存压力、DNS 错误、节点级故障
- **一键执行演练**: 自动构建 Chaos Mesh Workflow 并提交，服务级故障互斥保护
- **实时状态监控**: 自动同步 Chaos Mesh 工作流状态，超时保护机制
- **故障指标验证**: 根据故障类型自动关联对应的可观测指标，ECharts 时序图展示
- **观测数据收集**: Traces / Metrics / Logs 三类数据独立采集与下载

## 快速开始

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 初始化数据库（从拓扑报告导入 15 个接口）
python init_db.py ../docs/topology_report.md

# 启动开发服务器
export KUBECONFIG=~/.kube/coroot-config
python app.py
# 访问 http://localhost:5001
```

### Docker 构建

```bash
docker build --platform linux/amd64 -t ischaos-platform .
docker run -p 5000:5000 ischaos-platform
```

### K8s 部署

```bash
export KUBECONFIG=~/.kube/coroot-config

# 创建 RBAC 权限
kubectl apply -f k8s/rbac.yaml

# 部署服务
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml

# 访问 http://<节点IP>:30580
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `CHAOS_MESH_URL` | http://116.63.51.45:30854 | Chaos Mesh Dashboard 地址 |
| `COROOT_URL` | http://116.63.51.45:30800 | Coroot API 地址 |
| `COROOT_USERNAME` | admin | Coroot 登录用户名 |
| `COROOT_PASSWORD` | 123456 | Coroot 登录密码 |
| `COROOT_PROJECT_ID` | jtcsxpmc | Coroot 项目 ID |
| `TARGET_NAMESPACE` | train-ticket | 故障注入目标命名空间 |
| `DATABASE_PATH` | data/ischaos.db | SQLite 数据库路径 |
| `KUBECONFIG` | ~/.kube/coroot-config | K8s 配置文件路径 |

## 项目结构

```
ischaos-platform/
├── app.py                    # Flask 主入口
├── config.py                 # 配置管理
├── init_db.py                # 数据库初始化 + 拓扑导入
├── requirements.txt          # Python 依赖
├── Dockerfile                # 容器构建
├── k8s/                      # K8s 部署清单
├── models/                   # 数据模型层（SQLite CRUD）
├── services/                 # 业务逻辑层
├── routes/                   # Flask 路由（Blueprint）
├── templates/                # Jinja2 HTML 模板
├── static/                   # 静态资源（JS/CSS）
├── data/                     # 数据文件
└── docs/                     # 项目文档
```

## 故障类型

| 类型 | Chaos Mesh 类型 | 说明 |
|------|----------------|------|
| network_delay | NetworkChaos | 网络延迟注入 |
| network_loss | NetworkChaos | 网络丢包注入 |
| network_partition | NetworkChaos | 网络隔离 |
| pod_failure | PodChaos | Pod 故障模拟 |
| pod_kill | PodChaos | Pod 终止 |
| stress_cpu | StressChaos | CPU 压力注入 |
| stress_mem | StressChaos | 内存压力注入 |
| dns_error | DNSChaos | DNS 解析错误 |
| node_cpu | PhysicalMachineChaos | 节点 CPU 压力 |
| node_mem | PhysicalMachineChaos | 节点内存压力 |

## 文档

- [需求分析文档](docs/需求分析文档.md)
- [设计文档](docs/设计文档.md)
- [用户手册](docs/用户手册.md)
