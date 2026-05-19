from models import Base, User, Address
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session


def main():
    # 1. 创建引擎  sqlite:轻量级数据库（数据直接存储到文件中：echo=True:执行的各种DDL...语句都可以在控制台）
    engine = create_engine("sqlite:///mydb", echo=True)

    # # 2. 创建表
    # Base.metadata.create_all(engine)
    #
    # # 3. 使用上下文管理器方式使用session对象
    # with Session(engine) as session:
    #     spongebob = User(
    #         name="Mr 张",
    #         fullname="张三"
    #     )
    #
    #     sandy = User(
    #         name="sandy",
    #         fullname="Sandy Cheeks"
    #     )
    #
    #     patrick = User(name="patrick", fullname="Patrick Star")
    #
    #     session.add_all([spongebob, sandy, patrick])  # 像数据库中添加三条记录
    #
    #     session.commit()  # 不会自动提交（需要手动提交）---刷到磁盘

    with Session(engine) as session:
        # 4. 查询（定义查询语句）
        # stmt = select(User).where(User.name.in_(["Mr 张", "sandy"]))  # in
        stmt = select(User).where(User.name == 'Mr 张')  # in
        # 5. 执行查询语句(查询到多条记录)
        # for user in session.scalars(stmt):
        #     print(user)

        print(session.scalars(stmt).one())
        # print(type(session.scalars(stmt)))


if __name__ == '__main__':
    main()
