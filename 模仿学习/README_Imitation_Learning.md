# 模仿学习（Imitation Learning）学习笔记

## 1. 模仿学习是什么

模仿学习（Imitation Learning, IL）的核心目标是：

\[
\boxed{
\text{从专家示范中学习策略}
}
\]

专家通常提供轨迹：

\[
\tau=(s_0,a_0,s_1,a_1,\dots,s_T)
\]

多条专家轨迹组成：

\[
D_E=\{\tau_1,\tau_2,\dots,\tau_N\}
\]

其中：

- \(s_t\)：第 \(t\) 时刻的状态
- \(a_t\)：专家在状态 \(s_t\) 下采取的动作
- \(\pi_E\)：专家策略
- \(\pi_\theta\)：待学习策略

最终希望得到：

\[
\boxed{
\pi_\theta(a|s)
}
\]

即根据当前状态决定动作。

## 2. 模仿学习、监督学习与强化学习

### 2.1 监督学习

监督学习通常学习：

\[
\boxed{
x\rightarrow y
}
\]

预测错误一般不会改变下一条输入数据。

### 2.2 模仿学习

最基本的模仿学习学习：

\[
\boxed{
s\rightarrow a
}
\]

但动作会改变环境状态：

\[
\boxed{
s_t
\rightarrow
a_t
\rightarrow
s_{t+1}
\rightarrow
a_{t+1}
}
\]

因此模仿学习部署时属于**闭环序列决策**。

### 2.3 强化学习

强化学习通过奖励学习策略：

\[
\boxed{
\text{Reward}
\rightarrow
\text{Policy}
}
\]

模仿学习则主要通过专家示范学习：

\[
\boxed{
\text{Expert Demonstrations}
\rightarrow
\text{Policy}
}
\]

可以粗略理解为：

\[
\boxed{
\text{RL：告诉机器人什么是好}
}
\]

\[
\boxed{
\text{IL：告诉机器人优秀行为是什么样}
}
\]

## 3. MSE

MSE（Mean Squared Error）即均方误差：

\[
\boxed{
\text{MSE}
=
\frac{1}{N}
\sum_{i=1}^{N}
(\hat y_i-y_i)^2
}
\]

在连续动作 Behavior Cloning 中：

\[
\boxed{
\mathcal L(\theta)
=
\frac1N
\sum_i
\|\pi_\theta(s_i)-a_i^E\|^2
}
\]

其中：

- \(a_i^E\)：专家动作
- \(\pi_\theta(s_i)\)：模型预测动作

MSE 越小，说明模型在这些样本上的单步动作预测越接近专家。

但：

\[
\boxed{
\text{低 MSE}
\not\Rightarrow
\text{闭环任务表现一定好}
}
\]

## 4. Behavior Cloning

Behavior Cloning（BC，行为克隆）是最基本的模仿学习方法。

核心：

\[
\boxed{
\text{BC = 用监督学习复制专家动作}
}
\]

训练数据：

\[
D_E=\{(s_i,a_i)\}
\]

一般目标：

\[
\boxed{
\mathcal L(\theta)
=
-\mathbb E_{(s,a)\sim D_E}
\log\pi_\theta(a|s)
}
\]

连续动作在高斯假设下常退化为 MSE。

### 4.1 BC 的优势

- 简单
- 稳定
- 不需要奖励函数
- 不需要在线强化学习
- 可以完全离线训练
- 很适合作为机器人策略 baseline

### 4.2 BC 的核心问题：Distribution Shift

训练状态来自专家：

\[
\boxed{
s\sim d_{\pi_E}
}
\]

部署状态来自 learner：

\[
\boxed{
s\sim d_{\pi_\theta}
}
\]

通常：

\[
\boxed{
d_{\pi_E}\neq d_{\pi_\theta}
}
\]

模型一个小动作误差会改变下一时刻状态：

\[
a_t^\pi\neq a_t^E
\Rightarrow
s_{t+1}^\pi\neq s_{t+1}^E
\]

