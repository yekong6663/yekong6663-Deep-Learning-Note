# 4 服务与参数通信

## 4.1 服务与参数通信介绍

### 4.1.1 服务通信介绍

#### 查看服务信息
| 命令 | 作用 |
| :--- | :--- |
| `ros2 service list -t` | 列出所有服务及对应的消息接口 |
| `ros2 interface show <接口名>` | 查看服务接口详情，`---` 上方为请求，下方为响应 |
| `ros2 service call <服务名> <接口> "<请求内容>"` | 调用服务并传入参数 |

#### 可视化工具
- 启动 `rqt` → `Plugins` → `Services` → `Service Caller`，可图形化调用服务。

### 4.1.2 基于服务的参数通信

#### 常用命令
| 命令 | 作用 |
| :--- | :--- |
| `ros2 param list` | 列出所有参数 |
| `ros2 param describe <节点名>/<参数名>` | 查看参数详细信息 |
| `ros2 param get <节点名>/<参数名>` | 获取参数当前值 |
| `ros2 param set <节点名>/<参数名> <值>` | 修改参数值 |
| `ros2 param dump <节点名> > <文件名>.yaml` | 导出参数到 YAML 文件 |
| `ros2 run <功能包> <节点> --ros-args --params-file <文件.yaml>` | 从文件加载参数启动节点 |
| `ros2 param --help` | 查看参数相关命令帮助 |

#### 可视化工具
`rqt` → `Plugins` → `Configuration` → `Dynamic Reconfigure`，可动态修改参数。

---

## 4.2 Python 服务通信——人脸检测

### 4.2.1 自定义服务接口

#### 步骤
1. 创建功能包（依赖 `rosidl_default_generators`）。
2. 在功能包目录下创建 `srv` 文件夹，文件名采用大写驼峰命名法，扩展名 `.srv`。
3. 编写服务定义，使用 `---` 分割请求和响应部分，类型后加 `[]` 表示数组。
4. CMakeLists.txt 中注册：
   ```cmake
   rosidl_generate_interfaces(${PROJECT_NAME} "srv/FaceDetect.srv" DEPENDENCIES sensor_msgs)
   ```
5. package.xml 添加：
   ```xml
   <member_of_group>rosidl_interface_packages</member_of_group>
   ```
6. 构建并验证：
   ```bash
   colcon build
   source install/setup.bash
   ros2 interface show <功能包名>/srv/FaceDetect
   ```

### 4.2.2 Python 实现人脸检测（基础图像处理）

#### 安装依赖
```bash
pip3 install face_recognition -i https://pypi.tuna.tsinghua.edu.cn/simple
```
#### 功能包
```bash
ros2 pkg create service --build-type ament_python --dependencies rclpy 自定义消息接口功能包名 --license Apache-2.0
```

#### 资源文件处理
在 `setup.py` 中添加：
```python
('share/' + package_name + '/resource', ['resource/图片名.jpg']),
```

#### 常用库函数详解

##### 1. `face_recognition.face_locations`
| 项目 | 说明 |
| :--- | :--- |
| **使用格式** | `face_recognition.face_locations(img, number_of_times_to_upsample=1, model='hog')` |
| **参数** | `img`：图像的 NumPy 数组。<br>`number_of_times_to_upsample`（可选）：图像上采样次数，提高小脸检测精度，默认为 1。<br>`model`（可选）：检测模型，`'hog'`（默认，速度快）或 `'cnn'`（精度高）。 |
| **返回值** | 列表，每个元素为 `(top, right, bottom, left)` 元组，表示人脸位置。 |
| **作用** | 检测图像中所有人脸的位置坐标。 |
| **使用案例** | ```python<br>import face_recognition<br>import cv2<br><br>img = cv2.imread("photo.jpg")<br>locations = face_recognition.face_locations(img)<br>for top, right, bottom, left in locations:<br>    cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)<br>cv2.imshow("Result", img)<br>cv2.waitKey(0)<br>``` |

##### 2. OpenCV (`cv2`) 常用函数

