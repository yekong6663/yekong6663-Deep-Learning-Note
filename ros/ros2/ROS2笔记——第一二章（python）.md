好的，我已根据您的要求将标题中的顿号移除，改为纯数字加点（如 `1.1`）的格式。以下是调整后的笔记内容：

---

# 1 Python 篇

> **重要提示**  
> - 运行失败时，请从代码编写到运行的每一步逐一核查自身操作！  
> - 使用小鱼ROS一键安装 rosdep 后，后续请将 `rosdep` 替换为 `rosdepc` 使用。  
> - 文档中形如 `<内容>` 的占位符在实际输入时需去掉尖括号。

## 1.1 ROS 2 基础概念

ROS 2 有四大通信机制：

| 机制 | 说明 |
| :--- | :--- |
| **话题通信** | 发布—订阅模式，单向传输。 |
| **服务通信** | 客户端请求，服务端响应，双向。 |
| **动作通信** | 可反馈进度、可随时取消的长时间任务。 |
| **参数通信** | 节点参数的设置与读取。 |

### 1.1.1 节点 (ros2 node)
- `ros2 node list`：显示所有正在运行的节点名称。
- `ros2 node info <node_name>`：查看节点详细信息。
- `ros2 run <功能包名> <节点名>`：运行节点，如 `ros2 run turtlesim turtlesim_node`。

### 1.1.2 话题 (ros2 topic)
- `rqt_graph`：可视化节点、话题及它们之间的连接关系。
- `ros2 topic list`：列出所有活动话题。
- `ros2 topic list -t`：列出话题并显示消息类型。
- `ros2 topic echo <topic_name>`：实时查看话题发布的数据。
- `ros2 topic info <topic_name>`：查看话题详细信息。

---

## 1.2 环境准备与 Linux 基础

### 1.2.1 启动海龟模拟器示例
```bash
# 启动模拟器
ros2 run turtlesim turtlesim_node
# 键盘控制
ros2 run turtlesim turtle_teleop_key
```

### 1.2.2 在 Linux 下编写 Python 程序
- 使用 VS Code：终端输入 `code` 或 `cd <目录>; code ./` 打开当前文件夹。
- 新建文件：文件名必须以 `.py` 结尾。
- 保存：`Ctrl+S` 或开启自动保存。
- 运行方式：
  - 在 VS Code 集成终端中执行：`python3 <文件名>.py`
  - 或在文件首行添加 `#!/usr/bin/python3`，赋予执行权限 `chmod a+x <文件名>`，然后 `./<文件名>.py`

### 1.2.3 Linux 环境变量基础
- `echo $ROS_VERSION`：查看 ROS 版本。
- `printenv`：显示所有环境变量，可用 `| grep <关键词>` 过滤。
- `export 环境变量=路径`：临时修改环境变量（新终端失效）。
- 以 `.` 开头的文件为隐藏文件。

---

## 1.3 编写 Python 节点与功能包

### 1.3.1 编写第一个 Python 节点
```python
import rclpy
from rclpy.node import Node

def main(args=None):
    rclpy.init(args=args)           # 初始化 ROS 2
    node = Node("my_node")          # 创建节点
    rclpy.spin(node)                # 保持节点运行
    rclpy.shutdown()                # 关闭

if __name__ == "__main__":
    main()
```
- `import rclpy` 和 `from rclpy.node import Node`：导入必需模块。
- `rclpy.init()`：初始化运行时环境。
- `Node("节点名")`：创建节点实例。
- `rclpy.spin(node)`：让节点持续运行并处理回调。
- `rclpy.shutdown()`：关闭节点。
- `if __name__ == "__main__":`：确保脚本被直接运行时才执行主函数。

**运行与验证**  
```bash
python3 文件名.py
# 在另一个终端中查看节点
ros2 node list
```

### 1.3.2 日志打印
```python
node.get_logger().info("Hello ROS 2")
```
- 在类内部使用 `self.get_logger().info("...")`。

### 1.3.3 使用功能包组织节点
创建 Python 功能包：
```bash
ros2 pkg create demo_python_pkg --build-type ament_python --license Apache-2.0
```
- 功能包目录下会有同名子文件夹，需在其中编写 Python 源文件。

### 1.3.4 在功能包中运行节点（注册与构建）
**A. 注册节点（`setup.py`）**  
在 `console_scripts` 中添加：
```python
entry_points={
    'console_scripts': [
        '节点名 = 功能包名.文件名:main',
    ],
},
```
- 规则：`"脚本名 = 包名.模块名:主函数名"`

**B. 声明依赖（`package.xml`）**  
添加：
```xml
<depend>rclpy</depend>
```

**C. 编译与环境加载**
```bash
# 在工作空间根目录执行
colcon build
# 加载环境
source install/setup.bash
```

**D. 运行节点**
```bash
ros2 run 功能包名 脚本名
```

> **注意**：修改代码后需重新 `colcon build` 并 `source setup.bash`。

### 1.3.5 工作空间 (Workspace) 最佳实践
创建标准工作空间：
```bash
mkdir -p my_ws/src
cd my_ws
# 将功能包放入 src 目录
```
- 工作空间根目录包含 `src`（源码）、`build`（编译中间文件）、`install`（安装结果）、`log`（日志）。

### 1.3.7 回调函数与多线程

#### 1.3.7.1 回调函数
- 将函数名作为参数传递给另一个函数，在特定事件发生时被调用。
```python
def my_callback(data):
    print(data)

def processor(func, value):
    func(value)

processor(my_callback, "Hello")
```

#### 1.3.7.2 多线程 (`threading` 模块)
- **创建线程**：`t = threading.Thread(target=函数, args=参数元组)`
- **启动线程**：`t.start()`
- **等待线程结束**：`t.join()`
- **守护线程**：`t.daemon = True`（主线程结束时自动终止）

#### 1.3.7.4 生产者-消费者示例
```python
import threading, queue, time

q = queue.Queue()

def producer():
    for i in range(5):
        q.put(i)
        print(f"Produced {i}")
        time.sleep(0.5)

def consumer():
    while True:
        item = q.get()
        print(f"Consumed {item}")
        q.task_done()

threading.Thread(target=producer).start()
threading.Thread(target=consumer, daemon=True).start()
```

### 1.3.9 网络请求与 `requests` 库

#### 1.3.9.1 常用方法
- `requests.get(url, params=None)`
- `requests.post(url, data=None, json=None)`
- `requests.put(url, data=None)`
- `requests.delete(url)`

#### 1.3.9.2 响应对象属性
- `response.status_code`：HTTP 状态码。
- `response.headers`：响应头字典。
- `response.text`：响应体文本。
- `response.encoding`：内容编码。

#### 1.3.9.3 HTTP 状态码分类
- `1xx`：信息性。
- `2xx`：成功（如 200 OK）。
- `3xx`：重定向。
- `4xx`：客户端错误（如 404 Not Found）。
- `5xx`：服务器错误。

#### 1.3.9.4 多线程下载示例
```python
import threading
import requests

class Downloader:
    def download(self, url, callback):
        resp = requests.get(url)
        callback(url, resp.text)

    def start_download(self, urls, callback):
        threads = []
        for url in urls:
            t = threading.Thread(target=self.download, args=(url, callback))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

def print_result(url, content):
    print(f"Downloaded {url}, length={len(content)}")

downloader = Downloader()
downloader.start_download(["http://example.com"], print_result)
```
