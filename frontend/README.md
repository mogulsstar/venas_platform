# Venas Platform Frontend

这是Venas Platform的前端项目，使用React、TypeScript和Vite构建。

## 开发环境

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
# 或者
npm start
```

开发服务器将在 http://localhost:3000 上运行。

## 构建

```bash
npm run build
```

构建文件将输出到 `dist` 目录。

## 测试

```bash
# 运行所有测试
npm test

# 以监视模式运行测试
npm run test:watch
```

## 代码质量

```bash
# 运行ESLint
npm run lint

# 修复ESLint问题
npm run lint:fix

# 格式化代码
npm run format
```

## 项目结构

```
src/
├── components/    # 可重用组件
├── features/      # 特性模块（Redux切片）
├── pages/         # 页面组件
├── services/      # API服务
├── locales/       # 国际化文件
├── App.tsx        # 主应用组件
├── main.tsx       # 应用入口点
├── store.ts       # Redux存储配置
└── theme.ts       # MUI主题配置
```

## 环境变量

在项目根目录创建 `.env` 文件来设置环境变量。所有环境变量必须以 `VITE_` 开头。

例如：

```
VITE_API_URL=http://localhost:8000/api
```

在代码中使用：

```typescript
const apiUrl = import.meta.env.VITE_API_URL;
```
