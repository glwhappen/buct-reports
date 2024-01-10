import json
import os
import yaml # pyyaml
from loguru import logger


# ConfigManager.py
# 该模块定义了ConfigManager类，用于管理和操作YAML格式的配置文件。
# 主要功能包括：创建配置文件、读取配置、获取和更新配置参数。
# 这对于管理应用程序设置和参数非常有用，特别是在实验和开发环境中。

def find_project_root(current_dir):
    """
    向上搜索直到找到标识文件，确定项目的根目录
    """
    # 检查当前目录是否包含标识文件
    if os.path.isfile(os.path.join(current_dir, '.projectroot')):
        return current_dir
    # 获取上一级目录
    parent_dir = os.path.dirname(current_dir)
    if parent_dir == current_dir:
        # 已经到达了文件系统的根目录
        raise FileNotFoundError("无法找到项目根目录标识文件, 请在项目根目录下创建 .projectroot 文件.")
    # 递归继续向上搜索
    return find_project_root(parent_dir)

class ConfigManager:
    """
    ConfigManager 类用于管理YAML配置文件。
    它允许加载、获取、更新配置文件中的参数。
    """

    def __init__(self, config_name = 'config.yml'):
        """
        初始化ConfigManager实例。

        :param config_path: 配置文件的路径。
        """

        # 当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)

        # 项目根目录的路径
        project_root = find_project_root(os.path.dirname(current_file_path))

        # 构建config.yml的路径
        config_path = os.path.join(project_root, config_name)

        self.config_path = config_path
        # 检查文件是否存在，如果不存在则创建一个空文件
        if not os.path.exists(self.config_path):
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump({}, file)
        self.config = self._load_config()

    def _load_config(self):
        """
        加载YAML配置文件。
        如果文件不存在或无法解析，则抛出相应的异常。正常情况下会自动创建配置文件

        :return: 返回配置文件的内容。
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file {self.config_path} not found.")
        except yaml.YAMLError as exc:
            raise RuntimeError(f"Error while parsing YAML file: {exc}")

    def get_param(self, section, key, default=None):
        """
        获取配置文件中的参数值。

        :param section: 配置文件中的部分（如'experiment'）。
        :param key: 部分中的键。
        :param default: 如果键不存在，则返回的默认值。
        :return: 返回键对应的值，如果不存在则返回默认值。
        """
        # 构建环境变量的名称
        env_var = f"config_{section}_{key}"

        # 检查环境变量是否存在
        if env_var in os.environ:
            env_value = os.environ[env_var]
            # 尝试解析JSON格式的字符串
            if env_value.startswith('[') or env_value.startswith('{'):
                try:
                    logger.debug(f"get_param from env json {env_var} {env_value}")
                    return json.loads(env_value)
                except json.JSONDecodeError:
                    pass  # 如果不是有效的JSON，保持原样返回
            logger.debug(f"get_param from env {env_var} {env_value}")
            return env_value  # 直接返回环境变量的值

        if section in self.config and key in self.config[section]:
            logger.debug(f"get_param from section={section} key={key} value={self.config[section][key]}")
            return self.config[section][key]
        else:
            if default is not None:
                self.update_param(section, key, default)
                logger.debug(f"get_param update section={section} key={key} value={default}")
                return default
            else:
                raise KeyError(f"Param '{key}' not found in section '{section}', and no default value provided.")

    def update_param(self, section, key, value):
        """
        更新配置文件中的参数。

        :param section: 配置文件中的部分。
        :param key: 部分中的键。
        :param value: 要更新的值。
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        logger.debug(f"update_param section={section} key={key} value={value}")
        with open(self.config_path, 'w', encoding='utf-8') as file:
            yaml.dump(self.config, file, allow_unicode=True, default_flow_style=False)

if __name__ == '__main__':

    # 使用示例
    config_manager = ConfigManager("../config.yml")
    config_manager._load_config()
    learning_rate = config_manager.get_param('experiment', 'learning_rate', 0.1)
    print(f"Learning Rate: {learning_rate}")

    # 更新参数示例
    config_manager.update_param('experiment', 'learning_rate', 0.02)
