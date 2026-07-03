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

### 6.2.4 创建机器人及传感器部件
#### 传感器部件
在本章功能包的`urdf`文件夹下创建新的一个`fishbot`文件夹，再新建`base.xacro`；随后再创建一个专门用于存放传感器的文件夹`sensor`，创建文件`imu.xacro`、`camera.xacro`和`laser.xacro`
>注：文件后缀名也可以写成`.urdf.xacro`

##### base.xacro文件
```xml
<?xml version="1.0"?>
<!-- 由于只是定义一个模块，所以此处无需robot_name -->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    
    <!-- 定义 base_link 宏 -->
    <xacro:macro name="base_xacro" params="length radius">

        <link name="base_link">
            <visual>
                <origin xyz="0 0 0.0" rpy="0 0 0" />
                <geometry>
                    <cylinder length="${length}" radius="${radius}" />
                </geometry>
                <material name="white">
                    <color rgba="1.0 1.0 1.0 0.5"/>
                </material>
            </visual>
        </link>

    </xacro:macro>
    
</robot>
```
##### sensor文件下的imu.xacro
将6.2.3中的imu模块复制过来修改即可
```xml
<?xml version="1.0"?>
<!-- 由于只是定义一个模块，所以此处无需robot_name -->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    
    <!-- 定义 IMU 传感器宏 -->
    <xacro:macro name="imu_xacro" params="xyz">
        <link name="imu_link">
            <visual>
                <origin xyz="0 0 0" rpy="0 0 0" />
                <geometry>
                    <box size="0.02 0.02 0.02" />
                </geometry>
                <material name="black">
                    <color rgba="0 0 0 0.8" />
                </material>
            </visual>
        </link>
        
        <joint name="imu_joint" type="fixed">
            <parent link="base_link" />
            <child link="imu_link" />
            <!-- 修复：$(xyz) → ${xyz}，并补全 rpy -->
            <origin xyz="${xyz}" rpy="0 0 0" />
        </joint>
    </xacro:macro>
    
</robot>
```
##### sensor文件下的camere.xacro
```xml
<?xml version="1.0"?>
<!-- 由于只是定义一个模块，所以此处无需robot_name -->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    
    <!-- 定义相机传感器宏，具体细节同imu模块，只需要修改名称和位置即可 -->
    <xacro:macro name="camera_xacro" params="xyz">
        <!-- 相机部件 -->
        <link name="camera_link">
            <visual>
                <origin xyz="0 0 0.0" rpy="0 0 0" />
                <geometry>
                    <box size="0.02 0.10 0.02" />
                </geometry>
                <material name="green">
                    <color rgba="0.0 1.0 0.0 0.8" />
                </material>
            </visual>
        </link>
        
        <!-- 相机固定关节 -->
        <joint name="camera_joint" type="fixed">
            <parent link="base_link" />
            <child link="camera_link" />
            <origin xyz="${xyz}" rpy="0 0 0" />
        </joint>
    </xacro:macro>
    
</robot>
```
##### sensor文件夹下的laser.xacro
```xml
<?xml version="1.0"?>
<!-- 由于只是定义一个模块，所以此处无需robot_name -->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    
    <!-- 定义激光雷达宏 -->
    <xacro:macro name="laser_xacro" params="xyz">
        
        <!-- ====== 1. 雷达支撑杆 ====== -->
        <link name="laser_cylinder_link">
            <visual>
                <origin xyz="0 0 0" rpy="0 0 0" />
                <geometry>
                    <cylinder length="0.10" radius="0.01" />
                </geometry>
                <material name="green">
                    <color rgba="0.0 1.0 0.0 0.8" />
                </material>
            </visual>
        </link>
        
        <!-- 支撑杆固定关节（固定在 base_link 上） -->
        <!-- 雷达通过一个杆子固定在base上，所有有两个关节 -->
        <joint name="laser_cylinder_joint" type="fixed">
            <parent link="base_link" />
            <child link="laser_cylinder_link" />
            <!-- 修复：{$xyz} → ${xyz}，并补全 rpy -->
            <origin xyz="${xyz}" rpy="0 0 0" />
        </joint>
        
        <!-- ====== 2. 雷达主体 ====== -->
        <link name="laser_link">
            <visual>
                <origin xyz="0 0 0" rpy="0 0 0" />
                <geometry>
                    <cylinder length="0.02" radius="0.02" />
                </geometry>
                <material name="green">
                    <color rgba="0.0 1.0 0.0 0.8" />
                </material>
            </visual>
        </link>
        
        <!-- 雷达主体固定关节（固定在支撑杆顶端） -->
        <joint name="laser_joint" type="fixed">
            <parent link="laser_cylinder_link" />
            <child link="laser_link" />
            <origin xyz="0 0 0.05" rpy="0 0 0" />
        </joint>
        
    </xacro:macro>
    
</robot>
```

