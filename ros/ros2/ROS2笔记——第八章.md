# 第八章 导航进阶

在机器人导航中，**规划器**负责根据地图生成可行路径，**控制器**则根据路径控制机器人运动到目标位置。很多同学在研究路径规划或控制算法时，希望结合机器人进行验证，但从头构建完整的导航系统并不现实。

Navigation 2 通过 ROS 2 强大的**插件机制**，允许将自定义的规划器或控制器加载到导航系统中调用。


## 8.1 掌握 ROS 2 插件机制

在 ROS 2 中，插件机制允许在不修改主程序的情况下动态加载功能模块。例如安装 `rqt-tf-tree` 插件后，可在 `rqt` 中直接加载使用。在 Navigation 2 中使用自定义规划器和控制器，需要借助 **pluginlib** 库编写插件。

### 8.1.1 pluginlib 介绍与安装

**pluginlib** 是一个用于在 ROS 功能包中**动态加载和卸载插件**的 C++ 库。

**传统动态库 vs pluginlib**：

| 方式 | 特点 |
| :--- | :--- |
| **传统动态库** | 编译阶段需 `find_package` 查找库位置，用 `ament_target_dependencies` 链接，编译时链接器需关联库 |
| **pluginlib** | 无需提前查找和链接库，可在运行时通过参数动态加载/卸载插件 |

**安装 pluginlib**（通常安装 Navigation 2 时已作为依赖安装）：

```bash
sudo apt install ros-$ROS_DISTRO-pluginlib -y
```

安装完成后，即可通过具体示例学习 pluginlib 的使用方法。

### 8.1.2 定义插件抽象类

假设我们要创建一个简单的机器人运动控制器插件，支持多种运动控制方法（如直线运动、旋转运动、Z 字形运动等）。此时可创建一个**基类接口**，让插件继承基类并实现不同的控制方式。


#### 创建功能包

在工作空间 `chapt8/learn_pluginlib/src` 下创建功能包：

```bash
ros2 pkg create motion_control_system --dependencies pluginlib --license Apache-2.0
```


#### 定义抽象类头文件

在 `include/motion_control_system/motion_control_interface.hpp` 中定义抽象类：

```cpp
#ifndef MOTION_CONTROL_INTERFACE_HPP
#define MOTION_CONTROL_INTERFACE_HPP

namespace motion_control_system {
    class MotionController {
    public:
        virtual void start() = 0;   // 开始运动（纯虚函数）
        virtual void stop() = 0;    // 停止运动（纯虚函数）
        virtual ~MotionController() {}
    };
}

#endif // MOTION_CONTROL_INTERFACE_HPP
```


#### 抽象类与虚函数详解

##### 一、什么是虚函数？

虚函数是用 `virtual` 关键字声明的成员函数，支持**运行时多态**。当通过基类指针或引用调用虚函数时，C++ 会根据对象的**实际类型**（而不是指针的类型）决定调用哪个函数版本。

```cpp
class Base {
public:
    virtual void func() { cout << "Base" << endl; }
};

class Derived : public Base {
public:
    void func() override { cout << "Derived" << endl; }
};

Base* ptr = new Derived();
ptr->func();   // 输出：Derived（运行时决定，不是 Base）
```

如果不加 `virtual`，则属于**静态绑定**——编译时根据指针类型决定调用哪个函数，无法实现多态。


##### 二、什么是纯虚函数？

纯虚函数是在虚函数声明后加 `= 0` 的特殊虚函数，**在基类中没有实现**：

```cpp
virtual void start() = 0;   // 没有函数体，只有声明
```

**作用**：强制所有派生类必须提供该函数的具体实现。派生类若不实现，自身也会变成抽象类。


##### 三、什么是抽象类？

**抽象类** = 包含至少一个**纯虚函数**的类。

```cpp
class MotionController {          // 抽象类
public:
    virtual void start() = 0;     // 至少一个纯虚函数
    virtual ~MotionController() {}
};
```

**核心规则**：
- ❌ **不能实例化**：`MotionController mc;` 编译报错
- ✅ **只能被继承**：`class LineController : public MotionController`
- ✅ 派生类必须实现所有纯虚函数，否则派生类也是抽象类

```cpp
// ❌ 错误：抽象类不能实例化
MotionController controller;

// ✅ 正确：使用派生类
LineController controller;           // 栈上分配
MotionController* ptr = new LineController();  // 堆上分配
```


##### 四、为什么需要抽象类？

**1. 定义接口规范（契约）**

抽象类规定了一组方法签名（函数名、参数类型、返回值类型），所有派生类必须遵守。这样主程序可以安全地调用这些方法，无需担心某个插件缺少必要功能。

**2. 实现多态**

通过抽象类指针或引用，可以操作不同类型的派生类对象，执行不同版本的函数：

```cpp
void execute(MotionController* controller) {
    controller->start();   // 可能是直线运动、旋转运动或 Z 字形运动
}

LineController line;
RotateController rotate;

execute(&line);    // 执行 LineController::start()
execute(&rotate);  // 执行 RotateController::start()
```

**3. 分离接口与实现**

主程序只依赖抽象类（接口），不依赖具体实现类。新增运动方式时，只需创建新的派生类，主程序无需修改。

**4. 类型安全**

编译器会检查派生类是否实现了所有纯虚函数，确保不会出现“函数未实现”的运行时错误。


##### 五、虚析构函数

```cpp
virtual ~MotionController() {}
```

抽象类中必须声明虚析构函数。原因：当通过基类指针删除派生类对象时，如果没有虚析构函数，只会调用基类的析构函数，派生类的析构函数不会被调用，可能导致资源泄漏。

```cpp
MotionController* obj = new LineController();
delete obj;   // 有虚析构函数：先调用 LineController::~LineController()，再调用基类析构
```

即使虚析构函数的函数体为空，也必须声明。


##### 六、`override` 关键字（C++11）

派生类覆盖基类虚函数时，建议使用 `override` 关键字：

```cpp
class LineController : public MotionController {
public:
    void start() override {      // override 明确表示覆盖基类虚函数
        // 实现
    }
    void stop() override {
        // 实现
    }
};
```

**`override` 的作用**：
1. 提高代码可读性，明确表示这是覆盖基类虚函数
2. 编译器会检查基类是否有匹配的虚函数，防止拼写错误或签名不匹配

如果 `start` 拼写错误写成 `strart`，编译器会报错，而不是静默创建一个新的虚函数。


##### 七、抽象类在插件机制中的作用

在 ROS 2 插件开发中，抽象类作为**插件接口**（Plugin Interface）使用：

```
         MotionController（抽象类）
         ┌───────────────────────┐
         │ virtual void start()  │  ← 纯虚函数（接口规范）
         │ virtual void stop()   │  ← 纯虚函数（接口规范）
         └───────────────────────┘
                    │
         ┌──────────┼──────────┐
         ▼          ▼          ▼
    LineController RotateController ZigzagController
    (实现 start)   (实现 start)  (实现 start)
    (实现 stop)    (实现 stop)   (实现 stop)
```

主程序只与 `MotionController` 接口交互，通过 pluginlib 动态加载派生类插件，实现运行时的功能扩展。


#### 完整示例

```cpp
#include <iostream>
using namespace std;

// 1. 抽象类（接口规范）
class MotionController {
public:
    virtual void start() = 0;      // 纯虚函数
    virtual void stop() = 0;       // 纯虚函数
    virtual ~MotionController() {} // 虚析构函数
};

// 2. 派生类 1：直线运动
class LineController : public MotionController {
public:
    void start() override {
        cout << "直线运动开始" << endl;
    }
    void stop() override {
        cout << "直线运动停止" << endl;
    }
};

// 3. 派生类 2：旋转运动
class RotateController : public MotionController {
public:
    void start() override {
        cout << "旋转运动开始" << endl;
    }
    void stop() override {
        cout << "旋转运动停止" << endl;
    }
};

// 4. 使用多态
void run_controller(MotionController* controller) {
    controller->start();
    // ... 执行运动 ...
    controller->stop();
}

int main() {
    LineController line;
    RotateController rotate;

    run_controller(&line);    // 输出：直线运动开始/停止
    run_controller(&rotate);  // 输出：旋转运动开始/停止

    return 0;
}
```

接下来，所有运动控制插件都要继承 `MotionController`，并实现 `start()` 和 `stop()` 的具体逻辑。

### 8.1.3 编写并生成第一个插件

以旋转运动控制插件为例，演示如何编写、导出并构建一个 ROS 2 插件。

#### 编写插件头文件

在 `motion_control_system` 目录下创建 `spin_motion_controller.hpp`：

```cpp
#ifndef SPIN_MOTION_CONTROLLER_HPP
#define SPIN_MOTION_CONTROLLER_HPP

//导入抽象类
#include "motion_control_system/motion_control_interface.hpp"

// 定义抽象类的派生类，注意命名空间与原来一致
namespace motion_control_system {
    class SpinMotionController : public MotionController {
    public:
        void start() override;   // 覆盖基类纯虚函数
        void stop() override;    // 覆盖基类纯虚函数
    };
}

#endif // SPIN_MOTION_CONTROLLER_HPP
```

