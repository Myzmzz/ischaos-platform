/**
 * TopologyRenderer — AntV X6 v2 + Dagre TB 分层拓扑渲染器 (ES Module)。
 *
 * 微型卡片风格节点:
 *   - service-node   220×64  白底轻阴影 + 蓝色渐变图标区 + hexagon 图标
 *   - root-node      220×64  蓝色边框 + 深蓝渐变图标区(白色图标) + 渐变白底
 *   - db-node        160×52  虚线边框 + 灰色渐变图标区 + database 图标
 *   - fault 状态     红色边框 + 红色渐变图标区 + 脉冲动画
 *
 * 连线:
 *   - HTTP:    1.5px #94a3b8 实线, 实心箭头, manhattan 路由 + rounded(8)
 *   - MONGODB: 1px #cbd5e1 虚线(6 4), 空心箭头, manhattan + rounded(6)
 *   - 标签:   白底圆角药丸背景
 *
 * 交互:
 *   - hover 节点 → 高亮上下游路径(连线变蓝+流动动画), 其余 30% 透明
 *   - 点击 service/root 节点 → 触发 onNodeClick 回调
 *   - 画布拖拽 + 滚轮缩放
 */
import { Graph, Shape } from 'https://esm.sh/@antv/x6@2'
import dagre from 'https://esm.sh/dagre@0.8.5'

/* ═══════════════════════════════════════════
 *  1. 常量 & SVG 图标
 * ═══════════════════════════════════════════ */

const SERVICE_W = 220, SERVICE_H = 64;
const DB_W = 160, DB_H = 52;

/** Hexagon 图标 (用于 service 节点) */
const HEXAGON_ICON_BLUE = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
</svg>`;

const HEXAGON_ICON_WHITE = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
</svg>`;

const HEXAGON_ICON_RED = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
</svg>`;

const DB_ICON_GRAY = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
</svg>`;

const DB_ICON_RED = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
  <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
