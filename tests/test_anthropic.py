


import anthropic
import json

from typing import Any, Dict
from anthropic import (
    Anthropic,
    # beta_async_tool,
    # tool_runner,
    beta_async_tool,
    beta_tool,
    AsyncAnthropic,
    DefaultAioHttpClient,
    TextEvent,
    ParsedMessageStopEvent,
    ParsedContentBlockStopEvent,
    InputJsonEvent,
)

from anthropic.types import (
    ModelInfo,
    RawMessageDeltaEvent,
    RawContentBlockDeltaEvent,
    RawMessageStartEvent,
    RawContentBlockStartEvent,
    TextBlock,
    ToolUseBlock,
    ParsedMessage,
    ParsedTextBlock,
    Message,
)

import logging

from pydantic import BaseModel
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
    

# 询问天气的tool
@beta_async_tool
async def get_weather(location: str) -> str:
    """Get the weather for a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA
    Returns:
        A dictionary containing the location, temperature, and weather condition.
    """
    return json.dumps(
        {
            "location": location,
            "temperature": "68°F",
            "condition": "Sunny",
        }
    )

async def execute_tool(name, tool_input):
    """Execute a tool and return the result."""
    print("execute_tool: ", name, tool_input)
    result = None
    if name == "get_weather":
        result = await get_weather(tool_input["location"])
    else:
        raise ValueError(f"Tool {name} not found")
    return result

weather_tool = {
    "name": "get_weather",
    "description": "Get the weather in a city",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "The city to get the weather for"},
        },
        "required": ["location"],
    },
}


async def test_create_message(client: AsyncAnthropic, model: str, system: str, messages: list[dict[str, str]], tools: list[dict[str, Any]], max_tokens: int):
    message: Message = await client.messages.create(
        model=model,
        system=system,
        tools=tools,
        max_tokens=max_tokens,
        messages=messages,
    )

    # Message(id='0b08525e922c64911e8f1e81a77b9f26', container=None, content=[TextBlock(citations=None, text="I'm doing well, thanks for asking! The weather in Tokyo today is sunny. Is there anything else I can help you with?", type='text')], model='claude-3-haiku-20240307', role='assistant', stop_reason='end_turn', stop_sequence=None, type='message', usage=Usage(cache_creation=None, cache_creation_input_tokens=None, cache_read_input_tokens=None, inference_geo=None, input_tokens=429, output_tokens=31, server_tool_use=None, service_tier=None))
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    print(f"input_tokens: {input_tokens}, output_tokens: {output_tokens}")

    content = message.content
    for item in content:
        if isinstance(item, TextBlock):
            messages.append({"role": message.role, "content": item.text })
        elif isinstance(item, ToolUseBlock):
            print("ToolUseBlock: ", item)
            pass
    

    # print("message: ", message)

# async def test_create_stream_output(client: Anthropic, model: str, system: str, messages: list[dict[str, str]]):
    
#     try:
#         stream = await client.messages.create(
#             model=model,
#             max_tokens=1024,
#             system=system,
#             tools=[weather_tool],
#             messages=messages,
#             stream=True,
#         )

#         async for event in stream:
#             print("chunk: ", event)

#     except anthropic.APIError as e:
#         print(f"Error: {e}")

