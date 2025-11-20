-- ============================================
-- EHS系统数据库建表语句
-- 数据库名: ehs
-- ============================================
-- 数据库连接信息:
-- 主机: 127.0.0.1
-- 端口: 5432
-- 数据库名: ehs
-- 用户名: postgres
-- 密码: postgres
-- ============================================

-- 连接到数据库
\c ehs;

-- ============================================
-- 用户相关表
-- ============================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('enterprise', 'contractor', 'admin')),
    enterprise_staff_id INTEGER,
    contractor_staff_id INTEGER,
    phone VARCHAR(20),
    email VARCHAR(100),
    user_level INTEGER,
    audit_status INTEGER,
    temp_token VARCHAR(500),
    relay_name VARCHAR(100),
    sys_only_id BIGINT UNIQUE,
    name_str VARCHAR(100),
    role_type VARCHAR(100),
    role_level INTEGER,
    user_status INTEGER,
    work_type VARCHAR(100) NOT NULL DEFAULT '',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 值得注意的是： 在创建系统的时候给的初始的 admin 用户是系统管理员用户，user_level 为 0， user_status 为 1， role_level 为 0， role_type 为 'system'

-- user_level(即将废弃): -1 还有没有通过审核， 0 系统最高管理员, 1 企业管理员, 2 企业员工, 3 承包商管理员，4 承包商员工
-- audit_status: 1 还未提交审核， 2 审核通过， 3 待审核， 4 审核不通过 
-- name_str: 姓名
-- role_type: 角色类型, system 系统管理员, admin_enterprise 企业管理员, admin_contractor 承包商管理员, common_enterprise 企业员工, common_contractor 承包商员工
-- role_level: -1 用户还未选择角色 角色等级 0 系统管理员，1 企业管理员，2 企业员工，3 承包商管理员，4 承包商员工
-- user_status: 用户状态 0 未通过审核(废弃)，1 通过审核，2 待审核，3 审核不通过
-- work_type: 工种，默认空字符串
-- is_deleted: 假删除标记，false表示未删除，true表示已删除，默认false

-- ============================================
-- 企业和承包商信息表
-- ============================================

-- 企业信息表
CREATE TABLE IF NOT EXISTS enterprise_info (
    enterprise_id SERIAL PRIMARY KEY,
    license_file VARCHAR(255) NOT NULL,
    license_number VARCHAR(100),
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(100),
    company_address VARCHAR(255),
    legal_person VARCHAR(100),
    establish_date DATE,
    registered_capital NUMERIC(15, 2),
    applicant_name VARCHAR(100),
    business_status VARCHAR(50) NOT NULL DEFAULT '续存',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    parent_enterprise_id INTEGER,
    subsidiary_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_contractor_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    candidate_contractor_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    contractor_detail_info JSONB NOT NULL DEFAULT '{}'::jsonb,
    modification_log JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_parent_enterprise FOREIGN KEY (parent_enterprise_id) REFERENCES enterprise_info(enterprise_id) ON DELETE SET NULL
);

-- business_status: 续存，待审核，审核不通过，已注销
-- allowed_contractor_ids: 允许合作的承包商ID数组
-- candidate_contractor_ids: 候选承包商ID数组


