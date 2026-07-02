# 第六章 仿真
## 6.1 机器人的建模与仿真概述
### 6.1.1 移动机器人的结构
![alt text](image-19.png)
### 6.1.2 常用机器人的仿真平台——gazebo

## 6.2 使用URDF创建机器人
### 6.2.1 创建身体
#### URDF概述
URDF（Unified Robot Description Format，统一机器人描述格式），底层基于 **XML 可扩展标记语言**，专门用于完整描述机器人：
- 机械几何结构（连杆外形、尺寸、质量惯性）
- 关节传动关系（旋转/平移关节、限位、减速比）
- 搭载传感器、执行器安装位置与参数
- 碰撞、视觉渲染、物理仿真相关配置

#### **示例代码逐行解析**
```xml
<?xml version="1.0"?>
<!-- XML 文件头部声明，指定版本1.0，必须放在文件最顶部 -->
<robot name="first_robot">
    <!-- XML 注释，仅用于代码说明，程序解析时会自动忽略 -->
    <link name="base_link"></link>
    <!-- link 标签：代表机器人刚性连杆（刚体）
         name="base_link"：机器人基座连杆，是整个机器人的根坐标系，必不可少 -->
</robot>
```
**关键标签说明**
1. `<robot>`：根标签，整个机器人模型的容器，`name` 属性为机器人全局名称；
2. `<link>`：连杆单元，对应机器人一块不会形变的刚体（底盘、轮子、机械臂杆、摄像头支架等）；
3. XML 注释语法：`<!-- 注释内容 -->`，不能使用 `//`、`/* */` 这类C语言注释。

#### **代码操作**
**构建功能包**
```bash
ros2 pkg create fishbot_description --build-type ament_cmake --license Apache-2.0
```
一般会在该功能包下新建`URDF`文件夹专门存放，再次之下创建`.urdf`文件

**代码编写**
>注意urdf语言有对应的插件可以安装
```xml
<?xml version="1.0"?>
<robot name="first_robot">

    <!-- 机器人的身体部分 -->
    <link name="base_link">
        <!-- 部件的外观描述 -->
        <visual>
            <!-- 沿着自己几何中心的偏移和旋转量 -->
            <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0"/>
            <!-- 几何形状 -->
            <geometry>
                <!-- 圆柱体 radius半径0.10m 高度length0.12m -->
                <cylinder radius="0.10" length="0.12"/>
            </geometry>
            <!-- 材质颜色 -->
            <material name="">
                <color rgba="1.0 1.0 1.0 0.5"/>
            </material>
        </visual>
    </link>

    <!-- 机器人的U形部件，惯性测量传感器 -->
    <link name="imu_link">
        <!-- 部件的外观描述 -->
        <visual>
            <!-- 沿着自己几何中心的偏移和旋转量 -->
            <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0"/>
            <!-- 几何形状 -->
            <geometry>
                <box size="0.02 0.02 0.02"/>
            </geometry>
            <!-- 材质颜色 -->
            <material name="black">
                <color rgba="0.0 0.0 0.0 0.5"/>
            </material>
        </visual>
    </link>

    <!-- 机器人的关节，用于组合机器人的部件 -->
    <joint name="imu_joint" type="fixed">
        <parent link="base_link"/>
        <child link="imu_link"/>
        <origin xyz="0.0 0.0 0.03" rpy="0.0 0.0 0.0"/>
    </joint>

</robot>

```
**结构可视化**
在`urdf`文件夹下,输入：
```bash
urdf_to_graphviz.sh 文件名.urdf
```
可以生产对应的pdf结构图：![alt text](image-20.png)

### 6.2.2 在RViz中显示机器人
#### 操作步骤
**启动 RViz**
```bash
rviz2
```
**添加 RobotModel 显示插件**
在 RViz 中：
- 点击左下角 Add 按钮
- 选择 By display type → RobotModel
- 点击 OK
- 修改RobotModel下Description Source为File而非Topic
- 点击出现的`...`按钮，选择`.urdf`文件
![alt text](image-21.png)