进一步形成：

\[
\boxed{
\text{小误差}
\rightarrow
\text{状态偏移}
\rightarrow
\text{进入陌生状态}
\rightarrow
\text{更大误差}
}
\]

这称为：

\[
\boxed{\text{Compounding Error}}
\]

因此：

\[
\boxed{
\text{BC 的训练是监督学习，但部署是闭环序列决策}
}
\]

## 5. DAgger

DAgger 全称：

\[
\boxed{
\text{Dataset Aggregation}
}
\]

核心思想：

\[
\boxed{
\text{让 learner 产生状态，再让 expert 提供正确动作}
}
\]

BC：

\[
\boxed{
\text{Expert 产生状态 + Expert 给动作}
}
\]

DAgger：

\[
\boxed{
\text{Learner 产生状态 + Expert 给动作}
}
\]

训练循环：

\[
\pi_i
\rightarrow
\text{rollout}
\rightarrow
s\sim d_{\pi_i}
\rightarrow
\pi_E(s)
\]

得到新数据：

\[
(s,\pi_E(s))
\]

加入：

\[
\boxed{
D\leftarrow D\cup D_{\text{new}}
}
\]

再重新训练策略。

### 5.1 DAgger 解决什么问题

主要解决：

\[
\boxed{
\text{训练状态分布与部署状态分布不一致}
}
\]

尤其能够增加：

\[
\boxed{\text{Recovery States}}
\]

即模型已经偏离正常轨迹后如何恢复的数据。

### 5.2 DAgger 的代价

主要问题是：

\[
\boxed{\text{Expert Query Cost}}
\]

训练过程中需要持续查询专家。

## 6. Interactive / Active Imitation Learning

Interactive Imitation Learning 指 learner 在训练过程中继续和专家交互。

Active Imitation Learning 进一步研究：

\[
\boxed{
\text{哪些状态真正值得查询专家}
}
\]

常见触发依据：

- 模型不确定性高
- Ensemble 分歧大
- 状态风险高
- learner 即将失败
- OOD 状态

Expert Intervention 指：

\[
\boxed{
\text{必要时由专家纠正或接管 learner}
}
\]

核心目标可以概念性表示为：

\[
\boxed{
J
=
J_{\text{task}}
+
\lambda N_{\text{query}}
}
\]

即同时兼顾任务表现和专家查询成本。

## 7. Inverse Reinforcement Learning

Inverse Reinforcement Learning（IRL，逆强化学习）关注：

\[
\boxed{
\text{专家为什么这样做}
}
\]

普通强化学习：

\[
\boxed{
r
\rightarrow
\pi
}
\]

逆强化学习：

\[
\boxed{
\pi_E / D_E
\rightarrow
r
}
\]

完整流程通常是：

\[
\boxed{
D_E
\rightarrow
r
\rightarrow
\pi
}
\]

BC 学的是：

\[
\boxed{
\text{专家怎么做}
}
\]

IRL 试图学习：

\[
\boxed{
\text{专家在优化什么目标}
}
\]

### 7.1 Reward Ambiguity

同一种专家行为可能被很多奖励函数解释：

\[
\boxed{
\text{Expert Behavior}
\not\Rightarrow
\text{Unique Reward}
}
\]

这称为：

\[
\boxed{\text{Reward Ambiguity}}
\]

因此经典 IRL 需要额外结构或原则约束奖励函数。

## 8. Maximum Entropy IRL

MaxEnt IRL 不假设专家每次都选择唯一最优轨迹。

核心公式：

\[
\boxed{
P(\tau)
=
\frac{1}{Z}
e^{R(\tau)}
}
\]

其中：

\[
R(\tau)
=
\sum_t r(s_t,a_t)
\]

配分函数：

\[
\boxed{
Z
=
\sum_\tau e^{R(\tau)}
}
\]

直觉：

