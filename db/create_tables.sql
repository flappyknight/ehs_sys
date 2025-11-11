-- ============================================
-- EHS系统数据库建表语句
-- 数据库名: ehs
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
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 企业用户表
CREATE TABLE IF NOT EXISTS enterprise_user (
    user_id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL,
    dept_id INTEGER,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    position VARCHAR(100),
    role_type VARCHAR(100) NOT NULL,
    approval_level INTEGER NOT NULL DEFAULT 4,
    status BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 承包商用户表
CREATE TABLE IF NOT EXISTS contractor_user (
    user_id SERIAL PRIMARY KEY,
    contractor_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    id_number VARCHAR(50) NOT NULL,
    work_type VARCHAR(100) NOT NULL,
    role_type VARCHAR(10) NOT NULL DEFAULT 'normal',
    personal_photo VARCHAR(255) NOT NULL,
    status BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_contractor FOREIGN KEY (contractor_id) REFERENCES contractor(contractor_id) ON DELETE CASCADE
);

-- ============================================
-- 企业和承包商信息表
-- ============================================

-- 企业信息表
CREATE TABLE IF NOT EXISTS enterprise_info (
    enterprise_id SERIAL PRIMARY KEY,
    license_file VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(100),
    legal_person VARCHAR(100),
    establish_date DATE,
    registered_capital NUMERIC(15, 2),
    applicant_name VARCHAR(100),
    business_status VARCHAR(50) NOT NULL DEFAULT '续存',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    parent_enterprise_id INTEGER,
    subsidiary_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    allowed_contractor_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    modification_log JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_parent_enterprise FOREIGN KEY (parent_enterprise_id) REFERENCES enterprise_info(enterprise_id) ON DELETE SET NULL
);

-- 承包商信息表
CREATE TABLE IF NOT EXISTS contractor_info (
    contractor_id SERIAL PRIMARY KEY,
    license_file VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(100),
    legal_person VARCHAR(100),
    establish_date DATE,
    registered_capital NUMERIC(15, 2),
    applicant_name VARCHAR(100),
    business_status VARCHAR(50) NOT NULL DEFAULT '续存',
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    active_enterprise_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    inactive_enterprise_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    cooperation_detail_log JSONB NOT NULL DEFAULT '[]'::jsonb,
    modification_log JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 承包商表（旧表，保持兼容）
CREATE TABLE IF NOT EXISTS contractor (
    contractor_id SERIAL PRIMARY KEY,
    license_file VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(100),
    legal_person VARCHAR(100),
    establish_date DATE,
    registered_capital NUMERIC(15, 2),
    applicant_name VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 项目相关表
-- ============================================

-- 承包商项目表
CREATE TABLE IF NOT EXISTS contractor_project (
    project_id SERIAL PRIMARY KEY,
    contractor_id INTEGER NOT NULL,
    enterprise_id INTEGER NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    leader_name VARCHAR(100) NOT NULL,
    leader_phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_project_contractor FOREIGN KEY (contractor_id) REFERENCES contractor(contractor_id) ON DELETE CASCADE
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
    CONSTRAINT fk_ticket_applicant FOREIGN KEY (applicant) REFERENCES enterprise_user(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_worker FOREIGN KEY (worker) REFERENCES contractor_user(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_custodian FOREIGN KEY (custodians) REFERENCES enterprise_user(user_id) ON DELETE CASCADE
);

-- ============================================
-- 外键约束
-- ============================================

-- 用户表外键
ALTER TABLE users ADD CONSTRAINT fk_enterprise_staff FOREIGN KEY (enterprise_staff_id) REFERENCES enterprise_user(user_id) ON DELETE SET NULL;
ALTER TABLE users ADD CONSTRAINT fk_contractor_staff FOREIGN KEY (contractor_staff_id) REFERENCES contractor_user(user_id) ON DELETE SET NULL;

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

-- 承包商信息表索引
CREATE INDEX IF NOT EXISTS idx_contractor_info_company_name ON contractor_info(company_name);
CREATE INDEX IF NOT EXISTS idx_contractor_info_business_status ON contractor_info(business_status);
CREATE INDEX IF NOT EXISTS idx_contractor_info_is_deleted ON contractor_info(is_deleted);
CREATE INDEX IF NOT EXISTS idx_contractor_info_active_enterprise_ids ON contractor_info USING GIN(active_enterprise_ids);
CREATE INDEX IF NOT EXISTS idx_contractor_info_inactive_enterprise_ids ON contractor_info USING GIN(inactive_enterprise_ids);

-- 承包商表索引
CREATE INDEX IF NOT EXISTS idx_contractor_company_name ON contractor(company_name);

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
-- 表注释
-- ============================================

COMMENT ON TABLE users IS '用户表 - 存储所有用户的登录凭证';
COMMENT ON TABLE enterprise_user IS '企业用户表 - 存储企业员工详细信息';
COMMENT ON TABLE contractor_user IS '承包商用户表 - 存储承包商员工详细信息';
COMMENT ON TABLE enterprise_info IS '企业信息表 - 存储企业基本信息、组织关系及合作承包商信息';
COMMENT ON TABLE contractor_info IS '承包商信息表 - 存储承包商基本信息、合作状态及合作企业详情';
COMMENT ON TABLE contractor IS '承包商表（旧表，保持向后兼容）';
COMMENT ON TABLE contractor_project IS '承包商项目表';
COMMENT ON TABLE ticket IS '作业票表';

-- ============================================
-- 完成
-- ============================================

\echo '数据库表创建完成！'
\dt

