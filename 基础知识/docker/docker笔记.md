# Docker基础使用
## 1. Docker 基础概念

### 1.1 Docker 概述

Docker 是一种成熟高效的软件部署技术，利用**容器化**技术为应用程序封装独立的运行环境。每个运行环境称为一个**容器**，承载容器运行的计算机称为**宿主机**。

### 1.2 容器与虚拟机的区别

| 特性 | Docker 容器 | 虚拟机 |
| :--- | :--- | :--- |
| 内核 | 多个容器共享同一个系统内核 | 每个虚拟机包含一个完整的操作系统内核 |
| 资源占用 | 轻量，占用空间小 | 重量，占用空间大 |
| 启动速度 | 快（毫秒级） | 慢（秒级甚至分钟级） |

### 1.3 镜像 (Image)

- **定义**：镜像是容器的模板，可类比为软件安装包。
- **类比**：类似于制作糕点的模具，可用于创建多个糕点（容器），并可分享给他人。

### 1.4 容器 (Container)

- **定义**：容器是基于镜像运行的应用程序实例，可类比为安装好的软件。
- **类比**：类似于模具制作出的糕点。

### 1.5 Docker 仓库 (Registry)

- **定义**：用于存放和分享 Docker 镜像的场所。
- **Docker Hub**：Docker 的官方公共仓库，存储了大量用户分享的 Docker 镜像。

---

## 2. Docker 安装

> **运行环境**：Docker 通常基于 Linux 容器化技术。在 Windows 和 Mac 电脑上，Docker 通过虚拟化一个 Linux 子系统来运行。  
> **推荐环境**：Linux 系统宿主机是最佳的 Docker 实战环境。

### 2.1 Linux 系统安装