\[
\boxed{
R(\tau)\uparrow
\Rightarrow
P(\tau)\uparrow
}
\]

即高奖励轨迹更容易被专家选择，但其他合理轨迹仍然可以出现。

### 8.1 最大熵思想

最大熵原则可以理解为：

\[
\boxed{
\text{在满足专家示范约束的前提下，不额外假设专家存在更多偏好}
}
\]

### 8.2 Feature Expectation

如果奖励函数：

\[
r_\theta(s,a)=\theta^\top\phi(s,a)
\]

则可以定义：

\[
\mu(\pi)
=
\mathbb E_\pi
\left[
\sum_t\gamma^t\phi(s_t,a_t)
\right]
\]

核心思想：

\[
\boxed{
\mu(\pi)
\approx
\mu(\pi_E)
}
\]

即让 learner 的整体行为特征接近专家。

## 9. Occupancy Measure

Occupancy Measure 可以理解为策略的**状态-动作访问分布**：

\[
\boxed{
\rho_\pi(s,a)
=
(1-\gamma)
\sum_{t=0}^{\infty}
\gamma^t
P(s_t=s,a_t=a|\pi)
}
\]

直觉：

\[
\boxed{
\rho_\pi(s,a)
=
\text{策略长期访问 }(s,a)\text{ 的频率}
}
\]

可以把：

\[
\boxed{
\rho_\pi
}
\]

理解成策略的“行为指纹”。

如果：

\[
\boxed{
\rho_\pi(s,a)
\approx
\rho_E(s,a)
}
\]

说明 learner 的整体闭环行为接近 expert。

Feature Expectation 可以写成：

\[
\boxed{
\mu(\pi)
=
\sum_{s,a}
\rho_\pi(s,a)\phi(s,a)
}
\]

因此 Occupancy Matching 比单独 Feature Matching 更完整。

## 10. GAIL

GAIL 全称：

\[
\boxed{
\text{Generative Adversarial Imitation Learning}
}
\]

核心思想：

\[
\boxed{
\text{通过对抗训练直接匹配 expert 和 learner 的 occupancy measure}
}
\]

目标：

\[
\boxed{
\rho_\pi(s,a)
\approx
\rho_E(s,a)
}
\]

### 10.1 GAN 与 GAIL 对应关系

| GAN | GAIL |
|---|---|
| 真实数据 | Expert \((s,a)\) |
| Generator | Policy \(\pi\) |
| Fake sample | Learner rollout |
| Discriminator | \(D(s,a)\) |
| 匹配数据分布 | 匹配状态-动作访问分布 |

判别器判断：

\[
\boxed{
(s,a)\text{ 来自 Expert 还是 Learner}
}
\]

典型目标：

\[
\boxed{
\min_\pi\max_D
\;
\mathbb E_{\rho_E}
[\log D(s,a)]
+
\mathbb E_{\rho_\pi}
[\log(1-D(s,a))]
}
\]

策略可以使用判别器产生的 reward-like signal：

\[
\boxed{
r_D(s,a)
=
-\log(1-D(s,a))
}
\]

再利用 PPO、TRPO 等强化学习算法更新 Policy。

### 10.2 GAIL 的特点

优势：

- 不需要手工设计 Reward
- 不需要像 DAgger 那样持续查询专家
- 直接关注 learner 的闭环行为分布

代价：

- 需要持续环境 rollout
- 通常需要 RL
- 对抗训练不稳定
- 真机样本成本可能很高

## 11. Multimodal Behavior

复杂机器人任务中：

\[
\boxed{
\text{同一个状态可能有多个正确动作}
}
\]

例如：

\[
a_L=-1
\]

左绕正确，

\[
a_R=+1
\]

右绕也正确。

如果直接用 MSE：

\[
\hat a
=
\mathbb E[A]
\]

可能得到：

\[
\hat a=0
\]

反而成为不合理动作。

因此现代策略更希望学习：

\[
\boxed{
p(a|s)
}
\]

而不只是：