</svg>`;

/* ═══════════════════════════════════════════
 *  2. 注入全局动画样式（一次性）
 * ═══════════════════════════════════════════ */

if (!document.getElementById('topo-anim-styles')) {
    const styleEl = document.createElement('style');
    styleEl.id = 'topo-anim-styles';
    styleEl.textContent = `
        @keyframes topo-fault-pulse {
            0%   { box-shadow: 0 0 0 0 rgba(239,68,68,0.5); }
            70%  { box-shadow: 0 0 0 6px rgba(239,68,68,0); }
            100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
        }
        .topo-node-card {
            transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
        }
        .topo-node-card:hover {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.08), 0 4px 12px rgba(0,0,0,0.06) !important;
            transform: translateY(-1px);
        }
        .topo-fault-dot {
            position: absolute; top: 8px; right: 8px;
            width: 8px; height: 8px; border-radius: 50%;
            background: #ef4444;
            animation: topo-fault-pulse 1.5s infinite;
        }
        .topo-status-dot {
            position: absolute; top: 8px; right: 8px;
            width: 8px; height: 8px; border-radius: 50%;
            background: #22c55e;
        }
        /* 流动虚线动画（高亮时用） */
        @keyframes topo-flow-dash {
            from { stroke-dashoffset: 12; }
            to   { stroke-dashoffset: 0; }
        }
    `;
    document.head.appendChild(styleEl);
}

/* ═══════════════════════════════════════════
 *  3. 注册自定义 HTML 节点
 * ═══════════════════════════════════════════ */

/** 通用 Service 节点 — 微型卡片风格 */
Shape.HTML.register({
    shape: 'service-node',
    width: SERVICE_W,
    height: SERVICE_H,
    effect: ['data'],
    html(cell) {
        const { label, fault, faultLabel } = cell.getData() || {};
        const isFault = !!fault;

        const iconBg = isFault
            ? 'linear-gradient(135deg, #fef2f2, #fecaca)'
            : 'linear-gradient(135deg, #eff6ff, #dbeafe)';
        const icon = isFault ? HEXAGON_ICON_RED : HEXAGON_ICON_BLUE;
        const subText = isFault
            ? `<span style="color:#ef4444;">● ${faultLabel || '故障注入中'}</span>`
            : '<span>0 active faults</span>';

        const div = document.createElement('div');
        div.className = 'topo-node-card';
        div.style.cssText = `
            width:${SERVICE_W}px; height:${SERVICE_H}px; box-sizing:border-box;
            background:#ffffff;
            border:1px solid ${isFault ? '#ef4444' : '#e2e8f0'};
            ${isFault ? 'border-width:1.5px;' : ''}
            border-radius:12px;
            box-shadow:0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
            display:flex; align-items:center; gap:10px;
            padding:12px 14px; position:relative;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC',sans-serif;
            cursor:pointer;
        `;
        if (isFault) {
            div.style.background = 'linear-gradient(to bottom, #ffffff, #fef7f7)';
        }
        div.innerHTML = `
            <div style="width:36px;height:36px;border-radius:10px;
                 background:${iconBg};
                 display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                ${icon}
            </div>
            <div style="flex:1;min-width:0;">
                <div style="font-size:13px;color:#1e293b;font-weight:600;line-height:1.3;
                     overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                     title="${label}">${label}</div>
                <div style="font-size:11px;color:#94a3b8;line-height:1.3;margin-top:2px;">
                    ${subText}
                </div>
            </div>
            <div class="${isFault ? 'topo-fault-dot' : 'topo-status-dot'}"></div>
        `;
        return div;
    },
});

/** ROOT 入口节点 */
Shape.HTML.register({
    shape: 'root-node',
    width: SERVICE_W,
    height: SERVICE_H,
    effect: ['data'],
    html(cell) {
        const { label, fault, faultLabel } = cell.getData() || {};
        const isFault = !!fault;

        const iconBg = isFault
            ? 'linear-gradient(135deg, #fef2f2, #fecaca)'
            : 'linear-gradient(135deg, #3b82f6, #2563eb)';
        const icon = isFault ? HEXAGON_ICON_RED : HEXAGON_ICON_WHITE;
        const subText = isFault
            ? `<span style="color:#ef4444;">● ${faultLabel || '故障注入中'}</span>`
            : '<span style="color:#3b82f6;font-weight:500;">◆ 入口服务</span>';

        const div = document.createElement('div');
        div.className = 'topo-node-card';
        div.style.cssText = `
            width:${SERVICE_W}px; height:${SERVICE_H}px; box-sizing:border-box;
            background:${isFault ? 'linear-gradient(to bottom, #ffffff, #fef7f7)' : 'linear-gradient(to bottom, #ffffff, #f8faff)'};
            border:1.5px solid ${isFault ? '#ef4444' : '#3b82f6'};
            border-radius:12px;
            box-shadow:0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02);
            display:flex; align-items:center; gap:10px;
            padding:12px 14px; position:relative;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC',sans-serif;
            cursor:pointer;
        `;
        div.innerHTML = `
            <div style="width:36px;height:36px;border-radius:10px;
                 background:${iconBg};
                 display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                ${icon}
            </div>
            <div style="flex:1;min-width:0;">
                <div style="font-size:13px;color:#1e293b;font-weight:600;line-height:1.3;
                     overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                     title="${label}">${label}</div>
                <div style="font-size:11px;color:#94a3b8;line-height:1.3;margin-top:2px;">
                    ${subText}
                </div>
            </div>
            <div class="${isFault ? 'topo-fault-dot' : 'topo-status-dot'}"></div>
        `;
        return div;
    },
});

/** DB 节点 */
Shape.HTML.register({
    shape: 'db-node',
    width: DB_W,
    height: DB_H,
    effect: ['data'],
    html(cell) {
        const { label, fault } = cell.getData() || {};
        const isFault = !!fault;

        const iconBg = isFault
            ? 'linear-gradient(135deg, #fef2f2, #fecaca)'
            : 'linear-gradient(135deg, #f1f5f9, #e2e8f0)';
        const icon = isFault ? DB_ICON_RED : DB_ICON_GRAY;

        const div = document.createElement('div');
        div.className = 'topo-node-card';
        div.style.cssText = `
            width:${DB_W}px; height:${DB_H}px; box-sizing:border-box;
            background:${isFault ? 'linear-gradient(to bottom, #ffffff, #fef7f7)' : '#f8fafc'};
            border:1px dashed ${isFault ? '#ef4444' : '#cbd5e1'};
            ${isFault ? 'border-width:1.5px;' : ''}
            border-radius:10px;
            display:flex; align-items:center; gap:8px;
            padding:8px 12px; position:relative;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC',sans-serif;
            cursor:default;
        `;
        div.innerHTML = `
            <div style="width:32px;height:32px;border-radius:8px;
                 background:${iconBg};
                 display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                ${icon}
            </div>
            <div style="font-size:12px;color:#475569;font-weight:600;line-height:1.2;
                 overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1;min-width:0;"
                 title="${label}">${label}</div>
            ${isFault ? '<div class="topo-fault-dot"></div>' : ''}
        `;
        return div;
    },
});

/* ═══════════════════════════════════════════
 *  4. Dagre 布局计算
 * ═══════════════════════════════════════════ */

function computeLayout(nodes, edges) {
    const g = new dagre.graphlib.Graph();
    g.setGraph({ rankdir: 'TB', nodesep: 100, ranksep: 70, align: 'UL', marginx: 40, marginy: 40 });
    g.setDefaultEdgeLabel(() => ({}));

    for (const n of nodes) {
        const w = (n.type === 'db') ? DB_W : SERVICE_W;
        const h = (n.type === 'db') ? DB_H : SERVICE_H;
        g.setNode(n.id, { width: w, height: h });
    }
    for (const e of edges) {
        g.setEdge(e.source, e.target);
    }

    dagre.layout(g);

    const positions = new Map();
    for (const id of g.nodes()) {
        const pos = g.node(id);
        positions.set(id, {
            x: pos.x - pos.width / 2,
            y: pos.y - pos.height / 2,
            width: pos.width,
            height: pos.height,
        });
    }
    return positions;
}

/* ═══════════════════════════════════════════
 *  5. 数据预处理 — 合并同 id 节点 + 去重边
 * ═══════════════════════════════════════════ */

function dedup(topology) {
    const nodeMap = new Map();
    for (const n of topology.nodes) {
        if (!nodeMap.has(n.id)) {
            nodeMap.set(n.id, { ...n });
        }
    }
    const edgeSet = new Set();
    const edges = [];
    for (const e of topology.edges) {
        const key = `${e.source}→${e.target}`;
        if (!edgeSet.has(key)) {
            edgeSet.add(key);
            edges.push({ ...e });
        }
    }
    return { nodes: Array.from(nodeMap.values()), edges };
}

/* ═══════════════════════════════════════════
 *  6. 邻接表（hover 高亮用）
 * ═══════════════════════════════════════════ */

function buildAdjacency(edges) {
    const nodeEdges = new Map();
    const upstream = new Map();
    const downstream = new Map();
    const edgeMeta = new Map();

    const ensure = (map, key) => { if (!map.has(key)) map.set(key, new Set()); };

    for (const e of edges) {
        ensure(nodeEdges, e.source);
        ensure(nodeEdges, e.target);
        ensure(downstream, e.source);
        ensure(upstream, e.target);

        nodeEdges.get(e.source).add(e.id);
        nodeEdges.get(e.target).add(e.id);
        downstream.get(e.source).add(e.target);
        upstream.get(e.target).add(e.source);
        edgeMeta.set(e.id, { source: e.source, target: e.target });
    }

    return { nodeEdges, upstream, downstream, edgeMeta };
}

/** BFS 收集上下游节点 + 边 */
function collectConnected(nodeId, adj) {
    const visitedNodes = new Set([nodeId]);
    const visitedEdges = new Set();

    // BFS downstream
    const qDown = [nodeId];
    while (qDown.length) {
        const cur = qDown.shift();
        for (const next of (adj.downstream.get(cur) || [])) {
            if (!visitedNodes.has(next)) { visitedNodes.add(next); qDown.push(next); }
        }
    }
    // BFS upstream
    const qUp = [nodeId];
    while (qUp.length) {
        const cur = qUp.shift();
        for (const prev of (adj.upstream.get(cur) || [])) {
            if (!visitedNodes.has(prev)) { visitedNodes.add(prev); qUp.push(prev); }
        }
    }
    // 收集相关边
    for (const [eid, meta] of adj.edgeMeta) {
        if (visitedNodes.has(meta.source) && visitedNodes.has(meta.target)) {
            visitedEdges.add(eid);
        }
    }
    return { nodes: visitedNodes, edges: visitedEdges };
}

/* ═══════════════════════════════════════════
 *  7. 边样式
 * ═══════════════════════════════════════════ */

function isDbEdge(label) {
    return label === 'MONGODB' || label === 'REDIS' || label === 'MYSQL';
}

function makeEdgeAttrs(label) {
    if (isDbEdge(label)) {
        return {
            line: {
                stroke: '#cbd5e1', strokeWidth: 1,
                strokeDasharray: '6,4',
                targetMarker: {
                    name: 'classic', width: 6, height: 5,
                    fill: 'none', stroke: '#cbd5e1',
                },
            },
        };
    }
    return {
        line: {
            stroke: '#94a3b8', strokeWidth: 1.5,
            targetMarker: {
                name: 'block', width: 8, height: 6,
                fill: '#94a3b8',
            },
        },
    };
}

function makeEdgeLabel(label) {
    const isHttp = !isDbEdge(label);
    return [{
        position: 0.5,
        attrs: {
            label: {
                text: label,
                fill: isHttp ? '#64748b' : '#94a3b8',
                fontSize: isHttp ? 10 : 9,
                fontWeight: 500,
                fontFamily: '-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',
            },
            rect: {
                fill: '#fff', rx: 4, ry: 4,
                stroke: '#e2e8f0', strokeWidth: 0.5,
                refWidth: 8, refHeight: 4,
                refX: -4, refY: -2,
            },
        },
    }];
}

function makeEdgeRouter(label) {
    const isHttp = !isDbEdge(label);
    return {
        router: { name: 'manhattan', args: { padding: isHttp ? 20 : 16 } },
        connector: { name: 'rounded', args: { radius: isHttp ? 8 : 6 } },
    };
}

/* ═══════════════════════════════════════════
 *  8. 高亮 / 取消高亮
 * ═══════════════════════════════════════════ */

const DIM_OPACITY = 0.3;
const DIM_EDGE_OPACITY = 0.15;

/** 获取 HTML 节点的 DOM 元素 */
function findHtmlEl(graph, nodeId) {
    const view = graph.findViewByCell(nodeId);
    if (!view) return null;
    const fo = view.container.querySelector('foreignObject');
    return fo?.querySelector(':scope > div > div');
}

/** 高亮上下游路径 — 连线变蓝 + 流动虚线动画 */
function highlightPath(graph, adj, nodeId) {
    const connected = collectConnected(nodeId, adj);

    for (const cell of graph.getCells()) {
        if (cell.isNode()) {
            if (!connected.nodes.has(cell.id)) {
                cell.attr('body/opacity', DIM_OPACITY, { silent: true });
                const el = findHtmlEl(graph, cell.id);
                if (el) el.style.opacity = String(DIM_OPACITY);
            }
        } else if (cell.isEdge()) {
            if (connected.edges.has(cell.id)) {
                // 高亮：变蓝 + 流动动画
                cell.attr('line/stroke', '#3b82f6');
                cell.attr('line/strokeWidth', 2.5);
                cell.attr('line/strokeDasharray', '8,4');
                cell.attr('line/style/animation', 'topo-flow-dash 0.6s linear infinite');
                cell.attr('line/targetMarker/fill', '#3b82f6');
                cell.attr('line/targetMarker/stroke', '#3b82f6');
            } else {
                cell.attr('line/opacity', DIM_EDGE_OPACITY, { silent: true });
                const lbl = cell.getLabelAt(0);
                if (lbl?.attrs?.label) {
                    cell.setLabelAt(0, {
                        ...lbl,
                        attrs: {
                            ...lbl.attrs,
                            label: { ...lbl.attrs.label, opacity: DIM_EDGE_OPACITY },
                            rect: { ...lbl.attrs.rect, opacity: DIM_EDGE_OPACITY },
                        },
                    });
                }
            }
        }
    }
}

/** 清除所有高亮，恢复默认样式 */
function clearHighlight(graph) {
    for (const cell of graph.getCells()) {
        if (cell.isNode()) {
            cell.attr('body/opacity', 1, { silent: true });
            const el = findHtmlEl(graph, cell.id);
            if (el) { el.style.opacity = '1'; el.style.boxShadow = ''; }
        } else if (cell.isEdge()) {
            const label = cell.getData()?.label || '';
            const attrs = makeEdgeAttrs(label);
            cell.attr('line/stroke', attrs.line.stroke);
            cell.attr('line/strokeWidth', attrs.line.strokeWidth);
            cell.attr('line/strokeDasharray', attrs.line.strokeDasharray || '');
            cell.attr('line/style/animation', '');
            cell.attr('line/opacity', 1, { silent: true });
            cell.attr('line/targetMarker/fill', attrs.line.targetMarker.fill);
            cell.attr('line/targetMarker/stroke', attrs.line.targetMarker.stroke || attrs.line.targetMarker.fill);
            const lbl = cell.getLabelAt(0);
            if (lbl?.attrs?.label) {
                cell.setLabelAt(0, {
                    ...lbl,
                    attrs: {
                        ...lbl.attrs,
                        label: { ...lbl.attrs.label, opacity: 1 },
                        rect: { ...lbl.attrs.rect, opacity: 1 },
                    },
                });
            }
        }
    }
}

/* ═══════════════════════════════════════════
 *  9. 主渲染函数
 * ═══════════════════════════════════════════ */

/**
 * 渲染拓扑图到指定容器。
 *
 * @param {HTMLElement} container  - 挂载容器
 * @param {{ nodes: Array, edges: Array }} topology - 拓扑数据
 * @param {Object} [options]
 * @param {Set<string>} [options.faultServices] - 当前有故障的服务集合
 * @param {function(string):void} [options.onNodeClick] - 点击 service 节点回调
 * @returns {Graph}
 */
function render(container, topology, options = {}) {
    const { faultServices = new Set(), onNodeClick = null } = options;

    const { nodes: topoNodes, edges: topoEdges } = dedup(topology);
    const positions = computeLayout(topoNodes, topoEdges);

    // ── X6 节点 ──
    const x6Nodes = topoNodes.map(n => {
        const pos = positions.get(n.id);
        let shape = 'service-node';
        if (n.root) shape = 'root-node';
        else if (n.type === 'db') shape = 'db-node';

        const w = (n.type === 'db') ? DB_W : SERVICE_W;
        const h = (n.type === 'db') ? DB_H : SERVICE_H;

        return {
            id: n.id, shape,
            x: pos.x, y: pos.y, width: w, height: h,
            data: {
                label: n.label,
                type: n.type,
                root: n.root,
                fault: faultServices.has(n.id),
            },
        };
    });

    // ── X6 边 ──
    const x6Edges = topoEdges.map((e, i) => {
        const routing = makeEdgeRouter(e.label);
        return {
            id: `edge-${i}`, shape: 'edge',
            source: e.source, target: e.target,
            attrs: makeEdgeAttrs(e.label),
            labels: makeEdgeLabel(e.label),
            router: routing.router,
            connector: routing.connector,
            data: { label: e.label, source: e.source, target: e.target },
        };
    });

    // ── 创建 Graph ──
    const graph = new Graph({
        container,
        autoResize: true,
        background: { color: '#f8f9fb' },
        grid: {
            visible: true,
            type: 'dot',
            size: 20,
            args: { color: '#e2e8f0', thickness: 1 },
        },
        panning: { enabled: true },
        mousewheel: { enabled: true, zoomAtMousePosition: true, minScale: 0.3, maxScale: 3 },
        interacting: { nodeMovable: false },
        connecting: { enabled: false },
    });

    graph.fromJSON({ nodes: x6Nodes, edges: x6Edges });

    // ── 邻接表 ──
    const adj = buildAdjacency(x6Edges);

    // ── 事件 ──
    graph.on('node:mouseenter', ({ node }) => highlightPath(graph, adj, node.id));
    graph.on('node:mouseleave', () => clearHighlight(graph));
    graph.on('node:click', ({ node }) => {
        const data = node.getData() || {};
        if (data.type === 'service' && onNodeClick) onNodeClick(node.id);
    });

    graph.zoomToFit({ padding: 50, maxScale: 1.2 });
    return graph;
}

// 挂到 window 上供 topology.html 的内联脚本使用
window.TopologyRenderer = { render };