**代码说明**：
- 继承抽象类 `MotionController`
- 使用 `override` 关键字声明覆盖基类虚函数
- 位于 `motion_control_system` 命名空间下


#### 编写插件实现文件

在 `src` 目录下创建 `spin_motion_controller.cpp`：

```cpp
#include <iostream>
#include "motion_control_system/spin_motion_controller.hpp"
// 导入生成动态链接库插件的头文件
#include "pluginlib/class_list_macros.hpp"

namespace motion_control_system {
    void SpinMotionController::start() {
        std::cout << "SpinMotionController::start" << std::endl;
    }
    void SpinMotionController::stop() {
        std::cout << "SpinMotionController::stop" << std::endl;
    }
}

// 导出插件，参数：插件类名和抽象基类名
PLUGINLIB_EXPORT_CLASS(
    motion_control_system::SpinMotionController,
    motion_control_system::MotionController
)
```

**关键点**：
- `PLUGINLIB_EXPORT_CLASS` 宏来自 `pluginlib/class_list_macros.hpp`
- 两个参数：**要导出的类** 和 **抽象基类**
- 宏将插件注册到 pluginlib 系统中，使其可被动态加载

如果出现include报错，修改方法如下：
1. **打开设置入口**
   - 按 `Ctrl + Shift + P`
   - 输入 `C/C++: Edit Configurations (UI)`
   - 回车

2. **找到“包含路径”输入框**
   - 在配置界面中找到 `包含路径`（Include Path）输入框
   - 每行一个路径，按顺序添加

3. **添加以下路径**

```shell
${workspaceFolder}/**
${workspaceFolder}/learn_pluginlib/src/motion_control_system/include
/opt/ros/humble/include/**
```


#### 编写插件描述文件

在 `motion_control_system` 目录下（即功能包目录）创建 `spin_motion_plugins.xml`：

```xml
<library path="spin_motion_controller">
    <class name="motion_control_system/SpinMotionController"
           type="motion_control_system::SpinMotionController"
           base_class_type="motion_control_system::MotionController">
        <description>Spin Motion Controller</description>
    </class>
</library>
```

**标签说明**：

| 属性 | 说明 |
|------|------|
| `library path` | 动态库名称（不含 `lib` 前缀和 `.so` 后缀） |
| `class name` | 插件的唯一标识名称（插件名） |
| `type` | 插件类的完整类型名（命名空间+类名） |
| `base_class_type` | 抽象基类的完整类型名（命名空间+类名） |
| `description` | 插件描述信息 |


#### 修改 CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.8)
project(motion_control_system)

find_package(ament_cmake REQUIRED)
find_package(pluginlib REQUIRED)

# 以下代为关键代码：
include_directories(include)

# 生成动态库,SHARED表明生成共享库（动态库）
# 注意库名：spin_motion_controller必须与描述文件`spin_motion_plugins.xml`的'class name'一致 
add_library(spin_motion_controller SHARED
    src/spin_motion_controller.cpp
)
ament_target_dependencies(spin_motion_controller pluginlib)

# 安装库文件
install(TARGETS spin_motion_controller
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)

# 安装头文件
install(DIRECTORY include/
    DESTINATION include/
)

# 导出插件描述文件
pluginlib_export_plugin_description_file(
    motion_control_system
    spin_motion_plugins.xml
)

ament_package()
```

**关键指令**：

| 指令 | 作用 |
|------|------|
| `add_library(... SHARED ...)` | 生成动态库（`.so` 文件） |
| `install(TARGETS ...)` | 安装库到 `install` 目录 |
| `pluginlib_export_plugin_description_file` | 导出插件描述文件，供 pluginlib 发现 |


#### 构建

```bash
cd ~/chapt8/learn_pluginlib
colcon build --packages-select motion_control_system
source install/setup.bash
```

构建成功后，动态库位于：
```
install/motion_control_system/lib/libspin_motion_controller.so
```


#### 验证插件

查看已导出的插件：

```bash
# 查看插件列表
ros2 pkg plugins --pkg motion_control_system
```

输出示例：
```
motion_control_system::SpinMotionController  # 插件名称
```

至此，第一个 ROS 2 插件已成功生成。接下来可编写测试程序动态加载并使用该插件。

### 8.1.4 编写插件测试程序

pluginlib 不仅支持生成插件库，还提供了用于动态加载和调用插件的类和函数。本节编写一个测试程序，根据命令行参数加载指定的插件并调用其方法。


#### 测试程序代码

在 `src/test_plugin.cpp` 中编写：

```cpp
// 注意此处引入的是基类
#include "motion_control_system/motion_control_interface.hpp"
#include <pluginlib/class_loader.hpp>

int main(int argc, char **argv) {
    // 判断参数数量是否合法（程序名 + 插件名称）
    if (argc != 2)
        return 0;

    // 获取命令行参数作为控制器名称
    std::string controller_name = argv[1];

    // 1. 创建类加载器，类型也要填写基类名
    // 参数1：功能包名称
    // 参数2：抽象基类名称（含命名空间）
    pluginlib::ClassLoader<motion_control_system::MotionController>
        controller_loader("motion_control_system",
                          "motion_control_system::MotionController");

    // 2. 通过插件名称创建实例（返回 shared_ptr）
    auto controller = controller_loader.createSharedInstance(controller_name);

    // 3. 调用插件方法
    controller->start();
    controller->stop();

    return 0;
}
```

---

#### 代码流程说明

| 步骤 | 代码 | 说明 |
|------|------|------|
| **1. 创建类加载器** | `pluginlib::ClassLoader<BaseClass> loader(pkg, base_class_type)` | 指定功能包和基类类型 |
| **2. 加载插件实例** | `loader.createSharedInstance(plugin_name)` | 根据插件名称动态创建实例 |
| **3. 调用接口** | `controller->start()` | 通过基类指针调用虚函数，执行插件实现 |


#### 修改 CMakeLists.txt

添加测试程序的可执行文件并安装：

```cmake
# 添加测试程序
add_executable(test_plugin src/test_plugin.cpp)
ament_target_dependencies(test_plugin pluginlib)

# 安装可执行文件
install(TARGETS test_plugin
    DESTINATION lib/${PROJECT_NAME}
)
```


#### 构建与运行

```bash
# 构建
colcon build --packages-select motion_control_system

# 刷新环境
source install/setup.bash

# 运行测试（参数为插件名称）
ros2 run motion_control_system test_plugin motion_control_system/SpinMotionController
```

**运行结果**：
```
SpinMotionController::start
SpinMotionController::stop
```

#### 关键点说明

| 项目 | 说明 |
|------|------|
| **插件名称** | 必须与 `spin_motion_plugins.xml` 中 `<class name>` 属性一致 |
| **类加载器** | `ClassLoader` 模板类，需指定基类类型 |
| **创建实例** | `createSharedInstance()` 返回 `std::shared_ptr`，自动管理内存 |
| **动态加载** | 无需在编译时链接具体插件库，运行时根据名称加载 |

#### 扩展练习

可自行编写新的运动控制器插件（如直线运动、Z 字形运动），按照相同步骤：
1. 继承 `MotionController` 抽象类
2. 实现 `start()` 和 `stop()`
3. 导出插件（`PLUGINLIB_EXPORT_CLASS`）
4. 在 XML 描述文件中注册
5. 通过 `test_plugin` 加载测试

至此，已完成 ROS 2 pluginlib 插件机制的学习，接下来可将其应用于 Navigation 2 中自定义规划器和控制器的开发。

## 8.2 自定义导航规划器

在不同场景下，机器人可能需要不同的路径规划策略。例如，扫地机器人在回充时需要最短路径，在清扫时则要走“之字形”或“回字形”路径。当 Navigation 2 默认规划器不符合实际需求时，就需要自定义导航规划器。


### 8.2.1 自定义规划器介绍

路径规划器的任务是基于**初始位姿**、**目标位姿**和**环境地图**，计算出一条安全、有效的可行路径。在编写规划器前，需了解三个核心概念：**位姿表示**、**路径表示**和**地图表示**。

#### 一、位姿表示：`geometry_msgs/PoseStamped`

```bash
ros2 interface show geometry_msgs/msg/PoseStamped
```

```yaml
std_msgs/Header header
  builtin_interfaces/Time stamp
    int32 sec
    uint32 nanosec
  string frame_id          # 坐标系名称（如 "map"）
Pose pose
  Point position           # 位置（x, y, z）
    float64 x
    float64 y
    float64 z
  Quaternion orientation   # 朝向（四元数）
    float64 x 0
    float64 y 0
    float64 z 0
    float64 w 1
```

**说明**：`PoseStamped` 在 `Pose` 基础上增加了 `header`，包含时间戳和坐标系 ID。同一个坐标在不同坐标系下表示的实际位置不同。



#### 二、路径表示：`nav_msgs/Path`

```bash
ros2 interface show nav_msgs/msg/Path
```

```yaml
std_msgs/Header header        # 路径的坐标系
  string frame_id
