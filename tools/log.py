import functools
import inspect
import os

from loguru import logger
import time

# 定义装饰器以监控函数执行时间
# def monitor_function(func):
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         logger.debug(f"{func.__name__} ran in {end_time - start_time:.2f} seconds")
#         return result
#     return wrapper
logger.level("CALLING", no=11, color="<black>")
logger.level("PRINT", no=21, color="<black>")
def monitor_function2(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        logger.opt(depth=1).log("PRINT", f"{func.__name__}({signature})")
        try:
            value = func(*args, **kwargs)
            logger.opt(depth=1).log("PRINT", f"{func.__name__} returned {value!r}")
            return value
        except Exception as e:
            logger.opt(depth=1).exception(f"Error in {func.__name__}: {e}")
            raise

    return wrapper

def monitor_function3(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 获取函数的参数名
        func_args = func.__code__.co_varnames[:func.__code__.co_argcount]
        args_dict = dict(zip(func_args, args))
        args_dict.update(kwargs)  # 合并位置参数和关键字参数

        # 构建参数表示字符串
        args_repr = [f"{key}={value!r}" for key, value in args_dict.items()]
        signature = ", ".join(args_repr)
        logger.opt(depth=1).debug(f"Calling {func.__name__} with args: {signature}")

        # 执行函数并捕获结果或异常
        try:
            value = func(*args, **kwargs)
            logger.opt(depth=1).debug(f"{func.__name__} returned {value!r}")
            return value
        except Exception as e:
            logger.opt(depth=1).exception(f"Error in {func.__name__}: {e}")
            raise

    return wrapper



def format_arg_value(value):
    """ 格式化参数值，对于长字符串或长列表进行截断处理 """
    MAX_LENGTH = 300  # 最大长度
    MAX_ITEMS = 20    # 列表或元组中显示的最大项数

    if isinstance(value, str) and len(value) > MAX_LENGTH:
        return repr(value[:MAX_LENGTH] + "...")  # 截断长字符串
    elif isinstance(value, (list, tuple)) and len(value) > MAX_ITEMS:
        return repr(value[:MAX_ITEMS] + ["..."])  # 截断长列表或元组
    else:
        return repr(value)

def monitor_function(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 获取函数所在的文件名
        filename = os.path.basename(inspect.getfile(func))
        # 获取函数的参数名
        func_args = func.__code__.co_varnames[:func.__code__.co_argcount]
        args_dict = dict(zip(func_args, args))
        args_dict.update(kwargs)  # 合并位置参数和关键字参数
        # INDENT = '2024-01-09 23:53:17.005 | DEBUG    | __main__:<module>:81'
        INDENT = " " * 65
        # 格式化参数表示字符串
        args_repr = [f"{key}={format_arg_value(value)}" for key, value in args_dict.items()]
        signature = f", \n{INDENT}".join(args_repr)
        logger.opt(depth=1).log("CALLING", f"Calling {func.__name__} in {filename} with args: \n{INDENT}{signature}")

        # 执行函数并捕获结果或异常
        try:
            start_time = time.time()
            value = func(*args, **kwargs)
            end_time = time.time()
            logger.opt(depth=1).log("CALLING", f"Returned {end_time - start_time:.1f} seconds {func.__name__} in {filename}  {format_arg_value(value)}")
            return value
        except Exception as e:
            logger.opt(depth=1).exception(f"Error in {func.__name__}: {e}")
            raise

    return wrapper

def log_print(*args, **kwargs):
    """
    使用方法 print = log_print
    :param args:
    :param kwargs:
    :return:
    """
    # Define a custom format
    custom_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

    log_message = " ".join(str(arg) for arg in args)
    # 调整depth值以指向正确的调用位置
    logger.opt(depth=1).log("PRINT", log_message)

original_print = print  # Save the original print function
def enable_log_print(print):
    print = log_print  # Override the built-in print

def disable_log_print(print):
    print = original_print  # Restore the original print


# # 使用装饰器
# @monitor_function
# def some_function():
#     time.sleep(2)
#
# # 调用函数
# some_function()