async def test_stream_output(client: AsyncAnthropic, model: str, system: str, messages: list[dict[str, str]]):

    print("test_output: ", messages)
    try:
        async with client.messages.stream(
            model=model,
            max_tokens=4096,
            system=system,
            tools=[weather_tool],
            messages=messages,
        ) as stream:

            print("Text: ", end="", flush=True)
            async for text in stream.text_stream:
                print(text, end="", flush=True)

            print()
            final_message = await stream.get_final_message()
            if isinstance(final_message, ParsedMessage):
                # ParsedMessage(id='42560d07984dba097609a3778ce0efe5', container=None, content=[ParsedTextBlock(citations=None, text="Hello! As an AI assistant, I'm doing well and ready to help you. How can I assist you today?", type='text', parsed_output=None)], model='claude-3-haiku-20240307', role='assistant', stop_reason='end_turn', stop_sequence=None, type='message', usage=Usage(cache_creation=None, cache_creation_input_tokens=None, cache_read_input_tokens=None, inference_geo=None, input_tokens=350, output_tokens=27, server_tool_use=None, service_tier=None))
                input_tokens = final_message.usage.input_tokens
                output_tokens = final_message.usage.output_tokens
                print(f"input_tokens: {input_tokens}, output_tokens: {output_tokens}")

                content = final_message.content

                for item in content:
                    if isinstance(item, ParsedTextBlock):
                        messages.append({"role": "assistant", "content": item.text})
                    elif isinstance(item, ToolUseBlock):
                        if item.type == 'tool_use':
                            tool_input = item.input 
                            tool_name = item.name
                            tool_result = await execute_tool(tool_name, tool_input)
                            
                            messages.append({"role": "assistant", "content": [ {'id':item.id,'type':item.type,'name':item.name,'input':item.input} ] })
                            messages.append({"role": "user", "content": [{'type':'tool_result','tool_use_id':item.id,'content':tool_result}]})

                            # await test_create_message(client, model, system, messages)
                            # print("message: ", messages[-1])

                            await test_stream_output(client, model, system, messages)

            # ParsedMessage(id='435eb8f9dd17a0769cfe97c69bcdfe4f', container=None, content=[ToolUseBlock(id='toolu_bdrk_01TxuW8zrTwhP2Ximy4AfQhh', caller=None, input={'city': 'Tokyo'}, name='get_weather', type='tool_use')], model='claude-3-haiku-20240307', role='assistant', stop_reason='tool_use', stop_sequence=None, type='message', usage=Usage(cache_creation=None, cache_creation_input_tokens=None, cache_read_input_tokens=None, inference_geo=None, input_tokens=350, output_tokens=53, server_tool_use=None, service_tier=None))
            # {
            #   "id": "0696dd5152c51fe6862421c8106278e6",
            #   "content": [
            #     {
            #       "id": "toolu_bdrk_01RMvNTS5GscALeWquz9AzvF",
            #       "caller": null,
            #       "input": {
            #         "city": "Tokyo"
            #       },
            #       "name": "get_weather",
            #       "type": "tool_use"
            #     }
            #   ],
            #   "model": "claude-3-haiku-20240307",
            #   "role": "assistant",
            #   "stop_reason": "tool_use",
            #   "stop_sequence": null,
            #   "type": "message",
            #   "usage": {
            #     "input_tokens": 350,
            #     "output_tokens": 53
            #   }
            # }
            # print("message: ", message)


                # Start
                # if isinstance(event, RawMessageStartEvent):
                #     # RawMessageStartEvent(message=Message(id='41c0d97007b31375546bdc52d9db1078', container=None, content=[], model='claude-3-haiku-20240307', role='assistant', stop_reason=None, stop_sequence=None, type='message', usage=Usage(cache_creation=None, cache_creation_input_tokens=None, cache_read_input_tokens=None, inference_geo=None, input_tokens=18, output_tokens=4, server_tool_use=None, service_tier=None)), type='message_start')
                #     pass

                # if isinstance(event, RawContentBlockStartEvent):
                #     # RawContentBlockStartEvent(content_block=TextBlock(citations=None, text='', type='text'), index=0, type='content_block_start')
                #     pass

                # if isinstance(event, RawContentBlockDeltaEvent):
                #     # RawContentBlockDeltaEvent(delta=TextDelta(text="I don't actually", type='text_delta'), index=0, type='content_block_delta')
                #     pass

                # if isinstance(event, InputJsonEvent):
                    # InputJsonEvent(type='input_json', partial_json='', snapshot={})
                    # InputJsonEvent(type='input_json', partial_json='{"city": "To', snapshot={})
                    # pass

                # if isinstance(event, TextEvent):
                #     # TextEvent(type='text', text="I don't actually", snapshot="I don't actually")
                #     pass

                # if isinstance(event, RawMessageDeltaEvent):
                #     # RawMessageDeltaEvent(delta=Delta(container=None, stop_reason='end_turn', stop_sequence=None), type='message_delta', usage=MessageDeltaUsage(cache_creation_input_tokens=None, cache_read_input_tokens=None, input_tokens=18, output_tokens=78, server_tool_use=None))
                #     # RawMessageDeltaEvent(delta=Delta(container=None, stop_reason='max_tokens', stop_sequence=None), type='message_delta', usage=MessageDeltaUsage(cache_creation_input_tokens=None, cache_read_input_tokens=None, input_tokens=17, output_tokens=1, server_tool_use=None))
                #     usage = event.usage
                #     input_tokens = usage.input_tokens
                #     output_tokens = usage.output_tokens
                #     print(f"\ninput_tokens: {input_tokens}, output_tokens: {output_tokens}")
                #     pass

                # if isinstance(event, ParsedContentBlockStopEvent):
                #     # ParsedContentBlockStopEvent(index=0, type='content_block_stop', content_block=ParsedTextBlock(citations=None, text="I don't actually have information about the current weather. As an AI assistant, I don't have the ability to check real-time weather data. I can only provide information based on what my training data contains. If you'd like to know the current weather, I'd suggest checking an online weather service or app that can provide real-time weather reports for your location.", type='text', parsed_output=None))
                #     pass

                # if isinstance(event, ParsedMessageStopEvent):
                #     # ParsedMessageStopEvent(type='message_stop', message=ParsedMessage(id='41c0d97007b31375546bdc52d9db1078', container=None, content=[ParsedTextBlock(citations=None, text="I don't actually have information about the current weather. As an AI assistant, I don't have the ability to check real-time weather data. I can only provide information based on what my training data contains. If you'd like to know the current weather, I'd suggest checking an online weather service or app that can provide real-time weather reports for your location.", type='text', parsed_output=None)], model='claude-3-haiku-20240307', role='assistant', stop_reason='end_turn', stop_sequence=None, type='message', usage=Usage(cache_creation=None, cache_creation_input_tokens=None, cache_read_input_tokens=None, inference_geo=None, input_tokens=18, output_tokens=78, server_tool_use=None, service_tier=None)))
                #     # ParsedMessageStopEvent(type='message_stop', message=ParsedMessage(id='e5d3148ae572d8d1e4e8a293af4f3c8e', container=None, content=[ToolUseBlock(id='toolu_bdrk_015wGcdpjumb4JRdHNnhK298', caller=None, input={'city': 'Tokyo'}, name='get_weather', type='tool_use')], model='claude-3-haiku-20240307', role='assistant', stop_reason='tool_use', stop_sequence=None, type='message', usage=Usage(cache_creation=None, cache_creation_input_tokens=None, cache_read_input_tokens=None, inference_geo=None, input_tokens=350, output_tokens=53, server_tool_use=None, service_tier=None)))
                #     pass

                #     if event.message.stop_reason == 'tool_use':

                #         for content in event.message.content:
                #             if isinstance(content, ToolUseBlock):
                #                 tool_results = execute_tool(content.name, content.input)

                #                 # 将 tool_use 事件转成符合 API 要求的 content 数组
                #                 messages.append(
                #                     {
                #                         "role": "assistant",
                #                         "content": [
                #                             {
                #                                 "type": "tool_use",
                #                                 "id": content.id,
                #                                 "name": content.name,
                #                                 "input": content.input,
                #                             }
                #                         ],
                #                     }
                #                 )

                #                 # 将工具执行结果作为 tool_result 返回给模型
                #                 messages.append(
                #                     {
                #                         "role": "user",
                #                         "content": [
                #                             {
                #                                 "type": "tool_result",
                #                                 "tool_use_id": content.id,
                #                                 "content": tool_results,
                #                             }
                #                         ],
                #                     }
                #                 )

                #                 test_create_message(client, model, system, messages)




    
    except anthropic.APIError as e:
        logger.exception(e)
        