geometry_msgs/PoseStamped[] poses   # 路径点数组（按顺序采样）
```

**说明**：路径是一个 `PoseStamped` 数组，表示机器人从起点到终点的轨迹点集合。规划器将连续路径按一定距离采样，生成离散路径点。



#### 三、地图表示：`nav_msgs/OccupancyGrid`

```bash
ros2 interface show nav_msgs/msg/OccupancyGrid
```

```yaml
std_msgs/Header header
  string frame_id
MapMetaData info
  float32 resolution        # 地图分辨率（m/像素）
  uint32 width              # 地图宽度（像素）
  uint32 height             # 地图高度（像素）
  geometry_msgs/Pose origin # 地图原点在 map 坐标系中的位置
int8[] data                 # 栅格数据（按行存储）
```

**数据存储方式**：
- 从地图**左上角**开始，**从左到右**、**从上到下**按行存储
- 常见值：`0` = 空闲，`100` = 占据，`-1` = 未知

#### 四、坐标与栅格索引转换

在地图坐标系中查询某点 `(x, y)` 的占据状态：

```python
# 计算栅格索引
row_index = (y - info.origin.y) / info.resolution
col_index = (x - info.origin.x) / info.resolution
map_index = row_index * info.width + col_index

# 获取占据状态
occupied_status = data[map_index]
```

**说明**：
- `info.origin`：地图原点（通常为地图左下角）
- `info.resolution`：分辨率，如 `0.05` 表示每像素 0.05m
- `data`：一维数组，`row_index * width + col_index` 定位到具体栅格
- 换算公式即： $$\delta_x = \dfrac{x - \text{origin\_x}}{\text{resolution}},\delta_y = \dfrac{y - \text{origin\_y}}{\text{resolution}}$$其中 $\text{origin\_x}$ 和 $\text{origin\_y}$ 分别为地图原点的 x 和 y 坐标，$\text{resolution}$ 为分辨率（即栅格大小，相当于缩放比例）。

在自定义规划器时，需通过此方式判断路径上是否有障碍物。实际开发中可直接调用 Navigation 2 提供的接口完成转换和代价提取，无需手动编写转换函数。

### 8.2.2 搭建规划器插件框架

在自定义导航规划器之前，需搭建插件框架。本节创建 `CustomPlanner` 类，继承 `nav2_core::GlobalPlanner` 抽象基类，并实现其纯虚函数。
具体步骤为：
1. 创建功能包（依赖 nav2_core + pluginlib）
2. 编写头文件：继承 nav2_core::GlobalPlanner
3. 编写实现文件：重写 5 个虚函数
4. 编写插件描述 XML
5. 修改 CMakeLists.txt（生成库 + 导出描述文件）
6. 修改 package.xml（声明插件）
7. 构建 → 加载到 Nav2

#### 创建功能包

```bash
# 将第 7 章导航功能包复制到 src 目录
cp -r chapt7/chapt7_ws/src/* chapt8/chapt8_ws/src/

# 创建自定义规划器功能包
cd chapt8/chapt8_ws/src
ros2 pkg create nav2_custom_planner \
    --dependencies nav2_core pluginlib \
    --license Apache-2.0
```



#### 头文件：`nav2_custom_planner.hpp`

在 `include/nav2_custom_planner/` 下创建：

```cpp
#ifndef NAV2_CUSTOM_PLANNER_NAV2_CUSTOM_PLANNER_HPP_
#define NAV2_CUSTOM_PLANNER_NAV2_CUSTOM_PLANNER_HPP_

// 标准库头文件
#include <memory>   // std::shared_ptr, std::unique_ptr 等智能指针
#include <string>   // std::string 字符串

// ROS 2 消息定义：带坐标系的位姿（位置+朝向+时间戳+坐标系ID）
#include "geometry_msgs/msg/pose_stamped.hpp"

// ROS 2 C++ 客户端核心库：Node, rclcpp::init, spin 等
#include "rclcpp/rclcpp.hpp"

// Navigation 2 全局规划器抽象基类：定义规划器必须实现的接口
#include "nav2_core/global_planner.hpp"

// Navigation 2 生命周期节点工具：管理节点状态（Unconfigured → Inactive → Active）
#include "nav2_util/lifecycle_node.hpp"

// Navigation 2 机器人工具函数：如坐标转换、角度计算等
#include "nav2_util/robot_utils.hpp"

// 路径消息定义：一组 PoseStamped 组成的路径点序列
#include "nav_msgs/msg/path.hpp"

namespace nav2_custom_planner {

/**
 * @brief 自定义全局规划器类
 * 
 * 继承自 nav2_core::GlobalPlanner，实现自定义路径规划算法。
 * 需要说明的是，所有的方法均是继承自 nav2_core::GlobalPlanner 的。
 * 本规划器实现了最简单的"直线路径 + 障碍物检测"策略：
 *   1. 从起点到终点生成直线路径（线性插值）
 *   2. 检查路径上每个点是否在代价地图中为致命障碍物
 *   3. 若有障碍物则抛出 PlannerException，通知上层触发恢复行为
 */
class CustomPlanner : public nav2_core::GlobalPlanner {
public:
    /** 默认构造函数：不执行任何初始化，所有资源在 configure() 中分配 */
    CustomPlanner() = default;
    
    /** 析构函数：使用 default 让编译器生成默认析构，自动释放智能指针 */
    ~CustomPlanner() = default;

    // ============================================================
    // 生命周期管理方法（由 nav2_planner 服务器调用）
    // ============================================================
    
    /**
     * @brief 配置插件（加载时调用一次）
     * 
     * 这是插件初始化的入口，负责：
     *   1. 保存传入的节点指针、TF 缓存、代价地图等外部依赖
     *   2. 从参数服务器读取配置参数
     *   3. 为后续规划做准备
     * 
     * @param parent   生命周期节点的弱引用（防止循环引用）
     * @param name     插件名称（用于参数命名空间隔离，如 "CustomPlanner"）
     * @param tf       TF 缓存指针，用于查询坐标系变换
     * @param costmap_ros  代价地图 ROS 封装，可获取全局代价地图对象和坐标系
     */
    void configure(
        const rclcpp_lifecycle::LifecycleNode::WeakPtr &parent,
        std::string name,
        std::shared_ptr<tf2_ros::Buffer> tf,
        std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) override;

    /**
     * @brief 清理插件（卸载时调用一次）
     * 
     * 释放资源，重置成员变量到初始状态。
     * 调用顺序：deactivate() → cleanup()
     */
    void cleanup() override;

    /**
     * @brief 激活插件（使插件进入可用状态）
     * 
     * 在 configure() 之后调用，表示插件现在可以处理规划请求。
     * 可以在此进行一些需要延迟初始化的操作。
     */
    void activate() override;

    /**
     * @brief 停用插件（暂停插件功能）
     * 
     * 在 cleanup() 之前调用，表示插件即将停止工作。
     * 可在此停止任何后台线程或定时器。
     */
    void deactivate() override;

    // ============================================================
    // 核心规划方法（由 nav2_planner 服务器调用）
    // ============================================================
    
    /**
     * @brief 生成从起点到终点的路径（核心函数）
     * 
     * 这是规划器最重要的方法，被 nav2_planner 服务器调用以生成路径。
     * 
     * 实现策略（直线规划）：
     *   1. 检查起点和终点是否在全局坐标系中
     *   2. 按插值分辨率在两点间线性插值，生成一系列路径点
     *   3. 遍历路径点，检查每个点是否落在致命障碍物上
     *   4. 若有障碍物则抛出 PlannerException（规划失败）
     *   5. 若全部通过则返回完整路径
     * 
     * @param start  起始位姿（通常为机器人当前位置）
     * @param goal   目标位姿（导航目标点）
     * @return nav_msgs::msg::Path  路径点序列
     * @throws nav2_core::PlannerException  当路径被障碍物阻挡时抛出
     */
    nav_msgs::msg::Path createPlan(
        const geometry_msgs::msg::PoseStamped &start,
        const geometry_msgs::msg::PoseStamped &goal) override;

private:
    // ============================================================
    // 成员变量（在 configure() 中初始化）
    // ============================================================
    
    /** TF 缓存指针：用于查询任意两个坐标系之间的变换关系 */
    std::shared_ptr<tf2_ros::Buffer> tf_;

    /** 生命周期节点指针：用于获取日志、参数、时钟等功能 */
    nav2_util::LifecycleNode::SharedPtr node_;

    /** 全局代价地图指针：用于查询地图信息、障碍物检测 */
    nav2_costmap_2d::Costmap2D *costmap_;

    /** 全局坐标系名称：通常为 "map"，所有规划输入必须在此坐标系下 */
    std::string global_frame_;

    /** 插件名称：用于参数命名空间隔离，便于多实例配置 */
    std::string name_;

    /** 插值分辨率（单位：米）：控制路径点的密度，值越小路径点越密集 */
    double interpolation_resolution_;
};

}  // namespace nav2_custom_planner