\[
\boxed{
a=f(s)
}
\]

## 12. Sequence Modeling

机器人动作具有明显时间依赖：

\[
\boxed{
a_t
\text{ 不仅依赖 }s_t
}
\]

更一般：

\[
\boxed{
\pi(a_t|s_{\leq t},a_{<t})
}
\]

因此可以使用：

- RNN
- LSTM
- Transformer

来学习历史状态、动作与当前决策之间的关系。

核心：

\[
\boxed{
\text{把行为看成序列，而不是独立状态-动作样本}
}
\]

## 13. Action Chunking

传统单步策略：

\[
\boxed{
s_t\rightarrow a_t
}
\]

Action Chunking：

\[
\boxed{
s_t
\rightarrow
(a_t,a_{t+1},\dots,a_{t+H-1})
}
\]

即一次预测未来一小段动作。

优势：

- 动作更平滑
- 更容易表达短期行为模式
- 更适合双臂和精细操作
- 减少每个控制步完全重新决策的问题

实际部署通常使用 Receding Horizon：

\[
\boxed{
\text{Predict Many, Execute Few}
}
\]

例如预测 16 步，但只执行前 4 步，再重新观察并预测。

因此系统仍然保持闭环。

## 14. ACT

ACT：

\[
\boxed{
\text{Action Chunking with Transformers}
}
\]

核心：

\[
\boxed{
\text{Transformer}
+
\text{Action Chunking}
}
\]

Transformer 用于建模：

\[
\boxed{
\text{长时上下文与时序依赖}
}
\]

Action Chunking 用于生成：

\[
\boxed{
\text{连续、协调的一段未来动作}
}
\]

ACT 特别适合：

- 双臂操作
- 长时任务
- 精细机器人操作

## 15. Diffusion Policy

Diffusion Policy 将机器人动作模仿从简单回归升级为：

\[
\boxed{
\text{条件生成}
}
\]

传统 BC：

\[
\boxed{
a=f(s)
}
\]

Diffusion Policy：

\[
\boxed{
A\sim p_\theta(A|o)
}
\]

其中：

\[
A=(a_t,a_{t+1},\dots,a_{t+H-1})
\]

是一段 Action Chunk。

### 15.1 Diffusion 基本思想

训练：

\[
\boxed{
\text{真实动作}
\rightarrow
\text{加噪}
\rightarrow
\text{学习去噪}
}
\]

噪声过程可写为：

\[
x_t
=
\sqrt{\bar\alpha_t}x_0
+
\sqrt{1-\bar\alpha_t}\epsilon
\]

网络预测噪声：

\[
\epsilon_\theta(x_t,t)
\]

损失：

\[
\boxed{
\mathcal L
=
\|\epsilon-\epsilon_\theta(x_t,t)\|^2
}
\]

推理时：

\[
\boxed{
\text{随机噪声}
\rightarrow
\text{逐步去噪}
\rightarrow
\text{动作序列}
}
\]

### 15.2 Diffusion Policy 主要解决

\[
\boxed{
\text{Multimodal + High-dimensional + Temporally Correlated Actions}
}
\]

即：

- 多模态动作
- 高维动作
- 时间连续动作

### 15.3 Diffusion Policy 不能自动解决

它不能天然解决：

\[
\boxed{
\text{Distribution Shift}
}
\]

DAgger 解决的是：

\[
\boxed{
\text{数据覆盖问题}
}
\]

Diffusion Policy 解决的是：

\[
\boxed{
\text{复杂动作分布表达问题}
}
\]

两者并不冲突，可以组合。

## 16. Transformer

Transformer 在机器人策略中的重要作用是：

\[
\boxed{
\text{利用 Attention 建模长时上下文}
}
\]

Self-Attention：

\[
\boxed{
\operatorname{Attention}(Q,K,V)
=
\operatorname{softmax}
\left(
\frac{QK^\top}{\sqrt{d_k}}
\right)V
}
\]

直觉：