#### 机器人组装
在fishbot.xarco文件下
```xml
<?xml version="1.0"?>
<!-- 组装机器人需要name -->
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="fishbot">
    
    <!-- ========== 1. 包含所有零部件宏文件 ========== -->
    <!-- 注意：使用 $(find 包名) 语法查找功能包路径，注意括号和空格 -->
    <!-- $(find fishbot_description)即功能包的共享目录 -->
    <!-- 后续填写上文件目录即可 -->
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/base.urdf.xacro" />
    
    <!-- 传感器组件 -->
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/sensor/imu.urdf.xacro" />
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/sensor/laser.urdf.xacro" />
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/sensor/camera.urdf.xacro" />

    <!-- ========== 2. 调用宏生成各部件 ========== -->
    <!-- 宏调用格式：<xacro:宏名称 参数1="值1" 参数2="值2" ... />   -->
    <!-- 机器人身体：高 0.12m，半径 0.10m -->
    <xacro:base_xacro length="0.12" radius="0.1" />
    
    <!-- 传感器安装 -->
    <xacro:imu_xacro xyz="0 0 0.02" />        <!-- IMU 安装在身体上方 0.02m -->
    <xacro:laser_xacro xyz="0 0 0.10" />      <!-- 激光雷达安装在身体上方 0.10m -->
    <xacro:camera_xacro xyz="0.10 0 0.075" /> <!-- 相机安装在身体前方 0.10m，上方 0.075m -->

</robot>
```
#### 效果展示
输入
```bash
ros2 launch fishbot_description display_robot.launch.py model:=/home/fishros/chapt6/chapt6_ws/install/fishbot_description/share/fishbot_description/urdf/fishbot/fishbot.urdf.xacro
```

### 6.2.5 完善机器人执行器部件
#### 执行器
在`urdf/fishbot`文件下新建`actuator`文件夹，在其中新建文件`wheel.xacro`和`caster.xacro`
##### fishbot/actuator/wheel.urdf.xacro
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    <!-- 定义车轮宏 -->
    <!-- wheel_name: 车轮名称前缀（如 left/right），xyz: 安装位置偏移 -->
    <xacro:macro name="wheel_xacro" params="wheel_name xyz">
        <!-- 车轮部件 -->
        <link name="${wheel_name}_wheel_link">
            <visual>
                <!-- 绕 X 轴旋转 90°（1.57079 弧度），让圆柱体的轴指向 Y 方向 -->
                <origin xyz="0 0 0" rpy="1.57079 0 0" />
                <geometry>
                    <cylinder length="0.04" radius="0.032" />
                </geometry>
                <material name="yellow">
                    <color rgba="1.0 1.0 0.0 0.8" />
                </material>
            </visual>
        </link>

        <!-- 车轮关节（连续旋转关节，可无限转动即为continuous） -->
        <joint name="${wheel_name}_wheel_joint" type="continuous">
            <parent link="base_link" />
            <child link="${wheel_name}_wheel_link" />
            <origin xyz="${xyz}" />
            <!-- 绕 Y 轴旋转（车轮滚动方向） -->
            <axis xyz="0 1 0" />
        </joint>
    </xacro:macro>