#endif  // NAV2_CUSTOM_PLANNER_NAV2_CUSTOM_PLANNER_HPP_
```



#### 实现文件：`nav2_custom_planner.cpp`

在 `src/` 下创建：

```cpp
#include <cmath>       // std::hypot（计算欧氏距离）
#include <memory>      // 智能指针
#include <string>      // std::string

#include "nav2_util/node_utils.hpp"          // 参数声明工具：declare_parameter_if_not_declared
#include "nav2_core/exceptions.hpp"           // 导航异常：PlannerException
#include "nav2_custom_planner/nav2_custom_planner.hpp"  // 本插件头文件
#include "pluginlib/class_list_macros.hpp"    // 插件导出宏：PLUGINLIB_EXPORT_CLASS

// ============================================================
// 命名空间：与头文件保持一致
// ============================================================
namespace nav2_custom_planner {

// ============================================================
// 1. configure() —— 插件配置
// ============================================================
/**
 * 功能：插件的初始化入口，在加载时调用一次
 * 
 * 执行流程：
 *   1. 保存外部依赖（TF、节点指针、代价地图等）到成员变量
 *   2. 从参数服务器读取配置参数
 * 
 * 参数说明：
 *   parent        - 生命周期节点的弱引用（避免循环引用）
 *   name          - 插件名称，用于参数隔离（如 "CustomPlanner.interpolation_resolution"）
 *   tf            - TF 缓存，用于坐标系变换查询
 *   costmap_ros   - 代价地图封装，可获取地图对象和坐标系
 */
void CustomPlanner::configure(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr &parent,
    std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) {

    // 1.1 保存外部依赖
    tf_ = tf;                           // TF 缓存
    node_ = parent.lock();              // 弱引用 → 强引用（保证节点存活）
    name_ = name;                       // 插件名称
    costmap_ = costmap_ros->getCostmap();  // 从 ROS 封装中获取底层代价地图对象
    global_frame_ = costmap_ros->getGlobalFrameID();  // 如 "map"

    // 1.2 声明并读取参数
    // 如果参数未声明，则用默认值 0.1 创建；若已声明则跳过
    nav2_util::declare_parameter_if_not_declared(
        node_,
        name_ + ".interpolation_resolution",   // 参数名：如 "CustomPlanner.interpolation_resolution"
        rclcpp::ParameterValue(0.1));          // 默认值：0.1 米

    // 从参数服务器读取实际值到成员变量
    node_->get_parameter(name_ + ".interpolation_resolution",
                         interpolation_resolution_);
}

// ============================================================
// 2. cleanup() —— 清理
// ============================================================
/**
 * 功能：卸载时清理资源，由 nav2_planner 服务器在 deactivate() 之后调用
 * 
 * 当前实现只打印日志，不涉及资源释放（因为所有资源都是智能指针管理）
 */
void CustomPlanner::cleanup() {
    RCLCPP_INFO(node_->get_logger(),
                "清理 CustomPlanner 插件: %s", name_.c_str());
}

// ============================================================
// 3. activate() —— 激活
// ============================================================
/**
 * 功能：使插件进入可用状态，由 nav2_planner 服务器在 configure() 之后调用
 * 
 * 激活后，createPlan() 可以被正常调用
 */
void CustomPlanner::activate() {
    RCLCPP_INFO(node_->get_logger(),
                "激活 CustomPlanner 插件: %s", name_.c_str());
}

// ============================================================
// 4. deactivate() —— 停用
// ============================================================
/**
 * 功能：暂停插件功能，由 nav2_planner 服务器在 cleanup() 之前调用
 * 
 * 停用后，createPlan() 将不再被调用
 */
void CustomPlanner::deactivate() {
    RCLCPP_INFO(node_->get_logger(),
                "停用 CustomPlanner 插件: %s", name_.c_str());
}

// ============================================================
// 5. createPlan() —— 核心规划方法
// ============================================================
/**
 * 功能：生成从起点到终点的路径
 * 
 * 当前为骨架实现（返回空路径），实际算法将在后续实现：
 *   1. 线性插值生成直线路径
 *   2. 用代价地图检测路径上的障碍物
 *   3. 若有障碍物则抛出 PlannerException
 * 
 * @param start  起始位姿（通常是机器人当前位置）
 * @param goal   目标位姿
 * @return nav_msgs::msg::Path  路径点序列
 */
nav_msgs::msg::Path CustomPlanner::createPlan(
    const geometry_msgs::msg::PoseStamped &start,
    const geometry_msgs::msg::PoseStamped &goal) {

    nav_msgs::msg::Path global_path;
    // TODO: 实现规划算法（直线插值 + 障碍物检测）
    return global_path;
}

}  // namespace nav2_custom_planner

// ============================================================
// 6. 导出插件（关键步骤）
// ============================================================
/**
 * PLUGINLIB_EXPORT_CLASS(类名, 基类)
 * 
 * 作用：将 CustomPlanner 类注册到 pluginlib 系统中，
 *       使 Navigation 2 能通过插件名称动态加载这个类。
 * 
 * 参数1：派生类（要导出的具体插件类）
 * 参数2：基类（抽象接口，所有规划器必须继承）
 * 
 * 配合 XML 描述文件使用。
 */
PLUGINLIB_EXPORT_CLASS(nav2_custom_planner::CustomPlanner,
                       nav2_core::GlobalPlanner)
```



#### 插件描述文件：`custom_planner_plugin.xml`

```xml
<library path="nav2_custom_planner_plugin">
    <class name="nav2_custom_planner/CustomPlanner"
           type="nav2_custom_planner::CustomPlanner"
           base_class_type="nav2_core::GlobalPlanner">
        <description>自定义导航规划器插件示例</description>
    </class>
</library>
```



#### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.8)
project(nav2_custom_planner)

find_package(ament_cmake REQUIRED)
find_package(nav2_core REQUIRED)
find_package(pluginlib REQUIRED)

# 重点代码：
include_directories(include)

set(library_name ${PROJECT_NAME}_plugin)

add_library(${library_name} SHARED
    src/nav2_custom_planner.cpp
)

ament_target_dependencies(${library_name}
    nav2_core
    pluginlib
)

install(TARGETS ${library_name}
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
    DESTINATION include/
)

pluginlib_export_plugin_description_file(
    nav2_core
    custom_planner_plugin.xml
)
# 重点代码
ament_package()
```



#### package.xml 导出声明

在 `<export>` 标签中添加：

```xml
<export>
    <build_type>ament_cmake</build_type>
    <nav2_core plugin="${prefix}/custom_planner_plugin.xml" />
</export>
```



#### 构建

```bash
cd chapt8/chapt8_ws
colcon build --packages-select nav2_custom_planner
source install/setup.bash
```

**验证**：
- 动态库：`install/nav2_custom_planner/lib/libnav2_custom_planner_plugin.so`
- 插件描述文件：`install/nav2_custom_planner/share/nav2_custom_planner/`



#### 生命周期管理说明

| 方法 | 调用时机 | 作用 |
|------|----------|------|
| `configure` | 插件加载时 | 初始化参数、获取节点指针、代价地图、TF 缓存 |
| `activate` | 配置完成后 | 激活插件，准备规划 |
| `createPlan` | 需要路径规划时 | 执行规划算法，返回 `Path` |
| `deactivate` | 插件停用时 | 暂停插件活动 |
| `cleanup` | 插件卸载时 | 清理资源 |

> **注意**：插件类不直接继承 `Node`，而是通过 `configure` 方法传入节点指针，便于获取参数和日志。

### 8.2.3 实现自定义规划算法

本节以最简单的**直线规划策略**为例，演示如何实现自定义规划算法。当收到规划请求时，直接生成从起点到终点的直线路径，并检测路径上是否有障碍物，若有则抛出异常。


#### createPlan 方法完整实现

