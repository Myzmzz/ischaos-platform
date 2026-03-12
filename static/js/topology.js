/**
 * TopologyRenderer — AntV X6 v2 + Dagre TB 分层拓扑渲染器 (ES Module)。
 *
 * 自定义 HTML 节点:
 *   - service-node   180×60  白底灰边圆角  上方 SERVICE 小字 + 下方服务名
 *   - root-node      180×60  2px 蓝边 + 左侧蓝竖条
 *   - db-node        140×48  灰底虚线边 + 数据库图标
 *   - fault 状态     红边红底 + 右上角脉冲圆点
 *
 * 交互:
 *   - hover 节点 → 高亮上下游路径，其余 30% 透明
 *   - hover 边   → 边变粗变蓝，两端节点高亮
 *   - 点击 service/root 节点 → 触发 onNodeClick 回调
 *   - 画布拖拽 + 滚轮缩放
 */
import { Graph, Shape } from 'https://esm.sh/@antv/x6@2'
import dagre from 'https://esm.sh/dagre@0.8.5'

/* ═══════════════════════════════════════════
 *  1. 常量
 * ═══════════════════════════════════════════ */

const SERVICE_W = 180, SERVICE_H = 60;
const DB_W = 140, DB_H = 48;

const DB_ICON = `<svg width="16" height="16" viewBox="0 0 16 16" fill="none">
  <ellipse cx="8" cy="3.5" rx="6" ry="2.5" stroke="#9ca3af" stroke-width="1.2" fill="#f3f4f6"/>
  <path d="M2 3.5v9c0 1.38 2.69 2.5 6 2.5s6-1.12 6-2.5v-9" stroke="#9ca3af" stroke-width="1.2" fill="none"/>
  <ellipse cx="8" cy="12.5" rx="6" ry="2.5" stroke="#9ca3af" stroke-width="1.2" fill="none"/>
</svg>`;

/* ═══════════════════════════════════════════
 *  2. 注册自定义 HTML 节点
 * ═══════════════════════════════════════════ */

/** 通用 service 节点 */
Shape.HTML.register({
    shape: 'service-node',
    width: SERVICE_W,
    height: SERVICE_H,
    effect: ['data'],
    html(cell) {
        const { label, fault } = cell.getData() || {};
        const div = document.createElement('div');
        div.style.cssText = `
            width:${SERVICE_W}px; height:${SERVICE_H}px; box-sizing:border-box;
            background:#fff; border:1px solid #e5e7eb; border-radius:8px;
            display:flex; flex-direction:column; justify-content:center; align-items:center;
            padding:6px 10px; position:relative; transition:all 0.15s;
            font-family:ui-monospace,SFMono-Regular,monospace;
        `;
        if (fault) {
            div.style.border = '2px solid #dc2626';
            div.style.background = '#fef2f2';
        }
        div.innerHTML = `
            <div style="font-size:12px;color:#9ca3af;line-height:1;margin-bottom:4px;">SERVICE</div>
            <div style="font-size:14px;color:#111827;font-weight:500;line-height:1;
                 overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:160px;"
                 title="${label}">${label}</div>
            ${fault ? '<div class="topo-pulse-dot"></div>' : ''}
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
        const { label, fault } = cell.getData() || {};
        const div = document.createElement('div');
        div.style.cssText = `
            width:${SERVICE_W}px; height:${SERVICE_H}px; box-sizing:border-box;
            background:#fff; border:2px solid #2563eb; border-radius:8px;
            display:flex; flex-direction:row; align-items:stretch;
            position:relative; transition:all 0.15s; overflow:hidden;
            font-family:ui-monospace,SFMono-Regular,monospace;
        `;
        if (fault) {
            div.style.border = '2px solid #dc2626';
            div.style.background = '#fef2f2';
        }
        div.innerHTML = `
            <div style="width:3px;background:#2563eb;flex-shrink:0;
                 ${fault ? 'background:#dc2626;' : ''}"></div>
            <div style="flex:1;display:flex;flex-direction:column;justify-content:center;
                 align-items:center;padding:6px 10px;">
                <div style="font-size:12px;color:#2563eb;line-height:1;margin-bottom:4px;
                     font-weight:600;">ROOT</div>
                <div style="font-size:14px;color:#111827;font-weight:500;line-height:1;
                     overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:150px;"
                     title="${label}">${label}</div>
            </div>
            ${fault ? '<div class="topo-pulse-dot"></div>' : ''}
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
        const div = document.createElement('div');
        div.style.cssText = `
            width:${DB_W}px; height:${DB_H}px; box-sizing:border-box;
            background:#f9fafb; border:1px dashed #d1d5db; border-radius:8px;
            display:flex; flex-direction:row; justify-content:center; align-items:center;
            gap:8px; padding:6px 12px; position:relative; transition:all 0.15s;
            font-family:ui-monospace,SFMono-Regular,monospace;
        `;
        if (fault) {
            div.style.border = '2px solid #dc2626';
            div.style.background = '#fef2f2';
        }
        div.innerHTML = `
            ${DB_ICON}
            <span style="font-size:13px;color:#6b7280;font-weight:500;">${label}</span>
            ${fault ? '<div class="topo-pulse-dot"></div>' : ''}
        `;
        return div;
    },
});

/* ═══════════════════════════════════════════
 *  3. Dagre 布局计算
 * ═══════════════════════════════════════════ */

