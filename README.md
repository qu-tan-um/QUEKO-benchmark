# QUEKO - Quantum Mapping Examples with Known Optimal

## Usage of QUEKO generating script `queko.py`

We can construct a QUEKO circuit with a list of edges (between physical qubits),
the optimal depth, and the gate density vector, e.g., 
```python
temp_connection =  [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7),
                    (0, 8), (3, 11), (4, 12), (7, 15),
                    (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14), (14, 15)]
temp = queko(temp_connection, 3, (0.3, 0.4))
temp_ans = temp.output_queko()
print(temp_ans)
```
The output reads
```bash
[[10, 2, 0, 3, 9, 1, 8, 6, 5, 11, 15, 4, 13, 7, 12, 14], [[(9,), (5,), (8,), (12, 15), (3, 11), (13, 10), (4, 0)], [(8,), (11,), (13,), (1,), (6,), (5,), (10, 15), (4, 0), (3, 9), (14, 12)], [(10,), (15,), (5,), (14,), (2,), (0,), (3, 9), (6, 4)]]]
```
This is a list of two elements. The first element is a mapping that leads to
optimal depth. The second element is the circuit structure, which has many 'cycles',
each one is a list of tuples. If the tuple only has one element, it refers to a
single-qubit gate; if it has two elements, it refers to a two-qubit gate.
In this example, we set the optimal depth to 3 when `temp` is initialized, so there
are 3 cycles. We can easily generate a concrete circuit with the circuit
structure. In the first cycle, there is `(9,)` and `(12, 15)` (and some other gates), so in the QUEKO
circuit, there will be a single-qubit gate on `q[9]` and a two-qubit gate on
`q[12], q[15]`. (In the original paper, single-qubit gates are X gates and
two-qubit gates are CNOTs, but changing to other gates do not affect anything,
since we do not resynthesis gates in the qubit mapping phase.) There is a
qubit mapping indicated in `temp_ans` that leads to optimal depth 3, e.g.,
`q[9]` is mapped to 9-th element, i.e., node 11 as we specified the connection;
`q[12]` is mapped to node 13 and `q[15]` is mapped to node 14. As a quick check,
`[13, 14]` is indeed in `temp_connection`. Note that there may be other mapping
from `q[]` to the nodes that also leads to optimal depth.

## Information on circuits used in the paper
This is the benchmark circuits used in this [paper](https://arxiv.org/abs/2002.09783).
```
@Article{tc20-tan-cong-optimality-layout-queko,
  author        = {Tan, Bochen and Cong, Jason},
  journal       = {IEEE Transactions on Computers},
  title         = {Optimality Study of Existing Quantum Computing Layout Synthesis Tools},
  year          = {2020},
  month         = jul,
  archiveprefix = {arXiv},
  copyright     = {All rights reserved},
  doi           = {10.1109/TC.2020.3009140},
  eprint        = {2002.09783},
  language      = {en},
  primaryclass  = {quant-ph},
}
```

The device layouts can be found in `CONNECTION.py`, where `INDEX_CONNECTION_LIST` stores all the edges in the corresponding device layouts as tuples of qubit indices.

Generally, the set-up parameters of every QUEKO benchmark can be read off from its name:
- Device graph (`16QBT` is Rigetti Aspen-4, `20QBT` is IBM Tokyo, `53QBT` is IBM Rochester, `54QBT` is Google Sycamore)
- Optimal depth (`**CYC` means the optimal solution has `**` cycles)
- Gate density vector (`TFL` is [Toffoli gate](https://en.wikipedia.org/wiki/Toffoli_gate), `QSE` is quantum supremacy experiment[1])
- The serial number of its meta file (from `0` to `9`)

`BNTF` are **b**enchmarks that are **n**ear-**t**erm **f**easible (depth 5, 10, ..., 45). There are two sets of benchmarks: 1) Aspen-4 as device and TFL gate density, 2) Sycamore as device and QSE gate density.

`BSS` are **b**enchmarks for **s**calability **s**tudy (depth 100, 200, ..., 900). All four devices are tested.

`BIGD` are **b**enchmarks for **i**mpact of **g**ate **d**ensity on depth ratio. For all the `BIGD` benchmarks, the device is IBM Tokyo, the depth is 45. Their name also indicates the gate density vector (`_.0S1_.5S2` means the gate density vector components d1=0 and d2=0.5).

The benchmarks are `qasm` files easily derived from meta files. All the meta files are in `meta` folder. They are `csv` files of which each row is a cycle of gates. In every row of a meta file, there are multiple entries: a single integer means a single-qubit gate on the qubit with this index, an integer tuple means a two-qubit gate on the two qubits with those indices. Since we are only focusing on legalizing all the two-qubit gates under the device layout constraints, we only care about the qubits they use, not specifically what gates they are. For example, whether a two-qubit gate is a CZ gate or a CX gate makes no difference.

Accompanying each meta file, there is also a `solution` file. It contains the optimal mapping of the corresponding meta file. If the first line of solution files is `5`, then the optimal mapping for `q[0]` in the benchmark is physical qubit with index `5`. The second line stands for the optimal mapping of `q[1]`...

[1]: Arute, F., Arya, K., Babbush, R. _et al_. Quantum supremacy using a programmable superconducting processor. _Nature_ __574__, 505–510 (2019). [https://doi.org/10.1038/s41586-019-1666-5](https://doi.org/10.1038/s41586-019-1666-5)