```cpp
/**
 * @brief 自定义规划器的核心方法：生成从起点到终点的路径
 * 
 * 本实现采用最简单的"直线插值 + 障碍物检测"策略：
 *   1. 在起点和终点之间按固定分辨率线性插值生成路径点
 *   2. 检查每个路径点是否落在致命障碍物上
 *   3. 若有障碍物则抛出异常，否则返回完整路径
 * 
 * @param start 起始位姿（通常为机器人当前位置，需在 global_frame_ 坐标系下）
 * @param goal  目标位姿（需在 global_frame_ 坐标系下）
 * @return nav_msgs::msg::Path 生成的路径点序列
 * @throws nav2_core::PlannerException 当路径被障碍物阻挡时抛出
 */
nav_msgs::msg::Path
CustomPlanner::createPlan(const geometry_msgs::msg::PoseStamped &start,
                          const geometry_msgs::msg::PoseStamped &goal) {

    // ============================================================
    // 第 1 步：初始化路径消息
    // ============================================================
    nav_msgs::msg::Path global_path;              // 创建路径对象
    global_path.poses.clear();                    // 清空路径点列表（确保从空状态开始）
    global_path.header.stamp = node_->now();      // 设置当前时间戳
    global_path.header.frame_id = global_frame_;  // 设置坐标系（如 "map"）

    // ============================================================
    // 第 2 步：检查坐标系是否匹配
    // ============================================================
    // 原因：本规划器只接受 global_frame_（通常是 "map"）坐标系下的位姿
    //       如果来自其他坐标系（如 odom、base_footprint），需要先做坐标变换
    //       为简化示例，此处直接报错返回空路径
    if (start.header.frame_id != global_frame_) {
        RCLCPP_ERROR(node_->get_logger(),
                     "规划器仅接受来自 %s 坐标系的起始位置", global_frame_.c_str());
        return global_path;  // 返回空路径（不抛出异常，表示"无法处理"）
    }
    if (goal.header.frame_id != global_frame_) {
        RCLCPP_ERROR(node_->get_logger(),
                     "规划器仅接受来自 %s 坐标系的目标位置", global_frame_.c_str());
        return global_path;
    }

    // ============================================================
    // 第 3 步：计算插值步数和步进增量
    // ============================================================
    // 计算起点到终点的欧氏距离（直线距离）
    double distance = std::hypot(
        goal.pose.position.x - start.pose.position.x,
        goal.pose.position.y - start.pose.position.y);
    
    // 根据插值分辨率计算需要生成多少个路径点
    // 例如：距离 1.0m，分辨率 0.1m → 生成 10 个点
    int total_number_of_loop = distance / interpolation_resolution_;
    
    // 如果距离为 0（起点=终点），total_number_of_loop = 0

    // 计算每步在 x 和 y 方向上的增量
    double x_increment = (goal.pose.position.x - start.pose.position.x) / total_number_of_loop;
    double y_increment = (goal.pose.position.y - start.pose.position.y) / total_number_of_loop;

    // ============================================================
    // 第 4 步：生成路径点（线性插值）
    // ============================================================
    // 从起点开始，按固定步长逐步推进到终点，生成一系列路径点
    // 注：此处只设置位置 (x, y)，不设置朝向 (orientation)
    for (int i = 0; i < total_number_of_loop; ++i) {
        geometry_msgs::msg::PoseStamped pose;     // 创建单个路径点
        
        // 线性插值计算当前位置
        pose.pose.position.x = start.pose.position.x + x_increment * i;
        pose.pose.position.y = start.pose.position.y + y_increment * i;
        pose.pose.position.z = 0.0;               // 2D 规划，z 固定为 0
        
        pose.header.stamp = node_->now();         // 设置当前时间戳
        pose.header.frame_id = global_frame_;     // 设置坐标系
        
        global_path.poses.push_back(pose);        // 添加到路径中
    }

    // ============================================================
    // 第 5 步：检测路径是否经过障碍物
    // ============================================================
    // 遍历路径中的每一个点，检查该点在地图中的代价值
    // 如果遇到致命障碍物 (LETHAL_OBSTACLE)，则规划失败，抛出异常
    for (geometry_msgs::msg::PoseStamped pose : global_path.poses) {
        unsigned int mx, my;  // 栅格坐标（行列索引）
        
        // worldToMap: 将世界坐标 (x, y) 转换为栅格坐标 (mx, my)
        // 返回值 true 表示该点在代价地图范围内
        if (costmap_->worldToMap(pose.pose.position.x, pose.pose.position.y, mx, my)) {
            
            // getCost: 获取该栅格的代价值 (0~255)
            // 代价值越高，表示该位置越危险（越可能是障碍物）
            unsigned char cost = costmap_->getCost(mx, my);
            
            // LETHAL_OBSTACLE (254) 表示致命障碍物，机器人不能通过
            if (cost == nav2_costmap_2d::LETHAL_OBSTACLE) {
                RCLCPP_WARN(node_->get_logger(),
                            "在 (%f, %f) 检测到致命障碍物，规划失败。",
                            pose.pose.position.x, pose.pose.position.y);
                
                // 抛出 PlannerException 异常，通知上层控制器规划失败
                // 上层会触发恢复行为（如清理代价地图、原地等待等）
                throw nav2_core::PlannerException(
                    "无法创建目标规划: " + std::to_string(goal.pose.position.x) + ", " +
                    std::to_string(goal.pose.position.y));
            }
        }
        // 如果点在代价地图范围外，跳过检测（可能是未知区域）
    }

    // ============================================================
    // 第 6 步：添加目标点并返回路径
    // ============================================================
    // 将目标点作为路径的最后一个点（确保路径精确包含终点）
    // 注意：这里复制 goal，而不是使用循环中最后生成的点
    //       因为循环中生成的点可能因浮点误差不能精确等于 goal
    geometry_msgs::msg::PoseStamped goal_pose = goal;
    goal_pose.header.stamp = node_->now();
    goal_pose.header.frame_id = global_frame_;
    global_path.poses.push_back(goal_pose);

    // 返回完整路径，交由控制器执行跟踪
    return global_path;
}
```



#### 代码流程说明

| 步骤 | 操作 | 说明 |
|------|------|------|
| **1. 初始化路径** | 清空 `global_path.poses`，设置时间戳和坐标系 | 准备存放路径点 |
| **2. 坐标系检查** | 检查 `start` 和 `goal` 是否在 `global_frame_` 坐标系中 | 避免跨坐标系计算错误 |
| **3. 计算插值步数** | 用两点距离除以 `interpolation_resolution_` 得到循环次数 | 控制路径点的密度 |
| **4. 生成路径点** | 线性插值生成一系列 `PoseStamped` 点 | 形成直线路径 |
| **5. 障碍物检测** | 遍历路径点，通过 `costmap_` 检查是否经过致命障碍物 | 若检测到则抛出 `PlannerException` |
| **6. 返回路径** | 将目标点作为最后一个点加入路径并返回 | 路径生成成功 |



#### 关键函数说明

| 函数 | 作用 |
|------|------|
| `std::hypot(x, y)` | 计算两点间欧氏距离 |
| `costmap_->worldToMap(x, y, mx, my)` | 将世界坐标转换为栅格坐标 |
| `costmap_->getCost(mx, my)` | 获取栅格的代价值 |
| `nav2_costmap_2d::LETHAL_OBSTACLE` | 表示致命障碍物的代价值 |
| `throw nav2_core::PlannerException(...)` | 规划失败时抛出异常，通知上层控制器 |



#### 设计要点

1. **坐标系必须匹配**：只接受 `global_frame_` 坐标系下的位姿，避免跨坐标系转换的复杂性。
2. **插值分辨率**：通过 `interpolation_resolution_` 控制路径点密度，平衡精度与性能。
3. **障碍物检测**：使用代价地图判断路径是否穿过障碍物，是规划器安全性的关键保障。
4. **异常抛出**：路径被阻挡时抛出 `PlannerException`，由上层控制器处理（如触发恢复行为）。


#### 后续步骤

完成 `createPlan` 方法后，该规划器插件已可投入使用。接下来需要在 Navigation 2 配置文件中将该插件设置为默认规划器，并进行导航测试。

### 8.2.4 配置导航参数并测试

完成自定义规划器插件后，需在 Navigation 2 配置文件中将默认规划器替换为自定义规划器，并进行测试验证。

#### 修改导航参数配置

在 `fishbot_navigation2/config/nav2_params.yaml` 中，将 `planner_server` 的规划器插件替换为自定义插件：

```yaml
planner_server:
  ros__parameters:
    planner_plugins: ["GridBased"]           # 规划器名称列表
    use_sim_time: True                       # 使用仿真时间

    GridBased:                               # 规划器名称（与上面对应）
      plugin: "nav2_custom_planner/CustomPlanner"   # 插件类名（XML 中定义的 name）
      interpolation_resolution: 0.1          # 自定义参数：插值分辨率（米）
```

**配置说明**：

| 参数 | 说明 |
|------|------|
| `planner_plugins` | 规划器名称列表，可配置多个，第一个为默认 |
| `plugin` | 插件类名，必须与 XML 描述文件中的 `class name` 一致 |
| `interpolation_resolution` | 自定义参数，在 `configure()` 中声明并读取 |


#### 构建与测试

```bash
# 重新编译
colcon build --packages-select fishbot_navigation2 nav2_custom_planner
source install/setup.bash

# 启动仿真和导航
ros2 launch fishbot_description gazebo_robot.launch.py
ros2 launch fishbot_navigation2 navigation2.launch.py
```


#### 测试结果

**① 目标点无障碍时：规划成功**

在 RViz 中设置目标点，若路径上无障碍物，机器人规划出一条**直线路径**，并按路径移动。

**② 目标点被障碍物阻挡时：规划失败**

若目标点在障碍物后方，终端输出警告信息：

```
[WARN] [planner_server]: 在 (1.229790, -3.059576) 检测到致命障碍物，规划失败。
[WARN] [planner_server]: GridBased plugin failed to plan calculation to (1.97, -4.63): "无法创建目标规划：1.970607, -4.625847"
[WARN] [planner_server]: [compute_path_to_pose] [ActionServer] Aborting handle.
```