</robot>
```
##### fishbot/actuator/caster.urdf.xacro
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    <!-- 定义万向轮宏 -->
    <!-- caster_name: 万向轮名称前缀（如 front/back），xyz: 安装位置偏移 -->
    <xacro:macro name="caster_xacro" params="caster_name xyz">
        <!-- 万向轮部件 -->
        <link name="${caster_name}_caster_link">
            <visual>
                <origin xyz="0 0 0" rpy="0 0 0" />
                <geometry>
                    <!-- 万向轮：球体，半径 0.016m -->
                    <sphere radius="0.016" />
                </geometry>
                <material name="yellow">
                    <color rgba="1.0 1.0 0.0 0.8" />
                </material>
            </visual>
        </link>
        <!-- 万向轮关节（固定关节） -->
        <joint name="${caster_name}_caster_joint" type="fixed">
            <parent link="base_link" />
            <child link="${caster_name}_caster_link" />
            <origin xyz="${xyz}" />
            <!-- 固定关节不需要旋转轴，设为 0 0 0 -->
            <axis xyz="0 0 0" />
        </joint>
    </xacro:macro>
</robot>
```
#### 组装——fishbot/actuator/fishbot.urdf.xacro
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="fishbot">
    
    <!-- ========== 1. 包含宏文件 ========== -->
    <!-- 基础部件（身体） -->
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/base.urdf.xacro" />
    
    <!-- 传感器 -->
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/sensor/imu.urdf.xacro" />
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/sensor/laser.urdf.xacro" />
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/sensor/camera.urdf.xacro" />
    
    <!-- 执行器 -->
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/actuator/wheel.urdf.xacro" />
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/actuator/caster.urdf.xacro" />


    <!-- ========== 2. 调用宏生成各部件 ========== -->
    <!-- 机器人身体 -->
    <xacro:base_xacro length="0.12" radius="0.1" />
    
    <!-- 传感器 -->
    <xacro:imu_xacro xyz="0 0 0.02" />
    <xacro:laser_xacro xyz="0 0 0.10" />
    <xacro:camera_xacro xyz="0.10 0 0.075" />
    
    <!-- 执行器（主动轮 + 万向轮） -->
    <!-- 左轮：车身左侧 0.10m，下方 0.06m -->
    <xacro:wheel_xacro wheel_name="left" xyz="0 0.10 -0.06" />
    <!-- 右轮：车身右侧 0.10m，下方 0.06m -->
    <xacro:wheel_xacro wheel_name="right" xyz="0 -0.10 -0.06" />
    <!-- 轮子的半径刚好是base的一半 -->
    
    <!-- 前万向轮：车身前方 0.08m，下方 0.076m -->
    <xacro:caster_xacro caster_name="front" xyz="0.08 0.0 -0.076" />
    <!-- 后万向轮：车身后方 0.08m，下方 0.076m -->
    <xacro:caster_xacro caster_name="back" xyz="-0.08 0.0 -0.076" />

