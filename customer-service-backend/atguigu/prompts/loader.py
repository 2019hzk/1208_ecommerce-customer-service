"""
jinja2:模版引擎（计算逻辑和表现分开）



"""

from pathlib import Path


def load_prompt(prompt_file_name: str) -> str:
    """
    根据任务类型的提示词文件名字 读取对应文件的内容
    :param prompt_file_name:
    :return:
    """
    prompt_file_path = Path(__file__).resolve().parents[0] / "jinja2" / f"{prompt_file_name}.jinja2"

    return prompt_file_path.read_text(encoding="utf-8")



if __name__ == '__main__':
    print(load_prompt("turn_plan"))
