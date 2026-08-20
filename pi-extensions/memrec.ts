/**
 * MemRec Extension for pi
 *
 * 跨会话记忆持久化：对接 memrec CLI（RocksDB + 向量检索 + BM25 混合检索）。
 *
 * 功能：
 * 1. 注册 6 个 LLM 可调用工具：memrec_search / memrec_add / memrec_get / memrec_list / memrec_delete / memrec_stats
 * 2. 自动记忆注入：before_agent_start 时根据用户 prompt 自动检索相关记忆，注入系统提示
 * 3. 命令：/memrec（状态统计）、/memrec-auto（开关自动注入）
 *
 * 安装：复制到 ~/.pi/agent/extensions/ 或项目 .pi/extensions/ 后 /reload
 * 依赖：memrec CLI 已安装且在 PATH 中
 */
import type { ExtensionAPI, ExtensionContext } from "@mariozechner/pi-coding-agent";
import { Type } from "typebox";
import { StringEnum } from "@mariozechner/pi-ai";

/** 扩展配置（持久化到会话） */
interface MemrecConfig {
	autoInject: boolean; // 会话开始时自动检索注入
	autoInjectCount: number; // 自动注入条数
}

const CONFIG_ENTRY_TYPE = "memrec-config";
const MEMORY_TYPES = ["decision", "knowledge", "context", "preference", "conversation"] as const;
const SOURCES = ["user", "system", "inferred", "external"] as const;
const SCOPES = ["default", "project", "global", "all"] as const;

/** 单条记忆内容截断长度 */
const MAX_CONTENT_CHARS = 300;