**更改参考坐标系**
默认情况下会报错：![alt text](image-22.png)
是因为`global options`中的`fixed frmae`选择了不存在的`map`参考系
此时可以将其修改为`base_link`即可。但是需要注意的是，rviz2不会加载`joint`组件，需要我们自行加载。

**加载`joint`组件**
安装
```bash
sudo apt install ros-$ROS_DISTRO-joint-state-publisher
sudo apt install ros-$ROS_DISTRO-robot-state-publisher
```
| 项目 | joint_state_publisher | robot_state_publisher |
| ---- | ---- | ---- |
| 安装命令 | `sudo apt install ros-$ROS_DISTRO-joint-state-publisher` | `sudo apt install ros-$ROS_DISTRO-robot-state-publisher` |
| 核心作用 | 发布机器人各关节的角度状态数据 | 根据关节角度与URDF模型，计算并发布所有连杆之间的TF坐标变换 |
| 使用场景 | RViz可视化URDF时，存在可活动关节（非fixed固定关节），依靠该节点输出关节角度 | RViz加载URDF模型**必需节点**，将连杆位姿发布至`/tf`话题，供可视化、导航、定位模块读取坐标关系 |
| 依赖关系 | 无强制前置依赖 | 依赖joint_state_publisher输出的关节角度数据完成TF解算 |

**使用launch文件开启`joint_state_publisher`与`robot_state_publisher`节点**
在本功能包的CMakeList下填写：
```cmake
install(DIRECTORY launch urdf
    DESTINATION share/${PROJECT_NAME}
)
```
在本功能包下新建`launch`文件夹，在新建`.launch.py`文件
```py
# fish_robot.urdf
# display_robot.launch.py
# CMakeLists.txt

# ws > src > fishbot_description > launch > display_robot.launch.py > generate_launch_description

import launch
import launch_ros

# 获取功能包安装路径
from ament_index_python.packages import get_package_share_directory  
import os

import launch_ros.parameter_descriptions


def generate_launch_description():
    # ========== 1. 获取默认 URDF 路径 ==========
    urdf_package_path = get_package_share_directory("fishbot_description")
    default_urdf_path = os.path.join(urdf_package_path, 'urdf', 'fish_robot.urdf')

    # ========== 2. 声明 launch 参数 ==========
    action_declare_arg_model = launch.actions.DeclareLaunchArgument(
        name='model',
        default_value=str(default_urdf_path),
        description='加载的模型文件路径'
    )

    # ========== 3. 构建读取 URDF 内容的命令 ==========
    # 因为需要传入的是URDF文件的内容，而非其路径
    command_cat_urdf = launch.substitutions.Command(
        ['cat ', launch.substitutions.LaunchConfiguration('model')]
    )

    # ========== 4. 将命令结果包装为参数值 ==========
    robot_description_value = launch_ros.parameter_descriptions.ParameterValue(
        command_cat_urdf,
        value_type=str
    )

    # ========== 5. 创建 robot_state_publisher 节点 ==========
    # 订阅 /joint_states，计算并发布 TF
    # 原本 ros2 run robot_state_publisher robot_state_publisher可以运行
    # 但是其需要附加上特定的参数——robot_description
    # 需要传入URDF文件的详细内容作为参数
    # 参数名是固定的与参数值即robot_description_value
    action_robot_state_publisher = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_value}]
    )

    # ========== 6. 创建 joint_state_publisher 节点 ==========
    # 发布关节状态（默认所有关节角度为 0）
    # 原本 ros2 run joint_state_publisher joint_state_publisher可以运行
    action_joint_state_publisher = launch_ros.actions.Node(
        package='joint_state_publisher',
        executable='joint_state_publisher'
    )

    # ========== 7. 创建 RViz2 节点 ==========
    # 原本 ros2 run rviz2 rviz2可以运行
    action_rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2'
    )

    # ========== 8. 返回 LaunchDescription ==========
    return launch.LaunchDescription([
        action_declare_arg_model,
        action_joint_state_publisher,    
        action_robot_state_publisher,
        action_rviz_node,
    ])
```
**重新运行**
之后运行launch文件
```python
ros2 launch fishbot_description display_robot.launch.py
```
即可打开所有节点，传入URDF，运行Rviz2.重新如同之前一样操作（RobotModel、File加载、Global Options）
也可以保存配置目录（file、save configure as），可以在功能包下新建config文件夹存放，并且修改launch文件
```python

    default_config_path = os.path.join(urdf_package_path, 'config', 对应的配置文件全名)

    action_rviz_node = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d'， default_config_path]
    )

# arguments与parameter不同，相当于在命令行运行时加上由arguments拼接的参数
# 即 ros2 run rviz2 rviz2 -d default_config_path
```