**Navigation 2 默认行为**：
- 规划失败后，自动尝试**清理代价地图**、**原地等待**等恢复行为
- 若恢复后仍无法规划，会**重复尝试**并输出警告


#### 总结

| 步骤 | 操作 |
|------|------|
| ① | 修改 `nav2_params.yaml`，将 `plugin` 指向自定义规划器 |
| ② | 添加自定义参数（如 `interpolation_resolution`） |
| ③ | 重新编译功能包 |
| ④ | 启动仿真和导航，在 RViz 中测试规划效果 |

至此，已完成自定义规划器的开发与集成。机器人按自定义规划器规划的路径移动，路径跟踪由**控制器（Controller）** 负责，后续将学习自定义控制器。

## 8.3 自定义导航控制器

控制器的作用是将规划器生成的路径转换为速度控制指令，驱动机器人沿路径移动。当默认控制器无法满足特定需求时（如需要更小的转弯半径），可自定义控制器。


### 8.3.1 自定义控制器介绍

控制器继承抽象基类 `nav2_core::Controller`，需实现以下纯虚函数：

```cpp
/**
 * @brief 配置控制器
 * @param parent 指向用户节点的指针
 * @param name 插件名称
 * @param tf TF缓存指针
 * @param costmap_ros 代价地图指针
 */
virtual void configure(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr &parent,
    std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) = 0;

/**
 * @brief 清理资源
 */
virtual void cleanup() = 0;

/**
 * @brief 激活控制器
 */
virtual void activate() = 0;

/**
 * @brief 停用控制器
 */
virtual void deactivate() = 0;

/**
 * @brief 设置全局路径
 * @param path 全局路径
 */
virtual void setPlan(const nav_msgs::msg::Path &path) = 0;

/**
 * @brief 计算速度指令（核心方法）
 * @param pose 当前机器人位姿
 * @param velocity 当前机器人速度
 * @param goal_checker 目标检查器指针
 * @return 速度指令
 */
virtual geometry_msgs::msg::TwistStamped computeVelocityCommands(
    const geometry_msgs::msg::PoseStamped &pose,
    const geometry_msgs::msg::Twist &velocity,
    nav2_core::GoalChecker *goal_checker) = 0;

/**
 * @brief 设置速度限制
 * @param speed_limit 速度限制值
 * @param percentage true为百分比，false为绝对值
 */
virtual void setSpeedLimit(const double &speed_limit, const bool &percentage) = 0;
```

**生命周期**：`configure()` → `activate()` → `setPlan()` + `computeVelocityCommands()`（循环调用）→ `deactivate()` → `cleanup()`


### 8.3.2 搭建控制器插件框架

创建功能包 `nav2_custom_controller`，依赖 `nav2_core` 和 `pluginlib`。

#### 头文件：`custom_controller.hpp`

```cpp
#ifndef NAV2_CUSTOM_CONTROLLER_NAV2_CUSTOM_CONTROLLER_HPP_
#define NAV2_CUSTOM_CONTROLLER_NAV2_CUSTOM_CONTROLLER_HPP_

#include <memory>
#include <string>
#include <vector>
#include "nav2_core/controller.hpp"
#include "rclcpp/rclcpp.hpp"
#include "nav2_util/robot_utils.hpp"

namespace nav2_custom_controller {

class CustomController : public nav2_core::Controller {
public:
    CustomController() = default;
    ~CustomController() override = default;

    // 生命周期管理方法
    void configure(
        const rclcpp_lifecycle::LifecycleNode::WeakPtr &parent,
        std::string name,
        std::shared_ptr<tf2_ros::Buffer> tf,
        std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) override;

    void cleanup() override;
    void activate() override;
    void deactivate() override;

    // 核心方法
    geometry_msgs::msg::TwistStamped computeVelocityCommands(
        const geometry_msgs::msg::PoseStamped &pose,
        const geometry_msgs::msg::Twist &velocity,
        nav2_core::GoalChecker *goal_checker) override;

    void setPlan(const nav_msgs::msg::Path &path) override;
    void setSpeedLimit(const double &speed_limit, const bool &percentage) override;

protected:
    // 工具方法
    geometry_msgs::msg::PoseStamped getNearestTargetPose(
        const geometry_msgs::msg::PoseStamped &current_pose);

    double calculateAngleDifference(
        const geometry_msgs::msg::PoseStamped &current_pose,
        const geometry_msgs::msg::PoseStamped &target_pose);

    // 成员变量
    std::string plugin_name_;
    std::shared_ptr<tf2_ros::Buffer> tf_;
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros_;
    nav2_util::LifecycleNode::SharedPtr node_;
    nav2_costmap_2d::Costmap2D *costmap_;
    nav_msgs::msg::Path global_plan_;
    double max_angular_speed_;
    double max_linear_speed_;
};

}  // namespace nav2_custom_controller

#endif
```

#### 实现文件：`custom_controller.cpp`

```cpp
// ============================================================
// 头文件包含
// ============================================================

#include "nav2_custom_controller/custom_controller.hpp"  // 本插件头文件（类声明）
#include "nav2_core/exceptions.hpp"          // Navigation2 异常定义（PlannerException 等）
#include "nav2_util/geometry_utils.hpp"      // 几何工具函数（欧氏距离计算等）
#include "nav2_util/node_utils.hpp"          // 节点工具函数（参数声明/获取等）
#include <algorithm>                         // STL 算法（erase 等）
#include <memory>                            // 智能指针
#include <string>                            // std::string
#include <vector>                            // std::vector
#include "pluginlib/class_list_macros.hpp"   // 插件导出宏

namespace nav2_custom_controller {

// ============================================================
// 1. configure() —— 插件配置（加载时调用）
// ============================================================
/**
 * 功能：控制器初始化入口，保存外部依赖并读取配置参数
 * 
 * 参数说明：
 *   parent      - 生命周期节点的弱引用（防止循环引用）
 *   name        - 插件名称（用于参数命名空间隔离）
 *   tf          - TF 缓存指针（用于坐标系变换查询）
 *   costmap_ros - 代价地图 ROS 封装
 */
void CustomController::configure(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr &parent,
    std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) {

    // 1.1 保存外部依赖到成员变量
    node_ = parent.lock();                    // 弱引用 → 强引用，保证节点存活
    costmap_ros_ = costmap_ros;               // 保存代价地图 ROS 封装
    tf_ = tf;                                 // 保存 TF 缓存
    plugin_name_ = name;                      // 保存插件名称
    costmap_ = costmap_ros->getCostmap();     // 从 ROS 封装中获取底层代价地图对象

    // 1.2 声明并读取参数
    // 如果参数未声明，则用默认值 0.1 创建；若已声明则跳过
    nav2_util::declare_parameter_if_not_declared(
        node_,
        plugin_name_ + ".max_linear_speed",   // 参数名：如 "FollowPath.max_linear_speed"
        rclcpp::ParameterValue(0.1));         // 默认值：0.1 m/s

    // 从参数服务器读取实际值到成员变量
    node_->get_parameter(plugin_name_ + ".max_linear_speed", max_linear_speed_);

    // 角速度参数同理
    nav2_util::declare_parameter_if_not_declared(
        node_,
        plugin_name_ + ".max_angular_speed",
        rclcpp::ParameterValue(1.0));         // 默认值：1.0 rad/s
    node_->get_parameter(plugin_name_ + ".max_angular_speed", max_angular_speed_);
}

// ============================================================
// 2. cleanup() —— 清理（卸载时调用）
// ============================================================
/**
 * 功能：清理资源，由控制器管理器在 deactivate() 之后调用
 * 当前实现只打印日志（所有资源由智能指针管理，无需手动释放）
 */
void CustomController::cleanup() {
    RCLCPP_INFO(node_->get_logger(),
                "清理控制器: %s", plugin_name_.c_str());
}

// ============================================================
// 3. activate() —— 激活（配置完成后调用）
// ============================================================
/**
 * 功能：激活控制器，使其进入可用状态
 * 激活后 computeVelocityCommands() 可被正常调用
 */
void CustomController::activate() {
    RCLCPP_INFO(node_->get_logger(),
                "激活控制器: %s", plugin_name_.c_str());
}

// ============================================================
// 4. deactivate() —— 停用（清理前调用）
// ============================================================
/**
 * 功能：停用控制器，暂停控制功能
 * 停用后 computeVelocityCommands() 将不再被调用
 */
void CustomController::deactivate() {
    RCLCPP_INFO(node_->get_logger(),
                "停用控制器: %s", plugin_name_.c_str());
}

// ============================================================
// 5. setPlan() —— 设置全局路径
// ============================================================
/**
 * 功能：接收规划器生成的全局路径，存储在成员变量中
 * 该路径将作为 computeVelocityCommands() 的输入
 * 
 * @param path 全局路径（来自规划器）
 */
void CustomController::setPlan(const nav_msgs::msg::Path &path) {
    global_plan_ = path;   // 拷贝路径到成员变量
}

// ============================================================
// 6. setSpeedLimit() —— 设置速度限制
// ============================================================
/**
 * 功能：设置最大速度限制
 * 当前实现为空（本示例暂不支持动态速度限制）
 * 
 * @param speed_limit 速度限制值
 * @param percentage  是否按百分比设置
 */
void CustomController::setSpeedLimit(const double &speed_limit,
                                     const bool &percentage) {
    (void)speed_limit;   // 显式标记未使用参数，避免编译器警告
    (void)percentage;
}

// ============================================================
// 7. getNearestTargetPose() —— 获取最近目标点
// ============================================================
/**
 * 功能：从全局路径中找到距离当前机器人位置最近的点，并返回其下一个点
 * 
 * 策略说明：
 *   1. 遍历路径，找到距离当前位置最近的点（最小欧氏距离）
 *   2. 从路径中移除该点之前的所有点（已走过的路径）
 *   3. 返回下一个点作为目标点（若只剩一个点则返回该点本身）
 * 
 * 这样做能让控制器始终关注前方路径，实现路径跟踪
 * 
 * @param current_pose 当前机器人位姿（已在全局坐标系下）
 * @return 目标点（路径中最近点的下一个点）
 */
geometry_msgs::msg::PoseStamped CustomController::getNearestTargetPose(
    const geometry_msgs::msg::PoseStamped &current_pose) {

    ...
}

// ============================================================
// 8. calculateAngleDifference() —— 计算角度差
// ============================================================
/**
 * 功能：计算机器人当前朝向与目标点方向之间的角度差
 * 
 * 计算步骤：
 *   1. 从当前位姿的四元数中提取 yaw 角度（机器人朝向）
 *   2. 计算从当前位置指向目标点的方向角（atan2）
 *   3. 计算两者差值，并归一化到 [-π, π] 区间
 * 
 * @param current_pose 当前机器人位姿
 * @param target_pose  目标点位姿
 * @return 归一化的角度差（弧度），正值为需要左转，负值为需要右转
 */
double CustomController::calculateAngleDifference(
    const geometry_msgs::msg::PoseStamped &current_pose,
    const geometry_msgs::msg::PoseStamped &target_pose) {

    ...
}

// ============================================================
// 9. computeVelocityCommands() —— 核心控制方法
// ============================================================
/**
 * 功能：根据当前位姿和全局路径，计算速度控制指令
 * 
 * 控制策略（"旋转-直行"策略）：
 *   - 如果机器人朝向与目标点方向的角度差 > 18°（π/10）：
 *       → 原地旋转（线速度=0，角速度=最大角速度×方向）
 *   - 如果角度差 ≤ 18°：
 *       → 直线前进（角速度=0，线速度=最大线速度）
 * 
 * 这是一个简化的控制策略，实际应用中可在此基础上增加：
 *   - PID 控制实现平滑转向
 *   - 速度随距离变化的自适应控制
 *   - 碰撞检测与安全制动
 * 
 * @param pose  当前机器人位姿（通常来自里程计）
 * @param velocity 当前机器人速度（本示例未使用）
 * @param goal_checker 目标检查器指针（本示例未使用）
 * @return TwistStamped 速度指令（线速度 m/s + 角速度 rad/s）
 * @throws nav2_core::PlannerException 当路径为空或坐标变换失败时抛出
 */
geometry_msgs::msg::TwistStamped CustomController::computeVelocityCommands(
    const geometry_msgs::msg::PoseStamped &pose,
    const geometry_msgs::msg::Twist &,
    nav2_core::GoalChecker *) {

    ...
}

}  // namespace nav2_custom_controller

// ============================================================
// 10. 导出插件
// ============================================================
/**
 * PLUGINLIB_EXPORT_CLASS(派生类, 基类)
 * 
 * 作用：将 CustomController 注册到 pluginlib 系统中，
 *       使 Navigation2 能通过插件名称动态加载这个类。
 * 
 * 参数1：派生类（要导出的具体插件类）
 * 参数2：基类（抽象接口，所有控制器必须继承）
 */
PLUGINLIB_EXPORT_CLASS(nav2_custom_controller::CustomController,
                       nav2_core::Controller)
```

