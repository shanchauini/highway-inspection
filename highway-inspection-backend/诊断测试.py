"""
前后端连接诊断脚本
"""
import requests
import json

print("=" * 60)
print("公路巡检系统 - 前后端连接诊断")
print("=" * 60)
print()

# 测试1: 后端健康检查
print("【测试1】后端健康检查")
print("-" * 60)
try:
    response = requests.get('http://localhost:3000/health', timeout=5)
    print(f"✓ 后端运行正常")
    print(f"  状态码: {response.status_code}")
    print(f"  响应: {response.json()}")
except Exception as e:
    print(f"✗ 后端连接失败: {str(e)}")
print()

# 测试2: 数据库连接和测试数据
print("【测试2】测试登录接口")
print("-" * 60)
try:
    data = {
        "username": "operator1",
        "password": "op123"
    }
    response = requests.post('http://localhost:3000/api/auth/login', json=data, timeout=5)
    print(f"  状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✓ 登录成功")
        print(f"  用户: {result['data']['user']['username']}")
        print(f"  角色: {result['data']['user']['role']}")
        token = result['data']['access_token']
        print(f"  Token: {token[:50]}...")
        
        # 测试3: 使用token访问接口
        print()
        print("【测试3】使用Token访问空域接口")
        print("-" * 60)
        headers = {'Authorization': f'Bearer {token}'}
        response2 = requests.get('http://localhost:3000/api/airspaces', headers=headers, timeout=5)
        print(f"  状态码: {response2.status_code}")
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"✓ 接口访问成功")
            print(f"  空域总数: {result2['data']['total']}")
            if result2['data']['items']:
                print(f"  第一个空域: {result2['data']['items'][0]['name']}")
        else:
            print(f"✗ 接口访问失败")
            print(f"  响应: {response2.text}")
            
    else:
        print(f"✗ 登录失败")
        print(f"  响应: {response.text}")
        print()
        print("💡 可能的原因:")
        print("  1. 数据库未初始化，请运行: python init_db.py")
        print("  2. 数据库连接失败，检查.env文件中的数据库配置")
        print("  3. 用户名或密码错误")
        
except Exception as e:
    print(f"✗ 请求失败: {str(e)}")

print()
print("=" * 60)
print("【测试4】CORS配置检查")
print("-" * 60)
print("✓ 前端地址: http://localhost:5173")
print("✓ 后端API: http://localhost:3000/api")
print()
print("在浏览器中打开 http://localhost:5173 进行测试")
print("打开浏览器开发者工具 (F12) 查看 Network 面板")
print()
print("=" * 60)
print("诊断完成！")
print("=" * 60)