</robot>
```
### 6.2.6 贴合地面，添加虚拟部件

在仿真环境中，为了让机器人的轮子刚好贴合地面，同时为后续物理引擎提供一个准确的基准点，我们需要引入一个**虚拟部件（Virtual Link）**——`base_footprint`。
#### 问题现象：轮子陷入地面
在 RViz 中观察机器人时，如果直接将 `base_link` 的原点放在地面上，由于 `base_link` 通常是一个圆柱体，其几何中心位于圆柱体的中点，因此模型的下半部分会穿过地面，导致轮子看起来是陷入地下的。

#### 解决方案：添加 `base_footprint` 虚拟部件

`base_footprint` 是一个**空部件（Empty Link）**，它不包含任何几何形状，只作为一个坐标系参考点。它的作用是将机器人的**实际接地位置**与**视觉模型**分离开来。

- `base_footprint` 位于地面上（z = 0），代表机器人在世界中的真实位置。
- `base_link` 通过一个固定关节 `base_joint` 连接到 `base_footprint` 上方，偏移量为 `length/2.0 + 轮子半径 - 0.001`。

#### 修改后的 `base.urdf.xacro` 代码
在 `src/fishbot_description/urdf/fishbot/base.urdf.xacro` 中，添加以下内容：

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    <xacro:macro name="base_xacro" params="length radius">
        
        <!-- 1. 声明空部件 base_footprint（虚拟地面接触点） -->
        <!-- 虚拟存在，内容为空 -->
        <link name="base_footprint" />
        
        <!-- 2. 固定关节：将 base_link 连接在 base_footprint 上方 -->
        <!-- 其x、y与base_link相同；但是z -->
        <joint name="base_joint" type="fixed">
            <parent link="base_footprint" />
            <child link="base_link" />
            <!-- 高度偏移 = 身体高度的一半 + 轮子半径 - 1mm（让轮子刚好贴地） -->
            <origin xyz="0.0 0.0 ${length/2.0 + 0.032 - 0.001}" rpy="0 0 0" />
        </joint>

        <!-- 3. 原有的 base_link 定义 -->
        <link name="base_link">
            <visual>
                <origin xyz="0 0 0.0" rpy="0 0 0" />
                <geometry>
                    <cylinder length="${length}" radius="${radius}" />
                </geometry>
                <material name="white">
                    <color rgba="1.0 1.0 1.0 0.5" />
                </material>
            </visual>
        </link>
        
    </xacro:macro>
</robot>
```
#### RViz 配置调整

- 在 RViz 的 **Global Options** 中，将 **Fixed Frame** 从 `base_link` 改为 **`base_footprint`**。
- 此时，`base_footprint` 成为机器人的根坐标系，所有关节和部件的位置都基于此参考。

#### 验证结果

- 轮子不再陷入地面，而是刚好贴合地面。
- 机器人的移动和旋转将以 `base_footprint` 为基准，符合真实机器人的运动学特性。

## 6.3 添加物理属性让机器人更真实
### 6.3.1 为机器人部件添加碰撞属性
在 Gazebo 等物理仿真环境中，机器人需要与其他物体（如地面、障碍物）发生接触和碰撞。为了让物理引擎能够正确计算碰撞响应，必须在 URDF 中为每个部件**添加碰撞属性**。
#### 概念介绍

| 属性 | 作用 | 说明 |
| :--- | :--- | :--- |
| **visual** | 定义部件的**可视化外观** | 用于 RViz 等工具显示，不影响物理交互 |
| **collision** | 定义部件的**碰撞模型** | 用于 Gazebo 等物理引擎计算碰撞响应，可以简化形状以提升性能 |

> **注意**：`collision` 的形状可以与 `visual` 相同，也可以根据实际需要设置成更简单的几何体（如用盒体代替复杂网格），以降低计算开销。

#### 实现步骤
在 `link` 标签下添加 `collision` 子标签，内容与 `visual` 基本一致：

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    <xacro:macro name="base_xacro" params="length radius">
        
        <!-- base_footprint 虚拟地面接触点 -->
        <link name="base_footprint" />
        
        <!-- base_joint 固定关节 -->
        <joint name="base_joint" type="fixed">
            <parent link="base_footprint" />
            <child link="base_link" />
            <origin xyz="0.0 0.0 ${length/2.0 + 0.032 - 0.001}" rpy="0 0 0" />
        </joint>

        <!-- base_link 主体 -->
        <link name="base_link">
            <!-- 可视化外观 -->
            <visual>
                <origin xyz="0 0 0.0" rpy="0 0 0" />
                <geometry>
                    <cylinder length="${length}" radius="${radius}" />
                </geometry>
                <material name="white">
                    <color rgba="1.0 1.0 1.0 0.5" />
                </material>
            </visual>
            
            <!-- 碰撞属性（与 visual 一致） -->
            <collision>
                <origin xyz="0 0 0.0" rpy="0 0 0" />
                <geometry>
                    <cylinder length="${length}" radius="${radius}" />
                </geometry>
                <material name="white">
                    <color rgba="1.0 1.0 1.0 0.5" />
                </material>
            </collision>
        </link>
        
    </xacro:macro>