| 函数 | 使用格式 | 参数说明 | 作用 |
| :--- | :--- | :--- | :--- |
| `cv2.imread` | `cv2.imread(path, flag)` | `path`：图像路径。<br>`flag`：读取模式（如 `cv2.IMREAD_COLOR`）。 | 读取图像为 NumPy 数组。 |
| `cv2.imshow` | `cv2.imshow(window_name, image)` | `window_name`：窗口名。<br>`image`：要显示的图像。 | 在窗口中显示图像。 |
| `cv2.imwrite` | `cv2.imwrite(filename, img, params)` | `filename`：保存路径。<br>`img`：图像数据。<br>`params`：格式参数。 | 保存图像文件。 |
| `cv2.resize` | `cv2.resize(src, dsize, fx, fy)` | `src`：原图。<br>`dsize`：目标尺寸。<br>`fx/fy`：缩放因子。 | 缩放图像。 |
| `cv2.rectangle` | `cv2.rectangle(img, pt1, pt2, color, thickness)` | `pt1/pt2`：矩形对角点。<br>`color`：颜色。<br>`thickness`：线宽。 | 绘制矩形框。 |
| `cv2.putText` | `cv2.putText(img, text, org, fontFace, fontScale, color, thickness)` | `text`：文本。<br>`org`：起始坐标。<br>`fontFace`：字体。<br>`fontScale`：字号。 | 在图像上添加文字。 |
| `cv2.selectROI` | `cv2.selectROI(windowName, img, showCrosshair, fromCenter)` | `showCrosshair`：是否显示十字线。<br>`fromCenter`：是否从中心选择。 | 交互式选择 ROI 区域。 |

##### 3. `get_package_share_directory`
| 项目 | 说明 |
| :--- | :--- |
| **使用格式** | `get_package_share_directory(package_name, print_warning=False)` |
| **参数** | `package_name`：功能包名称。<br>`print_warning`：是否打印警告。 |
| **返回值** | 功能包的共享目录绝对路径。 |
| **作用** | 获取功能包安装后的 `share` 目录路径，用于定位资源文件。 |

#### 图像处理示例代码
```python
import cv2
import face_recognition
from ament_index_python.packages import get_package_share_directory
import os

# 获取图片路径
pkg_share = get_package_share_directory('demo_python_service')
img_path = os.path.join(pkg_share, 'resource', 'test.jpg')

# 读取并检测人脸
image = cv2.imread(img_path)
locations = face_recognition.face_locations(image)

# 绘制人脸框
for top, right, bottom, left in locations:
    cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)

cv2.imshow("Face Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

### 4.2.3 人脸检测服务端实现

#### ROS 与 OpenCV 图像转换——`cv_bridge`
| 项目 | 说明 |
| :--- | :--- |
| **导入方式** | `from cv_bridge import CvBridge` |
| **作用** | 实现 ROS 的 `sensor_msgs/Image` 与 OpenCV 的 `numpy.ndarray` 相互转换。 |
| **方法** | `cv2_to_imgmsg(cv_image)`：OpenCV → ROS Image。<br>`imgmsg_to_cv2(ros_image)`：ROS Image → OpenCV。 |

#### 服务端核心代码结构
```python
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from your_package.srv import FaceDetect
import face_recognition
import cv2
import time
import os
from ament_index_python.packages import get_package_share_directory

class FaceDetectService(Node):
    def __init__(self):
        super().__init__('face_detect_server')
        #建立服务
        self.srv = self.create_service(FaceDetect, 'detect_face', self.callback)
        #创建CvBridge
        self.bridge = CvBridge()
        #将face_recognitions的部分参数属性化
        self.number_of_times_to_upsample = 1 #在检测人脸前先把图像放大几次
        self.model = "hog" #使用什么模型（cnn：卷积神经网络）
        # 默认图片路径
        self.default_img_path = os.path.join(
            get_package_share_directory('your_package'),
            'resource', 'default.jpg'
        )

    '''
    有response和request的服务回调函数
    对传入的response进行读取
    对request进行赋值最后返回
    '''
    def callback(self, request, response):
        # 转换图像
        #如果request中有图像就使用（需要将ros2图像转化为cv2）
        if request.image.data:
            image = self.bridge.imgmsg_to_cv2(request.image)
        #如果没有读入默认图像
        else:
            image = cv2.imread(self.default_img_path)

        start_time = time.time()
        # 人脸检测
        locations = face_recognition.face_locations(
            image,
            number_of_times_to_upsample=self.number_of_times_to_upsample,
            model=self.model
        )
        elapsed = time.time() - start_time

        # 填充响应
        response.number = len(face_locations)
        response.use_time = elapsed
        for top, right, bottom, left in locations:
            response.top.append(top)
            response.right.append(right)
            response.bottom.append(bottom)
            response.left.append(left)
        #最后返回
        return response