-- 承包商信息表
CREATE TABLE IF NOT EXISTS contractor_info (
    contractor_id SERIAL PRIMARY KEY,
    license_file VARCHAR(255) NOT NULL,
    license_number VARCHAR(100),
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(100),
    company_address VARCHAR(255),
    legal_person VARCHAR(100),
    establish_date DATE,
    registered_capital NUMERIC(15, 2),
    applicant_name VARCHAR(100),
    business_status VARCHAR(50) NOT NULL DEFAULT '续存',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    active_enterprise_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    inactive_enterprise_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    pending_allowed_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    active_enterprise_detail JSONB NOT NULL DEFAULT '{}'::jsonb,
    cooperation_detail_log JSONB NOT NULL DEFAULT '[]'::jsonb,
    modification_log JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- business_status: 续存，待审核，审核不通过，已注销
-- active_enterprise_ids: 活跃合作企业ID数组
-- pending_allowed_ids: 待审核合作企业ID数组
-- active_enterprise_detail: 活跃合作企业详细信息
-- inactive_enterprise_ids: 已失效合作企业ID数组
-- cooperation_detail_log: 合作详情日志
-- modification_log: 修改记录日志

-- ============================================
-- 项目相关表
-- ============================================

-- 承包商项目表
CREATE TABLE IF NOT EXISTS contractor_project (
    project_id SERIAL PRIMARY KEY,
    contractor_id INTEGER NOT NULL,
    enterprise_id INTEGER NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    leader_name_str VARCHAR(100) NOT NULL,
    leader_phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 作业票表
-- ============================================

-- 作业票表
CREATE TABLE IF NOT EXISTS ticket (
    ticket_id SERIAL PRIMARY KEY,
    apply_date DATE NOT NULL,
    applicant INTEGER NOT NULL,
    area_id INTEGER,
    working_content VARCHAR(1024) NOT NULL,
    pre_st TIMESTAMP NOT NULL,
    pre_et TIMESTAMP NOT NULL,
    tools INTEGER NOT NULL DEFAULT 0,
    worker INTEGER NOT NULL,
    custodians INTEGER NOT NULL,
    danger INTEGER NOT NULL DEFAULT 0,
    protection INTEGER NOT NULL DEFAULT 0,
    hot_work INTEGER NOT NULL DEFAULT -1,
    work_height_level INTEGER NOT NULL DEFAULT 0,
    confined_space_id INTEGER,
    temp_power_id INTEGER,
    cross_work_group_id VARCHAR(50),
    signature VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ticket_applicant FOREIGN KEY (applicant) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_worker FOREIGN KEY (worker) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_custodian FOREIGN KEY (custodians) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================
-- 外键约束
-- ============================================

-- ============================================
-- 索引
-- ============================================

-- 用户表索引
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);

-- 企业信息表索引
CREATE INDEX IF NOT EXISTS idx_enterprise_company_name ON enterprise_info(company_name);
CREATE INDEX IF NOT EXISTS idx_enterprise_business_status ON enterprise_info(business_status);
CREATE INDEX IF NOT EXISTS idx_enterprise_is_deleted ON enterprise_info(is_deleted);
CREATE INDEX IF NOT EXISTS idx_enterprise_parent_id ON enterprise_info(parent_enterprise_id);
CREATE INDEX IF NOT EXISTS idx_enterprise_subsidiary_ids ON enterprise_info USING GIN(subsidiary_ids);
CREATE INDEX IF NOT EXISTS idx_enterprise_allowed_contractor_ids ON enterprise_info USING GIN(allowed_contractor_ids);
CREATE INDEX IF NOT EXISTS idx_enterprise_candidate_contractor_ids ON enterprise_info USING GIN(candidate_contractor_ids);
CREATE INDEX IF NOT EXISTS idx_enterprise_contractor_detail_info ON enterprise_info USING GIN(contractor_detail_info);

-- 承包商信息表索引
CREATE INDEX IF NOT EXISTS idx_contractor_info_company_name ON contractor_info(company_name);
CREATE INDEX IF NOT EXISTS idx_contractor_info_business_status ON contractor_info(business_status);
CREATE INDEX IF NOT EXISTS idx_contractor_info_is_deleted ON contractor_info(is_deleted);
CREATE INDEX IF NOT EXISTS idx_contractor_info_active_enterprise_ids ON contractor_info USING GIN(active_enterprise_ids);
CREATE INDEX IF NOT EXISTS idx_contractor_info_inactive_enterprise_ids ON contractor_info USING GIN(inactive_enterprise_ids);
CREATE INDEX IF NOT EXISTS idx_contractor_info_pending_allowed_ids ON contractor_info USING GIN(pending_allowed_ids);
CREATE INDEX IF NOT EXISTS idx_contractor_info_active_enterprise_detail ON contractor_info USING GIN(active_enterprise_detail);


-- 项目表索引
CREATE INDEX IF NOT EXISTS idx_contractor_project_contractor_id ON contractor_project(contractor_id);
CREATE INDEX IF NOT EXISTS idx_contractor_project_enterprise_id ON contractor_project(enterprise_id);

-- 作业票表索引
CREATE INDEX IF NOT EXISTS idx_ticket_apply_date ON ticket(apply_date);
CREATE INDEX IF NOT EXISTS idx_ticket_applicant ON ticket(applicant);
CREATE INDEX IF NOT EXISTS idx_ticket_worker ON ticket(worker);

-- ============================================
-- 触发器
-- ============================================

-- 企业信息表更新时间触发器
CREATE OR REPLACE FUNCTION update_enterprise_info_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_enterprise_info_updated_at
    BEFORE UPDATE ON enterprise_info
    FOR EACH ROW
    EXECUTE FUNCTION update_enterprise_info_updated_at();

-- 承包商信息表更新时间触发器
CREATE OR REPLACE FUNCTION update_contractor_info_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_contractor_info_updated_at
    BEFORE UPDATE ON contractor_info
    FOR EACH ROW
    EXECUTE FUNCTION update_contractor_info_updated_at();

-- ============================================
-- 表注释和字段注释
-- ============================================

-- 用户表注释
COMMENT ON TABLE users IS '用户表 - 存储所有用户的登录凭证和详细信息';
COMMENT ON COLUMN users.user_id IS '用户ID，主键，自增';
COMMENT ON COLUMN users.username IS '用户名，唯一，不可为空';
COMMENT ON COLUMN users.password_hash IS '密码哈希值，不可为空';
COMMENT ON COLUMN users.user_type IS '用户类型：enterprise(企业)、contractor(承包商)、admin(管理员)';
COMMENT ON COLUMN users.enterprise_staff_id IS '企业员工ID，关联企业员工信息';
COMMENT ON COLUMN users.contractor_staff_id IS '承包商员工ID，关联承包商员工信息';
COMMENT ON COLUMN users.phone IS '手机号码';
COMMENT ON COLUMN users.email IS '邮箱地址';
COMMENT ON COLUMN users.user_level IS '用户等级：-1未通过审核，0系统最高管理员，1企业管理员，2企业员工，3承包商管理员，4承包商员工';
COMMENT ON COLUMN users.audit_status IS '审核状态：1还未提交审核，2审核通过，3待审核，4审核不通过';
COMMENT ON COLUMN users.temp_token IS '临时令牌';
COMMENT ON COLUMN users.relay_name IS '中继名称';
COMMENT ON COLUMN users.sys_only_id IS '系统唯一ID，唯一，不可重复';
COMMENT ON COLUMN users.name_str IS '姓名';
COMMENT ON COLUMN users.role_type IS '角色类型';
COMMENT ON COLUMN users.role_level IS '角色等级';
COMMENT ON COLUMN users.user_status IS '用户状态';
COMMENT ON COLUMN users.work_type IS '工种，默认空字符串';
COMMENT ON COLUMN users.is_deleted IS '假删除标记，false表示未删除，true表示已删除，默认false';
COMMENT ON COLUMN users.created_at IS '创建时间，默认当前时间';
COMMENT ON COLUMN users.updated_at IS '更新时间，默认当前时间';

-- 企业信息表注释
COMMENT ON TABLE enterprise_info IS '企业信息表 - 存储企业基本信息、组织关系及合作承包商信息';
COMMENT ON COLUMN enterprise_info.enterprise_id IS '企业ID，主键，自增';
COMMENT ON COLUMN enterprise_info.license_file IS '营业执照文件路径，不可为空';
COMMENT ON COLUMN enterprise_info.license_number IS '营业执照号码';
COMMENT ON COLUMN enterprise_info.company_name IS '公司名称，不可为空';
COMMENT ON COLUMN enterprise_info.company_type IS '公司类型';
COMMENT ON COLUMN enterprise_info.company_address IS '公司地址';
COMMENT ON COLUMN enterprise_info.legal_person IS '法人代表';
COMMENT ON COLUMN enterprise_info.establish_date IS '成立日期';
COMMENT ON COLUMN enterprise_info.registered_capital IS '注册资本，数值类型，保留2位小数';
COMMENT ON COLUMN enterprise_info.applicant_name IS '申请人姓名';
COMMENT ON COLUMN enterprise_info.business_status IS '经营状态：续存、待审核、审核不通过、已注销，默认续存';
COMMENT ON COLUMN enterprise_info.is_deleted IS '是否已删除，布尔类型，默认false';
COMMENT ON COLUMN enterprise_info.parent_enterprise_id IS '父企业ID，外键关联enterprise_info表';
COMMENT ON COLUMN enterprise_info.subsidiary_ids IS '子公司ID数组，JSONB类型，默认空数组';
COMMENT ON COLUMN enterprise_info.allowed_contractor_ids IS '允许合作的承包商ID数组，JSONB类型，默认空数组';
COMMENT ON COLUMN enterprise_info.candidate_contractor_ids IS '候选承包商ID数组，JSONB类型，默认空数组';
COMMENT ON COLUMN enterprise_info.contractor_detail_info IS '承包商详细信息，JSONB类型，默认空字典，字典内部结构可由用户任意设置';
COMMENT ON COLUMN enterprise_info.modification_log IS '修改记录日志，JSONB类型，默认空数组';
COMMENT ON COLUMN enterprise_info.created_at IS '创建时间，默认当前时间';
COMMENT ON COLUMN enterprise_info.updated_at IS '更新时间，默认当前时间';

-- 承包商信息表注释
COMMENT ON TABLE contractor_info IS '承包商信息表 - 存储承包商基本信息、合作状态及合作企业详情';
COMMENT ON COLUMN contractor_info.contractor_id IS '承包商ID，主键，自增';
COMMENT ON COLUMN contractor_info.license_file IS '营业执照文件路径，不可为空';
COMMENT ON COLUMN contractor_info.license_number IS '营业执照号码';
COMMENT ON COLUMN contractor_info.company_name IS '公司名称，不可为空';
COMMENT ON COLUMN contractor_info.company_type IS '公司类型';
COMMENT ON COLUMN contractor_info.company_address IS '公司地址';
COMMENT ON COLUMN contractor_info.legal_person IS '法人代表';
COMMENT ON COLUMN contractor_info.establish_date IS '成立日期';
COMMENT ON COLUMN contractor_info.registered_capital IS '注册资本，数值类型，保留2位小数';
COMMENT ON COLUMN contractor_info.applicant_name IS '申请人姓名';
COMMENT ON COLUMN contractor_info.business_status IS '经营状态：续存、待审核、审核不通过、已注销，默认续存';
COMMENT ON COLUMN contractor_info.is_deleted IS '是否已删除，布尔类型，默认false';
COMMENT ON COLUMN contractor_info.active_enterprise_ids IS '活跃合作企业ID数组，JSONB类型，默认空数组';
COMMENT ON COLUMN contractor_info.inactive_enterprise_ids IS '已失效合作企业ID数组，JSONB类型，默认空数组';
COMMENT ON COLUMN contractor_info.pending_allowed_ids IS '尚处于等待审核的企业ID数组，JSONB类型，默认空数组';
COMMENT ON COLUMN contractor_info.active_enterprise_detail IS '合作企业详细信息，JSONB类型，默认空字典，用于存储合作企业的信息';
COMMENT ON COLUMN contractor_info.cooperation_detail_log IS '合作详情日志，JSONB类型，默认空数组';
COMMENT ON COLUMN contractor_info.modification_log IS '修改记录日志，JSONB类型，默认空数组';
COMMENT ON COLUMN contractor_info.created_at IS '创建时间，默认当前时间';
COMMENT ON COLUMN contractor_info.updated_at IS '更新时间，默认当前时间';

-- 承包商项目表注释
COMMENT ON TABLE contractor_project IS '承包商项目表';
COMMENT ON COLUMN contractor_project.project_id IS '项目ID，主键，自增';
COMMENT ON COLUMN contractor_project.contractor_id IS '承包商ID，不可为空';
COMMENT ON COLUMN contractor_project.enterprise_id IS '企业ID，不可为空';
COMMENT ON COLUMN contractor_project.project_name IS '项目名称，不可为空';
COMMENT ON COLUMN contractor_project.leader_name_str IS '负责人姓名，不可为空';
COMMENT ON COLUMN contractor_project.leader_phone IS '负责人电话，不可为空';
COMMENT ON COLUMN contractor_project.created_at IS '创建时间，默认当前时间';
COMMENT ON COLUMN contractor_project.updated_at IS '更新时间，默认当前时间';

-- 作业票表注释
COMMENT ON TABLE ticket IS '作业票表';
COMMENT ON COLUMN ticket.ticket_id IS '作业票ID，主键，自增';
COMMENT ON COLUMN ticket.apply_date IS '申请日期，不可为空';
COMMENT ON COLUMN ticket.applicant IS '申请人ID，不可为空，外键关联users表';
COMMENT ON COLUMN ticket.area_id IS '区域ID';
COMMENT ON COLUMN ticket.working_content IS '作业内容，不可为空，最大长度1024';
COMMENT ON COLUMN ticket.pre_st IS '预计开始时间，不可为空';
COMMENT ON COLUMN ticket.pre_et IS '预计结束时间，不可为空';
COMMENT ON COLUMN ticket.tools IS '工具，整数类型，默认0';
COMMENT ON COLUMN ticket.worker IS '作业人员ID，不可为空，外键关联users表';
COMMENT ON COLUMN ticket.custodians IS '监护人ID，不可为空，外键关联users表';
COMMENT ON COLUMN ticket.danger IS '危险等级，整数类型，默认0';
COMMENT ON COLUMN ticket.protection IS '防护措施，整数类型，默认0';
COMMENT ON COLUMN ticket.hot_work IS '动火作业，整数类型，默认-1';
COMMENT ON COLUMN ticket.work_height_level IS '作业高度等级，整数类型，默认0';
COMMENT ON COLUMN ticket.confined_space_id IS '受限空间ID';
COMMENT ON COLUMN ticket.temp_power_id IS '临时用电ID';
COMMENT ON COLUMN ticket.cross_work_group_id IS '交叉作业组ID，字符串类型';
COMMENT ON COLUMN ticket.signature IS '签名，字符串类型';
COMMENT ON COLUMN ticket.created_at IS '创建时间，默认当前时间';
COMMENT ON COLUMN ticket.updated_at IS '更新时间，默认当前时间';

-- ============================================
-- 完成
-- ============================================

\echo '数据库表创建完成！'
\dt

