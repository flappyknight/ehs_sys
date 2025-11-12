"""
企业入驻测试数据
"""

test_data = {
    # 企业基本信息
    "companyName": "北京科技有限公司",
    "legalPerson": "张三",
    "contactPhone": "13800138000",
    "address": "北京市朝阳区科技园区创新大厦A座1001室",
    "industryType": "manufacturing",  # 可选值: manufacturing, construction, chemical, energy, other
    "employeeCount": "201-500",  # 可选值: 1-50, 51-200, 201-500, 501-1000, 1000+
    "businessLicense": "91110000MA01234567",
    
    # 联系人信息
    "contactName": "李四",
    "contactPosition": "市场部经理",
    "contactEmail": "lisi@example.com",
    "remarks": "这是一家专注于智能制造的高科技企业，希望尽快完成入驻审核。",
    
    # 管理员信息
    "adminUsername": "admin_test001",
    "adminPassword": "666666",  # 至少6位
    "adminPhone": "14111111111",  # 必须唯一
    "adminEmail": "admin@example.com",
    
    # 临时token（前端自动生成）
    "tempToken": "test_token_1234567890"
}