1. 访问 [getdocker.com](https://getdocker.com) 获取安装脚本。
2. 执行安装脚本（示例）：
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```
3. 安装完成后，若非 root 用户，需在所有 `docker` 命令前添加 `sudo` 以获取管理员权限。

### 2.2 Windows 系统安装

1. **启用 Windows 功能**：勾选“Virtual Machine Platform”（虚拟机平台）和“适用于 Linux 的 Windows 子系统”（WSL）。
2. **重启电脑**：根据提示完成重启。
3. **安装 WSL**（以管理员身份打开命令提示符 CMD）：
   ```bash
   wsl --set-default-version 2
   wsl --update --web-download   # 国内网络建议添加 --web-download 减少下载失败
   ```
4. **下载并安装 Docker Desktop**：从官方网站下载对应 CPU 架构的安装包（Windows 通常为 AMD64），按提示完成安装。
5. **启动 Docker Desktop**：需保持 Docker Desktop 软件运行。
6. **验证安装**：在 Windows 终端输入：
   ```bash
   docker --version
   ```
   若能打印版本号则表示安装成功。

---

## 3. Docker 镜像管理命令

### 3.1 `docker pull` - 下载镜像

**功能**：从 Docker 仓库下载镜像到本地。

**镜像名称构成**：一个完整的镜像名称包含四部分：
```
[registry_address/][namespace/]image_name[:tag]
```
- `registry_address`：Docker 仓库的注册表地址。`docker.io` 表示 Docker Hub 官方仓库，可省略。
- `namespace`：命名空间，通常是作者或组织名称。`library` 是 Docker 官方仓库的命名空间，可省略。
- `image_name`：镜像的名称。
- `tag`：镜像的标签名，通常表示版本号。`latest` 表示最新版本，可省略。

**示例**：
```bash
docker pull nginx              # 从 Docker Hub 官方仓库下载最新版 Nginx 镜像
docker pull n8n/n8n            # 从 n8n 的私有仓库下载 n8n 镜像
```

**Docker Hub 网站**：[hub.docker.com](https://hub.docker.com) 是官方仓库，可搜索、查看镜像详情（如官方镜像、版本号、使用说明）。

**Registry（注册表）与 Repository（镜像库）**：
- **Registry**：整个 Docker Hub 网站可视为一个 Registry。
- **Repository**：一个 Repository（如 Nginx）存储了同一个镜像的不同版本。

**网络问题解决方案（镜像站配置）**：
- **Linux**：修改 `/etc/docker/daemon.json`，添加：
  ```json
  {
    "registry-mirrors": ["https://<your-mirror-address>"]
  }
  ```
  然后重启 Docker 服务：`sudo systemctl restart docker`
- **Windows / Mac**：在 Docker Desktop 的设置中，进入“Docker Engine”配置项，在 `registry-mirrors` 中添加镜像站地址，点击“Apply & Restart”。

### 3.2 `docker images` - 列出本地镜像

```bash
docker images
```

### 3.3 `docker rmi` - 删除镜像

```bash
docker rmi <镜像名称或ID>
```

### 3.4 镜像 CPU 架构（`--platform`）

- **背景**：Docker 镜像在不同的 CPU 架构（如 AMD64、ARM64）下有不同的版本。
- **默认行为**：`docker pull` 默认自动选择最适合当前宿主机 CPU 架构的镜像。
- **特殊情况**：
  - 对于某些低功耗迷你主机（如香橙派），其 CPU 架构通常为 ARM64，需确认所需镜像是否提供 ARM64 版本。
  - Mac 电脑（ARM64 架构）的 Docker Desktop 会使用 QEMU 模拟 x86-64 指令集以兼容部分 AMD64 镜像，但可能存在兼容性或性能开销。

---

## 4. Docker 容器管理命令

### 4.1 `docker run` - 创建并运行容器（最重要命令）

**功能**：使用指定的镜像创建并运行一个容器。  
**自动拉取**：如果本地不存在指定镜像，`docker run` 会先自动拉取镜像，再创建并运行容器。

**查看容器**：
```bash
docker ps          # 查看正在运行的容器
docker ps -a       # 查看所有容器（包括正在运行和已停止的）
```

`docker ps` 输出信息包括：`Container ID`（容器唯一ID）、`Image`（基于哪个镜像创建）、`Names`（容器名称）。

#### 常用选项详解

| 选项 | 功能 | 示例 |
| :--- | :--- | :--- |
| `-d` | 后台运行（Detached Mode），不阻塞终端 | `docker run -d nginx` |
| `-p` | 端口映射：`<宿主机端口>:<容器内部端口>` | `docker run -p 80:80 nginx` |
| `-v` | 挂载卷（数据持久化） | 见下文 |
| `-e` | 设置环境变量 | `docker run -e MY_VAR=value nginx` |
| `--name` | 为容器指定自定义名称（宿主机上唯一） | `docker run --name my_nginx nginx` |
| `-it` | 交互式终端（用于调试） | `docker run -it ubuntu /bin/bash` |
| `--rm` | 容器停止后自动删除 | `docker run --rm -it ubuntu /bin/bash` |
| `--restart` | 重启策略 | `docker run --restart unless-stopped nginx` |

**重启策略说明**：
- `always`：只要容器停止（包括内部错误、宿主机断电等），立即重启。
- `unless-stopped`：除非手动停止容器，否则都会尝试重启（生产环境推荐）。

#### 挂载卷详解（`-v`）

**目的**：实现数据的**持久化保存**。容器删除时内部数据会丢失，挂载卷可将数据保存在宿主机上。

- **绑定挂载 (Bind Mount)**：直接指定宿主机目录路径。
  ```bash
  docker run -v /宿主机/绝对路径:/容器内路径 ...
  ```
  > 注意：宿主机目录内容会覆盖容器内对应目录的原始内容。

- **命名卷挂载 (Named Volume)**：让 Docker 自动创建一个存储空间，并为其命名。
  ```bash
  docker volume create mydata
  docker run -v mydata:/容器内路径 ...
  ```
  > 特点：命名卷在第一次使用时，Docker 会将容器的文件夹内容同步到卷中进行初始化（绑定挂载无此功能）。

**卷管理命令**：
```bash
docker volume ls               # 列出所有卷
docker volume inspect <卷名>   # 查看卷详细信息（包括宿主机真实目录）
docker volume rm <卷名>        # 删除指定卷
docker volume prune            # 删除所有未被任何容器使用的卷
```

### 4.2 容器启停与管理

| 命令 | 作用 |
| :--- | :--- |
| `docker stop <容器ID或名称>` | 停止一个正在运行的容器 |
| `docker start <容器ID或名称>` | 重新启动一个已停止的容器 |
| `docker inspect <容器ID或名称>` | 查看容器的详细配置信息（输出复杂，可借助 AI 辅助分析） |
| `docker create <镜像名称>` | 只创建容器但不立即启动（之后需用 `docker start`） |

> **参数保留**：使用 `stop` 和 `start` 启停容器时，之前 `docker run` 设置的端口映射、挂载卷、环境变量等参数都会被 Docker 记录并保留，无需重新设置。

### 4.3 容器内部操作与调试

**查看日志**：
```bash
docker logs <容器ID或名称>      # 查看全部日志
docker logs -f <容器ID或名称>   # 滚动实时查看日志
```

**Docker 技术原理简述**：
- **Cgroups (Control Groups)**：限制和隔离进程的资源使用（CPU、内存、网络带宽等），确保容器不超出资源限制。
- **Namespaces**：隔离进程的资源视图，使容器只能看到自己内部的进程ID、网络、文件目录，而看不到宿主机的。
- **本质**：Docker 容器本质上是一个特殊的进程，但进入容器内部后表现如同一个独立的操作系统。

**`docker exec` - 在容器内部执行命令**：
```bash
docker exec <容器ID或名称> <命令>                     # 执行单条命令
docker exec -it <容器ID或名称> /bin/bash             # 进入交互式 Shell（或 /bin/sh）
```
示例：
```bash
docker exec my_nginx ps -ef        # 查看容器内进程
docker exec -it my_nginx /bin/bash # 进入容器进行调试
```
> 注意：容器内部通常是极简操作系统，可能缺失 `vi` 等常用工具，需要自行安装（Debian 系容器使用 `apt update && apt install vim`）。

---

## 5. Dockerfile - 构建镜像的蓝图

**定义**：Dockerfile 是一个文本文件，详细列出了制作 Docker 镜像的步骤和指令，可类比为制作模具的图纸。

### 5.1 基本结构与指令

| 指令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `FROM` | 指定基础镜像（所有 Dockerfile 的第一行） | `FROM ubuntu:22.04` |
| `WORKDIR` | 设置镜像内的工作目录 | `WORKDIR /app` |
| `COPY` | 将宿主机的文件或目录拷贝到镜像内 | `COPY . /app` |
| `RUN` | 在镜像构建过程中执行的命令 | `RUN apt update && apt install -y python3` |
| `EXPOSE` | 声明镜像提供服务的端口（仅为声明，非强制） | `EXPOSE 8080` |
| `CMD` | 容器运行时默认执行的启动命令（一个 Dockerfile 只能有一个） | `CMD ["python3", "app.py"]` |
| `ENTRYPOINT` | 与 `CMD` 类似，但优先级更高，不易被 `docker run` 覆盖 | `ENTRYPOINT ["python3"]` |

### 5.2 `docker build` - 构建镜像

```bash
docker build -t <镜像名称>[:<版本号>] <Dockerfile所在目录>
```
示例：
```bash
docker build -t docker-test .   # 在当前目录构建名为 docker-test 的镜像
```

### 5.3 镜像推送至 Docker Hub

1. **登录 Docker Hub**：`docker login`
2. **重新标记镜像**（推送时镜像名称必须包含用户名作为命名空间）：
   ```bash
   docker tag <本地镜像名称> <你的用户名>/<镜像名称>[:<版本号>]
   ```
3. **推送镜像**：
   ```bash
   docker push <你的用户名>/<镜像名称>[:<版本号>]
   ```
4. **验证**：在 Docker Hub 网站上可搜索到已推送的镜像，其他用户即可通过 `docker pull` 下载使用。

---

## 6. Docker 网络模式

### 6.1 Bridge（桥接模式）

- **默认模式**：所有容器默认连接到此网络。
- **内部 IP**：每个容器被分配一个内部 IP 地址（通常是 `172.17.x.x` 开头）。
- **通信**：同一 Bridge 网络内的容器可以通过内部 IP 互相访问。容器网络与宿主机网络默认隔离，需通过端口映射（`-p`）才能从宿主机访问。
- **自定义子网**：
  ```bash
  docker network create <子网名称>                 # 创建自定义网络
  docker run --network <子网名称> ...              # 容器加入该网络
  ```
  **优势**：
  - 同一子网内的容器可以使用**容器名称**互相访问（Docker 内部 DNS 机制）。
  - 不同子网之间默认隔离。

### 6.2 Host（主机模式）

- **功能**：容器直接共享宿主机的网络命名空间。
- **IP 地址**：容器直接使用宿主机的 IP 地址。
- **端口**：无需端口映射（`-p`），容器内的服务直接运行在宿主机的端口上。
- **用途**：解决一些复杂的网络问题。
- **语法**：`docker run --network host ...`

### 6.3 None（无网络模式）

- **功能**：容器不连接任何网络，完全隔离。
- **语法**：`docker run --network none ...`

### 6.4 网络管理命令

```bash
docker network ls          # 列出所有 Docker 网络（包括默认的 bridge、host、none 以及自定义子网）
docker network rm <网络名> # 删除自定义子网（默认网络不可删除）
```

---

## 7. Docker Compose - 多容器编排

**背景**：一个完整应用可能由多个模块（前端、后端、数据库）组成。若将所有模块打包成一个巨大容器，会导致故障蔓延、伸缩性差；若每个模块独立容器化，则管理多个容器（创建、网络配置）会增加复杂性。

**解决方案**：Docker Compose 是一种轻量级的容器编排技术，用于管理多个容器的创建和协同工作。

**核心**：使用 YAML 文件（通常命名为 `docker-compose.yml`）定义多服务应用。

### 7.1 YAML 文件结构示例

```yaml
version: '3.8'
services:
  mongodb:
    image: mongo:latest
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=pass
    volumes:
      - mongo_data:/data/db
  backend:
    build: ./backend
    ports:
      - "8080:80"
    depends_on:
      - mongodb
volumes:
  mongo_data:
```

**说明**：
- `services`：顶级元素，每个服务对应一个容器。
- 服务名称（如 `mongodb`）：对应 `docker run` 中的 `--name`。
- `image` / `build`：指定镜像或构建上下文。
- `environment`：对应 `-e` 参数。
- `volumes`：对应 `-v` 参数。
- `ports`：对应 `-p` 参数。
- **网络**：Compose 自动为每个项目创建一个默认子网，所有服务自动加入并通过**服务名称**互相访问。
- `depends_on`：定义启动顺序（确保依赖服务先启动，但不保证服务已就绪）。

### 7.2 Docker Compose 常用命令

| 命令 | 说明 |
| :--- | :--- |
| `docker compose up` | 启动所有服务（加 `-d` 后台运行） |
| `docker compose down` | 停止并删除所有服务、网络（加 `-v` 同时删除卷） |
| `docker compose stop` | 仅停止服务，不删除容器 |
| `docker compose start` | 启动已停止的服务 |
| `docker compose -f <文件名.yml> up` | 指定非默认名称的 Compose 文件 |

### 7.3 适用场景与对比

- **Docker Compose**：适合个人使用、单机运行的轻量级容器编排需求。
- **Kubernetes**：企业级服务器集群和大规模容器编排的解决方案，功能更为复杂。

---

## 8. 总结

本文涵盖了 Docker 的核心概念与实战操作，包括：
- 基础概念（镜像、容器、仓库）
- 在 Linux / Windows 上的安装方法
- 镜像管理命令（`pull`, `images`, `rmi`）
- 容器管理命令（`run`, `ps`, `stop`, `start`, `exec`, `logs` 等）
- 数据持久化（挂载卷）
- 使用 Dockerfile 构建自定义镜像
- 网络模式（bridge, host, none）
- 多容器编排工具 Docker Compose

掌握这些知识，即可高效使用 Docker 进行开发、测试和轻量级部署。


# 基于Devcontainer的Docker使用
🐳 WSL2 + Docker Desktop + Dev Container 完整环境搭建指南

本指南将带你完成在 Windows 系统上，利用 WSL2、Docker Desktop 和 VS Code 的 Dev Container 功能，搭建一个开箱即用的 ROS 2 开发环境。

##  整体架构

```
Windows 宿主机
├── Docker Desktop (提供 Docker 引擎)
├── WSL2 (Ubuntu 22.04/24.04)
│   ├── 项目代码 (/home/user/ros2_ws)
│   └── VS Code Server (通过 Remote-WSL 连接)
└── VS Code (前端界面，通过 Dev Container 连接到容器)
    └── 容器内开发环境 (ROS 2, Rviz2, Gazebo)
```

---

## 第一步：安装 Docker Desktop for Windows

### 1. 下载安装包
访问 Docker 官网下载 **Docker Desktop for Windows**：
[https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

### 2. 安装注意事项
- 双击安装包，按照向导进行安装。
- **关键步骤**：在安装过程中，务必勾选 **“Use WSL 2 instead of Hyper-V”** 选项。
- 安装完成后，重启电脑以确保所有组件正确加载。

### 3. 启用 WSL2 集成
1. 启动 Docker Desktop，进入 **Settings** (右上角齿轮图标)。
2. 选择 **Resources** > **WSL Integration**。
3. 确保以下两项均已开启：
   -  **Enable integration with my default WSL distro**
   -  在下方的发行版列表中，将你安装的 Ubuntu 发行版（例如 `Ubuntu-22.04`）的开关**打开**。
4. 点击 **Apply & Restart**。
   

### 4. 配置国内镜像加速 (可选但推荐)
在 Docker Desktop 的 **Settings** > **Docker Engine** 中，修改配置 JSON，添加镜像源：
```json
{
  "registry-mirrors": [
    "https://docker.xuanyuan.me",
    "https://docker.m.daocloud.io",
    "https://hub-mirror.c.163.com"
  ]
}
```
点击 **Apply & Restart** 生效。

---

## 第二步：在 WSL2 的 Ubuntu 中使用 Docker

完成上述配置后，你可以在 WSL2 的 Ubuntu 终端中直接使用 `docker` 命令。

### 1. 启动 Ubuntu 终端
在 Windows 开始菜单中找到你安装的 Ubuntu 发行版，点击打开。

### 2. 验证 Docker 可用性
```bash
# 检查 Docker 客户端版本
docker --version

# 运行 Hello World 测试容器
docker run --rm hello-world
```
如果看到欢迎信息，说明 Docker Desktop 已成功集成到 WSL2 中。

### 3. 将当前用户加入 docker 组 (可选)
为避免每次执行 `docker` 命令都要加 `sudo`，执行以下命令：
```bash
sudo usermod -aG docker $USER
```
**注意**：执行后需要**完全关闭当前终端，再重新打开**，才会生效。

### 4. 验证 GUI 显示 (WSLg)
WSL2 自带的 WSLg 功能可以自动处理图形界面转发。执行以下命令测试：
```bash
sudo apt update && sudo apt install -y x11-apps
xeyes
```
如果看到一双跟随鼠标的眼睛，说明 GUI 显示正常。

---

## 第三步：创建 ROS 2 项目并使用 Dev Container

### 1. 创建工作目录 (关键：务必放在 WSL2 内部)
```bash
# 注意：路径必须是 /home/用户名/... 开头，千万不要放在 /mnt/c/ 下！
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
```

### 2. 安装 VS Code 及必要扩展
- 在 Windows 中安装 [Visual Studio Code](https://code.visualstudio.com/)。
- 安装以下扩展：
  - **Remote Development** (微软官方)
  - **Dev Containers** (`ms-vscode-remote.remote-containers`)
  - **WSL** (`ms-vscode-remote.remote-wsl`)
>直接在 Windows 下的 VS Code 中安装这些扩展就可以了.

### 3. 在 WSL2 中打开项目
在 Ubuntu 终端中执行：
```bash
cd ~/ros2_ws
code .
```
这会自动通过 `Remote - WSL` 连接，在 VS Code 中打开当前目录。

### 4. 创建 Dev Container 配置文件
在 VS Code 中，创建 `.devcontainer` 文件夹，并在其中创建 `devcontainer.json` 文件。结构如下：
```
/home/你的用户名/
└── workspace/                    # 所有项目的总根目录
    └── ros2_ws/                  # 某一个具体的 ROS 2 工作空间（也可以是其他名字）
        ├── .devcontainer/
        │   └── devcontainer.json  # 存放上面的配置文件
        └── src/                   # 功能包源码
```

将以下内容粘贴到 `devcontainer.json` 中：
```
{
    // 容器在 VS Code 左下角显示的名称，便于识别当前工作环境
    "name": "ROS 2 Humble Dev (WSL2)",
    
    // 指定使用的 Docker 镜像，此处为官方 ROS 2 Humble 桌面完整版
    "image": "osrf/ros:humble-desktop-full",

    // 传递给 docker run 的额外参数，用于定制容器的运行模式
    "runArgs": [
        "--network=host",   // 共享宿主机网络栈，便于 ROS 2 多机通信和访问硬件设备
        "--ipc=host",       // 共享宿主机 IPC 命名空间，避免 Gazebo 仿真共享内存错误
        "--privileged"      // 赋予容器特权，允许访问 USB、摄像头等硬件设备
    ],

    // 容器内部的环境变量设置
    "containerEnv": {
        "DISPLAY": "${localEnv:DISPLAY}",           // 传递宿主机的 X11 显示地址，使容器内 GUI 程序能够显示在桌面上
        "QT_X11_NO_MITSHM": "1",                    // 禁用 Qt 共享内存扩展，防止 Rviz2 等应用黑屏或渲染异常
        "LIBGL_ALWAYS_SOFTWARE": "1",               // 强制使用软件渲染，解决部分 GPU 驱动兼容性问题
        "TERM": "xterm-256color"                    // 设置终端类型，使 bash 能够显示彩色输出
    },

    // 定义文件系统的挂载点，实现宿主机与容器之间的文件共享
    "mounts": [
        // 将宿主机上当前打开的项目文件夹（例如 ~/workspace/ros2_ws）绑定挂载到容器内的 /workspace
        "source=${localWorkspaceFolder},target=/workspace,type=bind",
        // 挂载 X11 Unix 套接字，使容器内 GUI 程序能与宿主机 X Server 通信
        "source=/tmp/.X11-unix,target=/tmp/.X11-unix,type=bind"
    ],

    // 容器启动后，VS Code 默认打开的目录（与上述挂载目标路径一致）
    "workspaceFolder": "/workspace",

    // VS Code 个性化设置，仅在当前容器环境中生效
    "customizations": {
        "vscode": {
            // 容器首次创建时自动安装的扩展，提供完整的 ROS 2 开发支持
            "extensions": [
                "ms-iot.vscode-ros",      // ROS 官方开发工具集，支持节点启动、调试、URDF 预览等功能
                "ms-python.python",        // Python 语言支持（语法高亮、智能感知、调试）
                "ms-vscode.cpptools",      // C++ 语言支持（IntelliSense、调试）
                "twxs.cmake"               // CMake 语法高亮和代码辅助
            ]
        }
    },

    // 容器首次创建后执行的初始化命令（单行字符串，多条命令用 && 连接）
    "postCreateCommand": "apt-get update && apt-get install -y bash-completion python3-colcon-common-extensions && sed -i 's/#force_color_prompt=yes/force_color_prompt=yes/' ~/.bashrc && echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc && echo 'if [ -f /workspace/install/setup.bash ]; then source /workspace/install/setup.bash; fi' >> ~/.bashrc && mkdir -p /workspace/src",
    // 具体解释：
    // 1. apt-get update                          更新软件包列表
    // 2. apt-get install -y ...                  安装 bash 命令补全和 colcon 编译工具扩展
    // 3. sed -i 's/#force_color_prompt=yes/...'  启用 bash 彩色提示符
    // 4. echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc  将 ROS 2 环境变量自动加载写入 .bashrc
    // 5. echo 'if [ -f /workspace/install/...'   如果工作空间已编译，则自动加载其 setup 文件
    // 6. mkdir -p /workspace/src                 提前创建 src 源码目录

    // 容器内使用的用户身份，root 可避免文件权限问题
    "remoteUser": "root"
}
```

### 5. 启动 Dev Container
使用位置：在指定的子工作空间中
保存文件后，VS Code 右下角会弹出提示：
> Folder contains a Dev Container configuration file. Reopen folder to develop in a container?

点击 **Reopen in Container**。

如果没有弹出提示，按 `F1`，输入 `reopen`，选择 **Dev Containers: Reopen in Container**。

### 6. 等待环境构建
- VS Code 会自动拉取 `osrf/ros:humble-desktop-full` 镜像（首次约需 3-5 分钟）。
- 构建完成后，左下角会显示 **Dev Container: ROS 2 Humble Dev (WSL2)**。

### 7. 验证开发环境
在 VS Code 的终端（此时已经是容器内终端）中运行：
```bash
rviz2
```
如果 Rviz2 窗口出现在 Windows 桌面上，恭喜你，环境搭建成功！

---

## ⚠️ 重要注意事项

| 项目 | 正确做法 | 错误做法 |
| :--- | :--- | :--- |
| **代码存放位置** | `~/ros2_ws` (WSL2 Linux 文件系统) | `/mnt/c/Users/.../ros2_ws` (Windows 文件系统) |
| **Docker 命令执行位置** | 在 WSL2 的 Ubuntu 终端中执行 | 在 Windows 的 PowerShell 或 CMD 中执行 |
| **VS Code 打开方式** | 在 Ubuntu 终端中执行 `code .` | 从 Windows 开始菜单打开 VS Code 再打开 `/mnt/c/` 下的项目 |
| **GUI 显示** | 依赖 WSLg 自动转发，配置简单 | 手动安装 VcXsrv 并配置 `DISPLAY` 环境变量 |

---

## 🐞 常见问题排查

### Q1: `docker: command not found`
- **原因**：Docker Desktop 未运行或 WSL2 集成未开启。
- **解决**：确保 Docker Desktop 在后台运行，并检查 Settings > Resources > WSL Integration 中你的发行版已勾选。

### Q2: Rviz2 启动后黑屏或无响应
- **解决**：在 `devcontainer.json` 的 `containerEnv` 中临时添加 `"LIBGL_ALWAYS_SOFTWARE": "1"` 以使用软件渲染。

### Q3: 容器内无法访问 USB 设备 (如激光雷达)
- **解决**：在 Windows 上使用 `usbipd` 工具将设备绑定到 WSL2，并在 `devcontainer.json` 的 `runArgs` 中保留 `"--privileged"` 参数。

### Q4: 文件修改后容器内未同步 (或相反)
- **原因**：这是 Dev Container 的默认行为，`mounts` 已实现双向同步。如出现异常，请检查项目是否在 `/mnt/c/` 下。
- **解决**：将项目移动到 `/home/用户/` 路径下。

### Q5: 如何更新或重建容器？
- 按 `F1`，输入 `rebuild`，选择 **Dev Containers: Rebuild and Reopen in Container**。

---

