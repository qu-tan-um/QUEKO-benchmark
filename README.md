# Quantum Mapping Examples with Known Optimal

This is the benchmark circuits used in this [paper]().

The device layouts can be found in `CONNECTION.py`, where `INDEX_CONNECTION_LIST` stores all the edges in the corresponding device layouts as tuples of qubit indices.

Generally, benchmark file names contain:
- Device layout (`16QBT` is Rigetti Aspen-4, `20QBT` is IBM Tokyo, `53QBT` is IBM Rochester, `54QBT` is Google Sycamore)
- Optimal depth (`05CYC` means the optimal solution has five cycles)
- Gate distribution vector (`TFL` is [Toffoli gate](https://en.wikipedia.org/wiki/Toffoli_gate), `QSE` is quantum supremacy experiment[1])
- The number of meta file where this file is sampled (specified below)

`BNTF` are **b**enchmarks that are **n**ear-**t**erm **f**easible (depth 5-45). There are two sets of files: 1) Aspen-4 as device and Toffoli gate as gate distribution, 2) Sycamore as device and Supremacy experiment as gate distribution.

`BSS` are **b**enchmarkss for **s**calability **s**tudy (depth 100-900). All four devices are tested.

`heatmap` holds the `qasm` files used in the experiments which investigate the influence of gate distribution on depth ratio in the paper. The naming is a bit different for this folder: 
- Device (all Tokyo)
- Depth (all 45)
- Gate distribution (`_.0S1_.5S2` means the gate distribution vector components s1=0 and s2=0.5.)
- The number of meta file

The benchmarks are easily derived from meta files. All the meta files are in `meta` folder. They are `csv` files whose each row is a cycle of gates. In every row of a meta file, there are multiple entries: a single integer means a single-qubit gate on the qubit with this index, an integer tuple means a two-qubit gate on the two qubits with those indices. Since we are only focusing on legalizing all the two-qubit gates under the device layout constraints, we only care about the qubits they use, not specifically what gates they are. For example, whether a two-qubit gate is a CZ gate or a CX gate makes no difference.

Accompanying each meta file, there is also a `_solution` file. It contains the optimal mapping of the corresponding meta file. If the first line of solution files is `5`, then the optimal mapping for `q[0]` in the benchmark is physical qubit with index `5`. The second line stands for the optimal mapping of `q[1]`...

[1]: Arute, F., Arya, K., Babbush, R. _et al_. Quantum supremacy using a programmable superconducting processor. _Nature_ __574__, 505–510 (2019). [https://doi.org/10.1038/s41586-019-1666-5](https://doi.org/10.1038/s41586-019-1666-5)
