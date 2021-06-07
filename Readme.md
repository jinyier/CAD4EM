# CAD4EM
##  <a name="reqs"></a> Requirements

[**Python 3**](https://www.anaconda.com/products/individual)

**NumPy 1.18+**

**PyCrypto 2.6.1+**

## <a name="S1"></a> Step 1: Input Vector Creation
`python3 gen_input_patterns.py`

This script is used to create sets of plaintext for a version of AES that matches the hardware implementation. Try `python gen_input_patterns --help` to see all available options.
By default this script creates 1000 lines of random plaintext, encrypts it,
creates a semifixed dataset for the zeroith byte, and then encrypts that.

**IN PROGRESS**: A custom plaintext ASCII file (`--plaintext_in_filename`) can be used to specify a key and plaintext. Each line should be a Key-Text Pair (KTP) with the key followed by the plaintext written in hexadecimal form. The MSB of the Key should be on the left hand side.

Note that CAD4EM outputs its generated KTPs in this same format.

**IN PROGRESS**: CAD4EM currently supports AES-128. It will be exapanded to have support for other forms of AES and potentially other ciphers

By default, a fixed key is created randomly. A set of plaintext (`--plaintext_filename`) is also randomly generated and encrypted using that key (`--ciphertext_filename`). The key can be specified through `--key`, It should be a list of decimal numbers with values between 0 and 255. If an initial vector is needed it should follow the same format but use the `--iv` argument. If both `--plaintext_in_filename` and `--key` are specified, the key from the input file is used. 

It is also possible to control the random seed used to create these values through `--seed`.
By default this value is a random integer between 0 and 1000 (inclusive).

The semifixed inputs are created to distinguish the Hamming Weight (HW) leakage of a certain byte (`--target_byte`) of the Sbox output from the first round of AES. This is done by setting all other bytes to output a zero from the Sbox on the first round, while choosing values that will result in a Sbox output with a target hamming weight (`--target_HW`).

By default, the random plaintext is saved to `rand_plain.txt`, the semifixed plaintext
is saved to `semi_plain.txt`, and the ciphertext from the plaintext is 
saved to `rand_cipher.txt` and the semifixed ciphertext saveed to `semi_cipher.text`. These are ASCII text files, with each line denoting a seperate input vector. These lines should be the key followed by the plaintext (with no space seperating them) written as hex values, with the MSB on the left and LSB on the right. These inputs can be resused between runs if desired. Locations for each can also be specified through the `--plaintext_filename, --semi_plain_filename, --ciphertext_filename, --semi_cipher_filename` arguments, respectively. By default this creates 1000 KTP for both sets, but this can be changed through the `--num_lines` argument. CAD4EM supports Electronic Codebook (ECB), Counter (CTR) and Cipher-Block Chaining (CBC) modes, which can be selected through the `--cipher_mode` argument.
## <a name="S2"></a> Step 2: Netlist Generation

A gate-level netlist for the Design Under Test (DUT) must be synthesized. CAD4EM only supports flattened verilog designs at this time. Users must also create a testbench to take in the plaintext and keys created through CAD4EM and pass these to their design. As each design is different, these details are left to the user, although we supply an example of such a netlist and testbench with the `synthed.v` and `tb.v` files, respectively. Note that these were made for the Xilinx Spartan-6 Main FPGA onboard the Sakura-G board.

## <a name="S3"></a> Step 3: Test Bench Modification
`python3 Read_Netlist.py`

This script reads in the netlist created in the [last step](https://github.com/jinyier/CAD4EM#S2) and uses it to
configure a simulation testbench.We can use `python Read_Netlist.py --help` to find all available arguments to
control the names of the input and output files.
 
By default, this takes in
a functional netlist which has a path specified by
`--timing_filename`. It ***modifies*** one important file, the testbench `tb.v`
(`--testbench_in_filename`). It uses `tb.v` as a template to create two new testbenches,
 as well as a number of intermediate files. Note that
this means that the framework for a testbench must exist prior to using this tool.
We do provide a sample testbench in the supplied `tb.v` but this will only work
for our provided AES-128 implementation.  Two new testbenches are created, each relating
to either the input random plaintext or the semifixed plaintext. By default these are called `tb_sim_rand.v`
and `tb_sim_semifixed.v`. Paths for these can be set via the `--testbench_out_filename` argument
although the semifixed file is always denoted by ending in "_semifixed.v" and the random ending in "_rand.v".

This step may require modification of the python code to in order to function for different processes.
The code simply searches for certain strings that denote target components ('FF' for flip-flops in this example) in the target testbench and records/replaces text
between them. Different testbenches will be coded differently and so the strings
we search for by default may not be present in every testbench. Please examine the 
`modify_test_bench` function in `Read_Netlist.py`, and especially the 
variables: `before_registers`, `after_registers`, `before_fanouts`, `after_fanouts`,
`before_plaintext_filename`, `after_plaintext_filename`, `before_l_trace_filename`,
and `after_l_trace_filename`. to modify this for different libraries.

## <a name="S4"></a> Step 4: Simulation
The resulting testbenches must now be run. These output the two L-trace files which are used in the [final analysis](https://github.com/jinyier/CAD4EM#S5). We provide examples of these outputs with the `rand_data_hd_0001_2000.txt` and `semi_data_hd_0001_2000.txt` files. Please note that these have measurements for 2000 KTPs instead of the default 1000.

## <a name="S5"></a> Step 5
`python3 gen_t_cals.py`

This script performs the t-test calculations used to analyze the L-traces generated in the [previous] step](https://github.com/jinyier/hw_cad4em#S4).
We can use `python gen_t_calcs.py --help` to view all available arguments. 

We can specify the number of L_traces we expect through `--num_traces`.
The 
paths to the input files can be specified with the `--rd_init_filename` 
(for the plaintext L-traces) and `--sf_init_filename` (for the semifixed 
L-traces). The final output can be specified through the `--t_calc_out_filename`
argument. 

This script will display two figures demonstrating the results
one at a time in quick succession. First, a running t-score is shown, which communicates how the t-score changes with additional samples. The second chart show the t-score at every given sample time, using all samples.
 