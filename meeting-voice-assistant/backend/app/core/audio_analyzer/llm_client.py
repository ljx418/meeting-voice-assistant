"""
LLM 客户端

支持 MiniMax（主用）和 DeepSeek（备用）
- 自动检测 MiniMax 失败或超时
- 无缝切换到 DeepSeek
"""

import logging
from typing import Optional
from langchain.chat_models.base import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from app.config import config

logger = logging.getLogger("audio_analyzer.llm_client")


class MiniMaxChatModel(BaseChatModel):
    """MiniMax Chat Model 封装"""

    model_name: str = "MiniMax-M2.7"
    api_key: str = ""
    endpoint: str = "https://api.minimax.chat/v1"
    temperature: float = 0.7
    max_tokens: int = 8192
    timeout: int = 120  # 超时时间（秒），默认使用 LLM 超时配置

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: Optional[list[str]] = None,
        **kwargs
    ):
        """生成响应 - 返回 ChatResult 格式"""
        from langchain_core.outputs import ChatGeneration, ChatResult

        import aiohttp
        import asyncio
        import threading

        # 获取超时配置
        llm_timeout = 120
        try:
            from app.config import config
            if hasattr(config, 'timeout') and config.timeout.llm_timeout:
                llm_timeout = int(config.timeout.llm_timeout)
        except Exception:
            pass

        # 用于在线程中运行的异步代码
        result_holder = [None]  # [error or result]
        done_event = threading.Event()

        async def _agenerate() -> str:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            # 转换消息格式
            formatted_messages = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    formatted_messages.append({
                        "role": "user",
                        "content": msg.content
                    })
                elif isinstance(msg, BaseMessage) and hasattr(msg, "content"):
                    formatted_messages.append({
                        "role": "user",
                        "content": msg.content
                    })

            payload = {
                "model": self.model_name,
                "messages": formatted_messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.endpoint}/text/chatcompletion_v2",
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=llm_timeout)
                    ) as resp:
                        if resp.status != 200:
                            error_text = await resp.text()
                            raise Exception(f"MiniMax API error: {resp.status} - {error_text}")

                        result = await resp.json()
                        # 验证响应结构
                        if not result or "choices" not in result or not result["choices"]:
                            raise Exception(f"MiniMax API invalid response: {result}")
                        return result["choices"][0]["message"]["content"]

            except asyncio.TimeoutError:
                raise Exception(f"MiniMax timeout after {llm_timeout}s")
            except aiohttp.ClientError as e:
                raise Exception(f"MiniMax connection error: {e}")
            except Exception as e:
                raise Exception(f"MiniMax error: {e}")

        def run_in_thread():
            """在线程中运行异步代码"""
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(_agenerate())
                result_holder[0] = result
            except Exception as e:
                result_holder[0] = e
            finally:
                done_event.set()

        # 在单独线程中运行异步代码
        thread = threading.Thread(target=run_in_thread)
        thread.daemon = True
        thread.start()

        # 等待结果，带超时（额外 10 秒缓冲）
        if done_event.wait(timeout=llm_timeout + 10):
            if isinstance(result_holder[0], Exception):
                raise result_holder[0]
            # 返回 ChatResult 格式（langchain 期望的格式）
            content = result_holder[0]
            generation = ChatGeneration(message=AIMessage(content=content))
            return ChatResult(generations=[generation])
        else:
            raise Exception(f"MiniMax timeout after {llm_timeout + 10}s")

    @property
    def _llm_type(self) -> str:
        return "minimax"


class LLMClient:
    """LLM 客户端，支持 MiniMax 主用 + DeepSeek 备用自动切换"""

    def __init__(self, llm_config=None):
        # llm_config 兼容旧接口，优先使用传入的配置，否则使用统一配置
        self._llm_config = llm_config or config.llm
        self._primary_model: Optional[BaseChatModel] = None
        self._backup_model: Optional[BaseChatModel] = None
        self._init_models()

    def _init_models(self):
        """初始化模型"""
        # 获取超时配置
        llm_timeout = 120
        try:
            from app.config import config
            if hasattr(config, 'timeout') and config.timeout.llm_timeout:
                llm_timeout = int(config.timeout.llm_timeout)
        except Exception:
            pass

        # MiniMax
        if self._llm_config.minimax_api_key:
            try:
                self._primary_model = MiniMaxChatModel(
                    model_name=self._llm_config.minimax_model,
                    api_key=self._llm_config.minimax_api_key,
                    endpoint=self._llm_config.minimax_endpoint or "https://api.minimax.chat/v1",
                    timeout=llm_timeout,
                )
                logger.info(f"[LLMClient] Primary: MiniMax ({self._llm_config.minimax_model})")
            except Exception as e:
                logger.warning(f"[LLMClient] Failed to init MiniMax: {e}")

        # DeepSeek 备用
        if self._llm_config.deepseek_api_key:
            try:
                self._backup_model = ChatOpenAI(
                    model=self._llm_config.deepseek_model,
                    api_key=self._llm_config.deepseek_api_key,
                    base_url=self._llm_config.deepseek_endpoint or "https://api.deepseek.com",
                    timeout=llm_timeout,
                )
                logger.info(f"[LLMClient] Backup: DeepSeek ({self._llm_config.deepseek_model})")
            except Exception as e:
                logger.warning(f"[LLMClient] Failed to init DeepSeek: {e}")

        if self._primary_model is None and self._backup_model is None:
            raise ValueError("No LLM provider configured. Set MINIMAX_API_KEY and/or DEEPSEEK_API_KEY")

    def invoke(self, prompt: str, use_backup: bool = False) -> str:
        """调用 LLM，失败时自动切换备用模型"""

        if use_backup:
            model = self._backup_model
            model_name = "DeepSeek"
        else:
            model = self._primary_model
            model_name = "MiniMax"

        if model is None:
            if not use_backup and self._backup_model:
                logger.info("[LLMClient] Primary unavailable, switching to DeepSeek")
                return self.invoke(prompt, use_backup=True)
            raise ValueError("No LLM model available")

        try:
            logger.info(f"[LLMClient] Invoking {model_name}")
            response = model.invoke([HumanMessage(content=prompt)])

            if hasattr(response, "content"):
                return response.content
            return str(response)

        except Exception as e:
            logger.error(f"[LLMClient] {model_name} error: {e}")

            # 自动切换到备用模型
            if not use_backup and self._backup_model:
                logger.info("[LLMClient] Falling back to DeepSeek")
                return self.invoke(prompt, use_backup=True)

            raise

    async def ainvoke(self, prompt: str, use_backup: bool = False) -> str:
        """异步调用 LLM"""
        return self.invoke(prompt, use_backup)
