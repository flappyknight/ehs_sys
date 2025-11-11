# EHS系统文档导航

## 📚 快速导航

### 🚀 快速开始
| 文档 | 说明 |
|------|------|
| [README.md](./README.md) | 项目概览和介绍 |
| [START_SERVER.md](./START_SERVER.md) | 服务器启动完整指南 |
| [DATABASE_SETUP.md](./DATABASE_SETUP.md) | 数据库基本设置 |

### 💻 开发指南
| 文档 | 说明 |
|------|------|
| [BACKEND_IMPLEMENTATION_GUIDE.md](./BACKEND_IMPLEMENTATION_GUIDE.md) | 后端实现指南 |
| [NEW_BUSINESS_LOGIC_GUIDE.md](./NEW_BUSINESS_LOGIC_GUIDE.md) | 新业务逻辑指南 |
| [TESTING_GUIDE.md](./TESTING_GUIDE.md) | 测试指南 |
| [project_plan.md](./project_plan.md) | 项目计划和架构 |

### 🗄️ 数据库文档
| 文档 | 说明 |
|------|------|
| [db/README.md](./db/README.md) | 数据库文档中心（入口） |
| [db/db_config_info.md](./db/db_config_info.md) | 数据库配置信息 |
| [db/db_info.md](./db/db_info.md) | 完整的表结构文档 |
| [db/TABLE_RELATIONSHIPS.md](./db/TABLE_RELATIONSHIPS.md) | 表关系图和数据流转 |
| [db/USAGE_GUIDE.md](./db/USAGE_GUIDE.md) | 数据库使用指南 |
| [db/IMPLEMENTATION_SUMMARY.md](./db/IMPLEMENTATION_SUMMARY.md) | 数据库实施总结 |

### 🛣️ 路由文档
| 文档 | 说明 |
|------|------|
| [routes/README.md](./routes/README.md) | 路由总览 |
| [routes/INDEX.md](./routes/INDEX.md) | 路由索引 |
| [routes/ROUTES_STRUCTURE.md](./routes/ROUTES_STRUCTURE.md) | 路由结构 |
| [routes/RESTRUCTURE_SUMMARY.md](./routes/RESTRUCTURE_SUMMARY.md) | 路由重构总结 |

### 🔧 脚本工具
| 脚本 | 说明 |
|------|------|
| [start-server.sh](./start-server.sh) | 启动服务器脚本 |
| [stop-server.sh](./stop-server.sh) | 停止服务器脚本 |
| [start-docker-db.sh](./start-docker-db.sh) | 启动Docker数据库脚本 |
| [db/execute_rebuild.sh](./db/execute_rebuild.sh) | 执行数据库重建脚本 |

### 📋 其他
| 文档 | 说明 |
|------|------|
| [CLEANUP_REPORT.md](./CLEANUP_REPORT.md) | 文档清理报告 |

---

## 📖 使用场景

### 场景1：新成员入职
1. 阅读 [README.md](./README.md) 了解项目
2. 按照 [DATABASE_SETUP.md](./DATABASE_SETUP.md) 设置数据库
3. 按照 [START_SERVER.md](./START_SERVER.md) 启动服务器
4. 阅读 [BACKEND_IMPLEMENTATION_GUIDE.md](./BACKEND_IMPLEMENTATION_GUIDE.md) 了解开发规范

### 场景2：开发新功能
1. 查看 [project_plan.md](./project_plan.md) 了解项目架构
2. 参考 [NEW_BUSINESS_LOGIC_GUIDE.md](./NEW_BUSINESS_LOGIC_GUIDE.md) 实现业务逻辑
3. 参考 [routes/README.md](./routes/README.md) 添加路由
4. 按照 [TESTING_GUIDE.md](./TESTING_GUIDE.md) 编写测试

### 场景3：数据库操作
1. 查看 [db/README.md](./db/README.md) 了解数据库文档结构
2. 查看 [db/db_info.md](./db/db_info.md) 了解表结构
3. 参考 [db/USAGE_GUIDE.md](./db/USAGE_GUIDE.md) 进行操作
4. 如需重建表，使用 [db/execute_rebuild.sh](./db/execute_rebuild.sh)

### 场景4：问题排查
1. 查看 [START_SERVER.md](./START_SERVER.md) 的故障排查部分
2. 查看 [db/db_config_info.md](./db/db_config_info.md) 的故障排查部分
3. 检查 `server.log` 日志文件

---

## 🎯 文档维护规范

### 文档命名规范
- 使用大写字母和下划线：`DOCUMENT_NAME.md`
- 避免在文件名中使用版本号（v1, v2）
- 使用清晰描述性的名称

### 文档分类
- **根目录**：核心文档和快速指南
- **db/**：数据库相关文档
- **routes/**：路由相关文档
- **子模块目录**：模块特定文档

### 更新原则
1. 直接更新现有文档，不要创建新版本
2. 重大更新在文档底部添加更新日志
3. 删除过时内容，不要保留注释掉的旧内容
4. 定期清理临时文档

---

**最后更新**: 2025-11-11  
**维护团队**: EHS系统开发团队