#### 插件描述文件：`nav2_custom_controller.xml`

```xml
<class_libraries>
    <library path="nav2_custom_controller_plugin">
        <class type="nav2_custom_controller::CustomController"
               base_class_type="nav2_core::Controller">
            <description>自定义导航控制器</description>
        </class>
    </library>
</class_libraries>
```

#### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.8)
project(nav2_custom_controller)

find_package(ament_cmake REQUIRED)
find_package(nav2_core REQUIRED)
find_package(pluginlib REQUIRED)

# 关键代码
include_directories(include)

set(library_name ${PROJECT_NAME}_plugin)

add_library(${library_name} SHARED
    src/custom_controller.cpp
)

ament_target_dependencies(${library_name}
    nav2_core
    pluginlib
)

install(TARGETS ${library_name}
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY include/
    DESTINATION include/
)

pluginlib_export_plugin_description_file(
    nav2_core
    nav2_custom_controller.xml
)
#
ament_package()
```

#### package.xml 导出声明

```xml
<!-- 无需写 name -->
<export>
    <build_type>ament_cmake</build_type>
    <nav2_core plugin="${prefix}/nav2_custom_controller.xml" />
</export>
```


### 8.3.3 实现自定义控制算法

采用**原地旋转 + 直行**策略：
- 目标点方向与当前朝向角度差 > 18° 时，原地旋转
- 角度差 ≤ 18° 时，直线前进
- 目标点取路径中距离当前位置最近点的**下一个点**

#### getNearestTargetPose 方法

```cpp
/**
 * @brief 从全局路径中获取当前机器人的最近目标点
 * 
 * 该函数的核心逻辑是：
 *   1. 遍历全局路径中的所有点，找到距离当前机器人最近的那个点
 *   2. 从路径中删除该最近点之前的所有点（表示机器人已经走过的路径）
 *   3. 返回最近点的下一个点作为目标点
 * 
 * 这种做法的好处：
 *   - 始终让机器人看向前方的路径点
 *   - 路径跟踪连续自然，不会有跳跃
 *   - 当路径只剩最后一个点时，直接返回该点作为目标点
 * 
 * @param current_pose 当前机器人的位姿（PoseStamped）
 * @return 目标点位姿（PoseStamped）
 */
geometry_msgs::msg::PoseStamped CustomController::getNearestTargetPose(
    const geometry_msgs::msg::PoseStamped &current_pose) {

    // 使用 nav2 工具库中的欧氏距离函数（方便比较两点之间的距离）
    using nav2_util::geometry_utils::euclidean_distance;

    // ============================================================
    // 第一步：找到路径中距离当前机器人最近的点
    // ============================================================

    // nearest_pose_index：最近点在路径数组中的索引，初始为 0
    int nearest_pose_index = 0;

    // 先计算当前机器人到路径第一个点的距离，作为最小距离的初始值
    double min_dist = euclidean_distance(current_pose, global_plan_.poses.at(0));

    // 从路径的第二个点开始遍历，逐个计算距离
    // 如果某个点距离更近，就更新最近点的索引和最小距离
    for (unsigned int i = 1; i < global_plan_.poses.size(); i++) {
        double dist = euclidean_distance(current_pose, global_plan_.poses.at(i));
        if (dist < min_dist) {
            nearest_pose_index = i;   // 更新最近点索引
            min_dist = dist;          // 更新最小距离
        }
    }

    // ============================================================
    // 第二步：从路径中移除最近点之前的所有点
    // ============================================================

    // erase(begin, begin + nearest_pose_index) 表示删除 [begin, begin + nearest_pose_index) 区间
    // 即删除从路径起点到最近点（不包括最近点）之间的所有点
    // 因为这些点已经被机器人走过了，无需再保留
    global_plan_.poses.erase(std::begin(global_plan_.poses),
                             std::begin(global_plan_.poses) + nearest_pose_index);

    // ============================================================
    // 第三步：返回下一个点作为目标点
    // ============================================================

    // 如果删除后路径中只剩下一个点（即该点就是最终的目标点），直接返回它
    if (global_plan_.poses.size() == 1) {
        return global_plan_.poses.at(0);
    }

    // 否则，返回最近点的下一个点作为目标点
    // 这样机器人会依次沿着路径前进，实现平滑的路径跟踪
    return global_plan_.poses.at(1);
}

```

#### calculateAngleDifference 方法

```cpp
/**
 * @brief 计算机器人当前朝向与目标点方向之间的角度差
 * 
 * 该函数计算从机器人当前位置指向目标点的方向角与机器人当前朝向之间的差值，
 * 并将结果归一化到 [-π, π] 范围内，用于后续的速度控制决策。
 * 
 * 计算步骤：
 *   1. 从当前位姿的四元数中提取 yaw（偏航角），表示机器人的当前朝向
 *   2. 使用 atan2 计算从机器人指向目标点的方向角（相对于 x 轴）
 *   3. 计算两个角度的差值，并归一化到 [-π, π] 之间
 * 
 * @param current_pose 当前机器人的位姿（包含位置和朝向四元数）
 * @param target_pose  目标点的位姿（包含位置信息）
 * @return 归一化后的角度差（弧度），范围 [-π, π]
 *         正值表示目标点在机器人左侧（需要左转），负值表示在右侧（需要右转）
 */
