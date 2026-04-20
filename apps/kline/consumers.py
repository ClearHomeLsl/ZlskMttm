# consumers.py
import json
import pandas as pd
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from utils.DBRedis import get_redis_connect  # 你的Redis连接函数
from utils.user_login_verify import login_verify_async
import asyncio


class KlineConsumer(AsyncWebsocketConsumer):
    """
    处理K线数据、历史价格、趋势通知的WebSocket
    支持订阅不同的交易对和时间周期
    """
    def __init__(self, *args, **kwargs):
        """初始化属性，确保在任何情况下都存在"""
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.username = None
        self.subscribed_rooms = set()  # 在这里初始化
        self.heartbeat_task = None

    async def connect(self):
        """客户端连接时进行认证"""
        # 从cookies或查询参数获取认证信息
        query_string = self.scope.get("query_string")
        auth_token, timeframe, symbol = query_string.decode().split("&")
        auth_token = auth_token.split("=")[1]
        timeframe = timeframe.split("=")[1]
        symbol = symbol.split("=")[1]
        room_name = f"kline_{timeframe}_{symbol}"
        is_login, jg = await login_verify_async(auth_token)

        if is_login:
            await self.close(code=4001, reason="登陆验证失败")
            return
        user = jg
        # 保存用户信息
        self.user_id = user.id
        self.username = user.username

        # 存储订阅的房间
        self.subscribed_rooms = set()
        await self.channel_layer.group_add(room_name, self.channel_name)
        # 接受连接
        await self.accept()


        # 启动心跳检测（可选）
        self.heartbeat_task = asyncio.create_task(self.send_heartbeat())

    async def disconnect(self, close_code):
        """客户端断开连接时清理资源"""
        try:
            # 设置连接状态为断开
            self._connected = False

            # 取消心跳任务 - 添加 None 检查
            if self.heartbeat_task is not None:  # 关键修改
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    print(f"取消心跳任务时出错: {e}")

            # 离开所有订阅的房间
            if hasattr(self, 'subscribed_rooms') and self.subscribed_rooms:
                for room in list(self.subscribed_rooms):
                    try:
                        if hasattr(self, 'channel_layer') and self.channel_layer:
                            await self.channel_layer.group_discard(room, self.channel_name)
                    except Exception as e:
                        print(f"离开房间 {room} 时出错: {e}")

                self.subscribed_rooms.clear()

        except Exception as e:
            print(f"disconnect方法执行出错: {e}")

    async def receive(self, text_data):
        """接收客户端消息（订阅/取消订阅请求）"""
        try:
            data = json.loads(text_data)
            action = data.get('action')  # subscribe, unsubscribe, get_old_price
            symbol = data.get('symbol')
            timeframe = data.get('timeframe', '1m')

            if not symbol:
                await self.send_error("缺少交易对参数(symbol)")
                return

            if action == 'subscribe':
                await self.handle_subscribe(symbol, timeframe)
            elif action == 'unsubscribe':
                await self.handle_unsubscribe(symbol, timeframe)
            elif action == 'get_old_price':
                await self.send_old_price(symbol)
            else:
                await self.send_error(f"未知操作: {action}")

        except json.JSONDecodeError:
            await self.send_error("无效的JSON格式")
        except Exception as e:
            await self.send_error(f"处理消息时出错: {str(e)}")

    async def handle_subscribe(self, symbol, timeframe):
        """处理订阅K线数据"""
        room_name = f"kline_{timeframe}_{symbol}"

        if room_name not in self.subscribed_rooms:
            # 加入房间组
            await self.channel_layer.group_add(room_name, self.channel_name)
            self.subscribed_rooms.add(room_name)

            # 立即发送当前K线数据
            current_data = await self.get_current_kline_data(symbol, timeframe)
            if current_data:
                await self.send(text_data=json.dumps({
                    "type": "kline_data",
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "data": current_data
                }))

            # 发送订阅成功确认
            await self.send(text_data=json.dumps({
                "type": "subscribe_success",
                "symbol": symbol,
                "timeframe": timeframe,
                "message": f"已订阅 {symbol} {timeframe} K线数据"
            }))

            # 可选：开始推送趋势通知
            await self.start_trend_notifications(symbol, timeframe)

    async def handle_unsubscribe(self, symbol, timeframe):
        """取消订阅"""
        room_name = f"kline_{timeframe}_{symbol}"

        if room_name in self.subscribed_rooms:
            await self.channel_layer.group_discard(room_name, self.channel_name)
            self.subscribed_rooms.remove(room_name)

            await self.send(text_data=json.dumps({
                "type": "unsubscribe_success",
                "symbol": symbol,
                "timeframe": timeframe,
                "message": f"已取消订阅 {symbol} {timeframe} K线数据"
            }))

    async def send_old_price(self, symbol):
        """发送历史价格"""
        old_price = await self.get_old_price(symbol)
        await self.send(text_data=json.dumps({
            "type": "old_price",
            "symbol": symbol,
            "old_price": old_price
        }))

    async def start_trend_notifications(self, symbol, timeframe):
        """启动趋势通知推送"""
        room_name = f"trend_{timeframe}_{symbol}"
        await self.channel_layer.group_add(room_name, self.channel_name)
        self.subscribed_rooms.add(room_name)

        # 发送最近的趋势变化
        trends = await self.get_recent_trends(symbol, timeframe)
        if trends:
            await self.send(text_data=json.dumps({
                "type": "trend_notifications",
                "symbol": symbol,
                "timeframe": timeframe,
                "data": trends
            }))

    # ========== 数据获取方法（同步转异步） ==========

    @database_sync_to_async
    def verify_token(self, auth_token):
        """验证token（如果token存储在数据库）"""
        # 这里简化处理，实际应该查数据库验证
        try:
            _, user_id, username = auth_token.split('_')
            r = get_redis_connect()
            if r.get(username):
                return True, user_id, username
        except:
            pass
        return False, None, None

    @database_sync_to_async
    def get_current_kline_data(self, symbol, timeframe):
        """获取当前K线数据"""
        try:
            r = get_redis_connect()
            key = f"{timeframe}_{symbol}_price"
            data = r.get(key)
            if data:
                data = json.loads(data)
                # 更新最新价格
                now_price = r.get(f"{symbol}_now_price")
                if now_price and data:
                    data[-1]["close"] = now_price
                return data
        except Exception as e:
            print(f"获取K线数据失败: {e}")
        return None

    @database_sync_to_async
    def get_old_price(self, symbol):
        """获取历史价格"""
        try:
            r = get_redis_connect()
            key = f"h1_{symbol}_price"
            data = r.get(key)
            if data:
                data = json.loads(data)
                df = pd.DataFrame(data)
                df["date"] = df["time"].astype("str").str[:10]
                old_price = df.groupby("date").last().iloc[-2]["close"].astype("str")
                return old_price
        except Exception as e:
            print(f"获取历史价格失败: {e}")
        return None

    @database_sync_to_async
    def get_recent_trends(self, symbol, timeframe):
        """获取最近的趋势变化"""
        try:
            r = get_redis_connect()
            key = f'{timeframe}_trend_change'
            trends = r.lrange(key, -20, -1)  # 获取最后20条
            return [json.loads(t) for t in trends]
        except Exception as e:
            print(f"获取趋势数据失败: {e}")
        return []

    async def send_heartbeat(self):
        """发送心跳包保持连接"""

        while True:
            try:
                await asyncio.sleep(30)
                await self.send(text_data=json.dumps({"type": "heartbeat", "timestamp": time.time()}))
            except:
                break

    async def send_error(self, message):
        """发送错误消息"""
        await self.send(text_data=json.dumps({
            "type": "error",
            "msg": message,
            "code": "1004",
            "response_type": "error"
        }))

    # ========== 群组消息处理方法 ==========

    async def kline_update(self, event):
        """接收K线更新消息（由外部系统触发）"""
        await self.send(text_data=json.dumps({
            "type": "kline_update",
            "symbol": event['symbol'],
            "timeframe": event['timeframe'],
            "sap_data": event['sap_data'],
            "data": event['data']
        }))

    async def trend_change(self, event):
        """接收趋势变化消息"""
        await self.send(text_data=json.dumps({
            "type": "trend_change",
            "symbol": event['symbol'],
            "timeframe": event['timeframe'],
            "sap_data": event['sap_data'],
            "data": event['data']
        }))