function computeLayout(nodes, edges) {
    const g = new dagre.graphlib.Graph();
    g.setGraph({ rankdir: 'TB', nodesep: 60, ranksep: 80, marginx: 30, marginy: 30 });
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
 *  4. 数据预处理 — 合并同 id 节点
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
 *  5. 邻接表（hover 高亮用）
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

    const qDown = [nodeId];
    while (qDown.length) {
        const cur = qDown.shift();
        for (const next of (adj.downstream.get(cur) || [])) {
            if (!visitedNodes.has(next)) { visitedNodes.add(next); qDown.push(next); }
        }
    }
    const qUp = [nodeId];
    while (qUp.length) {
        const cur = qUp.shift();
        for (const prev of (adj.upstream.get(cur) || [])) {
            if (!visitedNodes.has(prev)) { visitedNodes.add(prev); qUp.push(prev); }
        }
    }
    for (const [eid, meta] of adj.edgeMeta) {
        if (visitedNodes.has(meta.source) && visitedNodes.has(meta.target)) {
            visitedEdges.add(eid);
        }
    }
    return { nodes: visitedNodes, edges: visitedEdges };
}

/* ═══════════════════════════════════════════
 *  6. 边样式
 * ═══════════════════════════════════════════ */

function isDbEdge(label) {
    return label === 'MONGODB' || label === 'REDIS' || label === 'MYSQL';
}

function makeEdgeAttrs(label) {
    if (isDbEdge(label)) {
        return {
            line: {
                stroke: '#d1d5db', strokeWidth: 1, strokeDasharray: '4,3',
                targetMarker: { name: 'block', width: 7, height: 5, open: true, stroke: '#d1d5db', fill: 'none' },
            },
        };
    }
    return {
        line: {
            stroke: '#94a3b8', strokeWidth: 1,
            targetMarker: { name: 'block', width: 7, height: 5, fill: '#94a3b8' },
        },
    };
}

function makeEdgeLabel(label) {
    return [{
        position: 0.5,
        attrs: {
            label: { text: label, fill: '#9ca3af', fontSize: 10, fontFamily: 'system-ui, sans-serif' },
            rect:  { fill: '#fff', stroke: 'none', rx: 3, ry: 3 },
        },
    }];
}

/* ═══════════════════════════════════════════
 *  7. 高亮 / 取消高亮
 * ═══════════════════════════════════════════ */

const DIM_OPACITY = 0.15;

function findHtmlEl(graph, nodeId) {
    const view = graph.findViewByCell(nodeId);
    if (!view) return null;
    const fo = view.container.querySelector('foreignObject');
    return fo?.querySelector(':scope > div > div');
}

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
            if (!connected.edges.has(cell.id)) {
                cell.attr('line/opacity', DIM_OPACITY, { silent: true });
                const lbl = cell.getLabelAt(0);
                if (lbl?.attrs?.label) {
                    cell.setLabelAt(0, {
                        ...lbl,
                        attrs: { ...lbl.attrs, label: { ...lbl.attrs.label, opacity: DIM_OPACITY } },
                    });
                }
            }
        }
    }
}

function highlightEdge(graph, edgeCell) {
    edgeCell.attr('line/stroke', '#2563eb');
    edgeCell.attr('line/strokeWidth', 2);
    for (const nid of [edgeCell.getSourceCellId(), edgeCell.getTargetCellId()]) {
        const el = findHtmlEl(graph, nid);
        if (el) el.style.boxShadow = '0 0 0 2px #2563eb40';
    }
}

function clearHighlight(graph) {
    for (const cell of graph.getCells()) {
        if (cell.isNode()) {
            cell.attr('body/opacity', 1, { silent: true });
            const el = findHtmlEl(graph, cell.id);
            if (el) { el.style.opacity = '1'; el.style.boxShadow = 'none'; }
        } else if (cell.isEdge()) {
            const label = cell.getData()?.label || '';
            const attrs = makeEdgeAttrs(label);
            cell.attr('line/stroke', attrs.line.stroke);
            cell.attr('line/strokeWidth', attrs.line.strokeWidth);
            cell.attr('line/opacity', 1, { silent: true });
            const lbl = cell.getLabelAt(0);
            if (lbl?.attrs?.label) {
                cell.setLabelAt(0, {
                    ...lbl,
                    attrs: { ...lbl.attrs, label: { ...lbl.attrs.label, opacity: 1 } },
                });
            }
        }
    }
}

/* ═══════════════════════════════════════════
 *  8. 主渲染函数
 * ═══════════════════════════════════════════ */

/**
 * @param {HTMLElement} container
 * @param {{ nodes: Array, edges: Array }} topology
 * @param {Object} [options]
 * @param {Set<string>} [options.faultServices]
 * @param {function(string):void} [options.onNodeClick]
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
            data: { label: n.label, type: n.type, root: n.root, fault: faultServices.has(n.id) },
        };
    });

    // ── X6 边 ──
    const x6Edges = topoEdges.map((e, i) => ({
        id: `edge-${i}`, shape: 'edge',
        source: e.source, target: e.target,
        attrs: makeEdgeAttrs(e.label),
        labels: makeEdgeLabel(e.label),
        router: { name: 'manhattan', args: { padding: 20 } },
        connector: { name: 'rounded', args: { radius: 6 } },
        data: { label: e.label, source: e.source, target: e.target },
    }));

    // ── 创建 Graph ──
    const graph = new Graph({
        container,
        autoResize: true,
        background: { color: '#fafbfc' },
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
    graph.on('edge:mouseenter', ({ edge }) => highlightEdge(graph, edge));
    graph.on('edge:mouseleave', () => clearHighlight(graph));
    graph.on('node:click', ({ node }) => {
        const data = node.getData() || {};
        if (data.type === 'service' && onNodeClick) onNodeClick(node.id);
    });

    graph.zoomToFit({ padding: 50, maxScale: 1.2 });
    return graph;
}

// 挂到 window 上供 topology.html 的内联脚本使用
window.TopologyRenderer = { render };