</robot>
```
#### 其他部件添加碰撞属性（轮子、传感器等）

使用同样的方法，在 `wheel.urdf.xacro`、`imu.urdf.xacro`、`laser.urdf.xacro`、`camera.urdf.xacro` 等文件中，为每个 `link` 添加 `<collision>` 标签。

#### 在 RViz 中验证碰撞模型

1. 重新构建并运行 launch 文件：
   ```bash
   colcon build --packages-select fishbot_description
   source install/setup.bash
   ros2 launch fishbot_description display_robot.launch.py
   ```

2. 在 RViz 中，打开 **RobotModel** 显示插件配置面板：
   - **取消勾选** `Visual Enabled` → 隐藏可视化外观
   - **勾选** `Collision Enabled` → 显示碰撞模型

3. 若碰撞模型与外观一致，说明添加成功（如图 6-14 所示）。

### 6.3.2 为机器人部件添加质量与惯性
在 Gazebo 等物理仿真环境中，机器人部件不仅需要碰撞属性，还需要**质量（mass）** 和**惯性（inertia）** 属性。质量决定重力响应，惯性决定旋转运动的加速度响应。

#### 惯性矩阵简介

惯性矩阵是一个 \(3 \times 3\) 的对称矩阵，用于描述物体在三维空间中的旋转惯性：

\[
I = 
\begin{pmatrix}
I_{xx} & I_{xy} & I_{xz} \\
I_{xy} & I_{yy} & I_{yz} \\
I_{xz} & I_{yz} & I_{zz}
\end{pmatrix}
\]

由于矩阵对称（\(I_{xy}=I_{yx}\)、\(I_{xz}=I_{zx}\)、\(I_{yz}=I_{zy}\)），因此只需要 6 个独立数据即可完整描述。


#### 常见几何体的惯性矩阵计算公式

| 几何体 | 参数 | 惯性矩阵 |
| :--- | :--- | :--- |
| **长方体** | 质量 \(m\)，宽 \(w\)，高 \(h\)，长 \(d\) | \(I_{xx} = \frac{m}{12}(h^2+d^2)\)，\(I_{yy} = \frac{m}{12}(w^2+d^2)\)，\(I_{zz} = \frac{m}{12}(w^2+h^2)\)，其余为 0 |
| **圆柱体** | 质量 \(m\)，半径 \(r\)，高度 \(h\) | \(I_{xx}=I_{yy} = \frac{m}{12}(3r^2+h^2)\)，\(I_{zz} = \frac{m r^2}{2}\)，其余为 0 |
| **球体** | 质量 \(m\)，半径 \(r\) | \(I_{xx}=I_{yy}=I_{zz} = \frac{2}{5} m r^2\)，其余为 0 |

#### 定义质量与惯性宏
在 `urdf/fishbot/` 目录下新建 `common_inertia.xacro` 文件，定义质量与惯性的宏：

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">

    <!-- 长方体惯性宏 -->
    <!-- m: 质量(kg), w: 宽(m), h: 高(m), d: 长(m) -->
    <xacro:macro name="box_inertia" params="m w h d">
        <inertial>
            <mass value="${m}" />
            <inertia ixx="${m/12.0 * (h*h + d*d)}" ixy="0.0" ixz="0.0"
                     iyy="${m/12.0 * (w*w + d*d)}" iyz="0.0"
                     izz="${m/12.0 * (w*w + h*h)}" />
        </inertial>
    </xacro:macro>

    <!-- 圆柱体惯性宏 -->
    <!-- m: 质量(kg), r: 半径(m), h: 高度(m) -->
    <xacro:macro name="cylinder_inertia" params="m r h">
        <inertial>
            <mass value="${m}" />
            <inertia ixx="${m/12.0 * (3*r*r + h*h)}" ixy="0.0" ixz="0.0"
                     iyy="${m/12.0 * (3*r*r + h*h)}" iyz="0.0"
                     izz="${m/2.0 * r*r}" />
        </inertial>
    </xacro:macro>

    <!-- 球体惯性宏 -->
    <!-- m: 质量(kg), r: 半径(m) -->
    <xacro:macro name="sphere_inertia" params="m r">
        <inertial>
            <mass value="${m}" />
            <inertia ixx="${2.0/5.0 * m * r*r}" ixy="0.0" ixz="0.0"
                     iyy="${2.0/5.0 * m * r*r}" iyz="0.0"
                     izz="${2.0/5.0 * m * r*r}" />
        </inertial>
    </xacro:macro>

</robot>
```


