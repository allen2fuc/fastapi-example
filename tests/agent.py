

from typing import Any, Awaitable, Callable, List, Dict, Literal, Optional
from anthropic import (
    AsyncAnthropic,
    transform_schema
)
from anthropic.types import (
    Message,
    ParsedMessage,
    ParsedTextBlock,
    ToolUseBlock,
    TextBlock
)

import logging

from pydantic import BaseModel, Field
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


func_dict: dict[str, Callable] = {}
func_tools: List[Dict[str, Any]] = []


class OutputSchema(BaseModel):
    # 意图,聊天的意图，1. 闲聊 2.获取天气 3.其它
    intent: Literal["chat", "get_weather", "other"] = Field(description="The intent of the user's request，chat、get_weather、other")
    # 响应内容
    content: str = Field(description="The content of the user's request")


def agent_tool(name: str, description: str, input_schema: dict[str, Any]):
    def func_tool(func: Callable):
        func_dict[func.__name__] = func
        func_tools.append({
            'name': name,
            'description': description,
            'input_schema': input_schema,
        })
        return func
    return func_tool


async def _execute_function(func_name: str, func_args: Dict[str, Any]) -> Any:
    """Execute a tool and return the result."""
    return func_dict[func_name](**func_args)


class Agent:

    def __init__(
            self,
            client: AsyncAnthropic,
            **kwargs: Any,
    ):
        self.client = client
        self.params = kwargs

    async def create(self, messages: list[Dict[str, Any]], **kwargs: Any) -> Message:
        return await self.client.messages.create(
            messages=messages,
            **self.params,
            **kwargs,
        )

    async def stream(
        self,
        messages: list[Dict[str, Any]],
        callback_text: Callable[[str], Awaitable[None]],
        callback_final_message: Callable[[List[Dict[str, Any]], int, int], Awaitable[None]],
        **kwargs: Any,
    ):

        async def overwide_callback_final_message(messages: list[Dict[str, Any]], input_tokens: int, output_tokens: int):
            await callback_final_message(messages, input_tokens, output_tokens)
            await self.summarize_messages(messages, input_tokens, output_tokens)

        async with self.client.messages.stream(
            messages=messages,
            **self.params,
            **kwargs,
        ) as stream:

            async for text in stream.text_stream:
                await callback_text(text)

            final_message = await stream.get_final_message()

            await self._handle_stream_message(
                final_message, 
                messages, 
                callback_text, 
                overwide_callback_final_message
            )


    async def _handle_stream_message(
        self,
        handle_message: ParsedMessage,
        messages: list[Dict[str, Any]],
        callback_text: Callable[[str], Awaitable[None]],
        callback_final_message: Callable[[List[Dict[str, Any]], int, int], Awaitable[None]]
    ):

        usage = handle_message.usage
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens

        content: List[ParsedTextBlock | ToolUseBlock] = handle_message.content

        for item in content:
            if isinstance(item, ParsedTextBlock):
                self._handle_text_message(messages, "assistant", item.text)
            elif isinstance(item, ToolUseBlock):
                if item.type == 'tool_use':
                    await self._handle_tool_message(item, messages)
                    await self.stream(messages, callback_text=callback_text, callback_final_message=callback_final_message)
            else:
                logger.warning(f"unknown message type: {item}")
                continue

        await callback_final_message(messages, input_tokens, output_tokens)

    def _handle_text_message(
        self,
        messages: list[Dict[str, Any]],
        role: Literal["user", "assistant"],
        content: str | list[Dict[str, Any]]
    ):
        messages.append({"role": role, "content": content})

    async def _handle_tool_message(
        self,
        item: ToolUseBlock,
        messages: list[Dict[str, Any]]
    ):
        tool_name = item.name
        tool_input = item.input
        tool_result = await _execute_function(tool_name, tool_input)
        self._handle_text_message(
            messages, 
            "assistant", 
            [{'id': item.id, 'type': item.type, 'name': item.name, 'input': item.input}]
        )
        self._handle_text_message(
            messages, 
            "user", 
            [{'type': 'tool_result', 'tool_use_id': item.id, 'content': tool_result}]
        )

    async def _handle_message(self, msg: Message, messages: list[Dict[str, Any]]):
        usage = msg.usage
        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens

        content = msg.content
        for item in content:
            if isinstance(item, TextBlock):
                self._handle_text_message(messages, "assistant", item.text)
            elif isinstance(item, ToolUseBlock):
                if item.type == 'tool_use':
                    await self._handle_tool_message(item, messages)
                    resp = await self.create(messages)
                    await self._handle_message(resp, messages)  # 递归调用，处理工具调用结果
            else:
                logger.warning(f"unknown message type: {item}")
                continue

        return messages, input_tokens, output_tokens


    async def summarize_messages(
        # agent实例
        self,
        # 消息列表
        messages: list[Dict[str, Any]],
        # 输入Token数量
        input_tokens: int,
        # 输出Token数量
        output_tokens: int,
        # 限制记录数
        limit_count: int = 10,
        # 限制Token数量
        limit_tokens: int = 500,
    ) -> Any:

        tokens_count = input_tokens + output_tokens
        record_count = len(messages)
        is_chat_message = isinstance(messages[-1]['content'], str) # 排除函数调用消息

        if (record_count > limit_count or tokens_count > limit_tokens) and is_chat_message:

            logger.info(f"summarize_messages: record_count: {record_count}, tokens_count: {tokens_count}")

            new_messages = []
            content = "summarize the following messages: " + \
                '\n'.join([f"{msg['role']}: {msg['content']}" for msg in messages])
            self._handle_text_message(new_messages, "user", content)

            resp = await self.create(new_messages)
            new_messages, input_tokens, output_tokens = await self._handle_message(resp, new_messages)

            # 清理旧的messages,把新的追加进去
            messages.clear()
            messages.append(new_messages[-1])

        return messages, input_tokens, output_tokens