### 6.2.3 使用Xacro简化URDF
#### Xacro概述
Xacro 可以把重复的 URDF 代码打包成“宏”，传不同参数就能生成不同部件，省去复制粘贴。

#### Xacro语法
##### 命名空间声明（必须）
```xml
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="robot_name">
```
**作用**：告诉解析器这是一个 Xacro 文件，启用宏功能。

##### 宏定义
```xml
<xacro:macro name="宏名称" params="参数1 参数2 参数3">
    <!-- 这里写 URDF 代码，用 ${参数名} 引用传进来的值 -->
</xacro:macro>
```

| 部分 | 说明 |
| :--- | :--- |
| `name` | 宏的名字，调用时用 |
| `params` | 参数列表，用空格分隔 |
| `${参数名}` | 在宏内部引用参数值 |
| `</xacro:macro>` | **必须用闭合标签**，不能自闭合 |

##### 宏调用
```xml
<xacro:宏名称 参数1="值1" 参数2="值2" />
```

**示例**：
```xml
<!-- 定义 -->
<xacro:macro name="wheel" params="radius length">
    <link name="wheel_link">
        <visual>
            <geometry>
                <cylinder radius="${radius}" length="${length}"/>
            </geometry>
        </visual>
    </link>
</xacro:macro>

<!-- 调用 -->
<xacro:wheel radius="0.1" length="0.05"/>
```

##### 变量引用 `${}`
```xml
<!-- 在宏内部 -->
<origin xyz="0 0 ${height}" />
<link name="${prefix}_link" />
```

| 写法 | 含义 |
| :--- | :--- |
| `${参数名}` | 引用宏参数 |
| `${prefix}_link` | 字符串拼接（结果如 `left_wheel_link`） |

##### 数学表达式（高级）

```xml
<origin xyz="0 0 ${radius * 2}" />
<cylinder radius="${radius * 1.5}" length="${length / 2}" />
```

支持 `+`、`-`、`*`、`/` 等基本运算。

##### 文件包含（模块化）

```xml
<xacro:include filename="$(find my_pkg)/urdf/common.xacro" />
```

**作用**：把多个 Xacro 文件拆开，方便复用。比如把**颜色定义**、**传感器**、**关节**等分别放在不同文件里。

##### 条件判断（可选）

```xml
<xacro:if value="${use_camera}">
    <!-- 如果 use_camera 为 true，就包含这段代码 -->
    <xacro:include filename="camera.xacro" />
</xacro:if>
```

##### 常量定义

```xml
<xacro:property name="wheel_radius" value="0.1" />
<xacro:property name="wheel_length" value="0.05" />
```

**作用**：定义全局常量，在宏中引用 `${wheel_radius}`，方便统一修改。

---

##### 常用语法速查表

| 语法 | 示例 | 说明 |
| :--- | :--- | :--- |
| 声明命名空间 | `xmlns:xacro="http://www.ros.org/wiki/xacro"` | 必须加在 `<robot>` 标签中 |
| 定义宏 | `<xacro:macro name="M" params="a b">` | 定义可复用模板 |
| 闭合宏 | `</xacro:macro>` | **不能自闭合** |
| 调用宏 | `<xacro:M a="1" b="2"/>` | 生成实际代码 |
| 引用变量 | `${a}` | 获取参数值 |
| 字符串拼接 | `${prefix}_link` | 生成如 `left_link` |
| 数学运算 | `${radius * 2}` | 支持四则运算 |
| 包含文件 | `<xacro:include filename="path.xacro"/>` | 模块化拆分 |
| 条件判断 | `<xacro:if value="${flag}">` | 按条件包含代码 |
| 常量定义 | `<xacro:property name="pi" value="3.14159"/>` | 全局常量 |