#### 为各个部件添加质量与惯性
- 在每个部件的`.xacro`文件中，首先导入上述的宏文件
- 再在<link>之中引用宏
```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro">
    
    <!-- 1. 导入惯性宏定义文件 -->
    <xacro:include filename="$(find fishbot_description)/urdf/fishbot/common_inertia.xacro" />
    
    <xacro:macro name="base_xacro" params="length radius">
        
        <!-- base_footprint 虚拟地面接触点 -->
        <link name="base_footprint" />
        
        <!-- base_joint 固定关节 -->
        <joint name="base_joint" type="fixed">
            <parent link="base_footprint" />
            <child link="base_link" />
            <origin xyz="0.0 0.0 ${length/2.0 + 0.032 - 0.001}" rpy="0 0 0" />
        </joint>

        <!-- base_link 主体 -->
        <link name="base_link">
            <!-- 可视化外观 -->
            <visual>
                <origin xyz="0 0 0.0" rpy="0 0 0" />
                <geometry>
                    <cylinder length="${length}" radius="${radius}" />
                </geometry>
                <material name="white">
                    <color rgba="1.0 1.0 1.0 0.5" />
                </material>
            </visual>
            
            <!-- 碰撞属性 -->
            <collision>
                <origin xyz="0 0 0.0" rpy="0 0 0" />
                <geometry>
                    <cylinder length="${length}" radius="${radius}" />
                </geometry>
            </collision>

            <!-- ✅ 添加质量与惯性（圆柱体惯性宏） -->
            <!-- 质量设为 1.0 kg，半径和高度由宏参数传入 -->
            <xacro:cylinder_inertia m="1.0" r="${radius}" h="${length}" />
        </link>
        
    </xacro:macro>
</robot>
```

#### 其他部件修改示例

**车轮（wheel.urdf.xacro）**：
```xml
<link name="${wheel_name}_wheel_link">
    <!-- visual、collision 保持不变 -->
    <xacro:cylinder_inertia m="0.05" r="0.032" h="0.04" />
</link>
```

**IMU（imu.urdf.xacro）**：
```xml
<link name="imu_link">
    <!-- visual、collision 保持不变 -->
    <xacro:box_inertia m="0.01" w="0.02" h="0.02" d="0.02" />
</link>
```

**万向轮（caster.urdf.xacro）**：
```xml
<link name="${caster_name}_caster_link">
    <!-- visual、collision 保持不变 -->
    <xacro:sphere_inertia m="0.015" r="0.016" />
</link>
```

---

#### 在 RViz 中查看质量和惯性

1. 重新构建并运行 launch：
   ```bash
   colcon build --packages-select fishbot_description
   source install/setup.bash
   ros2 launch fishbot_description display_robot.launch.py
   ```

2. 在 RViz 的 **RobotModel** 配置面板中：
   - 取消勾选 `Visual Enabled`，隐藏外观
   - 勾选 `Mass Properties` → 显示质量分布![alt text](image-23.png)
   - 勾选 `Inertia` → 显示惯性张量![alt text](image-24.png)

3. 将鼠标悬停在部件上，可以查看具体数值。


## 6.4 在 Gazebo 中完成机器人仿真
Gazebo 是 ROS 2 生态中最常用的物理仿真软件，支持刚体动力学、碰撞检测、传感器仿真等功能，与 ROS 2 的集成最为成熟。
### 6.4.1 安装与使用 Gazebo 构建世界
#### 安装 Gazebo

```bash
sudo apt install gazebo
```

#### 下载 Gazebo 模型库

```bash
mkdir -p ~/.gazebo
cd ~/.gazebo
git clone https://gitee.com/ohhuo/gazebo_models.git ~/.gazebo/models
rm -rf ~/.gazebo/models/.git   # 删除 .git 防止误识别为模型
```