def create_agent(base_url: str, api_key: str, **kwargs: Any) -> Agent:
    params = {'api_key': api_key}
    if base_url is not None:
        params['base_url'] = base_url

    client = AsyncAnthropic(**params)
    return Agent(client=client, **kwargs)

async def main():
    @agent_tool(name="get_weather", description="Get the weather in a city", input_schema={'type': 'object', 'properties': {'location': {'type': 'string', 'description': 'The city to get the weather for'}}, 'required': ['location']})
    def get_weather(location: str) -> str:
        return f"The weather in {location} is sunny."

    agent = create_agent(
        base_url="https://api.jiekou.ai/anthropic",
        api_key="sk_EMCkI-4qXUXj2CkXG-Y6_yat65djagHfBQK0oCWhd14"
    )

    async def callback_text(text: str):
        print(text, end="", flush=True)

    async def callback_final_message(messages: list[Dict[str, Any]], input_tokens: int, output_tokens: int):
        # print(f"input_tokens: {input_tokens}, output_tokens: {output_tokens}")
        # print(f"messages: {messages}")
        logger.info(f"callback_final_message: input_tokens: {input_tokens}, output_tokens: {output_tokens}")


    messages = [{"role": "user", "content": "What's the weather in Tokyo?"}]
    await agent.stream(
        messages=messages, 
        callback_text=callback_text, 
        callback_final_message=callback_final_message,
        model="claude-3-haiku-20240307",
        system="You are a helpful assistant.",
        max_tokens=3000
    )

    # messages += [{"role": "user", "content": "Hello, how are you?"}]
    # await agent.stream(
    #     messages=messages, 
    #     callback_text=callback_text, 
    #     callback_final_message=callback_final_message
    # )

    # messages += [{"role": "user", "content": "write java code to print 'Hello, World!'"}]
    # await agent.stream(
    #     messages=messages, 
    #     callback_text=callback_text, 
    #     callback_final_message=callback_final_message
    # )

    print("\n--------------------------------")
    print("messages: ", messages)
    print("--------------------------------")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

    
