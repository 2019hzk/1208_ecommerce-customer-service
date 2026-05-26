import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert  # 小小
from atguigu.domain.state import DialogueState
from atguigu.model.dialogue_state_record import DialogueStateRecord


class DialogueStateRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def load(self, sender_id: str) -> DialogueState:
        """
        读操作
        :return:
        """

        # 1. 定义sql
        sql = select(DialogueStateRecord).where(DialogueStateRecord.sender_id == sender_id)

        # 2. 执行sql
        result = await self.session.execute(sql)

        # 3. 获取结果
        sate = result.scalar_one_or_none()

        if sate:
            state_dict = json.loads(sate.state_json)
            return DialogueState.from_dict(state_dict)

        return DialogueState(sender_id=sender_id)

    async def save(self, dialogue_state: DialogueState):
        """
        写操作(插入、修改)
        传统：插入之前先查询该条件（sender_id）对应的记录是否存在，如果不存在 则插入，反之修改
        进阶：负责将插入sql直接升级为修改sql(主键重复机制判断)
        :return:
        """

        # 1. 得到DialogueState的json字符串
        state_json: str = json.dumps(dialogue_state.to_dict(), ensure_ascii=False)

        # 2. 定义插入的sql语句
        insert_stmt = insert(DialogueStateRecord).values(
            sender_id=dialogue_state.sender_id, state_json=state_json
        )

        # 3. 升级update语句的sql
        update_stmt = insert_stmt.on_duplicate_key_update(
            state_json=insert_stmt.inserted.state_json
        )

        # 4. 执行sql
        await  self.session.execute(update_stmt)

        # 5. 提交
        await self.session.commit()
