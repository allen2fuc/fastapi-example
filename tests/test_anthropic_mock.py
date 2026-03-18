# uv run ruff check tests/test_anthropic_mock.py --fix
# uv run ruff format tests/test_anthropic_mock.py


import json
from typing import Any
from anthropic import (
    AsyncAnthropic,
)
from pydantic import BaseModel

class ExitException(Exception):
    pass

# ── Claude 工具定义（对齐 X8/X9 接口）──────────────────────────
TOOLS = [
    {
        "name": "get_system_status",
        "description": (
            "读取 Luxsin 设备的系统状态参数，包含：音量(volume 0-100)、"
            "当前选中的 PEQ 槽位(peqSelect)、PEQ 是否开启(peqEnable)、"
            "输入源(inputSource)、增益(gain)、静音状态等。"
            "当用户想了解或调整音量、输入源、增益、静音等基础参数时使用。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "获取原因（向用户展示）"},
            },
            "required": ["reason"],
        },
    },
    {
        "name": "get_peq_list",
        "description": (
            "读取 Luxsin 设备的全部 PEQ/EQ 模型列表及当前激活的频段滤波器参数。"
            "每个模型包含耳机名称、品牌、preamp 增益、以及最多10个滤波器(type/fc/gain/q)。"
            "当用户想优化音质、调整 EQ/PEQ、或询问当前耳机均衡设置时使用。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "获取原因（向用户展示）"},
            },
            "required": ["reason"],
        },
    },
    {
        "name": "set_system_params",
        "description": (
            "修改 Luxsin 设备 的系统参数，如音量(volume)、"
            "PEQ 槽位(peqSelect)、PEQ 开关(peqEnable)、"
            "输入源(inputSource)、增益(gain)等。"
            "在读取并分析当前状态后才调用此工具。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "params": {
                    "type": "object",
                    "description": "要修改的参数键值对，如 {\"volume\": 55, \"peqEnable\": 1}",
                },
                "description": {"type": "string", "description": "本次修改说明（向用户展示）"},
            },
            "required": ["params", "description"],
        },
    },
    {
        "name": "add_peq_model",
        "description": (
            "新增或覆盖一个 PEQ 模型到 Luxsin 设备。"
            "数据会用自定义 Base64 编码后通过 peqChange 接口写入设备。"
            "必须包含完整的滤波器列表（不足10个会自动补齐）。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name":    {"type": "string", "description": "模型名称，如 'Sennheiser HD 650 Optimized'"},
                "brand":   {"type": "string"},
                "model":   {"type": "string"},
                "preamp":  {"type": "number", "description": "前置增益(dB)，通常为负值防止削波"},
                "autoPre": {"type": "integer", "description": "0=手动preamp, 1=自动"},
                "filters": {
                    "type": "array",
                    "description": "滤波器列表，每项含 type(int)/fc(Hz)/gain(dB)/q",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "integer", "description": "滤波器类型: 0=LPF,1=HPF,2=BPF,3=NOTCH,4=PEAK,5=LSHELF,6=HSHELF,7=APF"},
                            "fc":   {"type": "number",  "description": "中心频率(Hz)"},
                            "gain": {"type": "number",  "description": "增益(dB)"},
                            "q":    {"type": "number",  "description": "Q值"},
                        },
                        "required": ["type", "fc", "gain", "q"],
                    },
                },
                "description": {"type": "string", "description": "本次操作说明（向用户展示）"},
            },
            "required": ["name", "brand", "model", "preamp", "filters", "description"],
        },
    },
    {
        "name": "remove_peq_model",
        "description": "从 Luxsin X9 删除一个 PEQ 模型（按名称）。",
        "input_schema": {
            "type": "object",
            "properties": {
                "name":        {"type": "string", "description": "要删除的模型名称"},
                "description": {"type": "string", "description": "操作说明"},
            },
            "required": ["name", "description"],
        },
    },
    {
        "name": "select_peq_model",
        "description": "切换 Luxsin X9 当前激活的 PEQ 槽位（通过修改 peqSelect 参数实现）。",
        "input_schema": {
            "type": "object",
            "properties": {
                "peq_index":   {"type": "integer", "description": "PEQ 列表下标（从0开始）"},
                "description": {"type": "string",  "description": "操作说明"},
            },
            "required": ["peq_index", "description"],
        },
    },
]

