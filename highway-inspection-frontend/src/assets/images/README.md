# 图片资源目录

## 使用说明

### 方法一：使用 public 目录（推荐，最简单）

1. 将您的公路巡检图片放入 `public/` 目录
2. 图片文件名为 `highway-inspection.jpg`
3. 在 `Login.vue` 中取消注释相应代码行：
   ```typescript
   const highwayImageUrl = ref<string>('/highway-inspection.jpg')
   ```

### 方法二：使用 assets/images 目录（需要编译）

1. 将图片放入此目录：`src/assets/images/highway-inspection.jpg`
   - **注意**：文件名必须是 `highway-inspection.jpg`（不是 .png）
   - 目前检测到您有 `highway-inspection.jpg.png` 文件，请重命名为 `highway-inspection.jpg`
2. 在 `Login.vue` 中取消注释导入语句：
   ```typescript
   import highwayImageLocal from '@/assets/images/highway-inspection.jpg'
   const highwayImageUrl = ref<string>(highwayImageLocal)
   ```

### 支持的图片格式
- JPG / JPEG（推荐）
- PNG
- WebP

### 图片要求
- **推荐尺寸**: 宽度 1200px 以上，高度自适应
- **文件大小**: 建议压缩到 500KB 以下，以提升加载速度

### 当前状态
- 当前使用备用图片（在线图片），页面可以正常显示
- 添加本地图片后，按上述方法修改代码即可切换