async def test_count_token(client: AsyncAnthropic, model: str, system: str, messages: list[dict[str, str]]):
    """
    目前使用中转接口不可用，需要使用官方接口
    """
    message_tokens_count = await client.messages.count_tokens(
        model=model,
        system=system,
        messages=messages
    )
    print("message_tokens_count: ", message_tokens_count)
    input_tokens = message_tokens_count.input_tokens
    output_tokens = message_tokens_count.output_tokens
    print(f"input_tokens: {input_tokens}, output_tokens: {output_tokens}")


async def test_tool_runner(client: AsyncAnthropic, model: str, system: str, messages: list[dict[str, str]]):
    try:
        tool_runner = client.beta.messages.tool_runner(
            model=model,
            max_tokens=1024,
            tools=[get_weather],
            system=system,
            messages=messages
        )
        async for event in tool_runner:
            print("event: ", event)
        # print("tool_runner: ", tool_runner)
    except anthropic.BadRequestError as e:
        # anthropic.BadRequestError: Error code: 400 - {'error': {'message': 'invalid beta flag, trace_id: 99c5ec094be0b06c3865163714afb267', 'type': ''}}
        logger.exception(e)

async def test_list_models(client: AsyncAnthropic):
    models = await client.models.list()
    # {
    #     "id": "gpt-5.4-pro",
    #     "display_name": "gpt-5.4-pro",
    #     "created": 1772765601,
    #     "object": "model",
    #     "owned_by": "unknown",
    #     "permission": None,
    #     "root": "",
    #     "parent": "",
    #     "input_token_price_per_m": 300000,
    #     "output_token_price_per_m": 1800000,
    #     "title": "gpt-5.4-pro",
    #     "description": "",
    #     "tags": [],
    #     "context_size": 1050000,
    #     "status": 1,
    #     "model_type": "chat",
    #     "max_output_tokens": 128000,
    #     "features": ["function-calling", "reasoning", "serverless"],
    #     "endpoints": ["responses"],
    #     "input_modalities": ["text", "image"],
    #     "output_modalities": ["text"],
    # }
    for model in models.data:
        print("display_name:", model.display_name)
       
        
# 实现自动汇总的功能
async def test_auto_summarize(client: AsyncAnthropic, model: str, system: str, messages: list[dict[str, str]], max_tokens: int = 1024) -> []:
    if len(messages) < 10 or max_tokens < 1024:
        return messages
    new_messages: list[dict[str, str]] = []
    new_messages.append({'role': 'user', 'content': 'summarize the following messages: ' + '\n'.join([f"{msg['role']}: {msg['content']}" for msg in messages])})

    await test_create_message(client, model, system, new_messages)
    return new_messages

async def main():

    model = "claude-3-haiku-20240307"
    system = "You are a helpful assistant."
    messages = [{"role": "user", "content": "hi, how are you? and what's the weather in Tokyo?"}]

    async with AsyncAnthropic(
        base_url="https://api.jiekou.ai/anthropic",
        api_key="sk_EMCkI-4qXUXj2CkXG-Y6_yat65djagHfBQK0oCWhd14",
        http_client=DefaultAioHttpClient(),
    ) as client:
        pass
       
        await test_stream_output(client, model, system, messages)
        # await test_tool_runner(client, model, system, messages)
        # await test_list_models(client)
        # await test_count_token(client, model, system, messages)

        print("messages: ", messages)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    