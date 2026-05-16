# Train-Ticket 压测链路拓扑报告

## 测试概览

- **测试文件**: tt_1.jmx
- **测试时间**: 2026-03-12 00:16:12 CST ~ 2026-03-12 00:18:13 CST
- **总接口数**: 15 个
- **总样本数**: 1831
- **数据来源**: Coroot ClickHouse（otel_traces 表，仅成功请求）
- **每接口采样 Trace 数**: 3 条

---

## 接口 1: Login

- **URL**: `http://116.63.51.45:32677/api/v1/users/login`
- **Coroot SpanName**: `POST /api/v1/users/login`
- **总请求数**: 10 (成功 10)
- **时间窗口**: 00:16:12 ~ 00:16:18

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-auth-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-verification-code-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-auth-service | MONGODB | MONGODB |
| ts-auth-service | ts-verification-code-service | HTTP |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "Login (POST /api/v1/users/login)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-auth-service",
        "type": "service",
        "label": "ts-auth-service",
        "root": true
      },
      {
        "id": "ts-verification-code-service",
        "type": "service",
        "label": "ts-verification-code-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-auth-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-auth-service",
        "target": "ts-verification-code-service",
        "label": "HTTP"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `4427a85390a1e441c0a533bc3bf64607` (总耗时: 91.3ms, span 数: 7)

```
└── [ts-auth-service] POST /api/v1/users/login  (0ms ~ 91ms, 91.3ms)
    ├── [ts-auth-service] GET  (2ms ~ 9ms, 6.6ms)
    │   └── [ts-verification-code-service] GET /api/v1/verifycode/verify/{verifyCode}  (5ms ~ 10ms, 4.5ms)
    ├── [ts-auth-service] UserRepository.findByUsername  (9ms ~ 11ms, 1.9ms)
    │   └── [ts-auth-service] find ts-auth-mongo.user  (10ms ~ 11ms, 0.8ms)
    └── [ts-auth-service] UserRepository.findByUsername  (87ms ~ 89ms, 1.8ms)
        └── [ts-auth-service] find ts-auth-mongo.user  (88ms ~ 89ms, 0.6ms)
```

**Trace 2**: `2f89230132ecefc80087ddb22d1a9dfc` (总耗时: 90.3ms, span 数: 7)

```
└── [ts-auth-service] POST /api/v1/users/login  (0ms ~ 90ms, 90.3ms)
    ├── [ts-auth-service] GET  (2ms ~ 7ms, 5.3ms)
    │   └── [ts-verification-code-service] GET /api/v1/verifycode/verify/{verifyCode}  (4ms ~ 8ms, 3.8ms)
    ├── [ts-auth-service] UserRepository.findByUsername  (8ms ~ 10ms, 1.7ms)
    │   └── [ts-auth-service] find ts-auth-mongo.user  (9ms ~ 10ms, 0.6ms)
    └── [ts-auth-service] UserRepository.findByUsername  (86ms ~ 88ms, 1.9ms)
        └── [ts-auth-service] find ts-auth-mongo.user  (87ms ~ 88ms, 0.7ms)
```

---

## 接口 2: 查票

- **URL**: `http://116.63.51.45:32677/api/v1/travelservice/trips/left`
- **Coroot SpanName**: `POST /api/v1/travelservice/trips/left`
- **总请求数**: 133 (成功 133)
- **时间窗口**: 00:16:14 ~ 00:18:12

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-travel-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-basic-service | service | 微服务 |
| ts-config-service | service | 微服务 |
| ts-order-service | service | 微服务 |
| ts-price-service | service | 微服务 |
| ts-route-service | service | 微服务 |
| ts-seat-service | service | 微服务 |
| ts-station-service | service | 微服务 |
| ts-ticketinfo-service | service | 微服务 |
| ts-train-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-basic-service | ts-price-service | HTTP |
| ts-basic-service | ts-route-service | HTTP |
| ts-basic-service | ts-station-service | HTTP |
| ts-basic-service | ts-train-service | HTTP |
| ts-config-service | MONGODB | MONGODB |
| ts-order-service | MONGODB | MONGODB |
| ts-price-service | MONGODB | MONGODB |
| ts-route-service | MONGODB | MONGODB |
| ts-seat-service | ts-config-service | HTTP |
| ts-seat-service | ts-order-service | HTTP |
| ts-seat-service | ts-travel-service | HTTP |
| ts-station-service | MONGODB | MONGODB |
| ts-ticketinfo-service | ts-basic-service | HTTP |
| ts-train-service | MONGODB | MONGODB |
| ts-travel-service | MONGODB | MONGODB |
| ts-travel-service | ts-order-service | HTTP |
| ts-travel-service | ts-route-service | HTTP |
| ts-travel-service | ts-seat-service | HTTP |
| ts-travel-service | ts-ticketinfo-service | HTTP |
| ts-travel-service | ts-train-service | HTTP |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "查票 (POST /api/v1/travelservice/trips/left)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-basic-service",
        "type": "service",
        "label": "ts-basic-service",
        "root": false
      },
      {
        "id": "ts-config-service",
        "type": "service",
        "label": "ts-config-service",
        "root": false
      },
      {
        "id": "ts-order-service",
        "type": "service",
        "label": "ts-order-service",
        "root": false
      },
      {
        "id": "ts-price-service",
        "type": "service",
        "label": "ts-price-service",
        "root": false
      },
      {
        "id": "ts-route-service",
        "type": "service",
        "label": "ts-route-service",
        "root": false
      },
      {
        "id": "ts-seat-service",
        "type": "service",
        "label": "ts-seat-service",
        "root": false
      },
      {
        "id": "ts-station-service",
        "type": "service",
        "label": "ts-station-service",
        "root": false
      },
      {
        "id": "ts-ticketinfo-service",
        "type": "service",
        "label": "ts-ticketinfo-service",
        "root": false
      },
      {
        "id": "ts-train-service",
        "type": "service",
        "label": "ts-train-service",
        "root": false
      },
      {
        "id": "ts-travel-service",
        "type": "service",
        "label": "ts-travel-service",
        "root": true
      }
    ],
    "edges": [
      {
        "source": "ts-basic-service",
        "target": "ts-price-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-train-service",
        "label": "HTTP"
      },
      {
        "source": "ts-config-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-price-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-route-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-config-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-travel-service",
        "label": "HTTP"
      },
      {
        "source": "ts-station-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-ticketinfo-service",
        "target": "ts-basic-service",
        "label": "HTTP"
      },
      {
        "source": "ts-train-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-train-service",
        "label": "HTTP"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `bd4562778b8ab4a9ca5e659bbde308d4` (总耗时: 145.2ms, span 数: 173)

```
└── [ts-travel-service] POST /api/v1/travelservice/trips/left  (0ms ~ 145ms, 145.2ms)
    ├── [ts-travel-service] GET  (0ms ~ 9ms, 8.9ms)
    │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (3ms ~ 10ms, 6.6ms)
    │       └── [ts-ticketinfo-service] GET  (3ms ~ 9ms, 5.9ms)
    │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (3ms ~ 8ms, 5.2ms)
    │               └── [ts-basic-service] GET  (3ms ~ 7ms, 4.5ms)
    │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (6ms ~ 8ms, 1.8ms)
    │                       └── [ts-station-service] StationRepository.findByName  (6ms ~ 7ms, 1.2ms)
    │                           └── [ts-station-service] find ts.station  (6ms ~ 7ms, 1.0ms)
    ├── [ts-travel-service] GET  (10ms ~ 14ms, 4.3ms)
    │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (10ms ~ 13ms, 3.4ms)
    │       └── [ts-ticketinfo-service] GET  (10ms ~ 12ms, 2.4ms)
    │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (11ms ~ 13ms, 2.2ms)
    │               └── [ts-basic-service] GET  (11ms ~ 12ms, 1.4ms)
    │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (12ms ~ 13ms, 1.1ms)
    │                       └── [ts-station-service] StationRepository.findByName  (12ms ~ 12ms, 0.4ms)
    │                           └── [ts-station-service] find ts.station  (12ms ~ 12ms, 0.3ms)
    ├── [ts-travel-service] TripRepository.findAll  (14ms ~ 14ms, 0.4ms)
    │   └── [ts-travel-service] find ts.trip  (14ms ~ 14ms, 0.3ms)
    ├── [ts-travel-service] GET  (15ms ~ 17ms, 1.8ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (15ms ~ 16ms, 0.8ms)
    │       └── [ts-route-service] RouteRepository.findById  (15ms ~ 15ms, 0.3ms)
    │           └── [ts-route-service] find ts.routes  (15ms ~ 15ms, 0.2ms)
    ├── [ts-travel-service] GET  (17ms ~ 19ms, 1.8ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (18ms ~ 19ms, 0.8ms)
    │       └── [ts-route-service] RouteRepository.findById  (18ms ~ 18ms, 0.3ms)
    │           └── [ts-route-service] find ts.routes  (18ms ~ 18ms, 0.2ms)
    ├── [ts-travel-service] GET  (19ms ~ 21ms, 1.8ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (20ms ~ 21ms, 0.7ms)
    │       └── [ts-route-service] RouteRepository.findById  (20ms ~ 20ms, 0.3ms)
... (143 more spans)
```

**Trace 2**: `e99643ce563b254c24c9bae97e92882b` (总耗时: 108.3ms, span 数: 173)

```
└── [ts-travel-service] POST /api/v1/travelservice/trips/left  (0ms ~ 108ms, 108.3ms)
    ├── [ts-travel-service] GET  (0ms ~ 5ms, 5.0ms)
    │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (2ms ~ 5ms, 3.3ms)
    │       └── [ts-ticketinfo-service] GET  (2ms ~ 5ms, 2.6ms)
    │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (2ms ~ 4ms, 2.2ms)
    │               └── [ts-basic-service] GET  (2ms ~ 3ms, 1.4ms)
    │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (3ms ~ 4ms, 1.1ms)
    │                       └── [ts-station-service] StationRepository.findByName  (3ms ~ 3ms, 0.5ms)
    │                           └── [ts-station-service] find ts.station  (3ms ~ 3ms, 0.3ms)
    ├── [ts-travel-service] GET  (5ms ~ 9ms, 4.1ms)
    │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (6ms ~ 9ms, 3.1ms)
    │       └── [ts-ticketinfo-service] GET  (6ms ~ 8ms, 2.3ms)
    │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (7ms ~ 9ms, 2.0ms)
    │               └── [ts-basic-service] GET  (7ms ~ 8ms, 1.4ms)
    │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (7ms ~ 8ms, 1.1ms)
    │                       └── [ts-station-service] StationRepository.findByName  (7ms ~ 7ms, 0.5ms)
    │                           └── [ts-station-service] find ts.station  (7ms ~ 7ms, 0.3ms)
    ├── [ts-travel-service] TripRepository.findAll  (9ms ~ 9ms, 0.4ms)
    │   └── [ts-travel-service] find ts.trip  (9ms ~ 9ms, 0.2ms)
    ├── [ts-travel-service] GET  (10ms ~ 12ms, 1.9ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (11ms ~ 12ms, 0.8ms)
    │       └── [ts-route-service] RouteRepository.findById  (11ms ~ 11ms, 0.3ms)
    │           └── [ts-route-service] find ts.routes  (11ms ~ 11ms, 0.2ms)
    ├── [ts-travel-service] GET  (12ms ~ 14ms, 1.8ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (13ms ~ 14ms, 0.7ms)
    │       └── [ts-route-service] RouteRepository.findById  (13ms ~ 13ms, 0.3ms)
    │           └── [ts-route-service] find ts.routes  (13ms ~ 13ms, 0.1ms)
    ├── [ts-travel-service] GET  (14ms ~ 16ms, 1.8ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (15ms ~ 16ms, 0.7ms)
    │       └── [ts-route-service] RouteRepository.findById  (15ms ~ 15ms, 0.3ms)
... (143 more spans)
```

---

## 接口 3: 查票2

- **URL**: `http://116.63.51.45:32677/api/v1/travel2service/trips/left`
- **Coroot SpanName**: `POST /api/v1/travel2service/trips/left`
- **总请求数**: 133 (成功 133)
- **时间窗口**: 00:16:14 ~ 00:18:12

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-travel2-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-basic-service | service | 微服务 |
| ts-route-service | service | 微服务 |
| ts-station-service | service | 微服务 |
| ts-ticketinfo-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-basic-service | ts-station-service | HTTP |
| ts-route-service | MONGODB | MONGODB |
| ts-station-service | MONGODB | MONGODB |
| ts-ticketinfo-service | ts-basic-service | HTTP |
| ts-travel2-service | MONGODB | MONGODB |
| ts-travel2-service | ts-route-service | HTTP |
| ts-travel2-service | ts-ticketinfo-service | HTTP |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "查票2 (POST /api/v1/travel2service/trips/left)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-basic-service",
        "type": "service",
        "label": "ts-basic-service",
        "root": false
      },
      {
        "id": "ts-route-service",
        "type": "service",
        "label": "ts-route-service",
        "root": false
      },
      {
        "id": "ts-station-service",
        "type": "service",
        "label": "ts-station-service",
        "root": false
      },
      {
        "id": "ts-ticketinfo-service",
        "type": "service",
        "label": "ts-ticketinfo-service",
        "root": false
      },
      {
        "id": "ts-travel2-service",
        "type": "service",
        "label": "ts-travel2-service",
        "root": true
      }
    ],
    "edges": [
      {
        "source": "ts-basic-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-route-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-station-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-ticketinfo-service",
        "target": "ts-basic-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `48cd122dce8620cfc32634f1c30c761f` (总耗时: 17.6ms, span 数: 39)

```
└── [ts-travel2-service] POST /api/v1/travel2service/trips/left  (0ms ~ 18ms, 17.6ms)
    ├── [ts-travel2-service] GET  (1ms ~ 4ms, 3.1ms)
    │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (1ms ~ 4ms, 2.9ms)
    │       └── [ts-ticketinfo-service] GET  (1ms ~ 3ms, 2.1ms)
    │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (2ms ~ 4ms, 1.8ms)
    │               └── [ts-basic-service] GET  (2ms ~ 3ms, 1.2ms)
    │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (2ms ~ 3ms, 1.0ms)
    │                       └── [ts-station-service] StationRepository.findByName  (2ms ~ 2ms, 0.4ms)
    │                           └── [ts-station-service] find ts.station  (2ms ~ 2ms, 0.3ms)
    ├── [ts-travel2-service] GET  (4ms ~ 7ms, 3.1ms)
    │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (4ms ~ 7ms, 3.1ms)
    │       └── [ts-ticketinfo-service] GET  (4ms ~ 6ms, 2.2ms)
    │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (5ms ~ 7ms, 1.9ms)
    │               └── [ts-basic-service] GET  (5ms ~ 6ms, 1.4ms)
    │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (5ms ~ 6ms, 1.2ms)
    │                       └── [ts-station-service] StationRepository.findByName  (5ms ~ 5ms, 0.5ms)
    │                           └── [ts-station-service] find ts.station  (5ms ~ 5ms, 0.4ms)
    ├── [ts-travel2-service] TripRepository.findAll  (7ms ~ 9ms, 1.5ms)
    │   └── [ts-travel2-service] find ts.trip  (7ms ~ 8ms, 1.3ms)
    ├── [ts-travel2-service] GET  (9ms ~ 10ms, 1.1ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (9ms ~ 10ms, 0.7ms)
    │       └── [ts-route-service] RouteRepository.findById  (9ms ~ 9ms, 0.3ms)
    │           └── [ts-route-service] find ts.routes  (9ms ~ 9ms, 0.2ms)
    ├── [ts-travel2-service] GET  (10ms ~ 11ms, 1.1ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (11ms ~ 12ms, 0.8ms)
    │       └── [ts-route-service] RouteRepository.findById  (11ms ~ 11ms, 0.3ms)
    │           └── [ts-route-service] find ts.routes  (11ms ~ 11ms, 0.2ms)
    ├── [ts-travel2-service] GET  (12ms ~ 13ms, 1.0ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (12ms ~ 13ms, 0.7ms)
    │       └── [ts-route-service] RouteRepository.findById  (12ms ~ 12ms, 0.3ms)
... (9 more spans)
```

**Trace 2**: `be89a697f59eb6feaf9ec61336e54a7c` (总耗时: 20.4ms, span 数: 39)

```
└── [ts-travel2-service] POST /api/v1/travel2service/trips/left  (0ms ~ 20ms, 20.4ms)
    ├── [ts-travel2-service] GET  (1ms ~ 8ms, 6.6ms)
    │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (1ms ~ 7ms, 6.3ms)
    │       └── [ts-ticketinfo-service] GET  (1ms ~ 6ms, 5.5ms)
    │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (2ms ~ 7ms, 5.2ms)
    │               └── [ts-basic-service] GET  (2ms ~ 6ms, 4.5ms)
    │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (6ms ~ 7ms, 1.0ms)
    │                       └── [ts-station-service] StationRepository.findByName  (6ms ~ 6ms, 0.4ms)
    │                           └── [ts-station-service] find ts.station  (6ms ~ 6ms, 0.3ms)
    ├── [ts-travel2-service] GET  (8ms ~ 11ms, 3.2ms)
    │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (8ms ~ 11ms, 3.0ms)
    │       └── [ts-ticketinfo-service] GET  (8ms ~ 10ms, 2.3ms)
    │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (9ms ~ 11ms, 2.1ms)
    │               └── [ts-basic-service] GET  (9ms ~ 10ms, 1.3ms)
    │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (10ms ~ 11ms, 1.0ms)
    │                       └── [ts-station-service] StationRepository.findByName  (10ms ~ 10ms, 0.4ms)
    │                           └── [ts-station-service] find ts.station  (10ms ~ 10ms, 0.3ms)
    ├── [ts-travel2-service] TripRepository.findAll  (11ms ~ 13ms, 1.5ms)
    │   └── [ts-travel2-service] find ts.trip  (11ms ~ 12ms, 1.3ms)
    ├── [ts-travel2-service] GET  (12ms ~ 13ms, 1.0ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (13ms ~ 14ms, 0.7ms)
    │       └── [ts-route-service] RouteRepository.findById  (13ms ~ 13ms, 0.3ms)
    │           └── [ts-route-service] find ts.routes  (13ms ~ 13ms, 0.1ms)
    ├── [ts-travel2-service] GET  (14ms ~ 15ms, 1.1ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (15ms ~ 16ms, 0.8ms)
    │       └── [ts-route-service] RouteRepository.findById  (15ms ~ 15ms, 0.3ms)
    │           └── [ts-route-service] find ts.routes  (15ms ~ 15ms, 0.2ms)
    ├── [ts-travel2-service] GET  (15ms ~ 16ms, 1.0ms)
    │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (16ms ~ 17ms, 0.7ms)
    │       └── [ts-route-service] RouteRepository.findById  (16ms ~ 16ms, 0.3ms)
... (9 more spans)
```

---

## 接口 4: 获取食物

- **URL**: `http://116.63.51.45:32677/api/v1/foodservice/foods/2026-03-31/Shang%20Hai/Su%20Zhou/G1234`
- **Coroot SpanName**: `GET /api/v1/foodservice/foods/{date}/{startStation}/{endStation}/{tripId}`
- **总请求数**: 133 (成功 133)
- **时间窗口**: 00:16:14 ~ 00:18:13

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-food-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-food-map-service | service | 微服务 |
| ts-route-service | service | 微服务 |
| ts-station-service | service | 微服务 |
| ts-travel-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-food-map-service | MONGODB | MONGODB |
| ts-food-service | ts-food-map-service | HTTP |
| ts-food-service | ts-station-service | HTTP |
| ts-food-service | ts-travel-service | HTTP |
| ts-route-service | MONGODB | MONGODB |
| ts-station-service | MONGODB | MONGODB |
| ts-travel-service | MONGODB | MONGODB |
| ts-travel-service | ts-route-service | HTTP |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "获取食物 (GET /api/v1/foodservice/foods/{date}/{startStation}/{endStation}/{tripId})",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-food-map-service",
        "type": "service",
        "label": "ts-food-map-service",
        "root": false
      },
      {
        "id": "ts-food-service",
        "type": "service",
        "label": "ts-food-service",
        "root": true
      },
      {
        "id": "ts-route-service",
        "type": "service",
        "label": "ts-route-service",
        "root": false
      },
      {
        "id": "ts-station-service",
        "type": "service",
        "label": "ts-station-service",
        "root": false
      },
      {
        "id": "ts-travel-service",
        "type": "service",
        "label": "ts-travel-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-food-map-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-food-service",
        "target": "ts-food-map-service",
        "label": "HTTP"
      },
      {
        "source": "ts-food-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-food-service",
        "target": "ts-travel-service",
        "label": "HTTP"
      },
      {
        "source": "ts-route-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-station-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-route-service",
        "label": "HTTP"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `629a9a52c0da321241ec1b7b9a4b80bb` (总耗时: 22.7ms, span 数: 25)

```
└── [ts-food-service] GET /api/v1/foodservice/foods/{date}/{startStation}/{endStation}/{tripId}  (0ms ~ 23ms, 22.7ms)
    ├── [ts-food-service] GET  (2ms ~ 7ms, 5.2ms)
    │   └── [ts-food-map-service] GET /api/v1/foodmapservice/trainfoods/{tripId}  (3ms ~ 7ms, 4.0ms)
    │       └── [ts-food-map-service] TrainFoodRepository.findByTripId  (4ms ~ 6ms, 1.7ms)
    │           └── [ts-food-map-service] find ts.trainfoods  (5ms ~ 6ms, 0.6ms)
    ├── [ts-food-service] GET  (7ms ~ 12ms, 4.9ms)
    │   └── [ts-travel-service] GET /api/v1/travelservice/routes/{tripId}  (9ms ~ 13ms, 3.6ms)
    │       ├── [ts-travel-service] TripRepository.findByTripId  (9ms ~ 10ms, 0.6ms)
    │       │   └── [ts-travel-service] find ts.trip  (9ms ~ 9ms, 0.3ms)
    │       └── [ts-travel-service] GET  (10ms ~ 12ms, 1.9ms)
    │           └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (10ms ~ 11ms, 0.7ms)
    │               └── [ts-route-service] RouteRepository.findById  (10ms ~ 10ms, 0.3ms)
    │                   └── [ts-route-service] find ts.routes  (10ms ~ 10ms, 0.2ms)
    ├── [ts-food-service] GET  (12ms ~ 14ms, 1.8ms)
    │   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (13ms ~ 14ms, 1.1ms)
    │       └── [ts-station-service] StationRepository.findByName  (13ms ~ 13ms, 0.5ms)
    │           └── [ts-station-service] find ts.station  (13ms ~ 13ms, 0.4ms)
    ├── [ts-food-service] GET  (14ms ~ 15ms, 1.3ms)
    │   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (15ms ~ 16ms, 1.0ms)
    │       └── [ts-station-service] StationRepository.findByName  (15ms ~ 15ms, 0.5ms)
    │           └── [ts-station-service] find ts.station  (15ms ~ 15ms, 0.4ms)
    └── [ts-food-service] POST  (16ms ~ 21ms, 4.7ms)
        └── [ts-food-map-service] POST /api/v1/foodmapservice/foodstores  (17ms ~ 21ms, 3.8ms)
            └── [ts-food-map-service] FoodStoreRepository.findByStationIdIn  (18ms ~ 19ms, 1.5ms)
                └── [ts-food-map-service] find ts.stores  (19ms ~ 19ms, 0.4ms)
```

**Trace 2**: `555abda1e26cc782e2cd516a6f425577` (总耗时: 25.4ms, span 数: 25)

```
└── [ts-food-service] GET /api/v1/foodservice/foods/{date}/{startStation}/{endStation}/{tripId}  (0ms ~ 25ms, 25.4ms)
    ├── [ts-food-service] GET  (2ms ~ 7ms, 5.4ms)
    │   └── [ts-food-map-service] GET /api/v1/foodmapservice/trainfoods/{tripId}  (4ms ~ 8ms, 4.0ms)
    │       └── [ts-food-map-service] TrainFoodRepository.findByTripId  (5ms ~ 7ms, 1.6ms)
    │           └── [ts-food-map-service] find ts.trainfoods  (6ms ~ 6ms, 0.5ms)
    ├── [ts-food-service] GET  (8ms ~ 14ms, 6.1ms)
    │   └── [ts-travel-service] GET /api/v1/travelservice/routes/{tripId}  (9ms ~ 14ms, 4.6ms)
    │       ├── [ts-travel-service] TripRepository.findByTripId  (9ms ~ 10ms, 0.6ms)
    │       │   └── [ts-travel-service] find ts.trip  (9ms ~ 9ms, 0.3ms)
    │       └── [ts-travel-service] GET  (10ms ~ 13ms, 2.5ms)
    │           └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (11ms ~ 12ms, 1.4ms)
    │               └── [ts-route-service] RouteRepository.findById  (11ms ~ 12ms, 0.5ms)
    │                   └── [ts-route-service] find ts.routes  (11ms ~ 11ms, 0.3ms)
    ├── [ts-food-service] GET  (14ms ~ 16ms, 2.1ms)
    │   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (15ms ~ 16ms, 1.3ms)
    │       └── [ts-station-service] StationRepository.findByName  (15ms ~ 16ms, 0.6ms)
    │           └── [ts-station-service] find ts.station  (15ms ~ 15ms, 0.4ms)
    ├── [ts-food-service] GET  (16ms ~ 18ms, 1.7ms)
    │   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (17ms ~ 18ms, 1.2ms)
    │       └── [ts-station-service] StationRepository.findByName  (17ms ~ 18ms, 0.5ms)
    │           └── [ts-station-service] find ts.station  (17ms ~ 17ms, 0.4ms)
    └── [ts-food-service] POST  (18ms ~ 23ms, 5.1ms)
        └── [ts-food-map-service] POST /api/v1/foodmapservice/foodstores  (20ms ~ 24ms, 4.0ms)
            └── [ts-food-map-service] FoodStoreRepository.findByStationIdIn  (21ms ~ 23ms, 1.5ms)
                └── [ts-food-map-service] find ts.stores  (22ms ~ 22ms, 0.4ms)
```

---

## 接口 5: 获取乘客信息

- **URL**: `http://116.63.51.45:32677/api/v1/contactservice/contacts/account/4d2a46c7-71cb-4cf1-b5bb-b68406d9da6f`
- **Coroot SpanName**: `GET /api/v1/contactservice/contacts/account/{accountId}`
- **总请求数**: 131 (成功 131)
- **时间窗口**: 00:16:15 ~ 00:18:12

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-contacts-service | service | 入口服务 (root) |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "获取乘客信息 (GET /api/v1/contactservice/contacts/account/{accountId})",
  "topology": {
    "nodes": [
      {
        "id": "ts-contacts-service",
        "type": "service",
        "label": "ts-contacts-service",
        "root": true
      }
    ],
    "edges": []
  }
}
```

</details>

### Trace 详情

**Trace 1**: `2cd45afbbadf2dc05eaca5f044b97e56` (总耗时: 0.3ms, span 数: 1)

```
└── [ts-contacts-service] POST  (0ms ~ 0ms, 0.3ms)
```

**Trace 2**: `5d0984409fae062d9ed2d3561ef24685` (总耗时: 0.3ms, span 数: 1)

```
└── [ts-contacts-service] POST  (0ms ~ 0ms, 0.3ms)
```

---

## 接口 6: 订票

- **URL**: `http://116.63.51.45:32677/api/v1/preserveservice/preserve`
- **Coroot SpanName**: `POST /api/v1/preserveservice/preserve`
- **总请求数**: 131 (成功 131)
- **时间窗口**: 00:16:15 ~ 00:18:13

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-preserve-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-basic-service | service | 微服务 |
| ts-config-service | service | 微服务 |
| ts-consign-price-service | service | 微服务 |
| ts-consign-service | service | 微服务 |
| ts-delivery-service | service | 微服务 |
| ts-food-service | service | 微服务 |
| ts-order-other-service | service | 微服务 |
| ts-order-service | service | 微服务 |
| ts-price-service | service | 微服务 |
| ts-route-service | service | 微服务 |
| ts-seat-service | service | 微服务 |
| ts-security-service | service | 微服务 |
| ts-station-service | service | 微服务 |
| ts-ticketinfo-service | service | 微服务 |
| ts-train-service | service | 微服务 |
| ts-travel-service | service | 微服务 |
| ts-user-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-basic-service | ts-price-service | HTTP |
| ts-basic-service | ts-route-service | HTTP |
| ts-basic-service | ts-station-service | HTTP |
| ts-basic-service | ts-train-service | HTTP |
| ts-config-service | MONGODB | MONGODB |
| ts-consign-price-service | MONGODB | MONGODB |
| ts-consign-service | MONGODB | MONGODB |
| ts-consign-service | ts-consign-price-service | HTTP |
| ts-delivery-service | MONGODB | MONGODB |
| ts-food-service | MONGODB | MONGODB |
| ts-food-service | ts-delivery-service | CONSUMER |
| ts-order-other-service | MONGODB | MONGODB |
| ts-order-service | MONGODB | MONGODB |
| ts-preserve-service | ts-consign-service | HTTP |
| ts-preserve-service | ts-food-service | HTTP |
| ts-preserve-service | ts-order-service | HTTP |
| ts-preserve-service | ts-seat-service | HTTP |
| ts-preserve-service | ts-security-service | HTTP |
| ts-preserve-service | ts-station-service | HTTP |
| ts-preserve-service | ts-ticketinfo-service | HTTP |
| ts-preserve-service | ts-travel-service | HTTP |
| ts-preserve-service | ts-user-service | HTTP |
| ts-price-service | MONGODB | MONGODB |
| ts-route-service | MONGODB | MONGODB |
| ts-seat-service | ts-config-service | HTTP |
| ts-seat-service | ts-order-service | HTTP |
| ts-seat-service | ts-travel-service | HTTP |
| ts-security-service | MONGODB | MONGODB |
| ts-security-service | ts-order-other-service | HTTP |
| ts-security-service | ts-order-service | HTTP |
| ts-station-service | MONGODB | MONGODB |
| ts-ticketinfo-service | ts-basic-service | HTTP |
| ts-train-service | MONGODB | MONGODB |
| ts-travel-service | MONGODB | MONGODB |
| ts-travel-service | ts-order-service | HTTP |
| ts-travel-service | ts-route-service | HTTP |
| ts-travel-service | ts-seat-service | HTTP |
| ts-travel-service | ts-ticketinfo-service | HTTP |
| ts-travel-service | ts-train-service | HTTP |
| ts-user-service | MONGODB | MONGODB |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "订票 (POST /api/v1/preserveservice/preserve)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-basic-service",
        "type": "service",
        "label": "ts-basic-service",
        "root": false
      },
      {
        "id": "ts-config-service",
        "type": "service",
        "label": "ts-config-service",
        "root": false
      },
      {
        "id": "ts-consign-price-service",
        "type": "service",
        "label": "ts-consign-price-service",
        "root": false
      },
      {
        "id": "ts-consign-service",
        "type": "service",
        "label": "ts-consign-service",
        "root": false
      },
      {
        "id": "ts-delivery-service",
        "type": "service",
        "label": "ts-delivery-service",
        "root": false
      },
      {
        "id": "ts-food-service",
        "type": "service",
        "label": "ts-food-service",
        "root": false
      },
      {
        "id": "ts-order-other-service",
        "type": "service",
        "label": "ts-order-other-service",
        "root": false
      },
      {
        "id": "ts-order-service",
        "type": "service",
        "label": "ts-order-service",
        "root": false
      },
      {
        "id": "ts-preserve-service",
        "type": "service",
        "label": "ts-preserve-service",
        "root": true
      },
      {
        "id": "ts-price-service",
        "type": "service",
        "label": "ts-price-service",
        "root": false
      },
      {
        "id": "ts-route-service",
        "type": "service",
        "label": "ts-route-service",
        "root": false
      },
      {
        "id": "ts-seat-service",
        "type": "service",
        "label": "ts-seat-service",
        "root": false
      },
      {
        "id": "ts-security-service",
        "type": "service",
        "label": "ts-security-service",
        "root": false
      },
      {
        "id": "ts-station-service",
        "type": "service",
        "label": "ts-station-service",
        "root": false
      },
      {
        "id": "ts-ticketinfo-service",
        "type": "service",
        "label": "ts-ticketinfo-service",
        "root": false
      },
      {
        "id": "ts-train-service",
        "type": "service",
        "label": "ts-train-service",
        "root": false
      },
      {
        "id": "ts-travel-service",
        "type": "service",
        "label": "ts-travel-service",
        "root": false
      },
      {
        "id": "ts-user-service",
        "type": "service",
        "label": "ts-user-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-basic-service",
        "target": "ts-price-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-train-service",
        "label": "HTTP"
      },
      {
        "source": "ts-config-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-consign-price-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-consign-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-consign-service",
        "target": "ts-consign-price-service",
        "label": "HTTP"
      },
      {
        "source": "ts-delivery-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-food-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-food-service",
        "target": "ts-delivery-service",
        "label": "CONSUMER"
      },
      {
        "source": "ts-order-other-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-preserve-service",
        "target": "ts-consign-service",
        "label": "HTTP"
      },
      {
        "source": "ts-preserve-service",
        "target": "ts-food-service",
        "label": "HTTP"
      },
      {
        "source": "ts-preserve-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-preserve-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-preserve-service",
        "target": "ts-security-service",
        "label": "HTTP"
      },
      {
        "source": "ts-preserve-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-preserve-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-preserve-service",
        "target": "ts-travel-service",
        "label": "HTTP"
      },
      {
        "source": "ts-preserve-service",
        "target": "ts-user-service",
        "label": "HTTP"
      },
      {
        "source": "ts-price-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-route-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-config-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-travel-service",
        "label": "HTTP"
      },
      {
        "source": "ts-security-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-security-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-security-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-station-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-ticketinfo-service",
        "target": "ts-basic-service",
        "label": "HTTP"
      },
      {
        "source": "ts-train-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-train-service",
        "label": "HTTP"
      },
      {
        "source": "ts-user-service",
        "target": "MONGODB",
        "label": "MONGODB"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `b9a73f7e5138473e51c200f4db01fc55` (总耗时: 205.3ms, span 数: 274)

```
└── [ts-preserve-service] POST /api/v1/preserveservice/preserve  (0ms ~ 205ms, 205.3ms)
    ├── [ts-preserve-service] GET  (2ms ~ 20ms, 18.2ms)
    │   └── [ts-security-service] GET /api/v1/securityservice/securityConfigs/{accountId}  (3ms ~ 21ms, 18.5ms)
    │       ├── [ts-security-service] GET  (4ms ~ 11ms, 6.7ms)
    │       │   └── [ts-order-service] GET /api/v1/orderservice/order/security/{checkDate}/{accountId}  (6ms ~ 12ms, 5.5ms)
    │       │       └── [ts-order-service] OrderRepository.findByAccountId  (6ms ~ 11ms, 4.7ms)
    │       │           ├── [ts-order-service] find ts.orders  (6ms ~ 8ms, 1.9ms)
    │       │           └── [ts-order-service] getMore ts.orders  (9ms ~ 11ms, 1.9ms)
    │       ├── [ts-security-service] GET  (12ms ~ 16ms, 3.7ms)
    │       │   └── [ts-order-other-service] GET /api/v1/orderOtherService/orderOther/security/{checkDate}/{accountId}  (13ms ~ 16ms, 2.6ms)
    │       │       └── [ts-order-other-service] OrderOtherRepository.findByAccountId  (13ms ~ 15ms, 1.6ms)
    │       │           └── [ts-order-other-service] find ts.orders  (13ms ~ 14ms, 1.2ms)
    │       ├── [ts-security-service] SecurityRepository.findByName  (16ms ~ 18ms, 1.8ms)
    │       │   └── [ts-security-service] find ts.security_config  (17ms ~ 18ms, 0.6ms)
    │       └── [ts-security-service] SecurityRepository.findByName  (18ms ~ 19ms, 1.3ms)
    │           └── [ts-security-service] find ts.security_config  (18ms ~ 19ms, 0.5ms)
    ├── [ts-preserve-service] GET  (21ms ~ 25ms, 4.4ms)
    ├── [ts-preserve-service] POST  (26ms ~ 124ms, 97.6ms)
    │   └── [ts-travel-service] POST /api/v1/travelservice/trip_detail  (27ms ~ 124ms, 96.5ms)
    │       ├── [ts-travel-service] GET  (27ms ~ 31ms, 4.3ms)
    │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (29ms ~ 32ms, 3.2ms)
    │       │       └── [ts-ticketinfo-service] GET  (29ms ~ 31ms, 2.5ms)
    │       │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (29ms ~ 31ms, 2.0ms)
    │       │               └── [ts-basic-service] GET  (29ms ~ 30ms, 1.4ms)
    │       │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (30ms ~ 31ms, 1.1ms)
    │       │                       └── [ts-station-service] StationRepository.findByName  (30ms ~ 31ms, 0.6ms)
    │       │                           └── [ts-station-service] find ts.station  (30ms ~ 30ms, 0.4ms)
    │       ├── [ts-travel-service] TripRepository.findByTripId  (27ms ~ 27ms, 0.3ms)
    │       │   └── [ts-travel-service] find ts.trip  (27ms ~ 27ms, 0.2ms)
    │       ├── [ts-travel-service] GET  (32ms ~ 36ms, 4.2ms)
... (244 more spans)
```

**Trace 2**: `d5ebecf4f554efd296c624f281d06314` (总耗时: 207.8ms, span 数: 269)

```
└── [ts-preserve-service] POST /api/v1/preserveservice/preserve  (0ms ~ 208ms, 207.8ms)
    ├── [ts-preserve-service] GET  (2ms ~ 16ms, 14.4ms)
    │   └── [ts-security-service] GET /api/v1/securityservice/securityConfigs/{accountId}  (3ms ~ 17ms, 13.8ms)
    │       ├── [ts-security-service] GET  (4ms ~ 8ms, 4.3ms)
    │       │   └── [ts-order-service] GET /api/v1/orderservice/order/security/{checkDate}/{accountId}  (6ms ~ 9ms, 3.2ms)
    │       │       └── [ts-order-service] OrderRepository.findByAccountId  (6ms ~ 9ms, 2.5ms)
    │       │           └── [ts-order-service] find ts.orders  (6ms ~ 8ms, 1.9ms)
    │       ├── [ts-security-service] GET  (9ms ~ 12ms, 3.0ms)
    │       │   └── [ts-order-other-service] GET /api/v1/orderOtherService/orderOther/security/{checkDate}/{accountId}  (10ms ~ 13ms, 2.6ms)
    │       │       └── [ts-order-other-service] OrderOtherRepository.findByAccountId  (10ms ~ 12ms, 1.6ms)
    │       │           └── [ts-order-other-service] find ts.orders  (10ms ~ 11ms, 1.2ms)
    │       ├── [ts-security-service] SecurityRepository.findByName  (13ms ~ 14ms, 1.2ms)
    │       │   └── [ts-security-service] find ts.security_config  (13ms ~ 13ms, 0.4ms)
    │       └── [ts-security-service] SecurityRepository.findByName  (14ms ~ 15ms, 1.1ms)
    │           └── [ts-security-service] find ts.security_config  (14ms ~ 14ms, 0.4ms)
    ├── [ts-preserve-service] GET  (17ms ~ 21ms, 4.2ms)
    ├── [ts-preserve-service] POST  (22ms ~ 109ms, 87.1ms)
    │   └── [ts-travel-service] POST /api/v1/travelservice/trip_detail  (24ms ~ 109ms, 84.7ms)
    │       ├── [ts-travel-service] GET  (24ms ~ 28ms, 4.3ms)
    │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (25ms ~ 28ms, 3.3ms)
    │       │       └── [ts-ticketinfo-service] GET  (25ms ~ 27ms, 2.5ms)
    │       │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (26ms ~ 28ms, 2.0ms)
    │       │               └── [ts-basic-service] GET  (26ms ~ 27ms, 1.4ms)
    │       │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (27ms ~ 28ms, 1.2ms)
    │       │                       └── [ts-station-service] StationRepository.findByName  (27ms ~ 27ms, 0.4ms)
    │       │                           └── [ts-station-service] find ts.station  (27ms ~ 27ms, 0.3ms)
    │       ├── [ts-travel-service] TripRepository.findByTripId  (24ms ~ 24ms, 0.3ms)
    │       │   └── [ts-travel-service] find ts.trip  (24ms ~ 24ms, 0.2ms)
    │       ├── [ts-travel-service] GET  (29ms ~ 33ms, 3.9ms)
    │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (30ms ~ 33ms, 2.9ms)
... (239 more spans)
```

---

## 接口 7: 查看所有订单

- **URL**: `http://116.63.51.45:32677/api/v1/orderOtherService/orderOther/refresh`
- **Coroot SpanName**: `POST /api/v1/orderOtherService/orderOther/refresh`
- **总请求数**: 130 (成功 130)
- **时间窗口**: 00:16:16 ~ 00:18:10

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-order-other-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-station-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-order-other-service | MONGODB | MONGODB |
| ts-order-other-service | ts-station-service | HTTP |
| ts-station-service | MONGODB | MONGODB |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "查看所有订单 (POST /api/v1/orderOtherService/orderOther/refresh)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-order-other-service",
        "type": "service",
        "label": "ts-order-other-service",
        "root": true
      },
      {
        "id": "ts-station-service",
        "type": "service",
        "label": "ts-station-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-order-other-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-other-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-station-service",
        "target": "MONGODB",
        "label": "MONGODB"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `f834c7f3e82366c329903f9f1f582d39` (总耗时: 7.4ms, span 数: 9)

```
└── [ts-order-other-service] POST /api/v1/orderOtherService/orderOther/refresh  (0ms ~ 7ms, 7.4ms)
    ├── [ts-order-other-service] OrderOtherRepository.findByAccountId  (1ms ~ 3ms, 1.7ms)
    │   └── [ts-order-other-service] find ts.orders  (1ms ~ 2ms, 1.3ms)
    └── [ts-order-other-service] POST  (3ms ~ 6ms, 3.0ms)
        └── [ts-station-service] POST /api/v1/stationservice/stations/namelist  (5ms ~ 6ms, 1.4ms)
            ├── [ts-station-service] StationRepository.findById  (5ms ~ 5ms, 0.4ms)
            │   └── [ts-station-service] find ts.station  (5ms ~ 5ms, 0.3ms)
            └── [ts-station-service] StationRepository.findById  (5ms ~ 5ms, 0.4ms)
                └── [ts-station-service] find ts.station  (5ms ~ 5ms, 0.3ms)
```

**Trace 2**: `b4fa70c9662d2b0fb4a6a340bb209a73` (总耗时: 7.4ms, span 数: 9)

```
└── [ts-order-other-service] POST /api/v1/orderOtherService/orderOther/refresh  (0ms ~ 7ms, 7.4ms)
    ├── [ts-order-other-service] OrderOtherRepository.findByAccountId  (1ms ~ 3ms, 1.7ms)
    │   └── [ts-order-other-service] find ts.orders  (1ms ~ 2ms, 1.2ms)
    └── [ts-order-other-service] POST  (3ms ~ 6ms, 3.3ms)
        └── [ts-station-service] POST /api/v1/stationservice/stations/namelist  (5ms ~ 6ms, 1.4ms)
            ├── [ts-station-service] StationRepository.findById  (5ms ~ 5ms, 0.5ms)
            │   └── [ts-station-service] find ts.station  (5ms ~ 5ms, 0.3ms)
            └── [ts-station-service] StationRepository.findById  (5ms ~ 5ms, 0.4ms)
                └── [ts-station-service] find ts.station  (5ms ~ 5ms, 0.3ms)
```

---

## 接口 8: 托运

- **URL**: `http://116.63.51.45:32677/api/v1/consignservice/consigns`
- **Coroot SpanName**: `POST /api/v1/consignservice/consigns`
- **总请求数**: 130 (成功 130)
- **时间窗口**: 00:16:16 ~ 00:18:11

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-consign-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-consign-price-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-consign-price-service | MONGODB | MONGODB |
| ts-consign-service | MONGODB | MONGODB |
| ts-consign-service | ts-consign-price-service | HTTP |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "托运 (POST /api/v1/consignservice/consigns)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-consign-price-service",
        "type": "service",
        "label": "ts-consign-price-service",
        "root": false
      },
      {
        "id": "ts-consign-service",
        "type": "service",
        "label": "ts-consign-service",
        "root": true
      }
    ],
    "edges": [
      {
        "source": "ts-consign-price-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-consign-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-consign-service",
        "target": "ts-consign-price-service",
        "label": "HTTP"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `d6b0c5381552191df002dd0c27204b51` (总耗时: 12.2ms, span 数: 7)

```
└── [ts-consign-service] POST /api/v1/consignservice/consigns  (0ms ~ 12ms, 12.2ms)
    ├── [ts-consign-service] GET  (1ms ~ 9ms, 7.7ms)
    │   └── [ts-consign-price-service] GET /api/v1/consignpriceservice/consignprice/{weight}/{isWithinRegion}  (4ms ~ 9ms, 5.4ms)
    │       └── [ts-consign-price-service] ConsignPriceConfigRepository.findByIndex  (5ms ~ 7ms, 2.4ms)
    │           └── [ts-consign-price-service] find ts.consign_price  (6ms ~ 7ms, 1.4ms)
    └── [ts-consign-service] ConsignRepository.save  (9ms ~ 10ms, 1.3ms)
        └── [ts-consign-service] update ts.consign_record  (10ms ~ 10ms, 0.4ms)
```

**Trace 2**: `d218c3d592339a45fec0ba784138e351` (总耗时: 18.5ms, span 数: 7)

```
└── [ts-consign-service] POST /api/v1/consignservice/consigns  (0ms ~ 18ms, 18.5ms)
    ├── [ts-consign-service] GET  (2ms ~ 14ms, 11.6ms)
    │   └── [ts-consign-price-service] GET /api/v1/consignpriceservice/consignprice/{weight}/{isWithinRegion}  (6ms ~ 14ms, 8.0ms)
    │       └── [ts-consign-price-service] ConsignPriceConfigRepository.findByIndex  (9ms ~ 13ms, 3.5ms)
    │           └── [ts-consign-price-service] find ts.consign_price  (10ms ~ 12ms, 2.2ms)
    └── [ts-consign-service] ConsignRepository.save  (15ms ~ 16ms, 1.5ms)
        └── [ts-consign-service] update ts.consign_record  (15ms ~ 16ms, 0.6ms)
```

---

## 接口 9: 取票

- **URL**: `http://116.63.51.45:32677/api/v1/executeservice/execute/collected/23305f6a-636e-49e4-bb29-07771a10a1f4`
- **Coroot SpanName**: `GET /api/v1/executeservice/execute/collected/{orderId}`
- **总请求数**: 130 (成功 130)
- **时间窗口**: 00:16:17 ~ 00:18:11

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-execute-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-order-other-service | service | 微服务 |
| ts-order-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-execute-service | ts-order-other-service | HTTP |
| ts-execute-service | ts-order-service | HTTP |
| ts-order-other-service | MONGODB | MONGODB |
| ts-order-service | MONGODB | MONGODB |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "取票 (GET /api/v1/executeservice/execute/collected/{orderId})",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-execute-service",
        "type": "service",
        "label": "ts-execute-service",
        "root": true
      },
      {
        "id": "ts-order-other-service",
        "type": "service",
        "label": "ts-order-other-service",
        "root": false
      },
      {
        "id": "ts-order-service",
        "type": "service",
        "label": "ts-order-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-execute-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-execute-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-order-other-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-service",
        "target": "MONGODB",
        "label": "MONGODB"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `4635e2bee731f9de693d26abd8b015f7` (总耗时: 10.9ms, span 数: 9)

```
└── [ts-execute-service] GET /api/v1/executeservice/execute/collected/{orderId}  (0ms ~ 11ms, 10.9ms)
    ├── [ts-execute-service] GET  (2ms ~ 5ms, 3.5ms)
    │   └── [ts-order-service] GET /api/v1/orderservice/order/{orderId}  (3ms ~ 5ms, 2.4ms)
    │       └── [ts-order-service] OrderRepository.findById  (3ms ~ 4ms, 1.4ms)
    │           └── [ts-order-service] find ts.orders  (3ms ~ 4ms, 1.1ms)
    └── [ts-execute-service] GET  (6ms ~ 9ms, 3.0ms)
        └── [ts-order-other-service] GET /api/v1/orderOtherService/orderOther/{orderId}  (6ms ~ 9ms, 2.6ms)
            └── [ts-order-other-service] OrderOtherRepository.findById  (6ms ~ 8ms, 1.7ms)
                └── [ts-order-other-service] find ts.orders  (6ms ~ 7ms, 1.3ms)
```

**Trace 2**: `a8e47ef434ad4ed4baceec522eca3611` (总耗时: 11.7ms, span 数: 9)

```
└── [ts-execute-service] GET /api/v1/executeservice/execute/collected/{orderId}  (0ms ~ 12ms, 11.7ms)
    ├── [ts-execute-service] GET  (1ms ~ 5ms, 3.8ms)
    │   └── [ts-order-service] GET /api/v1/orderservice/order/{orderId}  (3ms ~ 6ms, 2.6ms)
    │       └── [ts-order-service] OrderRepository.findById  (3ms ~ 5ms, 1.7ms)
    │           └── [ts-order-service] find ts.orders  (3ms ~ 4ms, 1.3ms)
    └── [ts-execute-service] GET  (6ms ~ 10ms, 3.8ms)
        └── [ts-order-other-service] GET /api/v1/orderOtherService/orderOther/{orderId}  (7ms ~ 10ms, 3.4ms)
            └── [ts-order-other-service] OrderOtherRepository.findById  (7ms ~ 9ms, 2.0ms)
                └── [ts-order-other-service] find ts.orders  (8ms ~ 9ms, 1.4ms)
```

---

## 接口 10: 进站

- **URL**: `http://116.63.51.45:32677/api/v1/executeservice/execute/execute/23305f6a-636e-49e4-bb29-07771a10a1f4`
- **Coroot SpanName**: `GET /api/v1/executeservice/execute/execute/{orderId}`
- **总请求数**: 130 (成功 130)
- **时间窗口**: 00:16:17 ~ 00:18:12

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-execute-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-order-other-service | service | 微服务 |
| ts-order-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-execute-service | ts-order-other-service | HTTP |
| ts-execute-service | ts-order-service | HTTP |
| ts-order-other-service | MONGODB | MONGODB |
| ts-order-service | MONGODB | MONGODB |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "进站 (GET /api/v1/executeservice/execute/execute/{orderId})",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-execute-service",
        "type": "service",
        "label": "ts-execute-service",
        "root": true
      },
      {
        "id": "ts-order-other-service",
        "type": "service",
        "label": "ts-order-other-service",
        "root": false
      },
      {
        "id": "ts-order-service",
        "type": "service",
        "label": "ts-order-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-execute-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-execute-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-order-other-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-service",
        "target": "MONGODB",
        "label": "MONGODB"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `5a1359d7c4191b2fa1e287f8f2c59e05` (总耗时: 9.4ms, span 数: 9)

```
└── [ts-execute-service] GET /api/v1/executeservice/execute/execute/{orderId}  (0ms ~ 9ms, 9.4ms)
    ├── [ts-execute-service] GET  (1ms ~ 4ms, 3.1ms)
    │   └── [ts-order-service] GET /api/v1/orderservice/order/{orderId}  (2ms ~ 4ms, 1.9ms)
    │       └── [ts-order-service] OrderRepository.findById  (2ms ~ 3ms, 1.2ms)
    │           └── [ts-order-service] find ts.orders  (2ms ~ 3ms, 1.1ms)
    └── [ts-execute-service] GET  (4ms ~ 7ms, 3.4ms)
        └── [ts-order-other-service] GET /api/v1/orderOtherService/orderOther/{orderId}  (5ms ~ 8ms, 3.2ms)
            └── [ts-order-other-service] OrderOtherRepository.findById  (6ms ~ 8ms, 1.6ms)
                └── [ts-order-other-service] find ts.orders  (6ms ~ 7ms, 1.2ms)
```

**Trace 2**: `70414b0c54c6cd5503fb82d862d31181` (总耗时: 18.0ms, span 数: 9)

```
└── [ts-execute-service] GET /api/v1/executeservice/execute/execute/{orderId}  (0ms ~ 18ms, 18.0ms)
    ├── [ts-execute-service] GET  (1ms ~ 12ms, 11.5ms)
    │   └── [ts-order-service] GET /api/v1/orderservice/order/{orderId}  (3ms ~ 13ms, 10.3ms)
    │       └── [ts-order-service] OrderRepository.findById  (3ms ~ 13ms, 9.6ms)
    │           └── [ts-order-service] find ts.orders  (3ms ~ 12ms, 9.4ms)
    └── [ts-execute-service] GET  (13ms ~ 16ms, 3.0ms)
        └── [ts-order-other-service] GET /api/v1/orderOtherService/orderOther/{orderId}  (14ms ~ 16ms, 2.3ms)
            └── [ts-order-other-service] OrderOtherRepository.findById  (14ms ~ 15ms, 1.4ms)
                └── [ts-order-other-service] find ts.orders  (14ms ~ 15ms, 1.1ms)
```

---

## 接口 11: 支付

- **URL**: `http://116.63.51.45:32677/api/v1/inside_pay_service/inside_payment`
- **Coroot SpanName**: `POST /api/v1/inside_pay_service/inside_payment`
- **总请求数**: 130 (成功 130)
- **时间窗口**: 00:16:18 ~ 00:18:12

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-inside-payment-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-order-other-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-inside-payment-service | ts-order-other-service | HTTP |
| ts-order-other-service | MONGODB | MONGODB |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "支付 (POST /api/v1/inside_pay_service/inside_payment)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-inside-payment-service",
        "type": "service",
        "label": "ts-inside-payment-service",
        "root": true
      },
      {
        "id": "ts-order-other-service",
        "type": "service",
        "label": "ts-order-other-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-inside-payment-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-order-other-service",
        "target": "MONGODB",
        "label": "MONGODB"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `018ffb8497ff614905bf21addf35b64a` (总耗时: 9.6ms, span 数: 5)

```
└── [ts-inside-payment-service] POST /api/v1/inside_pay_service/inside_payment  (0ms ~ 10ms, 9.6ms)
    └── [ts-inside-payment-service] GET  (3ms ~ 7ms, 4.3ms)
        └── [ts-order-other-service] GET /api/v1/orderOtherService/orderOther/{orderId}  (3ms ~ 7ms, 4.2ms)
            └── [ts-order-other-service] OrderOtherRepository.findById  (4ms ~ 6ms, 1.9ms)
                └── [ts-order-other-service] find ts.orders  (4ms ~ 5ms, 1.3ms)
```

**Trace 2**: `9b5409f2e0c5ad792b7609033a20e8a0` (总耗时: 8.3ms, span 数: 5)

```
└── [ts-inside-payment-service] POST /api/v1/inside_pay_service/inside_payment  (0ms ~ 8ms, 8.3ms)
    └── [ts-inside-payment-service] GET  (2ms ~ 6ms, 4.3ms)
        └── [ts-order-other-service] GET /api/v1/orderOtherService/orderOther/{orderId}  (3ms ~ 7ms, 4.2ms)
            └── [ts-order-other-service] OrderOtherRepository.findById  (4ms ~ 6ms, 1.7ms)
                └── [ts-order-other-service] find ts.orders  (5ms ~ 6ms, 1.3ms)
```

---

## 接口 12: 查便宜票

- **URL**: `http://116.63.51.45:32677/api/v1/travelplanservice/travelPlan/cheapest`
- **Coroot SpanName**: `POST /api/v1/travelplanservice/travelPlan/cheapest`
- **总请求数**: 130 (成功 130)
- **时间窗口**: 00:16:19 ~ 00:18:13

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-travel-plan-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-basic-service | service | 微服务 |
| ts-config-service | service | 微服务 |
| ts-order-other-service | service | 微服务 |
| ts-order-service | service | 微服务 |
| ts-price-service | service | 微服务 |
| ts-route-plan-service | service | 微服务 |
| ts-route-service | service | 微服务 |
| ts-seat-service | service | 微服务 |
| ts-station-service | service | 微服务 |
| ts-ticketinfo-service | service | 微服务 |
| ts-train-service | service | 微服务 |
| ts-travel-service | service | 微服务 |
| ts-travel2-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-basic-service | ts-price-service | HTTP |
| ts-basic-service | ts-route-service | HTTP |
| ts-basic-service | ts-station-service | HTTP |
| ts-basic-service | ts-train-service | HTTP |
| ts-config-service | MONGODB | MONGODB |
| ts-order-other-service | MONGODB | MONGODB |
| ts-order-service | MONGODB | MONGODB |
| ts-price-service | MONGODB | MONGODB |
| ts-route-plan-service | ts-travel-service | HTTP |
| ts-route-plan-service | ts-travel2-service | HTTP |
| ts-route-service | MONGODB | MONGODB |
| ts-seat-service | ts-config-service | HTTP |
| ts-seat-service | ts-order-other-service | HTTP |
| ts-seat-service | ts-order-service | HTTP |
| ts-seat-service | ts-travel-service | HTTP |
| ts-seat-service | ts-travel2-service | HTTP |
| ts-station-service | MONGODB | MONGODB |
| ts-ticketinfo-service | ts-basic-service | HTTP |
| ts-train-service | MONGODB | MONGODB |
| ts-travel-plan-service | ts-route-plan-service | HTTP |
| ts-travel-plan-service | ts-seat-service | HTTP |
| ts-travel-plan-service | ts-station-service | HTTP |
| ts-travel-plan-service | ts-ticketinfo-service | HTTP |
| ts-travel-service | MONGODB | MONGODB |
| ts-travel-service | ts-order-service | HTTP |
| ts-travel-service | ts-route-service | HTTP |
| ts-travel-service | ts-seat-service | HTTP |
| ts-travel-service | ts-ticketinfo-service | HTTP |
| ts-travel-service | ts-train-service | HTTP |
| ts-travel2-service | MONGODB | MONGODB |
| ts-travel2-service | ts-order-other-service | HTTP |
| ts-travel2-service | ts-route-service | HTTP |
| ts-travel2-service | ts-seat-service | HTTP |
| ts-travel2-service | ts-ticketinfo-service | HTTP |
| ts-travel2-service | ts-train-service | HTTP |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "查便宜票 (POST /api/v1/travelplanservice/travelPlan/cheapest)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-basic-service",
        "type": "service",
        "label": "ts-basic-service",
        "root": false
      },
      {
        "id": "ts-config-service",
        "type": "service",
        "label": "ts-config-service",
        "root": false
      },
      {
        "id": "ts-order-other-service",
        "type": "service",
        "label": "ts-order-other-service",
        "root": false
      },
      {
        "id": "ts-order-service",
        "type": "service",
        "label": "ts-order-service",
        "root": false
      },
      {
        "id": "ts-price-service",
        "type": "service",
        "label": "ts-price-service",
        "root": false
      },
      {
        "id": "ts-route-plan-service",
        "type": "service",
        "label": "ts-route-plan-service",
        "root": false
      },
      {
        "id": "ts-route-service",
        "type": "service",
        "label": "ts-route-service",
        "root": false
      },
      {
        "id": "ts-seat-service",
        "type": "service",
        "label": "ts-seat-service",
        "root": false
      },
      {
        "id": "ts-station-service",
        "type": "service",
        "label": "ts-station-service",
        "root": false
      },
      {
        "id": "ts-ticketinfo-service",
        "type": "service",
        "label": "ts-ticketinfo-service",
        "root": false
      },
      {
        "id": "ts-train-service",
        "type": "service",
        "label": "ts-train-service",
        "root": false
      },
      {
        "id": "ts-travel-plan-service",
        "type": "service",
        "label": "ts-travel-plan-service",
        "root": true
      },
      {
        "id": "ts-travel-service",
        "type": "service",
        "label": "ts-travel-service",
        "root": false
      },
      {
        "id": "ts-travel2-service",
        "type": "service",
        "label": "ts-travel2-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-basic-service",
        "target": "ts-price-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-train-service",
        "label": "HTTP"
      },
      {
        "source": "ts-config-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-other-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-price-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-route-plan-service",
        "target": "ts-travel-service",
        "label": "HTTP"
      },
      {
        "source": "ts-route-plan-service",
        "target": "ts-travel2-service",
        "label": "HTTP"
      },
      {
        "source": "ts-route-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-config-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-travel-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-travel2-service",
        "label": "HTTP"
      },
      {
        "source": "ts-station-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-ticketinfo-service",
        "target": "ts-basic-service",
        "label": "HTTP"
      },
      {
        "source": "ts-train-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-route-plan-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-train-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-train-service",
        "label": "HTTP"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `f105471808edc6d641b50caf48002683` (总耗时: 666.5ms, span 数: 1039)

```
└── [ts-travel-plan-service] POST /api/v1/travelplanservice/travelPlan/cheapest  (0ms ~ 667ms, 666.5ms)
    ├── [ts-travel-plan-service] POST  (1ms ~ 433ms, 431.9ms)
    │   └── [ts-route-plan-service] POST /api/v1/routeplanservice/routePlan/cheapestRoute  (4ms ~ 434ms, 429.6ms)
    │       ├── [ts-route-plan-service] POST  (5ms ~ 305ms, 300.0ms)
    │       │   └── [ts-travel-service] POST /api/v1/travelservice/trips/left  (7ms ~ 306ms, 298.6ms)
    │       │       ├── [ts-travel-service] GET  (7ms ~ 15ms, 7.9ms)
    │       │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (9ms ~ 15ms, 6.0ms)
    │       │       │       └── [ts-ticketinfo-service] GET  (9ms ~ 14ms, 4.8ms)
    │       │       │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (9ms ~ 14ms, 4.5ms)
    │       │       │               └── [ts-basic-service] GET  (9ms ~ 13ms, 3.9ms)
    │       │       │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (12ms ~ 13ms, 1.4ms)
    │       │       │                       └── [ts-station-service] StationRepository.findByName  (12ms ~ 12ms, 0.5ms)
    │       │       │                           └── [ts-station-service] find ts.station  (12ms ~ 12ms, 0.3ms)
    │       │       ├── [ts-travel-service] GET  (15ms ~ 20ms, 5.0ms)
    │       │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (16ms ~ 19ms, 3.3ms)
    │       │       │       └── [ts-ticketinfo-service] GET  (16ms ~ 18ms, 2.3ms)
    │       │       │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (17ms ~ 19ms, 2.1ms)
    │       │       │               └── [ts-basic-service] GET  (17ms ~ 18ms, 1.5ms)
    │       │       │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (18ms ~ 19ms, 1.2ms)
    │       │       │                       └── [ts-station-service] StationRepository.findByName  (18ms ~ 19ms, 0.6ms)
    │       │       │                           └── [ts-station-service] find ts.station  (18ms ~ 18ms, 0.4ms)
    │       │       ├── [ts-travel-service] TripRepository.findAll  (20ms ~ 20ms, 0.4ms)
    │       │       │   └── [ts-travel-service] find ts.trip  (20ms ~ 20ms, 0.2ms)
    │       │       ├── [ts-travel-service] GET  (21ms ~ 23ms, 1.8ms)
    │       │       │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (21ms ~ 22ms, 0.8ms)
    │       │       │       └── [ts-route-service] RouteRepository.findById  (21ms ~ 21ms, 0.3ms)
    │       │       │           └── [ts-route-service] find ts.routes  (21ms ~ 21ms, 0.2ms)
    │       │       ├── [ts-travel-service] POST  (23ms ~ 47ms, 23.9ms)
    │       │       │   └── [ts-ticketinfo-service] POST /api/v1/ticketinfoservice/ticketinfo  (25ms ~ 47ms, 21.6ms)
    │       │       │       └── [ts-ticketinfo-service] POST  (25ms ~ 46ms, 20.8ms)
... (1009 more spans)
```

**Trace 2**: `9c228044e03bbedac8730eaf6e17b882` (总耗时: 662.0ms, span 数: 1039)

```
└── [ts-travel-plan-service] POST /api/v1/travelplanservice/travelPlan/cheapest  (0ms ~ 662ms, 662.0ms)
    ├── [ts-travel-plan-service] POST  (1ms ~ 430ms, 429.1ms)
    │   └── [ts-route-plan-service] POST /api/v1/routeplanservice/routePlan/cheapestRoute  (4ms ~ 431ms, 426.5ms)
    │       ├── [ts-route-plan-service] POST  (5ms ~ 283ms, 278.2ms)
    │       │   └── [ts-travel-service] POST /api/v1/travelservice/trips/left  (7ms ~ 284ms, 276.8ms)
    │       │       ├── [ts-travel-service] GET  (7ms ~ 15ms, 7.6ms)
    │       │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (9ms ~ 15ms, 6.5ms)
    │       │       │       └── [ts-ticketinfo-service] GET  (9ms ~ 14ms, 5.5ms)
    │       │       │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (12ms ~ 15ms, 3.0ms)
    │       │       │               └── [ts-basic-service] GET  (12ms ~ 14ms, 1.7ms)
    │       │       │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (13ms ~ 14ms, 1.1ms)
    │       │       │                       └── [ts-station-service] StationRepository.findByName  (13ms ~ 13ms, 0.5ms)
    │       │       │                           └── [ts-station-service] find ts.station  (13ms ~ 13ms, 0.4ms)
    │       │       ├── [ts-travel-service] GET  (15ms ~ 20ms, 4.6ms)
    │       │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (16ms ~ 19ms, 3.4ms)
    │       │       │       └── [ts-ticketinfo-service] GET  (16ms ~ 19ms, 2.7ms)
    │       │       │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (17ms ~ 19ms, 2.5ms)
    │       │       │               └── [ts-basic-service] GET  (17ms ~ 19ms, 1.7ms)
    │       │       │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (18ms ~ 19ms, 1.4ms)
    │       │       │                       └── [ts-station-service] StationRepository.findByName  (18ms ~ 19ms, 0.8ms)
    │       │       │                           └── [ts-station-service] find ts.station  (18ms ~ 19ms, 0.7ms)
    │       │       ├── [ts-travel-service] GET  (20ms ~ 22ms, 2.0ms)
    │       │       │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (22ms ~ 23ms, 1.0ms)
    │       │       │       └── [ts-route-service] RouteRepository.findById  (22ms ~ 22ms, 0.4ms)
    │       │       │           └── [ts-route-service] find ts.routes  (22ms ~ 22ms, 0.2ms)
    │       │       ├── [ts-travel-service] TripRepository.findAll  (20ms ~ 20ms, 0.4ms)
    │       │       │   └── [ts-travel-service] find ts.trip  (20ms ~ 20ms, 0.3ms)
    │       │       ├── [ts-travel-service] POST  (23ms ~ 41ms, 17.9ms)
    │       │       │   └── [ts-ticketinfo-service] POST /api/v1/ticketinfoservice/ticketinfo  (25ms ~ 41ms, 15.6ms)
    │       │       │       └── [ts-ticketinfo-service] POST  (25ms ~ 40ms, 14.8ms)
... (1009 more spans)
```

---

## 接口 13: preseveother

- **URL**: `http://116.63.51.45:32677/api/v1/preserveotherservice/preserveOther`
- **Coroot SpanName**: `POST /api/v1/preserveotherservice/preserveOther`
- **总请求数**: 127 (成功 127)
- **时间窗口**: 00:16:20 ~ 00:18:12

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-preserve-other-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-order-other-service | service | 微服务 |
| ts-order-service | service | 微服务 |
| ts-security-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-order-other-service | MONGODB | MONGODB |
| ts-order-service | MONGODB | MONGODB |
| ts-preserve-other-service | ts-security-service | HTTP |
| ts-security-service | MONGODB | MONGODB |
| ts-security-service | ts-order-other-service | HTTP |
| ts-security-service | ts-order-service | HTTP |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "preseveother (POST /api/v1/preserveotherservice/preserveOther)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-order-other-service",
        "type": "service",
        "label": "ts-order-other-service",
        "root": false
      },
      {
        "id": "ts-order-service",
        "type": "service",
        "label": "ts-order-service",
        "root": false
      },
      {
        "id": "ts-preserve-other-service",
        "type": "service",
        "label": "ts-preserve-other-service",
        "root": true
      },
      {
        "id": "ts-security-service",
        "type": "service",
        "label": "ts-security-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-order-other-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-preserve-other-service",
        "target": "ts-security-service",
        "label": "HTTP"
      },
      {
        "source": "ts-security-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-security-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-security-service",
        "target": "ts-order-service",
        "label": "HTTP"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `f2af7664ade73ce1941d79b86c0f84f6` (总耗时: 25.4ms, span 数: 17)

```
└── [ts-preserve-other-service] POST /api/v1/preserveotherservice/preserveOther  (0ms ~ 25ms, 25.4ms)
    ├── [ts-preserve-other-service] GET  (3ms ~ 18ms, 15.0ms)
    │   └── [ts-security-service] GET /api/v1/securityservice/securityConfigs/{accountId}  (4ms ~ 19ms, 14.6ms)
    │       ├── [ts-security-service] GET  (5ms ~ 11ms, 5.9ms)
    │       │   └── [ts-order-service] GET /api/v1/orderservice/order/security/{checkDate}/{accountId}  (7ms ~ 12ms, 4.8ms)
    │       │       └── [ts-order-service] OrderRepository.findByAccountId  (7ms ~ 11ms, 3.9ms)
    │       │           ├── [ts-order-service] find ts.orders  (7ms ~ 9ms, 1.9ms)
    │       │           └── [ts-order-service] getMore ts.orders  (10ms ~ 11ms, 1.2ms)
    │       ├── [ts-security-service] GET  (12ms ~ 15ms, 2.8ms)
    │       │   └── [ts-order-other-service] GET /api/v1/orderOtherService/orderOther/security/{checkDate}/{accountId}  (13ms ~ 15ms, 2.5ms)
    │       │       └── [ts-order-other-service] OrderOtherRepository.findByAccountId  (13ms ~ 14ms, 1.5ms)
    │       │           └── [ts-order-other-service] find ts.orders  (13ms ~ 14ms, 1.2ms)
    │       ├── [ts-security-service] SecurityRepository.findByName  (15ms ~ 16ms, 1.2ms)
    │       │   └── [ts-security-service] find ts.security_config  (15ms ~ 15ms, 0.4ms)
    │       └── [ts-security-service] SecurityRepository.findByName  (16ms ~ 17ms, 0.9ms)
    │           └── [ts-security-service] find ts.security_config  (17ms ~ 17ms, 0.3ms)
    └── [ts-preserve-other-service] GET  (19ms ~ 23ms, 4.2ms)
```

**Trace 2**: `6546898d15fc07fed31683cca97a8f22` (总耗时: 34.2ms, span 数: 17)

```
└── [ts-preserve-other-service] POST /api/v1/preserveotherservice/preserveOther  (0ms ~ 34ms, 34.2ms)
    ├── [ts-preserve-other-service] GET  (2ms ~ 24ms, 22.2ms)
    │   └── [ts-security-service] GET /api/v1/securityservice/securityConfigs/{accountId}  (4ms ~ 25ms, 21.2ms)
    │       ├── [ts-security-service] GET  (8ms ~ 18ms, 9.8ms)
    │       │   └── [ts-order-service] GET /api/v1/orderservice/order/security/{checkDate}/{accountId}  (10ms ~ 17ms, 7.5ms)
    │       │       └── [ts-order-service] OrderRepository.findByAccountId  (10ms ~ 17ms, 6.6ms)
    │       │           ├── [ts-order-service] find ts.orders  (10ms ~ 13ms, 3.1ms)
    │       │           └── [ts-order-service] getMore ts.orders  (14ms ~ 16ms, 2.0ms)
    │       ├── [ts-security-service] GET  (18ms ~ 21ms, 3.0ms)
    │       │   └── [ts-order-other-service] GET /api/v1/orderOtherService/orderOther/security/{checkDate}/{accountId}  (18ms ~ 21ms, 2.7ms)
    │       │       └── [ts-order-other-service] OrderOtherRepository.findByAccountId  (18ms ~ 20ms, 1.6ms)
    │       │           └── [ts-order-other-service] find ts.orders  (18ms ~ 19ms, 1.3ms)
    │       ├── [ts-security-service] SecurityRepository.findByName  (21ms ~ 22ms, 1.4ms)
    │       │   └── [ts-security-service] find ts.security_config  (22ms ~ 23ms, 0.6ms)
    │       └── [ts-security-service] SecurityRepository.findByName  (23ms ~ 24ms, 0.8ms)
    │           └── [ts-security-service] find ts.security_config  (23ms ~ 23ms, 0.4ms)
    └── [ts-preserve-other-service] GET  (25ms ~ 31ms, 6.0ms)
```

---

## 接口 14: 查换乘票

- **URL**: `http://116.63.51.45:32677/api/v1/travelplanservice/travelPlan/minStation`
- **Coroot SpanName**: `POST /api/v1/travelplanservice/travelPlan/minStation`
- **总请求数**: 127 (成功 127)
- **时间窗口**: 00:16:20 ~ 00:18:13

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-travel-plan-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-basic-service | service | 微服务 |
| ts-config-service | service | 微服务 |
| ts-order-other-service | service | 微服务 |
| ts-order-service | service | 微服务 |
| ts-price-service | service | 微服务 |
| ts-route-plan-service | service | 微服务 |
| ts-route-service | service | 微服务 |
| ts-seat-service | service | 微服务 |
| ts-station-service | service | 微服务 |
| ts-ticketinfo-service | service | 微服务 |
| ts-train-service | service | 微服务 |
| ts-travel-service | service | 微服务 |
| ts-travel2-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-basic-service | ts-price-service | HTTP |
| ts-basic-service | ts-route-service | HTTP |
| ts-basic-service | ts-station-service | HTTP |
| ts-basic-service | ts-train-service | HTTP |
| ts-config-service | MONGODB | MONGODB |
| ts-order-other-service | MONGODB | MONGODB |
| ts-order-service | MONGODB | MONGODB |
| ts-price-service | MONGODB | MONGODB |
| ts-route-plan-service | ts-route-service | HTTP |
| ts-route-plan-service | ts-station-service | HTTP |
| ts-route-plan-service | ts-travel-service | HTTP |
| ts-route-plan-service | ts-travel2-service | HTTP |
| ts-route-service | MONGODB | MONGODB |
| ts-seat-service | ts-config-service | HTTP |
| ts-seat-service | ts-order-other-service | HTTP |
| ts-seat-service | ts-order-service | HTTP |
| ts-seat-service | ts-travel-service | HTTP |
| ts-seat-service | ts-travel2-service | HTTP |
| ts-station-service | MONGODB | MONGODB |
| ts-ticketinfo-service | ts-basic-service | HTTP |
| ts-train-service | MONGODB | MONGODB |
| ts-travel-plan-service | ts-route-plan-service | HTTP |
| ts-travel-plan-service | ts-seat-service | HTTP |
| ts-travel-plan-service | ts-station-service | HTTP |
| ts-travel-plan-service | ts-ticketinfo-service | HTTP |
| ts-travel-service | MONGODB | MONGODB |
| ts-travel-service | ts-order-service | HTTP |
| ts-travel-service | ts-route-service | HTTP |
| ts-travel-service | ts-seat-service | HTTP |
| ts-travel-service | ts-ticketinfo-service | HTTP |
| ts-travel-service | ts-train-service | HTTP |
| ts-travel2-service | MONGODB | MONGODB |
| ts-travel2-service | ts-order-other-service | HTTP |
| ts-travel2-service | ts-route-service | HTTP |
| ts-travel2-service | ts-seat-service | HTTP |
| ts-travel2-service | ts-ticketinfo-service | HTTP |
| ts-travel2-service | ts-train-service | HTTP |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "查换乘票 (POST /api/v1/travelplanservice/travelPlan/minStation)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-basic-service",
        "type": "service",
        "label": "ts-basic-service",
        "root": false
      },
      {
        "id": "ts-config-service",
        "type": "service",
        "label": "ts-config-service",
        "root": false
      },
      {
        "id": "ts-order-other-service",
        "type": "service",
        "label": "ts-order-other-service",
        "root": false
      },
      {
        "id": "ts-order-service",
        "type": "service",
        "label": "ts-order-service",
        "root": false
      },
      {
        "id": "ts-price-service",
        "type": "service",
        "label": "ts-price-service",
        "root": false
      },
      {
        "id": "ts-route-plan-service",
        "type": "service",
        "label": "ts-route-plan-service",
        "root": false
      },
      {
        "id": "ts-route-service",
        "type": "service",
        "label": "ts-route-service",
        "root": false
      },
      {
        "id": "ts-seat-service",
        "type": "service",
        "label": "ts-seat-service",
        "root": false
      },
      {
        "id": "ts-station-service",
        "type": "service",
        "label": "ts-station-service",
        "root": false
      },
      {
        "id": "ts-ticketinfo-service",
        "type": "service",
        "label": "ts-ticketinfo-service",
        "root": false
      },
      {
        "id": "ts-train-service",
        "type": "service",
        "label": "ts-train-service",
        "root": false
      },
      {
        "id": "ts-travel-plan-service",
        "type": "service",
        "label": "ts-travel-plan-service",
        "root": true
      },
      {
        "id": "ts-travel-service",
        "type": "service",
        "label": "ts-travel-service",
        "root": false
      },
      {
        "id": "ts-travel2-service",
        "type": "service",
        "label": "ts-travel2-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-basic-service",
        "target": "ts-price-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-train-service",
        "label": "HTTP"
      },
      {
        "source": "ts-config-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-other-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-price-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-route-plan-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-route-plan-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-route-plan-service",
        "target": "ts-travel-service",
        "label": "HTTP"
      },
      {
        "source": "ts-route-plan-service",
        "target": "ts-travel2-service",
        "label": "HTTP"
      },
      {
        "source": "ts-route-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-config-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-travel-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-travel2-service",
        "label": "HTTP"
      },
      {
        "source": "ts-station-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-ticketinfo-service",
        "target": "ts-basic-service",
        "label": "HTTP"
      },
      {
        "source": "ts-train-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-route-plan-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-train-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-train-service",
        "label": "HTTP"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `8ffee56fb935465db8cdfc195aa0f4f1` (总耗时: 670.4ms, span 数: 1079)

```
└── [ts-travel-plan-service] POST /api/v1/travelplanservice/travelPlan/minStation  (0ms ~ 670ms, 670.4ms)
    ├── [ts-travel-plan-service] POST  (2ms ~ 429ms, 426.9ms)
    │   └── [ts-route-plan-service] POST /api/v1/routeplanservice/routePlan/minStopStations  (4ms ~ 429ms, 424.6ms)
    │       ├── [ts-route-plan-service] GET  (5ms ~ 8ms, 3.0ms)
    │       │   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (6ms ~ 8ms, 1.8ms)
    │       │       └── [ts-station-service] StationRepository.findByName  (6ms ~ 7ms, 0.8ms)
    │       │           └── [ts-station-service] find ts.station  (6ms ~ 7ms, 0.6ms)
    │       ├── [ts-route-plan-service] GET  (8ms ~ 11ms, 2.5ms)
    │       │   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (9ms ~ 11ms, 1.6ms)
    │       │       └── [ts-station-service] StationRepository.findByName  (9ms ~ 10ms, 0.6ms)
    │       │           └── [ts-station-service] find ts.station  (9ms ~ 9ms, 0.4ms)
    │       ├── [ts-route-plan-service] GET  (11ms ~ 14ms, 2.7ms)
    │       │   └── [ts-route-service] GET /api/v1/routeservice/routes/{startId}/{terminalId}  (12ms ~ 14ms, 1.7ms)
    │       │       └── [ts-route-service] RouteRepository.findAll  (12ms ~ 13ms, 0.6ms)
    │       │           └── [ts-route-service] find ts.routes  (12ms ~ 12ms, 0.4ms)
    │       ├── [ts-route-plan-service] POST  (14ms ~ 17ms, 2.8ms)
    │       │   └── [ts-travel-service] POST /api/v1/travelservice/trips/routes  (16ms ~ 18ms, 1.6ms)
    │       │       ├── [ts-travel-service] TripRepository.findByRouteId  (16ms ~ 16ms, 0.5ms)
    │       │       │   └── [ts-travel-service] find ts.trip  (16ms ~ 16ms, 0.3ms)
    │       │       ├── [ts-travel-service] TripRepository.findByRouteId  (16ms ~ 16ms, 0.2ms)
    │       │       │   └── [ts-travel-service] find ts.trip  (16ms ~ 16ms, 0.1ms)
    │       │       ├── [ts-travel-service] TripRepository.findByRouteId  (16ms ~ 16ms, 0.2ms)
    │       │       │   └── [ts-travel-service] find ts.trip  (17ms ~ 17ms, 0.1ms)
    │       │       └── [ts-travel-service] TripRepository.findByRouteId  (17ms ~ 17ms, 0.2ms)
    │       │           └── [ts-travel-service] find ts.trip  (17ms ~ 17ms, 0.1ms)
    │       ├── [ts-route-plan-service] POST  (17ms ~ 27ms, 10.2ms)
    │       │   └── [ts-travel2-service] POST /api/v1/travel2service/trips/routes  (19ms ~ 27ms, 8.0ms)
    │       │       ├── [ts-travel2-service] TripRepository.findByRouteId  (19ms ~ 21ms, 1.7ms)
    │       │       │   └── [ts-travel2-service] find ts.trip  (20ms ~ 21ms, 1.3ms)
    │       │       ├── [ts-travel2-service] TripRepository.findByRouteId  (21ms ~ 23ms, 1.8ms)
... (1049 more spans)
```

**Trace 2**: `41a57de3163342c944f28aefa50a60ba` (总耗时: 722.9ms, span 数: 1079)

```
└── [ts-travel-plan-service] POST /api/v1/travelplanservice/travelPlan/minStation  (0ms ~ 723ms, 722.9ms)
    ├── [ts-travel-plan-service] POST  (2ms ~ 431ms, 429.2ms)
    │   └── [ts-route-plan-service] POST /api/v1/routeplanservice/routePlan/minStopStations  (5ms ~ 431ms, 426.0ms)
    │       ├── [ts-route-plan-service] GET  (6ms ~ 9ms, 3.4ms)
    │       │   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (8ms ~ 10ms, 1.6ms)
    │       │       └── [ts-station-service] StationRepository.findByName  (8ms ~ 9ms, 0.8ms)
    │       │           └── [ts-station-service] find ts.station  (8ms ~ 9ms, 0.5ms)
    │       ├── [ts-route-plan-service] GET  (10ms ~ 12ms, 2.3ms)
    │       │   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (11ms ~ 12ms, 1.2ms)
    │       │       └── [ts-station-service] StationRepository.findByName  (11ms ~ 11ms, 0.5ms)
    │       │           └── [ts-station-service] find ts.station  (11ms ~ 11ms, 0.3ms)
    │       ├── [ts-route-plan-service] GET  (13ms ~ 16ms, 2.5ms)
    │       │   └── [ts-route-service] GET /api/v1/routeservice/routes/{startId}/{terminalId}  (14ms ~ 15ms, 1.4ms)
    │       │       └── [ts-route-service] RouteRepository.findAll  (14ms ~ 15ms, 0.5ms)
    │       │           └── [ts-route-service] find ts.routes  (14ms ~ 14ms, 0.3ms)
    │       ├── [ts-route-plan-service] POST  (15ms ~ 18ms, 3.3ms)
    │       │   └── [ts-travel-service] POST /api/v1/travelservice/trips/routes  (17ms ~ 19ms, 2.0ms)
    │       │       ├── [ts-travel-service] TripRepository.findByRouteId  (17ms ~ 17ms, 0.5ms)
    │       │       │   └── [ts-travel-service] find ts.trip  (17ms ~ 17ms, 0.3ms)
    │       │       ├── [ts-travel-service] TripRepository.findByRouteId  (18ms ~ 18ms, 0.3ms)
    │       │       │   └── [ts-travel-service] find ts.trip  (18ms ~ 18ms, 0.2ms)
    │       │       ├── [ts-travel-service] TripRepository.findByRouteId  (18ms ~ 18ms, 0.2ms)
    │       │       │   └── [ts-travel-service] find ts.trip  (18ms ~ 18ms, 0.2ms)
    │       │       └── [ts-travel-service] TripRepository.findByRouteId  (18ms ~ 18ms, 0.2ms)
    │       │           └── [ts-travel-service] find ts.trip  (18ms ~ 18ms, 0.1ms)
    │       ├── [ts-route-plan-service] POST  (19ms ~ 28ms, 9.0ms)
    │       │   └── [ts-travel2-service] POST /api/v1/travel2service/trips/routes  (21ms ~ 28ms, 6.7ms)
    │       │       ├── [ts-travel2-service] TripRepository.findByRouteId  (21ms ~ 23ms, 1.6ms)
    │       │       │   └── [ts-travel2-service] find ts.trip  (21ms ~ 22ms, 1.3ms)
    │       │       ├── [ts-travel2-service] TripRepository.findByRouteId  (23ms ~ 24ms, 1.4ms)
... (1049 more spans)
```

---

## 接口 15: 查快速票

- **URL**: `http://116.63.51.45:32677/api/v1/travelplanservice/travelPlan/quickest`
- **Coroot SpanName**: `POST /api/v1/travelplanservice/travelPlan/quickest`
- **总请求数**: 126 (成功 126)
- **时间窗口**: 00:16:21 ~ 00:18:13

### 链路拓扑

**节点列表:**

| ID | 类型 | 说明 |
|---|---|---|
| ts-travel-plan-service | service | 入口服务 (root) |
| MONGODB | db | 数据库 |
| ts-basic-service | service | 微服务 |
| ts-config-service | service | 微服务 |
| ts-order-other-service | service | 微服务 |
| ts-order-service | service | 微服务 |
| ts-price-service | service | 微服务 |
| ts-route-plan-service | service | 微服务 |
| ts-route-service | service | 微服务 |
| ts-seat-service | service | 微服务 |
| ts-station-service | service | 微服务 |
| ts-ticketinfo-service | service | 微服务 |
| ts-train-service | service | 微服务 |
| ts-travel-service | service | 微服务 |
| ts-travel2-service | service | 微服务 |

**边列表:**

| 调用方 | 被调方 | 协议 |
|---|---|---|
| ts-basic-service | ts-price-service | HTTP |
| ts-basic-service | ts-route-service | HTTP |
| ts-basic-service | ts-station-service | HTTP |
| ts-basic-service | ts-train-service | HTTP |
| ts-config-service | MONGODB | MONGODB |
| ts-order-other-service | MONGODB | MONGODB |
| ts-order-service | MONGODB | MONGODB |
| ts-price-service | MONGODB | MONGODB |
| ts-route-plan-service | ts-travel-service | HTTP |
| ts-route-plan-service | ts-travel2-service | HTTP |
| ts-route-service | MONGODB | MONGODB |
| ts-seat-service | ts-config-service | HTTP |
| ts-seat-service | ts-order-other-service | HTTP |
| ts-seat-service | ts-order-service | HTTP |
| ts-seat-service | ts-travel-service | HTTP |
| ts-seat-service | ts-travel2-service | HTTP |
| ts-station-service | MONGODB | MONGODB |
| ts-ticketinfo-service | ts-basic-service | HTTP |
| ts-train-service | MONGODB | MONGODB |
| ts-travel-plan-service | ts-route-plan-service | HTTP |
| ts-travel-plan-service | ts-seat-service | HTTP |
| ts-travel-plan-service | ts-station-service | HTTP |
| ts-travel-plan-service | ts-ticketinfo-service | HTTP |
| ts-travel-service | MONGODB | MONGODB |
| ts-travel-service | ts-order-service | HTTP |
| ts-travel-service | ts-route-service | HTTP |
| ts-travel-service | ts-seat-service | HTTP |
| ts-travel-service | ts-ticketinfo-service | HTTP |
| ts-travel-service | ts-train-service | HTTP |
| ts-travel2-service | MONGODB | MONGODB |
| ts-travel2-service | ts-order-other-service | HTTP |
| ts-travel2-service | ts-route-service | HTTP |
| ts-travel2-service | ts-seat-service | HTTP |
| ts-travel2-service | ts-ticketinfo-service | HTTP |
| ts-travel2-service | ts-train-service | HTTP |

<details>
<summary>拓扑数据 (JSON)</summary>

```json
{
  "interface": "查快速票 (POST /api/v1/travelplanservice/travelPlan/quickest)",
  "topology": {
    "nodes": [
      {
        "id": "MONGODB",
        "type": "db",
        "label": "MONGODB",
        "root": false
      },
      {
        "id": "ts-basic-service",
        "type": "service",
        "label": "ts-basic-service",
        "root": false
      },
      {
        "id": "ts-config-service",
        "type": "service",
        "label": "ts-config-service",
        "root": false
      },
      {
        "id": "ts-order-other-service",
        "type": "service",
        "label": "ts-order-other-service",
        "root": false
      },
      {
        "id": "ts-order-service",
        "type": "service",
        "label": "ts-order-service",
        "root": false
      },
      {
        "id": "ts-price-service",
        "type": "service",
        "label": "ts-price-service",
        "root": false
      },
      {
        "id": "ts-route-plan-service",
        "type": "service",
        "label": "ts-route-plan-service",
        "root": false
      },
      {
        "id": "ts-route-service",
        "type": "service",
        "label": "ts-route-service",
        "root": false
      },
      {
        "id": "ts-seat-service",
        "type": "service",
        "label": "ts-seat-service",
        "root": false
      },
      {
        "id": "ts-station-service",
        "type": "service",
        "label": "ts-station-service",
        "root": false
      },
      {
        "id": "ts-ticketinfo-service",
        "type": "service",
        "label": "ts-ticketinfo-service",
        "root": false
      },
      {
        "id": "ts-train-service",
        "type": "service",
        "label": "ts-train-service",
        "root": false
      },
      {
        "id": "ts-travel-plan-service",
        "type": "service",
        "label": "ts-travel-plan-service",
        "root": true
      },
      {
        "id": "ts-travel-service",
        "type": "service",
        "label": "ts-travel-service",
        "root": false
      },
      {
        "id": "ts-travel2-service",
        "type": "service",
        "label": "ts-travel2-service",
        "root": false
      }
    ],
    "edges": [
      {
        "source": "ts-basic-service",
        "target": "ts-price-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-basic-service",
        "target": "ts-train-service",
        "label": "HTTP"
      },
      {
        "source": "ts-config-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-other-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-order-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-price-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-route-plan-service",
        "target": "ts-travel-service",
        "label": "HTTP"
      },
      {
        "source": "ts-route-plan-service",
        "target": "ts-travel2-service",
        "label": "HTTP"
      },
      {
        "source": "ts-route-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-config-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-travel-service",
        "label": "HTTP"
      },
      {
        "source": "ts-seat-service",
        "target": "ts-travel2-service",
        "label": "HTTP"
      },
      {
        "source": "ts-station-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-ticketinfo-service",
        "target": "ts-basic-service",
        "label": "HTTP"
      },
      {
        "source": "ts-train-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-route-plan-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-station-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-plan-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-order-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel-service",
        "target": "ts-train-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "MONGODB",
        "label": "MONGODB"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-order-other-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-route-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-seat-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-ticketinfo-service",
        "label": "HTTP"
      },
      {
        "source": "ts-travel2-service",
        "target": "ts-train-service",
        "label": "HTTP"
      }
    ]
  }
}
```

</details>

### Trace 详情

**Trace 1**: `cef6575bff7fdc448016eb5b49bfbd76` (总耗时: 1317.3ms, span 数: 1039)

```
└── [ts-travel-plan-service] POST /api/v1/travelplanservice/travelPlan/quickest  (0ms ~ 1317ms, 1317.3ms)
    ├── [ts-travel-plan-service] POST  (1ms ~ 769ms, 768.1ms)
    │   └── [ts-route-plan-service] POST /api/v1/routeplanservice/routePlan/quickestRoute  (4ms ~ 770ms, 765.8ms)
    │       ├── [ts-route-plan-service] POST  (5ms ~ 565ms, 560.3ms)
    │       │   └── [ts-travel-service] POST /api/v1/travelservice/trips/left  (7ms ~ 566ms, 559.0ms)
    │       │       ├── [ts-travel-service] GET  (7ms ~ 12ms, 4.7ms)
    │       │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (9ms ~ 12ms, 3.0ms)
    │       │       │       └── [ts-ticketinfo-service] GET  (9ms ~ 11ms, 1.9ms)
    │       │       │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (9ms ~ 11ms, 1.7ms)
    │       │       │               └── [ts-basic-service] GET  (9ms ~ 10ms, 1.2ms)
    │       │       │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (10ms ~ 11ms, 0.9ms)
    │       │       │                       └── [ts-station-service] StationRepository.findByName  (10ms ~ 10ms, 0.4ms)
    │       │       │                           └── [ts-station-service] find ts.station  (10ms ~ 10ms, 0.3ms)
    │       │       ├── [ts-travel-service] GET  (12ms ~ 16ms, 3.6ms)
    │       │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (13ms ~ 16ms, 2.7ms)
    │       │       │       └── [ts-ticketinfo-service] GET  (13ms ~ 15ms, 2.0ms)
    │       │       │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (13ms ~ 15ms, 1.7ms)
    │       │       │               └── [ts-basic-service] GET  (13ms ~ 14ms, 1.1ms)
    │       │       │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (14ms ~ 15ms, 0.9ms)
    │       │       │                       └── [ts-station-service] StationRepository.findByName  (14ms ~ 14ms, 0.4ms)
    │       │       │                           └── [ts-station-service] find ts.station  (14ms ~ 14ms, 0.3ms)
    │       │       ├── [ts-travel-service] TripRepository.findAll  (15ms ~ 15ms, 0.4ms)
    │       │       │   └── [ts-travel-service] find ts.trip  (15ms ~ 15ms, 0.2ms)
    │       │       ├── [ts-travel-service] GET  (16ms ~ 18ms, 2.0ms)
    │       │       │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (17ms ~ 18ms, 0.8ms)
    │       │       │       └── [ts-route-service] RouteRepository.findById  (17ms ~ 17ms, 0.3ms)
    │       │       │           └── [ts-route-service] find ts.routes  (17ms ~ 17ms, 0.2ms)
    │       │       ├── [ts-travel-service] POST  (18ms ~ 46ms, 28.4ms)
    │       │       │   └── [ts-ticketinfo-service] POST /api/v1/ticketinfoservice/ticketinfo  (21ms ~ 47ms, 26.2ms)
    │       │       │       └── [ts-ticketinfo-service] POST  (21ms ~ 46ms, 25.4ms)
... (1009 more spans)
```

**Trace 2**: `6f0dd7353dee54f3afa608492a6ae99a` (总耗时: 677.7ms, span 数: 1039)

```
└── [ts-travel-plan-service] POST /api/v1/travelplanservice/travelPlan/quickest  (0ms ~ 678ms, 677.7ms)
    ├── [ts-travel-plan-service] POST  (1ms ~ 408ms, 407.2ms)
    │   └── [ts-route-plan-service] POST /api/v1/routeplanservice/routePlan/quickestRoute  (4ms ~ 409ms, 404.7ms)
    │       ├── [ts-route-plan-service] POST  (5ms ~ 280ms, 275.0ms)
    │       │   └── [ts-travel-service] POST /api/v1/travelservice/trips/left  (7ms ~ 280ms, 273.4ms)
    │       │       ├── [ts-travel-service] GET  (7ms ~ 11ms, 4.1ms)
    │       │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (8ms ~ 11ms, 3.0ms)
    │       │       │       └── [ts-ticketinfo-service] GET  (8ms ~ 10ms, 2.2ms)
    │       │       │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (8ms ~ 10ms, 1.8ms)
    │       │       │               └── [ts-basic-service] GET  (8ms ~ 9ms, 1.3ms)
    │       │       │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (9ms ~ 10ms, 1.0ms)
    │       │       │                       └── [ts-station-service] StationRepository.findByName  (9ms ~ 9ms, 0.5ms)
    │       │       │                           └── [ts-station-service] find ts.station  (9ms ~ 9ms, 0.3ms)
    │       │       ├── [ts-travel-service] GET  (11ms ~ 18ms, 7.2ms)
    │       │       │   └── [ts-ticketinfo-service] GET /api/v1/ticketinfoservice/ticketinfo/{name}  (12ms ~ 18ms, 6.2ms)
    │       │       │       └── [ts-ticketinfo-service] GET  (12ms ~ 17ms, 5.2ms)
    │       │       │           └── [ts-basic-service] GET /api/v1/basicservice/basic/{stationName}  (13ms ~ 18ms, 4.9ms)
    │       │       │               └── [ts-basic-service] GET  (13ms ~ 17ms, 4.3ms)
    │       │       │                   └── [ts-station-service] GET /api/v1/stationservice/stations/id/{stationNameForId}  (16ms ~ 17ms, 1.2ms)
    │       │       │                       └── [ts-station-service] StationRepository.findByName  (16ms ~ 17ms, 0.5ms)
    │       │       │                           └── [ts-station-service] find ts.station  (16ms ~ 16ms, 0.4ms)
    │       │       ├── [ts-travel-service] TripRepository.findAll  (18ms ~ 18ms, 0.4ms)
    │       │       │   └── [ts-travel-service] find ts.trip  (19ms ~ 19ms, 0.2ms)
    │       │       ├── [ts-travel-service] GET  (19ms ~ 21ms, 1.8ms)
    │       │       │   └── [ts-route-service] GET /api/v1/routeservice/routes/{routeId}  (20ms ~ 21ms, 0.7ms)
    │       │       │       └── [ts-route-service] RouteRepository.findById  (20ms ~ 20ms, 0.3ms)
    │       │       │           └── [ts-route-service] find ts.routes  (20ms ~ 20ms, 0.2ms)
    │       │       ├── [ts-travel-service] POST  (21ms ~ 45ms, 24.3ms)
    │       │       │   └── [ts-ticketinfo-service] POST /api/v1/ticketinfoservice/ticketinfo  (23ms ~ 45ms, 22.1ms)
    │       │       │       └── [ts-ticketinfo-service] POST  (23ms ~ 44ms, 21.1ms)
... (1009 more spans)
```

---
