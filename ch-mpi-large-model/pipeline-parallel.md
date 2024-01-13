naive pipeline是实现流水线并行训练的最直接的方法，我们将模型分为多个部分，每个部分分配一个GPU，然后进行训练，在分割模型的边界处插入通信步骤。
我们以这个4层顺序模型为例：
Output=L4(L3(L2(L1(Input))))

如果把这个模型的计算分配给两个GPU，例如：
- GPU1：intermediate = L2(L1(input))
- GPU2：output = L4(L3(intermediate))

所以，为了完成前向传递，我们把GPU1计算出来的结果张量 intermediate 传输到GPU2，对于后向传递，我们把梯度 intermediate 从GPU2发送到GPU1。这样，模型并行训练会保持与单节点相同的输出和梯度。

如图，仅需要使用节点到节点通信（MPI.Send 和 MPI.Recv），并且不需要任何集体通信原语。
![[pipeline 并行图1.png]]

数据并行和流水线并行一同作用的示意图：![[pipeline 并行图2.png]]