#### Xacro的代码实现
在6.2.2的`urdf`文件夹下创建`.xacro`文件，将原本的`.urdf`文件修改为`.xacro`文件
```xml
<?xml version="1.0"?>
<!-- 机器人的总标题需要修改，加上xmlns:xacro="http://www.ros.org/wiki/xacro" -->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="first_robot">

    <!-- ========== 1. 定义 base_link 宏 ========== -->
    <!-- 作用：生成机器人身体（圆柱体） -->
    <!-- 参数：length（圆柱高度），radius（圆柱半径） -->

    <xacro:macro name="base_link" params="length radius"> <!-- 在声明宏前需要声明宏名称与参数 -->

        <!-- 余下编写同.urdf文件，不过相应的参数使用${参数}来代替 -->
        <link name="base_link">
            <visual>
                <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0"/>
                <geometry>
                    <cylinder radius="${radius}" length="${length}"/>
                </geometry>
                <material name="white">
                    <color rgba="1.0 1.0 1.0 0.5"/>
                </material>
            </visual>
        </link>

    </xacro:macro>

    <!-- ========== 2. 定义 imu_link 宏 ========== -->
    <!-- 作用：生成 IMU 传感器部件（小立方体） -->
    <!-- 参数：imu_name（部件名称前缀），xyz（安装位置偏移） -->
    <!-- 在xacro文件中，使用宏生成的部件和关节名称必须是不重复，所以此处需要将连接名和关节名参数化 -->
    <xacro:macro name="imu_link" params="imu_name xyz">

        <link name="${imu_name}_link">
            <visual>
                <origin xyz="0.0 0.0 0.0" rpy="0.0 0.0 0.0"/>
                <geometry>
                    <box size="0.02 0.02 0.02"/>
                </geometry>
                <material name="black">
                    <color rgba="0.0 0.0 0.0 0.5"/>
                </material>
            </visual>
        </link>

        <!-- 定义关节：将 imu_link 固定在 base_link 上 -->
        <joint name="${imu_name}_joint" type="fixed">
            <parent link="base_link"/>
            <child link="${imu_name}_link"/>
            <origin xyz="${xyz}" rpy="0.0 0.0 0.0"/>
        </joint>

    </xacro:macro>

    <!-- ========== 3. 调用宏，生成实际部件 ========== -->
    <!-- 注意如果没有前后的<>、<\>而是中间省略的写法即下面的使用宏，需要在最后加上/ -->
    <!-- 生成身体：圆柱高 0.12m，半径 0.1m -->
    <xacro:base_link length="0.12" radius="0.1"/>

    <!-- 生成上方 IMU：安装在 base_link 正上方 0.03m 处 -->
    <xacro:imu_link imu_name="imu_up" xyz="0.0 0.0 0.03"/>

    <!-- 生成下方 IMU：安装在 base_link 正下方 0.03m 处 -->
    <xacro:imu_link imu_name="imu_down" xyz="0.0 0.0 -0.03"/>

</robot>
```
--
#### 将Xacro转化为urdf
Xacro文件无法直接使用，需要转化为urdf文件
```bash
# 安装工具
sudo apt install ros-$ROS_DISTRO-xacro

# 转换
xacro 文件路径
```
---
#### launch文件启动
修改一下6.2.2中的launch文件中
```python
    command_cat_urdf = launch.substitutions.Command(
        ['cat ', launch.substitutions.LaunchConfiguration('model')]
    )
```
为
```python
    command_cat_urdf = launch.substitutions.Command(
        ['xacro ', launch.substitutions.LaunchConfiguration('model')]
    )
```
只需要在命令行输入
```bash
ros2 launch fishbot_description display_robot.launch.py model:=xacro文件路径名
```

## 6.2.4 创建机器人及传感器部件