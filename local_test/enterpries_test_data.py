"""
企业入驻测试数据
Enterprise Settlement Test Data
"""

# 测试数据1
test_data_1 = {
    # 企业基本信息（对应enterprise_info表）
    "companyName": "北京科技有限公司",  # 必填
    "legalPerson": "张三",  # 可选
    "establishDate": "2020-01-15",  # 可选，日期格式 YYYY-MM-DD
    "registeredCapital": "1000.00",  # 可选，注册资本（万元）
    "applicantName": "李四",  # 可选，申请人姓名
    "licenseFile": "test_license_001.pdf",  # 必填，营业执照扫描件（实际测试时应该是文件对象）
    
    # 管理员信息（对应users和enterprise_user表）
    "adminUsername": "admin_test001",  # 必填，必须唯一（检查users、enterprise_user、contractor_user表）
    "adminPassword": "666666",  # 必填，至少6位
    "adminPhone": "14111111111",  # 必填，必须唯一（检查users、enterprise_user、contractor_user表）
    "adminEmail": "admin_test001@example.com",  # 必填，必须唯一（检查users、enterprise_user表）
    
    # 临时token（前端自动生成）
    "tempToken": "test_token_1234567890"  # 必填
}

# 测试数据2
test_data_2 = {
    # 企业基本信息（对应enterprise_info表）
    "companyName": "上海建筑工程有限公司",  # 必填
    "legalPerson": "王五",  # 可选
    "establishDate": "2018-05-20",  # 可选，日期格式 YYYY-MM-DD
    "registeredCapital": "5000.00",  # 可选，注册资本（万元）
    "applicantName": "赵六",  # 可选，申请人姓名
    "licenseFile": "test_license_002.pdf",  # 必填，营业执照扫描件（实际测试时应该是文件对象）
    
    # 管理员信息（对应users和enterprise_user表）
    "adminUsername": "admin_test002",  # 必填，必须唯一（检查users、enterprise_user、contractor_user表）
    "adminPassword": "123456",  # 必填，至少6位
    "adminPhone": "15222222222",  # 必填，必须唯一（检查users、enterprise_user、contractor_user表）
    "adminEmail": "admin_test002@example.com",  # 必填，必须唯一（检查users、enterprise_user表）
    
    # 临时token（前端自动生成）
    "tempToken": "test_token_2345678901"  # 必填
}

# 测试数据3
test_data_3 = {
    # 企业基本信息（对应enterprise_info表）
    "companyName": "深圳化工集团有限公司",  # 必填
    "legalPerson": "孙七",  # 可选
    "establishDate": "2015-03-10",  # 可选，日期格式 YYYY-MM-DD
    "registeredCapital": "8000.50",  # 可选，注册资本（万元）
    "applicantName": "周八",  # 可选，申请人姓名
    "licenseFile": "test_license_003.pdf",  # 必填，营业执照扫描件（实际测试时应该是文件对象）
    
    # 管理员信息（对应users和enterprise_user表）
    "adminUsername": "admin_test003",  # 必填，必须唯一（检查users、enterprise_user、contractor_user表）
    "adminPassword": "888888",  # 必填，至少6位
    "adminPhone": "15333333333",  # 必填，必须唯一（检查users、enterprise_user、contractor_user表）
    "adminEmail": "admin_test003@example.com",  # 必填，必须唯一（检查users、enterprise_user表）
    
    # 临时token（前端自动生成）
    "tempToken": "test_token_3456789012"  # 必填
}

# 测试数据4
test_data_4 = {
    # 企业基本信息（对应enterprise_info表）
    "companyName": "广州能源科技股份有限公司",  # 必填
    "legalPerson": "吴九",  # 可选
    "establishDate": "2019-11-25",  # 可选，日期格式 YYYY-MM-DD
    "registeredCapital": "12000.00",  # 可选，注册资本（万元）
    "applicantName": "郑十",  # 可选，申请人姓名
    "licenseFile": "test_license_004.pdf",  # 必填，营业执照扫描件（实际测试时应该是文件对象）
    
    # 管理员信息（对应users和enterprise_user表）
    "adminUsername": "admin_test004",  # 必填，必须唯一（检查users、enterprise_user、contractor_user表）
    "adminPassword": "999999",  # 必填，至少6位
    "adminPhone": "15444444444",  # 必填，必须唯一（检查users、enterprise_user、contractor_user表）
    "adminEmail": "admin_test004@example.com",  # 必填，必须唯一（检查users、enterprise_user表）
    
    # 临时token（前端自动生成）
    "tempToken": "test_token_4567890123"  # 必填
}

# 所有测试数据列表
test_data_list = [
    test_data_1,
    test_data_2,
    test_data_3,
    test_data_4
]

# 为了向后兼容，保留原来的 test_data 变量
test_data = test_data_1