export default function memrecExtension(pi: ExtensionAPI) {
	let config: MemrecConfig = { autoInject: true, autoInjectCount: 5 };

	// ==================== 配置持久化 ====================

	function persistConfig() {
		pi.appendEntry<MemrecConfig>(CONFIG_ENTRY_TYPE, config);
	}

	function restoreConfig(ctx: ExtensionContext) {
		for (const entry of ctx.sessionManager.getBranch()) {
			if (entry.type === "custom" && entry.customType === CONFIG_ENTRY_TYPE) {
				const data = entry.data as MemrecConfig | undefined;
				if (data) {
					config = {
						autoInject: data.autoInject ?? config.autoInject,
						autoInjectCount: data.autoInjectCount ?? config.autoInjectCount,
					};
				}
			}
		}
	}

	// ==================== memrec CLI 调用 ====================

	/**
	 * 执行 memrec 命令并解析 JSON-RPC 输出。
	 * 失败抛出 Error，由调用方决定处理方式。
	 */
	async function execMemrec(args: string[], signal?: AbortSignal): Promise<any> {
		const result = await pi.exec("memrec", args, { signal, timeout: 20000 });
		if (result.code !== 0) {
			const detail = (result.stderr || result.stdout || "").trim().slice(0, 500);
			throw new Error(`memrec 命令失败(code=${result.code}): ${detail}`);
		}
		const stdout = result.stdout.trim();
		if (!stdout) {
			throw new Error("memrec 无输出");
		}
		let parsed: any;
		try {
			parsed = JSON.parse(stdout);
		} catch {
			throw new Error(`memrec 输出非 JSON: ${stdout.slice(0, 200)}`);
		}
		if (parsed.error) {
			throw new Error(`memrec 错误: ${JSON.stringify(parsed.error).slice(0, 300)}`);
		}
		return parsed.result;
	}

	// ==================== 格式化辅助 ====================

	function clip(text: string, maxLen = MAX_CONTENT_CHARS): string {
		const t = text?.trim() ?? "";
		if (t.length <= maxLen) return t;
		return t.slice(0, maxLen) + "...";
	}

	function formatMemory(m: any, index: number): string {
		const type = m.memory_type ?? "unknown";
		const tags = Array.isArray(m.tags) && m.tags.length > 0 ? ` #${m.tags.join(" #")}` : "";
		const scope = m.scope === "global" ? " [global]" : "";
		return `${index}. [${type}${tags}${scope}] ${clip(m.content)}`;
	}

	function formatMemories(memories: any[]): string {
		if (!memories || memories.length === 0) return "（无相关记忆）";
		return memories.map((m, i) => formatMemory(m, i + 1)).join("\n");
	}

	/** scope 枚举 → CLI 参数 */
	function scopeArgs(scope: string): string[] {
		switch (scope) {
			case "project":
				return ["--project-only"];
			case "global":
				return ["--global-only"];
			case "all":
				return ["--all"];
			default:
				return [];
		}
	}

	/** 格式化统计信息 */
	function formatStats(stats: any): string {
		return [
			`记忆总数: ${stats.total_memories ?? "?"}`,
			`活跃记忆: ${stats.active_memories ?? "?"}`,
			`已删除: ${stats.deleted_memories ?? "?"}`,
			`存储占用: ${stats.storage_usage ?? "?"}`,
		].join("\n");
	}

	// ==================== 自动记忆注入 ====================

	pi.on("before_agent_start", async (event, ctx) => {
		if (!config.autoInject) return;

		const query = event.prompt?.trim();
		// 过短的输入（如"继续"）没有检索价值
		if (!query || query.length < 4) return;

		let memories: any[] = [];
		try {
			const result = await execMemrec(
				["search", query, "-k", String(config.autoInjectCount), "--min-score", "0.6"],
				ctx.signal,
			);
			memories = result.results ?? [];
		} catch {
			// memrec 不可用/超时：静默跳过，不影响会话
			return;
		}

		if (memories.length === 0) return;

		const block = [
			"## 相关历史记忆（memrec 自动检索）",
			"以下是与当前任务相关的历史记忆，可参考但不盲从，以当前项目实际情况为准：",
			formatMemories(memories),
		].join("\n");

		return {
			systemPrompt: event.systemPrompt + "\n\n" + block,
		};
	});

	// ==================== 工具注册 ====================

	pi.registerTool({
		name: "memrec_search",
		label: "MemRec Search",
		description:
			"语义检索跨会话记忆（memrec）。使用混合检索（KNN+BM25+MMR）搜索历史知识、决策、偏好。支持中文。触发场景：任务开始前检索相关历史、查找之前的决策/知识/用户偏好。",
		promptSnippet: "检索跨会话历史记忆（memrec）",
		promptGuidelines: [
			"Use memrec_search at the start of a task to retrieve relevant historical memories from previous sessions.",
			"Use memrec_add to store important decisions, knowledge, and user preferences for future sessions.",
		],
		parameters: Type.Object({
			query: Type.String({ description: "搜索关键词，支持中文（如：认证方案、构建流程、用户偏好）" }),
			topK: Type.Optional(Type.Number({ description: "返回数量，默认 10" })),
			minScore: Type.Optional(Type.Number({ description: "最低相似度阈值 0-1，默认 0.5，越接近 1 越严格" })),
			scope: Type.Optional(
				StringEnum(SCOPES, {
					description: "搜索范围：default=当前项目+公共记忆，project=仅当前项目，global=仅公共记忆，all=跨项目",
				}),
			),
			memoryType: Type.Optional(
				Type.String({ description: "记忆类型过滤：decision/knowledge/context/preference/conversation" }),
			),
		}),
		async execute(_toolCallId, params, signal, _onUpdate) {
			if (signal?.aborted) throw new Error("已取消");
			const args = ["search", params.query];
			if (params.topK) args.push("-k", String(params.topK));
			if (params.minScore !== undefined) args.push("--min-score", String(params.minScore));
			args.push(...scopeArgs(params.scope ?? "default"));
			if (params.memoryType) args.push("--mtype", params.memoryType);

			const result = await execMemrec(args, signal);
			const memories = result.results ?? [];
			const text = memories.length === 0
				? "未找到相关记忆"
				: `找到 ${memories.length} 条相关记忆:\n${formatMemories(memories)}`;
			return {
				content: [{ type: "text", text }],
				details: { count: memories.length, memories },
			};
		},
	});

	pi.registerTool({
		name: "memrec_add",
		label: "MemRec Add",
		description:
			"存储跨会话记忆（memrec）。记录重要决策、知识点、项目上下文、用户偏好。触发场景：做出关键决策后、学到新知识、用户表达偏好、项目重要配置变更。",
		promptSnippet: "存储跨会话记忆（memrec）",
		parameters: Type.Object({
			content: Type.String({ description: "记忆内容，简洁完整地描述事实/决策/偏好" }),
			memoryType: Type.Optional(
				StringEnum(MEMORY_TYPES, {
					description: "记忆类型：decision=关键决策（推荐加 critical 标签），knowledge=知识点，context=项目配置/环境，preference=用户偏好（推荐 global），conversation=对话记录",
				}),
			),
			tags: Type.Optional(Type.Array(Type.String(), { description: "标签，如 critical/auth/rust/best-practice" })),
			global: Type.Optional(Type.Boolean({ description: "true=公共记忆（跨项目共享，适合用户偏好），默认 false=项目记忆" })),
			source: Type.Optional(
				StringEnum(SOURCES, {
					description: "来源：user=用户明确表达（权重最高），system=系统生成，inferred=AI推断（权重较低），external=外部导入",
				}),
			),
		}),
		async execute(_toolCallId, params, signal) {
			if (signal?.aborted) throw new Error("已取消");
			const args = ["add", params.content, "-t", params.memoryType ?? "knowledge"];
			for (const tag of params.tags ?? []) args.push("--tag", tag);
			if (params.global) args.push("--global");
			if (params.source) args.push("--source", params.source);

			const result = await execMemrec(args, signal);
			const id = result?.id ?? result?.memory?.id ?? "?";
			return {
				content: [{ type: "text", text: `记忆已保存 (id: ${id}, 类型: ${params.memoryType ?? "knowledge"})` }],
				details: { id },
			};
		},
	});

	pi.registerTool({
		name: "memrec_get",
		label: "MemRec Get",
		description: "获取单条记忆的完整内容（memrec）。按 ID 查询，可能包含较长原文。",
		promptSnippet: "获取单条记忆详情（memrec）",
		parameters: Type.Object({
			id: Type.String({ description: "记忆 ID（UUID）" }),
		}),
		async execute(_toolCallId, params, signal) {
			if (signal?.aborted) throw new Error("已取消");
			const result = await execMemrec(["get", params.id], signal);
			const memory = result?.memory;
			if (!memory) {
				return { content: [{ type: "text", text: `未找到记忆: ${params.id}` }], details: {} };
			}
			const text = [
				`ID: ${memory.id}`,
				`类型: ${memory.memory_type}`,
				`标签: ${(memory.tags ?? []).join(", ") || "无"}`,
				`范围: ${memory.scope}`,
				`来源: ${memory.source}`,
				`重要性: ${memory.importance}`,
				`创建时间: ${memory.created_at}`,
				`---`,
				memory.content,
			].join("\n");
			return { content: [{ type: "text", text }], details: { memory } };
		},
	});

	pi.registerTool({
		name: "memrec_list",
		label: "MemRec List",
		description: "列出记忆（memrec）。按时间倒序查看记忆列表，可按范围和数量限制。",
		promptSnippet: "列出跨会话记忆（memrec）",
		parameters: Type.Object({
			limit: Type.Optional(Type.Number({ description: "返回数量，默认 20" })),
			scope: Type.Optional(
				StringEnum(SCOPES, {
					description: "搜索范围：default=当前项目+公共记忆，project=仅当前项目，global=仅公共记忆，all=跨项目",
				}),
			),
		}),
		async execute(_toolCallId, params, signal) {
			if (signal?.aborted) throw new Error("已取消");
			const args = ["list"];
			if (params.limit) args.push("--limit", String(params.limit));
			args.push(...scopeArgs(params.scope ?? "default"));

			const result = await execMemrec(args, signal);
			const memories = result.memories ?? [];
			const text = memories.length === 0
				? "暂无记忆"
				: `共 ${memories.length} 条记忆:\n${formatMemories(memories)}`;
			return {
				content: [{ type: "text", text }],
				details: { count: memories.length, memories },
			};
		},
	});

	pi.registerTool({
		name: "memrec_delete",
		label: "MemRec Delete",
		description: "删除一条记忆（memrec）。按 ID 删除，谨慎使用，删除后不可恢复。",
		promptSnippet: "删除跨会话记忆（memrec）",
		parameters: Type.Object({
			id: Type.String({ description: "要删除的记忆 ID（UUID）" }),
		}),
		async execute(_toolCallId, params, signal) {
			if (signal?.aborted) throw new Error("已取消");
			await execMemrec(["delete", params.id], signal);
			return {
				content: [{ type: "text", text: `记忆已删除: ${params.id}` }],
				details: { id: params.id },
			};
		},
	});

	pi.registerTool({
		name: "memrec_stats",
		label: "MemRec Stats",
		description: "查看 memrec 记忆库统计信息（总数、活跃数、已删除数、存储占用）。",
		promptSnippet: "查看 memrec 记忆统计",
		parameters: Type.Object({}),
		async execute(_toolCallId, _params, signal) {
			if (signal?.aborted) throw new Error("已取消");
			const stats = await execMemrec(["stats"], signal);
			return {
				content: [{ type: "text", text: formatStats(stats) }],
				details: { stats },
			};
		},
	});

	// ==================== 命令注册 ====================

	pi.registerCommand("memrec", {
		description: "查看 memrec 记忆统计与自动注入配置",
		handler: async (_args, ctx) => {
			try {
				const stats = await execMemrec(["stats"]);
				ctx.ui.notify(
					`memrec: ${stats.active_memories ?? "?"} 活跃 / ${stats.total_memories ?? "?"} 总记忆 | 自动注入: ${config.autoInject ? "开" : "关"}(${config.autoInjectCount}条)`,
					"info",
				);
			} catch (e: any) {
				ctx.ui.notify(`memrec 不可用: ${e.message}`, "error");
			}
		},
	});

	pi.registerCommand("memrec-auto", {
		description: "控制自动记忆注入: /memrec-auto on|off|<数量>",
		handler: async (args, ctx) => {
			const arg = args?.trim().toLowerCase();
			if (arg === "on" || arg === "true" || arg === "1") {
				config.autoInject = true;
				persistConfig();
				ctx.ui.notify(`自动注入已开启（${config.autoInjectCount} 条/次）`, "success");
			} else if (arg === "off" || arg === "false" || arg === "0") {
				config.autoInject = false;
				persistConfig();
				ctx.ui.notify("自动注入已关闭", "success");
			} else if (arg && /^\d+$/.test(arg)) {
				config.autoInjectCount = Math.max(1, Math.min(20, parseInt(arg, 10)));
				config.autoInject = true;
				persistConfig();
				ctx.ui.notify(`自动注入已开启，${config.autoInjectCount} 条/次`, "success");
			} else {
				ctx.ui.notify(`用法: /memrec-auto on|off|<数量>（当前: ${config.autoInject ? "开" : "关"}, ${config.autoInjectCount} 条/次）`, "warning");
			}
		},
	});

	// ==================== 状态恢复 ====================

	pi.on("session_start", async (_event, ctx) => {
		restoreConfig(ctx);
	});

	pi.on("session_tree", async (_event, ctx) => {
		restoreConfig(ctx);
	});
}