#### 启动 Gazebo

```bash
gazebo
```

启动后默认加载空世界（Empty World）。

#### 插入模型

- 点击左侧 **Insert** 选项卡
- 选择模型（如 `Ambulance`）
- 在场景中单击即可放置
- 右键模型 → **Delete** 可移除

#### 构建自定义房间（Building Editor）

1. **进入编辑模式**：工具栏 → **Edit** → **Building Editor**
2. **绘制墙体**：左侧选择 **Create Walls** → **Wall**，在右上角绘制房间
3. **退出并保存**：选择 **File** → **Exit Building Editor**
   - 弹出对话框时选择 **Save and Exit**
   - 输入模型名称（如 `room`）
   - 选择保存位置：`fishbot_description` 功能包目录下新建 `world` 文件夹
   - 单击 **Save** 保存

#### 保存 Gazebo 世界

1. **File** → **Save World As**
2. 选择 `fishbot_description/world/` 目录
3. 命名为 `custom_room.world`
4. 单击 **Save**

下次启动时可直接加载该世界：

```bash
gazebo src/fishbot_description/world/custom_room.world
```

### SDF 文件格式简介

Gazebo 使用的模型描述格式为 **SDF（Simulation Description Format）**，它与 URDF 结构相似，但功能更丰富（支持光源、物理参数、传感器等）。

**世界文件（.world）** 和 **模型文件（model.sdf）** 均为 XML 格式：

```xml
<sdf version='1.7'>
    <world name='default'>
        <link name='link'>
            <collision name='collision'>
                <geometry>...</geometry>
            </collision>
            <visual name='visual'>
                <geometry>...</geometry>
                <material>...</material>
            </visual>
        </link>
    </world>
</sdf>
```

> **注意**：SDF 继承了 URDF 的 `<link>`、`<visual>`、`<collision>` 等标签，并扩展了更多仿真相关属性。

---

### 常用 Gazebo 命令总结

| 命令 | 作用 |
| :--- | :--- |
| `gazebo` | 启动 Gazebo（空世界） |
| `gazebo <世界文件路径>` | 加载指定世界文件 |
| `sudo apt install gazebo` | 安装 Gazebo |
| `killall gzserver` | 强制关闭 Gazebo 后端进程 |

## 6.4.2 在 Gazebo 中加载机器人模型

Gazebo 使用 SDF 格式描述模型，而机器人建模使用的是 URDF。ROS 2 提供了 `gazebo-ros-pkgs` 功能包，可自动完成 URDF 到 SDF 的转换。

### 安装 gazebo-ros-pkgs 插件

```bash
sudo apt install ros-$ROS_DISTRO-gazebo-ros-pkgs
```

### 创建 Gazebo 仿真启动文件

在 `src/fishbot_description/launch/` 下新建 `gazebo_sim.launch.py`：

```python
import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # 获取功能包路径
    robot_name_in_model = "fishbot"
    urdf_tutorial_path = get_package_share_directory('fishbot_description')
    default_model_path = urdf_tutorial_path + '/urdf/fishbot/fishbot.urdf.xacro'
    default_world_path = urdf_tutorial_path + '/world/custom_room.world'

    # 声明 launch 参数（支持命令行传入模型路径）
    action_declare_arg_mode_path = launch.actions.DeclareLaunchArgument(
        name='model', default_value=str(default_model_path),
        description='URDF 的绝对路径'
    )

    # 使用 xacro 展开 URDF，生成 robot_description 参数
    robot_description = launch_ros.parameter_descriptions.ParameterValue(
        launch.substitutions.Command(
            ['xacro ', launch.substitutions.LaunchConfiguration('model')]
        ),
        value_type=str
    )

    # 启动 robot_state_publisher，发布 /robot_description 话题
    robot_state_publisher_node = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description}]
    )

    # 包含 gazebo.launch.py（启动 Gazebo 并加载世界）
    launch_gazebo = launch.actions.IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            [get_package_share_directory('gazebo_ros'), '/launch', '/gazebo.launch.py']
        ),
        launch_arguments={
            'world': default_world_path,
            'verbose': 'true'
        }.items()
    )

    # 请求 Gazebo 加载机器人（从 /robot_description 话题获取 URDF）
    spawn_entity_node = launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', '/robot_description',
            '-entity', robot_name_in_model,
        ]
    )

    return launch.LaunchDescription([
        action_declare_arg_mode_path,
        robot_state_publisher_node,
        launch_gazebo,
        spawn_entity_node
    ])
```

