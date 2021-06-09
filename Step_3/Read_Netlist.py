import sys
import argparse
import os

def netlist_preprocess (timing_filename='tb_time_impl.v', preprocessed_filename="timing_preprocessed.txt"):
    '''
    net list preprocessing
    :param timing_filename: timing.v file to use
    :param preprocessed_filename: name of preprocessed file
    :return: None
    '''
    # open the timing file
    timing_file = open(timing_filename, 'r')
    timing_data = timing_file.readlines()
    # find the number of lines in the file
    timing_data_length = len(timing_data)
    # open the empty preprocessing file
    preprocessed_file = open(preprocessed_filename, 'w+')
    # kept while format from supplied files. For each line in timing,
    for line_number in range(timing_data_length):
        # if it ends in a ;
        if ";" in timing_data[line_number]:
            # save the whole line
            print(timing_data[line_number], sep="", end="", file=preprocessed_file)
        # otherwise, it isn't the end of the line
        else:
            # don't print the newline character
            print(timing_data[line_number][0:-1], sep="", end="", file=preprocessed_file)
        # move to the next line
        line_number += 1

    preprocessed_file.close()
    # print for visual confirmation
    print(timing_data[7500:7502])
    print(timing_data_length)
    print(line_number)


def extract_registers_from_preprocessed_file(preprocessed_filename,
                                             raw_register_filename):
    '''
    extract raw registers or lines??? not sure
    :param preprocessed_filename: the preprocessed data
    :param raw_register_filename: extract the raw registers
    :return: None
    '''
    # read in the preprocessed file
    preprocessed_file = open(preprocessed_filename, 'r')
    preprocessed_data = preprocessed_file.readlines()
    # get the number of lines in it
    preprocessed_data_length = len(preprocessed_data)
    # start an empty list
    raw_registers = []
    # kept while format from supplied files. For each line in the preproccessed code,
    for current_line_number  in range(preprocessed_data_length):
        # if it has X_FF
        if "X_FF #" not in preprocessed_data[current_line_number]:
            # Keep it
            continue
        raw_registers.append(preprocessed_data[current_line_number])
    register_file = open(raw_register_filename, 'w+')

    #  kept while format from supplied files. For each line in timing,
    for register_file_line_number in range(len(raw_registers)):
        # write the register of the same number to the raw registers file
        print(raw_registers[register_file_line_number], sep="", end="", file=register_file)
    register_file.close()

    print("first_step_over")

    # 常用函数
    # remove padding / unwanted lines
    for i in preprocessed_data:  # 不考虑.PAD
        if ".PAD" in i or "X_ZERO" in i:
            preprocessed_data.remove(i)


def str_part0(input_string, splitter):  # s1s2都为字符串，基于s2把s1分成两段并返回前半段,且不包括s2
    '''
    split an input string and return the first part
    :param input_string: string to split
    :param splitter: str to split on
    :return: first part of the split string
    '''
    split_string = input_string.split(splitter, 1)
    if len(split_string) == 1:
        return None
    return split_string[0]


def str_part1(input_string, splitter):  # s1s2都为字符串，基于s2把s1分成两段并返回后半段,且不包括s2
    '''
    split an input string and return the second part
    :param input_string: string to split
    :param splitter: str to split on
    :return: second part of the split string
    '''
    split_string = input_string.split(splitter, 1)
    if len(split_string) == 1:
        return None
    return split_string[1]


def str_output(input_string):  # 将字符串中的.O()的内容输出为字符串
    '''
    get the string that exists between two sub_strs
    :param input_string:input str
    :return: string between 0.( and ), or None
    '''
    after_0 = input_string.split(".O(")[1]
    before_0 = after_0.split(")")[0]
    if len(after_0) == 1 or len(before_0) == 1:
        return None
    return before_0


def find_target_between_p(target_str, data_list):  # 将所有(s1)存在的行都找出来，生成并返回列表
    '''
    find a target str in a list of strs
    :param target_str:
    :param data_list:
    :return: all lines that have the the target str
    '''
    out = []
    op_target_cp = '(' + target_str + ')'
    for i in data_list:
        if op_target_cp in i:
            out.append(i)
    return out


