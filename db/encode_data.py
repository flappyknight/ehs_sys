"""
数据编解码模块
用于处理作业申请票中的多选项字段的二进制编码和解码
注意：特殊作业相关的编解码函数已移除，现在使用独立表存储
"""

from typing import List, Dict

# 主要工具选项
TOOLS_OPTIONS = [
    "电焊机",
    "氩弧焊机", 
    "氧乙炔气割",
    "切割机",
    "角磨机",
    "砂轮机",
    "扳手",
    "螺丝刀",
    "钳子",
    "电钻",
    "手动葫芦",
    "电动葫芦",
    "吊车",
    "其他"
]

# 危险识别选项
DANGER_OPTIONS = [
    "易燃易爆",
    "有毒有害",
    "惰性气体",
    "高压气体/液体",
    "粉尘",
    "腐蚀",
    "放射",
    "泄漏环境",
    "明火/电弧",
    "火花",
    "静电",
    "触电",
    "高/低温",
    "噪声",
    "受限空间",
    "人员坠落",
    "坠物",
    "坍塌",
    "绊倒滑倒",
    "机械伤害",
    "车辆伤害",
    "照明不良",
    "不利天气",
    "其他"
]

# 防护措施选项
PROTECTION_OPTIONS = [
    "安全帽",
    "护目镜",
    "防护面屏",
    "防弧面罩",
    "防毒面罩",
    "半面罩",
    "活性炭口罩",
    "耳塞/耳罩",
    "空呼器",
    "长管呼吸器",
    "防护手套",
    "安全鞋",
    "绝缘鞋",
    "绝缘手套",
    "安全绳/带",
    "反光背心",
    "防静电工作服",
    "其他"
]

# 动火等级选项（新增）
HOT_WORK_LEVELS = {
    -1: "未动火",
    0: "特级动火",
    1: "一级动火", 
    2: "二级动火"
}

# 受限空间等级选项（新增）
CONFINED_SPACE_LEVELS = {
    1: "一级",
    2: "二级"
}

# 作业高度等级选项（新增）
WORK_HEIGHT_LEVELS = {
    0: "0级（最低风险）",
    1: "1级",
    2: "2级", 
    3: "3级",
    4: "4级（最高风险）"
}

def encode_options(selected_options: List[str], all_options: List[str]) -> int:
    """
    将选中的选项编码为十进制数
    
    Args:
        selected_options: 选中的选项列表
        all_options: 所有可选项列表
    
    Returns:
        编码后的十进制数
    """
    if not selected_options:
        return 0
    
    binary_str = ""
    for option in all_options:
        if option in selected_options:
            binary_str += "1"
        else:
            binary_str += "0"
    
    # 将二进制字符串转换为十进制
    return int(binary_str, 2) if binary_str else 0

def decode_options(encoded_value: int, all_options: List[str]) -> List[str]:
    """
    将十进制数解码为选中的选项列表
    
    Args:
        encoded_value: 编码的十进制数
        all_options: 所有可选项列表
    
    Returns:
        选中的选项列表
    """
    if encoded_value == 0:
        return []
    
    # 将十进制转换为二进制字符串
    binary_str = bin(encoded_value)[2:]  # 去掉 '0b' 前缀
    
    # 补齐长度，确保与选项数量一致
    binary_str = binary_str.zfill(len(all_options))
    
    selected_options = []
    for i, bit in enumerate(binary_str):
        if bit == "1" and i < len(all_options):
            selected_options.append(all_options[i])
    
    return selected_options

# 工具相关的编解码函数
def encode_tools(selected_tools: List[str]) -> int:
    """编码主要工具"""
    return encode_options(selected_tools, TOOLS_OPTIONS)

def decode_tools(encoded_value: int) -> List[str]:
    """解码主要工具"""
    return decode_options(encoded_value, TOOLS_OPTIONS)

# 危险识别相关的编解码函数
def encode_danger(selected_dangers: List[str]) -> int:
    """编码危险识别"""
    return encode_options(selected_dangers, DANGER_OPTIONS)

def decode_danger(encoded_value: int) -> List[str]:
    """解码危险识别"""
    return decode_options(encoded_value, DANGER_OPTIONS)

# 防护措施相关的编解码函数
def encode_protection(selected_protections: List[str]) -> int:
    """编码防护措施"""
    return encode_options(selected_protections, PROTECTION_OPTIONS)

def decode_protection(encoded_value: int) -> List[str]:
    """解码防护措施"""
    return decode_options(encoded_value, PROTECTION_OPTIONS)

# 获取所有选项的函数，用于前端展示
def get_all_tools_options() -> List[str]:
    """获取所有工具选项"""
    return TOOLS_OPTIONS.copy()

def get_all_danger_options() -> List[str]:
    """获取所有危险识别选项"""
    return DANGER_OPTIONS.copy()

def get_all_protection_options() -> List[str]:
    """获取所有防护措施选项"""
    return PROTECTION_OPTIONS.copy()

# 新增：获取动火等级选项
def get_hot_work_levels() -> Dict[int, str]:
    """获取动火等级选项"""
    return HOT_WORK_LEVELS.copy()

def get_hot_work_level_name(level: int) -> str:
    """根据等级获取动火等级名称"""
    return HOT_WORK_LEVELS.get(level, "未知等级")

# 新增：获取受限空间等级选项
def get_confined_space_levels() -> Dict[int, str]:
    """获取受限空间等级选项"""
    return CONFINED_SPACE_LEVELS.copy()

def get_confined_space_level_name(level: int) -> str:
    """根据等级获取受限空间等级名称"""
    return CONFINED_SPACE_LEVELS.get(level, "未知等级")

# 新增：获取作业高度等级选项
def get_work_height_levels() -> Dict[int, str]:
    """获取作业高度等级选项"""
    return WORK_HEIGHT_LEVELS.copy()

def get_work_height_level_name(level: int) -> str:
    """根据等级获取作业高度等级名称"""
    return WORK_HEIGHT_LEVELS.get(level, "未知等级")

# 获取选项索引的函数，用于调试
def get_options_info() -> Dict[str, Dict[str, int]]:
    """获取所有选项的索引信息，用于调试"""
    return {
        "tools": {option: i for i, option in enumerate(TOOLS_OPTIONS)},
        "danger": {option: i for i, option in enumerate(DANGER_OPTIONS)},
        "protection": {option: i for i, option in enumerate(PROTECTION_OPTIONS)},
        "hot_work_levels": HOT_WORK_LEVELS,
        "confined_space_levels": CONFINED_SPACE_LEVELS,
        "work_height_levels": WORK_HEIGHT_LEVELS
    }