double CustomController::calculateAngleDifference(
    const geometry_msgs::msg::PoseStamped &current_pose,
    const geometry_msgs::msg::PoseStamped &target_pose) {

    // ============================================================
    // 第一步：获取当前机器人的朝向角（偏航角 yaw）
    // ============================================================
    // tf2::getYaw() 从四元数中提取绕 Z 轴的旋转角度（即偏航角）
    // 四元数: (x, y, z, w) → 提取 yaw
    // 返回值范围: [-π, π]
    double current_robot_yaw = tf2::getYaw(current_pose.pose.orientation);

    // ============================================================
    // 第二步：计算从当前位置指向目标点的方向角
    // ============================================================
    // std::atan2(y, x) 计算向量 (x, y) 与 x 轴正方向之间的夹角
    // 这里计算的是：目标点相对于当前点的位置向量 (dx, dy)
    // 返回值范围: [-π, π]
    double target_angle = std::atan2(
        target_pose.pose.position.y - current_pose.pose.position.y,  // dy
        target_pose.pose.position.x - current_pose.pose.position.x   // dx
    );

    // ============================================================
    // 第三步：计算角度差并归一化到 [-π, π]
    // ============================================================
    // angle_diff = 目标方向 - 当前朝向
    // 正值：目标在左侧，需要左转；负值：目标在右侧，需要右转
    double angle_diff = target_angle - current_robot_yaw;

    // 归一化处理：将角度差限制在 [-π, π] 范围内
    // 因为角度差可能超过 ±π，需要将其转换到等效的最近角度
    // 例如：270° 等效于 -90°，这样机器人不会绕远路
    if (angle_diff < -M_PI) {
        angle_diff += 2.0 * M_PI;   // 太负了，加一圈
    } else if (angle_diff > M_PI) {
        angle_diff -= 2.0 * M_PI;   // 太正了，减一圈
    }

    // 返回归一化后的角度差
    // 例如：
    //   - 目标在正前方 → 返回 0
    //   - 目标在正左方 → 返回 π/2
    //   - 目标在正右方 → 返回 -π/2
    //   - 目标在正后方 → 返回 π 或 -π
    return angle_diff;
}
```

#### computeVelocityCommands 方法

```cpp
/**
 * @brief 核心控制方法：根据当前位姿和全局路径计算速度控制指令
 * 
 * 该函数是控制器的核心入口，由 Navigation2 的 controller_server 周期性调用。
 * 它实现了"旋转-直行"的简化控制策略：
 *   - 当机器人朝向与目标方向偏差较大（>18°）时，原地旋转
 *   - 当偏差较小时，直线前进
 * 
 * 完整执行流程：
 *   1. 检查路径是否为空 → 抛出异常
 *   2. 将当前位姿转换到全局坐标系（map 系）
 *   3. 从路径中选取最近目标点并计算角度偏差
 *   4. 根据角度偏差决定旋转或直行
 *   5. 输出速度指令
 * 
 * @param pose          当前机器人位姿（通常来自里程计/定位系统）
 * @param velocity      当前机器人速度（本示例中未使用）
 * @param goal_checker  目标检查器指针（本示例中未使用）
 * @return TwistStamped 速度指令（线速度 m/s，角速度 rad/s）
 * @throws nav2_core::PlannerException 当路径为空或坐标变换失败时抛出
 */
geometry_msgs::msg::TwistStamped CustomController::computeVelocityCommands(
    const geometry_msgs::msg::PoseStamped &pose,
    const geometry_msgs::msg::Twist &,
    nav2_core::GoalChecker *) {

    // ============================================================
    // 第一步：检查路径是否为空
    // ============================================================
    // 如果全局路径为空，说明没有可跟踪的路径，抛出异常
    // 上层（controller_server）会捕获这个异常，触发恢复行为
    if (global_plan_.poses.empty()) {
        throw nav2_core::PlannerException("收到空路径");
    }

    // ============================================================
    // 第二步：将当前位姿转换到全局坐标系
    // ============================================================
    // 输入的 pose 可能来自里程计坐标系（odom），需要转换到 map 坐标系
    // 因为路径是在 map 坐标系下规划的，坐标系统一才能正确计算
    geometry_msgs::msg::PoseStamped pose_in_global_frame;
    if (!nav2_util::transformPoseInTargetFrame(
            pose,                     // 输入：当前位姿（任意坐标系）
            pose_in_global_frame,     // 输出：转换后的位姿
            *tf_,                     // TF 缓存指针
            global_plan_.header.frame_id,  // 目标坐标系（如 "map"）
            0.1)) {                   // 超时时间（秒）
        // 转换失败，抛出异常
        throw nav2_core::PlannerException("无法转换位姿到全局坐标系");
    }

    // ============================================================
    // 第三步：获取目标点并计算角度偏差
    // ============================================================
    // getNearestTargetPose() 从路径中取出当前需要跟踪的目标点
    // calculateAngleDifference() 计算机器人朝向与目标方向的角度差
    auto target_pose = getNearestTargetPose(pose_in_global_frame);
    double angle_diff = calculateAngleDifference(pose_in_global_frame, target_pose);

    // ============================================================
    // 第四步：根据角度偏差计算速度指令
    // ============================================================
    geometry_msgs::msg::TwistStamped cmd_vel;
    cmd_vel.header.frame_id = pose_in_global_frame.header.frame_id;  // 坐标系
    cmd_vel.header.stamp = node_->get_clock()->now();               // 时间戳

    // 控制策略：角度偏差 > 18°（π/10）时原地旋转，否则直线前进
    // 
    // 为什么选择 18°？
    //   - 这是一个经验阈值，根据机器人转向能力可调
    //   - 太大：机器人走 S 形，路径跟踪不精确
    //   - 太小：机器人频繁转向，运动不流畅
    if (fabs(angle_diff) > M_PI / 10.0) {
        // === 情况一：原地旋转 ===
        // 线速度 = 0，只旋转
        // 角速度的方向由 angle_diff 的正负决定：
        //   angle_diff > 0 → 目标在左侧 → 左转（角速度为正）
        //   angle_diff < 0 → 目标在右侧 → 右转（角速度为负）
        cmd_vel.twist.linear.x = 0.0;
        cmd_vel.twist.angular.z = (angle_diff > 0 ? 1.0 : -1.0) * max_angular_speed_;
    } else {
        // === 情况二：直线前进 ===
        // 朝向已经对准目标方向，直接前进
        // 角速度 = 0，保持直线
        cmd_vel.twist.linear.x = max_linear_speed_;
        cmd_vel.twist.angular.z = 0.0;
    }

    // ============================================================
    // 第五步：输出调试信息
    // ============================================================
    // 将速度指令打印到终端，便于调试和监控
    // 在实车测试时可降低日志级别，避免影响性能
    RCLCPP_INFO(node_->get_logger(),
                "控制器: %s 发送速度 (%f, %f)",
                plugin_name_.c_str(),
                cmd_vel.twist.linear.x,
                cmd_vel.twist.angular.z);

    return cmd_vel;
}
```


### 8.3.4 配置导航参数并测试

修改 `nav2_params.yaml` 中的 `controller_server` 配置为（将原有的配置注释，新添加）：

```yaml
controller_server:
  ros__parameters:
    use_sim_time: True
    FollowPath:
      plugin: "nav2_custom_controller::CustomController"
      max_linear_speed: 0.1
      max_angular_speed: 1.0
```

#### 运行测试

```bash
# 构建
colcon build --packages-select nav2_custom_controller fishbot_navigation2
source install/setup.bash

# 启动仿真和导航
ros2 launch fishbot_description gazebo_robot.launch.py
ros2 launch fishbot_navigation2 navigation2.launch.py
```

#### 运行日志

```
[controller_server]: 控制器: FollowPath 发送速度 (0.000000, -1.000000)
[controller_server]: 控制器: FollowPath 发送速度 (0.000000, -0.000000)
[controller_server]: 控制器: FollowPath 发送速度 (0.100000, -1.000000)
```


## 8.4 小结

本章首先学习了 ROS 2 插件机制（pluginlib），包括插件的定义、编写、生成和加载。基于插件机制，实现了：
- **自定义规划器**：直线路径生成 + 障碍物检测
- **自定义控制器**：原地旋转 + 直行策略跟踪路径

完整的自定义控制器开发流程：
```
创建功能包（依赖 nav2_core + pluginlib）
    ↓
头文件：继承 nav2_core::Controller
    ↓
实现文件：重写 6 个虚函数（configure/cleanup/activate/deactivate/setPlan/computeVelocityCommands）
    ↓
编写 XML 描述文件
    ↓
CMakeLists.txt：add_library + pluginlib_export_plugin_description_file
    ↓
package.xml：导出插件声明
    ↓
构建 → 修改 nav2_params.yaml 加载插件 → 测试
```