def find_and_remove_duplicate_targets_between_p(target_str, data_list):
    '''
    remove unwanted strs from a list of target strs found in a list of strs
    :param target_str: str to find
    :param data_list: data to search
    :return: list of target strs found in data_list, that don't match a second condition
    '''
    found_strs = find_target_between_p(target_str, data_list)
    if len(found_strs) == 0:
        return found_strs  # 返回空列表好 还是None好？？
    else:
        for i in found_strs:
            if ".O(" + target_str + ")" in i:  # 没考虑单元的信号接入自己的情况,验证没有该情况出现
                found_strs.remove(i)
        return found_strs


def str_next_output(target_str, data_list):
    '''
    find target strs in a list of strs and return them cleaned
    :param target_str: str to find
    :param data_list: all data to search, a list of strs
    :return: cleaned list of target strs
    '''
    found_targets = list()
    found_targets.extend(find_and_remove_duplicate_targets_between_p(target_str, data_list))
    cleaned_targets = list()
    if len(found_targets) == 0:
        return None
    else:
        for i in found_targets:
            cleaned_targets.append(str_output(i))
        return cleaned_targets


def extract_fanouts_from_preprocessed_file(raw_registers_filename='20190920_lab2_FF.txt',
                                           preprocessed_filename="timing_preprocessed.txt",
                                           register_filename='20190920_lab2_FF_O.txt',
                                           fanout_filename='20190920_lab2_FF_O_FANOUT.txt'):
    '''
    extract fan outs and registers from preprocessed timing files and the raw registers
    :param raw_registers_filename: path to the raw registers file
    :param preprocessed_filename: path to the preprocessed file
    :param register_filename: file path to save the register data to
    :param fanout_filename: file path to save the fan out data to
    :return: None
    '''
    # open and read the input files
    preprocessed_file = open(preprocessed_filename, 'r')
    preprocessed_data = preprocessed_file.readlines()
    raw_registers_file = open(raw_registers_filename, "r")
    raw_registers = raw_registers_file.readlines()

    registers = []
    # copy all the raw registers into a list
    for current_line_number in range(len(raw_registers)):
        registers.append(str_output(raw_registers[current_line_number]))
    # make sure they are the same length
    print(len(raw_registers))
    print(len(registers))

    register_file = open(register_filename, 'w+')
    register_filenumber = 0

    print("second_step_over")

    # 看节点有没有重复的   批量注释
    # kept from the supplied code
    loop_unit_all = list(set(registers))
    print(len(loop_unit_all))
    register_file = open(register_filename, 'w+')  # 第一部分文本打印
    for register_filenumber in range(len(loop_unit_all)):
        print(
            ",uut." + loop_unit_all[register_filenumber],
            sep="", end='', file=register_file)
    register_file.close()
    print(register_filenumber)

    loop_unit_all_fanout = []
    # for all registers
    for i in loop_unit_all:
        # if there are no fan outs
        if str_next_output(i, preprocessed_data) is None:
            # set fan out to 0
            fanout_number = 0
        # otherwise
        else:
            fanout_number = len(str_next_output(i, preprocessed_data))
        loop_unit_all_fanout.append(fanout_number)
    print(len(loop_unit_all_fanout))
    # save fanout information into the fanout file
    fanout_file = open(fanout_filename, 'w+')  # 第二部分文本打印
    fanout_file_length = len(loop_unit_all_fanout) - 1
    for fanout_line_number in range(len(loop_unit_all_fanout)):
        # it has some weird formatting, I'm guessing for planahead?
        print(
            loop_unit_all_fanout[fanout_line_number], "*(data2[", fanout_file_length, "]^data1[", fanout_file_length, "])+",
            sep="", end='', file=fanout_file)
        fanout_file_length -= 1
    fanout_file.close()
    print(fanout_line_number)
    #print("regs", loop_unit_all)
    #print("fanout", loop_unit_all_fanout)