SYSTEM = """你是 Luxsin X9 音频设备的智能助手，帮助用户优化和管理设备参数。

设备能力：
- 音量控制（0-100，R2R 精度 0.1dB）
- 10 频段参数均衡器（PEQ），支持多个模型切换
- 增益设置、输入源切换、静音控制
- 2500+ 耳机 EQ 数据库（HP-EQ）

工作原则：
1. 先读取当前状态，再提出修改建议
2. 给出具体参数值对比（修改前→修改后）
3. 解释每个修改的音频效果原因
4. 等用户确认后才调用 set/add/remove 工具
5. PEQ 滤波器类型：0=低通,1=高通,2=带通,3=陷波,4=峰值,5=低架,6=高架,7=全通"""


class Event(BaseModel):
    event: str
    data: dict[str, Any]

def create_client():
    anthropic_client = AsyncAnthropic(
        base_url="https://api.jiekou.ai/anthropic",
        api_key="sk_EMCkI-4qXUXj2CkXG-Y6_yat65djagHfBQK0oCWhd14",
    )
    return anthropic_client

def sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

async def run_claude(client: AsyncAnthropic, messages: list[dict[str, Any]]):
    tool_calls = []      # 工具调用列表
    current_tool = None  # 正在构建的工具调用
    async with client.messages.stream(
        model="claude-3-haiku-20240307",
        system=SYSTEM,
        messages=messages,
        tools=TOOLS,
        temperature=0.7,
        max_tokens=2048,
    ) as stream:
        async for event in stream:
            if event.type == "text":
                yield sse("text", {"delta": event.text})
            elif event.type == "content_block_start":
                blk = event.content_block
                if blk.type == "tool_use":
                    current_tool = {"id": blk.id, "name": blk.name, "input": ""}
            elif event.type == "content_block_delta":
                if event.delta.type == "input_json_delta" and current_tool:
                    current_tool["input"] += event.delta.partial_json
            elif event.type == "content_block_stop":
                if current_tool:
                    current_tool["input"] = json.loads(current_tool["input"] or "{}")
                    tool_calls.append(current_tool)
                    current_tool = None

        final = await stream.get_final_message()
        messages.append({"role": "assistant", "content": final.content})

    if tool_calls:
        for tc in tool_calls:
            yield sse("tool_call", {
                "tool_use_id": tc["id"],
                "name":        tc["name"],
                "input":       tc["input"],
            })
        yield sse("waiting_confirmation", {"count": len(tool_calls)})
    else:
        yield sse("done", {})

def is_exit_command(user_input: str) -> bool:
    return user_input == "exit" or user_input == "quit"

async def main():

    client = create_client()
    messages: list[dict[str, Any]] = []
    while True:
        try:
            user_input = input("Enter your message: ")
            if is_exit_command(user_input):
                raise ExitException()

            user_input = user_input.strip()
            if user_input == "":
                print("Empty input, skipping...")
                continue

            if user_input == 'messages':
                print("---------------- messages ----------------")
                for message in messages:
                    print("message: ", message)
                print("---------------- messages ----------------")
                continue

            print("--------------------------------")
            print("user_input: ", user_input)
            print("--------------------------------")

            messages.append({"role": "user", "content": user_input})

            stream = run_claude(client, messages)
            async for event in stream:
                print("event: ", event)

        except (KeyboardInterrupt, ExitException) as e:
            print("Exiting...")
            break
        except Exception as e:
            print("Error: ", e)
            continue


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