### 关键节点说明

| 节点/操作 | 作用 |
| :--- | :--- |
| `robot_state_publisher` | 加载 URDF 并发布到 `/robot_description` 话题 |
| `IncludeLaunchDescription` | 包含 `gazebo.launch.py`，启动 Gazebo 并加载世界 |
| `spawn_entity.py` | 从 `/robot_description` 获取 URDF，转换为 SDF 并加载到 Gazebo |

### 修改 CMakeLists.txt

确保 `world` 目录被安装到功能包目录下：

```cmake
install(DIRECTORY world launch urdf
    DESTINATION share/${PROJECT_NAME}
)
```

### 启动 Gazebo 仿真

```bash
colcon build --packages-select fishbot_description
source install/setup.bash
ros2 launch fishbot_description gazebo_sim.launch.py
```

此时机器人在 Gazebo 中显示（如图 6-29 所示），但颜色为默认白色，因为部分 URDF 标签未自动转换。

---

## 6.4.3 使用 Gazebo 标签扩展 URDF

`<gazebo>` 标签用于向 Gazebo 传递配置，可修改颜色、物理属性或添加插件。

### 修改传感器颜色

在 `laser.urdf.xacro` 中添加 `<gazebo>` 标签，将雷达改为黑色：

```xml
<xacro:macro name="laser_xacro" params="xyz">
    <!-- 原有内容保持不变 -->

    <!-- 修改雷达支撑杆颜色 -->
    <gazebo reference="laser_cylinder_link">
        <material>Gazebo/Black</material>
    </gazebo>

    <!-- 修改雷达主体颜色 -->
    <gazebo reference="laser_link">
        <material>Gazebo/Black</material>
    </gazebo>
</xacro:macro>
```

> 除 `Gazebo/Black` 外，还可使用 `Gazebo/Blue`、`Gazebo/Red`、`Gazebo/Green` 等内置颜色。

### 修改轮子摩擦系数（橡胶材质）

在 `wheel.urdf.xacro` 中添加摩擦配置，提高切向/法向摩擦系数：

```xml
<xacro:macro name="wheel_xacro" params="wheel_name xyz">
    <!-- 原有内容保持不变 -->

    <gazebo reference="${wheel_name}_wheel_link">
        <mu1 value="20.0" />      <!-- 切向摩擦系数 -->
        <mu2 value="20.0" />      <!-- 法向摩擦系数 -->
        <kp value="1000000000.0" /> <!-- 接触刚度 -->
        <kd value="1.0" />          <!-- 阻尼系数 -->
    </gazebo>
</xacro:macro>
```

### 修改万向轮（支撑作用，摩擦力为零）

在 `caster.urdf.xacro` 中将摩擦力设置为 0：

```xml
<xacro:macro name="caster_xacro" params="caster_name xyz">
    <!-- 原有内容保持不变 -->

    <gazebo reference="${caster_name}_caster_link">
        <mu1 value="0.0" />
        <mu2 value="0.0" />
        <kp value="1000000000.0" />
        <kd value="1.0" />
    </gazebo>
</xacro:macro>
```

### Gazebo 标签常用配置项

| 子标签 | 作用 | 默认值 |
| :--- | :--- | :--- |
| `mu1` | 切向摩擦系数 | 1.0 |
| `mu2` | 法向摩擦系数 | 1.0 |
| `kp` | 接触刚度系数 | 1e12 |
| `kd` | 阻尼系数 | 1.0 |
| `material` | 材质颜色 | 根据 URDF 设置 |

完成修改后重新构建并启动仿真，即可看到颜色变化和物理效果调整（如图 6-30 所示）。😊