def modify_test_bench(fanout_filename, register_filename, tb_in, testbench_filename, input_plaintext_filename,
                      l_trace_output):
    fanout_file = open(fanout_filename)
    fanouts = ""
    for line in fanout_file:
        fanouts += line
    fanout_file.close()
    fanouts = fanouts[:-1]

    register_file = open(register_filename)
    registers = ""
    for line in register_file:
        registers += line
    register_file.close()
    registers = registers[1:]

    testbench_file = open(tb_in, "rt")
    tb_contents = ""
    for line in testbench_file:
        tb_contents += line
    testbench_file.close()
    # replace the text between "//data1 <= data1_1;", i.e. the registers
    before_registers = tb_contents.split("data1<={")[0]
    after_registers = tb_contents.split("//data1 <= data1_1;")[1]
    tb_contents = before_registers+"data1<={"+registers+"};\n\t\t\t//data1 <= data1_1;\n"+after_registers
    # replace the text between "plot<= (" and "]));" i.e. the fanouts
    before_fanouts = tb_contents.split("plot<= (")[0]
    after_fanouts = tb_contents.split("]));")[1]
    tb_contents = before_fanouts + "plot<= (" + fanouts + ");" + after_fanouts
    # replace the text between 'readmemh("' and '",data);' i.e. the plaintext in
    before_plaintext_filename = tb_contents.split('readmemh("')[0]
    #print(before_plaintext_filename)
    after_plaintext_filename = tb_contents.split('", ktp_data);')[1]
    plain_tb = before_plaintext_filename + 'readmemh("'+input_plaintext_filename+'", ktp_data);'+after_plaintext_filename
    # replace the text between '$fopen("' and '"w");' i.e. the l trace out
    before_l_trace_filename = plain_tb.split('$fopen("')[0]
    after_l_trace_filename = plain_tb.split('"w");')[1]
    final_tb = before_l_trace_filename + '$fopen("' + l_trace_output + '", "w");' + after_l_trace_filename
    # write altered contents
    testbench_file = open(testbench_filename, "wt")
    testbench_file.writelines(final_tb)
    testbench_file.close()


def main(timing, pre, raw_targs, reg, fan, tb_in, tb_out, plain_text_path, semifixed_path):
    netlist_preprocess(timing_filename=timing, preprocessed_filename=pre)
    
    extract_registers_from_preprocessed_file(raw_register_filename=raw_targs, preprocessed_filename=pre)
    
    extract_fanouts_from_preprocessed_file(preprocessed_filename=pre, raw_registers_filename=raw_targs,
                                           register_filename=reg, fanout_filename=fan)
                                           
    modify_test_bench(register_filename=reg, fanout_filename=fan, testbench_filename=tb_out[:-2]+"_rand.v",
                      input_plaintext_filename=plain_text_path, l_trace_output="plaintext_L_trace.txt", tb_in=tb_in)
                      
    modify_test_bench(register_filename=reg, fanout_filename=fan, testbench_filename=tb_out[:-2]+"_semifixed.v",
                      input_plaintext_filename=semifixed_path, l_trace_output="semifixed_L_trace.txt", tb_in=tb_in)


if __name__ == "__main__":
    sep = os.path.sep
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--timing_filename', action='store', type=str, default='..'+sep+'Step_2'+sep+'synthed.v',
                            help='path to input timing file')
        parser.add_argument('--preprocessed_filename', action='store', type=str, default="timing_preprocessed.txt",
                            help='path to output preprocessed file')
        parser.add_argument('--raw_targets_filename', action='store', type=str, default='20190920_FF_raw.txt',
                            help='path to output raw target components file')
        parser.add_argument('--targets_filename', action='store', type=str, default='20190920_FF.txt',
                            help='path to output register file')
        parser.add_argument('--fanout_filename', action='store', type=str, default='20190920_FF_FANOUT.txt',
                            help='path to output fanout file')
        parser.add_argument('--testbench_in_filename', action='store', type=str, default='..'+sep+'Step_2'+sep+'tb.v',
                            help='path to input tb file')
        parser.add_argument('--testbench_out_filename', action='store', type=str, default='tb_sim.v',
                            help='path to output tb file')
        parser.add_argument('--plaintext_filename', action='store', type=str, default='rand_plain.txt',
                            help='name of input plaintext file')
        parser.add_argument('--semifixed_filename', action='store', type=str, default='semi_plain.txt',
                            help='name of input semifixed plaintext file')


        args = parser.parse_args()
        fanout = args.fanout_filename
        targs = args.targets_filename
        raw_targs = args.raw_targets_filename
        timing = args.timing_filename
        plain_text = args.plaintext_filename
        sf_text = args.semifixed_filename
        assert timing[-2:] == '.v', "timing file must be verilog"
        pre = args.preprocessed_filename
        tb_in = args.testbench_in_filename
        assert tb_in[-2:] == '.v', "testbench wrapper must be verilog"
        tb_out = args.testbench_out_filename
        assert tb_out[-2:] == '.v', "testbench wrapper must be verilog"
        sys.exit(main(fan=fanout, raw_targs=raw_targs, timing=timing, pre=pre, reg=targs, tb_in=tb_in,
                      plain_text_path=plain_text, semifixed_path=sf_text, tb_out=tb_out))
    except KeyboardInterrupt:
        sys.exit()
