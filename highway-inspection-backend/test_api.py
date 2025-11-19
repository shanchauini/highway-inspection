"""
API测试脚本
用于快速测试后端接口是否正常工作
"""
import requests
import json

BASE_URL = 'http://localhost:3000/api'


def test_health():
    """测试健康检查"""
    print("=" * 50)
    print("测试健康检查")
    print("=" * 50)
    
    response = requests.get('http://localhost:3000/health')
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    print()


def test_register():
    """测试用户注册"""
    print("=" * 50)
    print("测试用户注册")
    print("=" * 50)
    
    data = {
        "username": "testuser",
        "password": "test123"
    }
    
    response = requests.post(f'{BASE_URL}/auth/register', json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_login():
    """测试用户登录"""
    print("=" * 50)
    print("测试用户登录")
    print("=" * 50)
    
    data = {
        "username": "operator1",
        "password": "op123"
    }
    
    response = requests.post(f'{BASE_URL}/auth/login', json=data)
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        token = result['data']['access_token']
        print(f"\n获取到Token: {token[:50]}...")
        return token
    
    print()
    return None


def test_get_current_user(token):
    """测试获取当前用户"""
    print("=" * 50)
    print("测试获取当前用户")
    print("=" * 50)
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(f'{BASE_URL}/auth/current', headers=headers)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_get_airspaces(token):
    """测试获取空域列表"""
    print("=" * 50)
    print("测试获取空域列表")
    print("=" * 50)
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(f'{BASE_URL}/airspaces', headers=headers)
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print(f"总数: {result['data']['total']}")
        print(f"空域列表:")
        for item in result['data']['items']:
            print(f"  - {item['number']}: {item['name']} ({item['type']}, {item['status']})")
    else:
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print()


def test_get_flights(token):
    """测试获取飞行申请列表"""
    print("=" * 50)
    print("测试获取飞行申请列表")
    print("=" * 50)
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(f'{BASE_URL}/flights', headers=headers)
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        print(f"总数: {result['data']['total']}")
        print(f"申请列表:")
        for item in result['data']['items']:
            print(f"  - ID {item['id']}: {item['task_purpose']} - {item['status']}")
    else:
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    print()


def run_tests():
    """运行所有测试"""
    print("\n")
    print("╔════════════════════════════════════════════════╗")
    print("║     公路巡检系统 API 测试                      ║")
    print("╚════════════════════════════════════════════════╝")
    print("\n")
    
    # 测试健康检查
    test_health()
    
    # 测试注册（可选）
    # test_register()
    
    # 测试登录
    token = test_login()
    
    if not token:
        print("登录失败，无法继续测试！")
        print("请确保：")
        print("1. 后端服务正在运行")
        print("2. 数据库已正确配置")
        print("3. 已运行 init_db.py 初始化测试数据")
        return
    
    # 测试需要认证的接口
    test_get_current_user(token)
    test_get_airspaces(token)
    test_get_flights(token)
    
    print("=" * 50)
    print("所有测试完成！")
    print("=" * 50)


if __name__ == '__main__':
    try:
        run_tests()
    except requests.exceptions.ConnectionError:
        print("\n[错误] 无法连接到后端服务！")
        print("请确保后端服务已启动: python run.py")
    except Exception as e:
        print(f"\n[错误] 测试过程中出现异常: {str(e)}")

