import numpy as qk
import matplotlib.pyplot as plt
import sys
import argparse
import os


def random_trace_processing(num=2000, sim_init_filename='data_hd_0001_2000.txt',
                            out_filename="rd_trace.txt"):
    '''
    processes td trace
    TODO figure out what td is
    TODO figure out what num is
    :param num: number of lines?
    :param sim_init_filename: data file in
    :param out_filename: path to save data
    :return:
    '''
    sim_rd_trace = qk.zeros((num, 28), dtype=qk.int16)
    sim_init_trace = qk.genfromtxt(sim_init_filename)
    sim_rd_trace = qk.reshape(sim_init_trace, (num, 28))

    #m, n = sim_td_trace.shape

    rd_trace = sim_rd_trace
    qk.savetxt(out_filename, rd_trace, delimiter=',')


def semifixed_trace_processing(num=2000, sim_init_data='semi_data_hd_0001_2000.txt',
                               out_filename='sf_trace.txt'):
    '''
    preprocess semi fixed data
    TODO figure out what num is
    :param num: ?
    :param sim_init_data: file to read from
    :param out_filename: file to save to
    :return:
    '''
    sim_sf_trace = qk.zeros((num, 28), dtype=qk.int16)
    sim_init_trace = qk.genfromtxt(sim_init_data)
    sim_sf_trace = qk.reshape(sim_init_trace, (num, 28))
    sf_trace = sim_sf_trace
    # TODO this doesn't match semifixed.mat
    qk.savetxt(out_filename, sf_trace, delimiter=',')


def compute_traces(num=2000, rd_filename="rd_trace.txt", sf_filename="sf_trace.txt", out_filename="t_calcs.txt"):
    '''
    #TODO what is num?
    use t-test to compute traces
    :param num: ?
    :param rd_filename: rd file to read from
    :param sf_filename: semifixed file to read from
    :param out_filename: file to save to
    :return:
    '''
    # read in data
    rd_trace = qk.genfromtxt(rd_filename, delimiter=',')
    sf_trace = qk.genfromtxt(sf_filename, delimiter=',')
    m, n = rd_trace.shape
    # check values

    # initialze out traces
    out_t_values = qk.zeros((m, n))
    # for each row
    for j in range(n):
        # for each column
        for i in range(m):
            # find the sums up to that row along each column
            mu0 = qk.mean(sf_trace[0:i+1, j])
            mu1 = qk.mean(rd_trace[0:i+1, j])
            # compute variations and then normalize them
            stdev0 = qk.var(sf_trace[0:i+1, j])
            stdev1 = qk.var(rd_trace[0:i+1, j])
            # update out_t_values with tvalue
            try:
                out_t_values[i, j] = (mu0 - mu1) / (qk.sqrt(stdev0 ** 2 / i + stdev1 ** 2 / i))
            except ZeroDivisionError:
                out_t_values[i, j] = qk.nan
    # do some plotting
    plt.figure(1)
    for i in range(n):
        plt.plot(out_t_values[:, i], c=get_color(i), marker=get_shape(i),markersize=1)
    plt.xlabel('number of traces')
    plt.ylabel('T-test value')
    plt.show()

    plt.figure(2)
    plt.plot(out_t_values[num-1, :])
    plt.show()
    qk.savetxt(out_filename, out_t_values, delimiter=',')


def get_color(num):
    num = num % 3
    if num == 0:
        return 'b'
    elif num == 1:
        return 'g'
    else:
        return 'r'

def get_shape(num):
    num = num % 28
    num = int(num/4)
    if num == 0:
        return '^'
    elif num == 1:
        return 'o'
    elif num == 2:
        return '+'
    else:
        return 'v'


def main(num_traces, rd_in, rd_out, sf_in, sf_out, t_calc_out):
    random_trace_processing(num=num_traces, sim_init_filename=rd_in, out_filename=rd_out)
    semifixed_trace_processing(num=num_traces, sim_init_data=sf_in, out_filename=sf_out)
    compute_traces(num=num_traces, rd_filename=rd_out, sf_filename=sf_out, out_filename=t_calc_out)

if __name__ == "__main__":
    sep = os.path.sep
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--random_out_filename', action='store', type=str, default='rd_trace.txt',
                            help='path to input timing file')
        parser.add_argument('--random_init_filename', action='store', type=str, default='..'+sep+'Step_4'+sep+'rand_data_hd_0001_2000.txt',
                            help='path to input timing file')
        parser.add_argument('--semifixed_out_filename', action='store', type=str, default='sf_trace.txt',
                            help='path to input timing file')
        parser.add_argument('--semifixed_init_filename', action='store', type=str, default='..'+sep+'Step_4'+sep+'semi_data_hd_0001_2000.txt',
                            help='path to input timing file')
        parser.add_argument('--t_calc_out_filename', action='store', type=str, default='t_calcs.txt',
                            help='path to input timing file')
        parser.add_argument('--num_traces', action='store', type=int, default=2000,
                            help='number of traces')

        args = parser.parse_args()

        rd_out = args.random_out_filename
        rd_in = args.random_init_filename
        sf_out = args.semifixed_out_filename
        sf_in = args.semifixed_init_filename
        t_calc = args.t_calc_out_filename
        num_traces = args.num_traces

        sys.exit(main(rd_in=rd_in, rd_out=rd_out, sf_in=sf_in, sf_out=sf_out, t_calc_out=t_calc, num_traces=num_traces))
    except KeyboardInterrupt:
        sys.exit()