def main():
    rclpy.init()
    node = FaceDetectService()
    rclpy.spin(node)
    rclpy.shutdown()
```
构造默认测试图片的完整路径
```python
#方法1
self.default_image_path = os.path.join(
        get_package_share_directory('demo_python_service'),
        'resource/default.jpg '
    )
'''
1.get_package_share_directory('demo_python_service') 
会返回 ROS 2 包 demo_python_service 的共享目录
目录通常是 install/demo_python_service/share/demo_python_service
再拼上 resource/default.jpg，这样无论包安装到哪都能找到这张图
2.os.path.join
会将传入的字符串自动添加上"/"合并
'''

#方法2
'''
不使用os手动合并
'''
self.default_image_path=get_package_share_directory('demo_python_service')+"/resource/default.jpg"
#不要忘记在setup.py中为图片添加路径
```
#### colcon build构建

```bash
colcon build …
source install/setup.bash
```
可以使用查看详细信息（-t：查看路径）
```bash
ros2 service list -t
```
使用传输信息
```bash
ros2 service call /服务名 消息接口
```
注意：
- 服务只有传入后才会有返回
- 图片名不要写错！
- 只要源码有改动（包括 .py、.cpp、CMakeLists.txt、package.xml 等）都要执行：
```bash
colcon build --packages-select face_detection_show_pkg
source install/setup.bash
```

### 4.2.4 人脸检测客户端实现

#### 客户端核心方法
| 方法 | 说明 |
| :--- | :--- |
| `create_client(srv_type, srv_name)` | 创建服务客户端对象。 |
| `client.wait_for_service(timeout_sec)` | 等待服务端上线，返回布尔值。 |
| `client.call_async(request)` | 异步发送请求，返回 `Future` 对象。 |
| `rclpy.spin_until_future_complete(node, future)` | 阻塞等待异步结果完成。 |
| `future.result()` | 获取服务端返回的 `Response`。 |

#### 客户端完整代码示例
```python
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from your_package.srv import FaceDetect
import cv2
import os
from ament_index_python.packages import get_package_share_directory

class FaceDetectClient(Node):
    def __init__(self):
        super().__init__('face_detect_client')
        #建立客户端
        self.client = self.create_client(FaceDetect, 'detect_face')
        #建立图像转换对象
        self.bridge = CvBridge()
        #等待服务端响应
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')
        #成员函数调用
        self.send_request()

    def send_request(self):
        # 读取测试图片
        pkg_share = get_package_share_directory('your_package')
        img_path = os.path.join(pkg_share, 'resource', 'test.jpg')
        img = cv2.imread(img_path)

        # 构造请求
        request = FaceDetect.Request()
        request.image = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')

        # 异步发送
        future = self.client.call_async(request)#异步传输消息
        rclpy.spin_until_future_complete(self, future)#阻塞当前线程直到future.done()完成
        response = future.result()#获取结果

        #特别说明：不可以使用
        #while future.done()is not: time.sleep()

        # 显示结果
        if response is not None:
            self.display_result(img, response)

    def display_result(self, img, response):
        for i in range(response.number):
            left = response.left[i]
            right = response.right[i]
            top = response.top[i]
            bottom = response.bottom[i]
            cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.imshow("Detection Result", img)
        cv2.waitKey(0)

def main():
    rclpy.init()
    node = FaceDetectClient()
    rclpy.spin_once(node, timeout_sec=1)
    rclpy.shutdown()
```

---

## 4.3 C++ 服务通信——巡逻海龟

### 4.3.1 自定义服务接口
与 Python 类似，创建 `.srv` 文件，定义请求（目标坐标）和响应（结果状态），构建步骤同前。

### 4.3.2 创建服务端

#### 核心步骤
1. 声明服务共享指针：`rclcpp::Service<接口>::SharedPtr service_;`
2. 创建服务：`service_ = this->create_service<接口>(服务名, 回调函数);`
3. 回调函数采用 Lambda 表达式：
   ```cpp
   [this](const Request::SharedPtr req, Response::SharedPtr res) {
       // 处理 req，填充 res
   }
   ```

#### 服务端代码示例
```cpp
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <turtlesim/msg/pose.hpp>
#include "turtle_move_interface/srv/turtle_move.hpp"