\[
\boxed{
\text{根据当前需要，从历史信息中选择最重要的信息}
}
\]

机器人可以利用：

- 历史图像
- 历史动作
- 当前状态
- 语言指令

共同决定未来动作。

## 17. VLA

VLA：

\[
\boxed{
\text{Vision-Language-Action}
}
\]

输入：

\[
\boxed{
\text{Vision}
+
\text{Language}
+
\text{Robot State}
}
\]

输出：

\[
\boxed{
\text{Action}
}
\]

例如：

\[
(\text{桌面图像},
\text{“拿起红杯子”})
\rightarrow
\text{机器人抓取动作}
\]

VLA 的目标从：

\[
\boxed{
\text{一个任务一个 Policy}
}
\]

发展到：

\[
\boxed{
\text{One Policy, Many Tasks}
}
\]

很多 VLA 的底层训练仍然可以看成：

\[
\boxed{
\text{大规模、多任务 Behavior Cloning}
}
\]

## 18. 模仿学习方法总对比

| 方法 | 主要解决的问题 | 专家持续在线 | 环境交互 | 是否显式学习 Reward |
|---|---|---:|---:|---:|
| BC | 最简单地复制专家动作 | 否 | 否 | 否 |
| DAgger | Distribution Shift | 是 | 是 | 否 |
| Active / Intervention IL | 专家查询成本 | 部分 | 是 | 否 |
| IRL | 推断专家目标 | 否 | 通常需要 | 是 |
| MaxEnt IRL | 专家随机性、多种合理轨迹 | 否 | 通常需要 | 是 |
| GAIL | 匹配整体行为分布 | 否 | 是 | 不强调真实 Reward |
| ACT | 长时序 + Action Chunk | 否 | 训练可离线 | 否 |
| Diffusion Policy | 多模态、高维动作生成 | 否 | 训练可离线 | 否 |
| VLA | 多任务、多模态泛化 | 否 | 视训练方式而定 | 通常否 |

## 19. 整套课程的逻辑主线

最开始：

\[
\boxed{
\text{Expert Demonstrations}
}
\]

最简单：

\[
\downarrow
\]

\[
\boxed{
BC
}
\]

出现：

\[
\boxed{
\text{Distribution Shift}
}
\]

于是：

\[
\downarrow
\]

\[
\boxed{
DAgger
}
\]

进一步考虑专家成本：

\[
\downarrow
\]

\[
\boxed{
\text{Interactive / Active IL}
}
\]

开始问：

\[
\boxed{
\text{专家为什么这么做}
}
\]

于是：

\[
\downarrow
\]

\[
\boxed{
IRL
}
\]

允许多种合理专家行为：

\[
\downarrow
\]

\[
\boxed{
MaxEnt\ IRL
}
\]

进一步描述整体行为：

\[
\downarrow
\]

\[
\boxed{
\rho_\pi(s,a)
}
\]

于是：

\[
\downarrow
\]

\[
\boxed{
GAIL
}
\]

进入复杂机器人操作：

\[
\boxed{
\text{Multimodality}
+
\text{Temporal Dependency}
}
\]

于是：

\[
\downarrow
\]

\[
\boxed{
\text{Sequence Modeling}
+
\text{Action Chunking}
}
\]

进一步得到：

\[
\boxed{
ACT
}
\]

以及：

\[
\boxed{
Diffusion Policy
}
\]

最终走向：

\[
\boxed{
VLA
}
\]

## 20. 用三个问题理解模仿学习研究

以后阅读模仿学习论文时，可以先问三个问题。

### 20.1 Data

\[
\boxed{
\text{训练数据从哪里来？}
}
\]

典型研究：

- BC
- DAgger
- Active IL
- Intervention

### 20.2 Objective

\[
\boxed{
\text{到底在模仿什么？}
}
\]

可能是：

- Expert Action
- Reward
- Feature Expectation
- Occupancy Measure

典型研究：

- BC
- IRL
- GAIL

