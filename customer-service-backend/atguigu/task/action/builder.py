import importlib
import inspect
import pkgutil
from atguigu.task.action.runner import ActionRunner
from atguigu.task.action.registry import ActionRegistry
from atguigu.task.action.base import Action
from atguigu.task.action.builtin.listener import ActionListener
from atguigu.task.action.builtin.response import ActionResponse


def register_builtin_action(action_runner: ActionRunner):
    action_listener = ActionListener()
    action_response = ActionResponse()
    action_runner.registry.register(action_listener)
    action_runner.registry.register(action_response)


def register_customer_action(action_runner: ActionRunner):
    """
    自动扫描自定义action的包 然后完整action的注册
    :param action_runner:
    :return:
    """

    package = importlib.import_module("atguigu.task.action.customer")

    for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__, prefix=f"{package.__name__}."):

        if is_pkg:
            continue
        module = importlib.import_module(module_name)
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if not issubclass(obj, Action) or obj is Action:
                continue
            if obj.__module__ != module.__name__:
                continue
            action_runner.registry.register(obj())


def build_action_runner() -> ActionRunner:
    action_runner = ActionRunner(ActionRegistry())
    register_builtin_action(action_runner)
    register_customer_action(action_runner)
    return action_runner


if __name__ == '__main__':

     build_action_runner()