class TurtleMoveServer : public rclcpp::Node {
public:
    TurtleMoveServer() : Node("turtle_move_server") {
        service_ = this->create_service<turtle_move_interface::srv::TurtleMove>(
            "move_turtle",
            [this](const Request::SharedPtr req, Response::SharedPtr res) {
                if (req->target_x >= 0.0 && req->target_y >= 0.0) {
                    target_x_ = req->target_x;
                    target_y_ = req->target_y;
                    res->result = Response::SUCCESS;
                } else {
                    res->result = Response::FAIL;
                }
            });
    }
private:
    rclcpp::Service<turtle_move_interface::srv::TurtleMove>::SharedPtr service_;
    double target_x_, target_y_;
};
```

### 4.3.3 创建客户端

#### 客户端三步走
1. 等待服务：`client->wait_for_service(timeout)`
2. 构造请求：`auto req = std::make_shared<Request>(); req->target_x = ...;`
3. 异步发送：`auto future = client->async_send_request(req);`

#### 客户端代码示例
```cpp
#include <rclcpp/rclcpp.hpp>
#include "turtle_move_interface/srv/turtle_move.hpp"
#include <cstdlib>
#include <ctime>

class TurtleMoveClient : public rclcpp::Node {
public:
    TurtleMoveClient() : Node("turtle_move_client") {
        client_ = this->create_client<turtle_move_interface::srv::TurtleMove>("move_turtle");
        timer_ = this->create_wall_timer(std::chrono::seconds(2), [this]() { send_random_target(); });
        srand(time(NULL));
    }

    void send_random_target() {
        if (!client_->wait_for_service(std::chrono::seconds(1))) {
            RCLCPP_WARN(this->get_logger(), "Service not available");
            return;
        }
        auto req = std::make_shared<turtle_move_interface::srv::TurtleMove::Request>();
        req->target_x = rand() % 12;
        req->target_y = rand() % 12;
        auto future = client_->async_send_request(req,
            [this](rclcpp::Client<turtle_move_interface::srv::TurtleMove>::SharedFuture f) {
                auto res = f.get();
                if (res->result == res->SUCCESS) {
                    RCLCPP_INFO(this->get_logger(), "Move command accepted");
                }
            });
    }
private:
    rclcpp::Client<turtle_move_interface::srv::TurtleMove>::SharedPtr client_;
    rclcpp::TimerBase::SharedPtr timer_;
};
```

---

## 4.4 Python 节点参数操作

### 4.4.1 参数声明与获取

| 方法 | 使用格式 | 作用 |
| :--- | :--- | :--- |
| `declare_parameter` | `self.declare_parameter('param_name', default_value)` | 声明参数并设置默认值。 |
| `get_parameter` | `value = self.get_parameter('param_name').value` | 获取参数当前值。 |
| `set_parameters` | `self.set_parameters([rclpy.Parameter('name', value)])` | 设置自身节点参数。 |

#### 代码示例
```python
class ParamNode(Node):
    def __init__(self):
        super().__init__('param_node')
        self.declare_parameter('speed', 0.5)
        self.speed = self.get_parameter('speed').value
```

### 4.4.2 订阅参数更新

| 方法 | 说明 |
| :--- | :--- |
| `add_on_set_parameters_callback(callback)` | 注册参数修改时的回调函数。 |

#### 回调函数示例
```python
from rcl_interfaces.msg import SetParametersResult

def parameter_callback(self, params):
    for param in params:
        if param.name == 'speed':
            self.speed = param.value
    return SetParametersResult(successful=True)
```

### 4.4.3 客户端修改其他节点参数

#### 所需接口
- 服务类型：`rcl_interfaces/srv/SetParameters`
- 消息类型：`rcl_interfaces/msg/Parameter`、`ParameterValue`、`ParameterType`

#### 完整代码示例
```python
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType

class ParamClient(Node):
    def __init__(self):
        super().__init__('param_client')
        self.client = self.create_client(SetParameters, '/target_node/set_parameters')
        self.set_speed(2.0)

    def set_speed(self, speed):
        # 构造参数值
        val = ParameterValue()
        val.double_value = speed
        val.type = ParameterType.PARAMETER_DOUBLE

        # 构造参数
        param = Parameter()
        param.name = 'speed'
        param.value = val

        # 发送请求
        req = SetParameters.Request()
        req.parameters = [param]
        future = self.client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        return future.result()
```

---

## 4.5 C++ 节点参数操作

### 4.5.1 参数声明与获取

| 方法 | 使用格式 | 作用 |
| :--- | :--- | :--- |
| `declare_parameter` | `this->declare_parameter("name", default_value);` | 声明参数。 |
| `get_parameter` | `this->get_parameter("name", variable);` | 获取参数值存入变量。 |
| `set_parameter` | `this->set_parameter(rclcpp::Parameter("name", value));` | 设置参数。 |

### 4.5.2 订阅参数更新

```cpp
#include <rcl_interfaces/msg/set_parameters_result.hpp>

auto callback = [this](const std::vector<rclcpp::Parameter> & params) {
    rcl_interfaces::msg::SetParametersResult result;
    result.successful = true;
    for (const auto & p : params) {
        if (p.get_name() == "speed") {
            speed_ = p.as_double();
        }
    }
    return result;
};
callback_handle_ = this->add_on_set_parameters_callback(callback);
```

### 4.5.3 客户端修改其他节点参数

```cpp
#include <rcl_interfaces/srv/set_parameters.hpp>
#include <rcl_interfaces/msg/parameter.hpp>
#include <rcl_interfaces/msg/parameter_value.hpp>
#include <rcl_interfaces/msg/parameter_type.hpp>

void set_remote_param(const std::string & node_name, double speed) {
    auto client = this->create_client<rcl_interfaces::srv::SetParameters>("/" + node_name + "/set_parameters");
    if (!client->wait_for_service(std::chrono::seconds(1))) return;

    auto req = std::make_shared<rcl_interfaces::srv::SetParameters::Request>();
    rcl_interfaces::msg::Parameter param;
    param.name = "speed";
    param.value.double_value = speed;
    param.value.type = rcl_interfaces::msg::ParameterType::PARAMETER_DOUBLE;
    req->parameters.push_back(param);

    auto future = client->async_send_request(req);
    rclcpp::spin_until_future_complete(this->get_node_base_interface(), future);
}
```

---

## 4.6 Launch 文件批量启动

### 4.6.1 基础 Launch 文件

#### 文件位置
在功能包目录下创建 `launch` 文件夹，编写 `*.launch.py` 文件。

#### 代码模板
```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='your_package',
            executable='your_node',
            output='screen',
        ),
    ])
```

#### 注册（CMakeLists.txt）
```cmake
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})
```

#### 注册（setup.py）
```python
from glob import glob
('share/' + package_name + '/launch', glob('launch/*.launch.py')),
```

#### 启动命令
```bash
ros2 launch your_package your_launch.launch.py
```

### 4.6.2 传递参数

```python
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    speed_arg = DeclareLaunchArgument('speed', default_value='0.5')
    return LaunchDescription([
        speed_arg,
        Node(
            package='your_package',
            executable='your_node',
            parameters=[{'speed': LaunchConfiguration('speed')}],
        ),
    ])
```

启动时指定参数：
```bash
ros2 launch your_package your_launch.launch.py speed:=1.0
```

### 4.6.3 Launch 进阶组件

| 组件 | 使用格式 | 作用 |
| :--- | :--- | :--- |
| `IncludeLaunchDescription` | `launch.actions.IncludeLaunchDescription(launch.launch_description_sources.PythonLaunchDescriptionSource([path]))` | 包含其他 launch 文件。 |
| `LogInfo` | `launch.actions.LogInfo(msg="message")` | 打印信息。 |
| `ExecuteProcess` | `launch.actions.ExecuteProcess(cmd=['command', 'arg1'])` | 执行系统命令。 |
| `GroupAction` | `launch.actions.GroupAction([action1, action2])` | 组合多个动作。 |
| `TimerAction` | `launch.actions.TimerAction(period=5.0, actions=[action])` | 延迟执行动作。 |
| `IfCondition` | `condition=launch.conditions.IfCondition(LaunchConfiguration('use_xxx'))` | 条件执行动作。 |