### 20.3 Policy Representation

\[
\boxed{
\text{如何表示复杂行为？}
}
\]

典型研究：

- RNN / LSTM
- Transformer
- ACT
- Diffusion Policy
- VLA

因此可以建立总框架：

\[
\boxed{
\text{Imitation Learning}
=
\text{Data}
+
\text{Objective}
+
\text{Policy Representation}
}
\]

## 21. 八个必须真正掌握的核心节点

建议优先掌握：

\[
\boxed{
1.\ BC
}
\]

\[
\boxed{
2.\ Distribution\ Shift
}
\]

\[
\boxed{
3.\ DAgger
}
\]

\[
\boxed{
4.\ IRL
}
\]

\[
\boxed{
5.\ Occupancy\ Measure
}
\]

\[
\boxed{
6.\ GAIL
}
\]

\[
\boxed{
7.\ Action\ Chunking
}
\]

\[
\boxed{
8.\ Diffusion\ Policy
}
\]

其余方法可以围绕这八个节点继续扩展。

## 22. 项目学习路线

下一阶段建议单独开一个项目学习对话，按下面顺序动手。

### 阶段 1：Behavior Cloning 最小实验

目标：

\[
\boxed{
\text{亲眼看到低 MSE 不等于高闭环成功率}
}
\]

完成：

- 建立简单二维环境
- 手工定义 Expert Policy
- 收集 Expert Demonstration
- PyTorch 训练 BC
- 计算 Offline MSE
- Closed-loop Rollout
- 比较 Expert 与 BC 的轨迹

### 阶段 2：Distribution Shift 实验

目标：

\[
\boxed{
\text{观察训练状态分布和部署状态分布的差异}
}
\]

完成：

- 缩窄专家数据分布
- 改变初始状态
- 加入扰动
- 绘制状态访问区域
- 测量 rollout failure

### 阶段 3：DAgger

目标：

\[
\boxed{
\text{加入 Recovery States 后提升闭环性能}
}
\]

流程：

\[
\text{BC Rollout}
\rightarrow
\text{Expert Label}
\rightarrow
D\leftarrow D\cup D_{\text{new}}
\rightarrow
\text{Retrain}
\]

比较：

- BC
- DAgger

### 阶段 4：Sequence / Action Chunking

目标：

\[
\boxed{
\text{从单步预测扩展到动作序列预测}
}
\]

完成：

- 构造历史观测
- 预测 Action Chunk
- Receding Horizon 执行
- 比较单步策略与 Chunk Policy

### 阶段 5：Diffusion Policy

目标：

\[
\boxed{
\text{理解和实现条件动作生成}
}
\]

完成：

- 动作序列加噪
- Noise Prediction
- Iterative Denoising
- Conditional Observation
- Action Chunk Generation
- Multimodal 行为实验

### 阶段 6：真实机器人方向

进入更完整的机器人研究后，再逐步学习：

- ACT
- Diffusion Policy
- Robomimic
- Real Robot Demonstration Collection
- Recovery / Intervention Data
- Offline + Online Fine-tuning
- VLA

## 23. 当前学习阶段

理论主线第一轮已经完成：

\[
\boxed{
BC
\rightarrow
DAgger
\rightarrow
IRL
\rightarrow
MaxEnt\ IRL
\rightarrow
GAIL
\rightarrow
ACT
\rightarrow
Diffusion\ Policy
\rightarrow
VLA
}
\]

下一阶段不再继续堆概念，而是进入：

\[
\boxed{
\text{代码实现}
+
\text{实验现象}
+
\text{论文复现}
}
\]

推荐新的项目对话从下面这句话开始：

> 我已经完成模仿学习基础理论学习，现在开始项目实践。请从 Behavior Cloning 最小实验开始，带我逐步完成 BC → Distribution Shift → DAgger → Action Chunking → Diffusion Policy，并保持课堂式讲解，每一步先解释原理，再写代码，再分析实验结果。
