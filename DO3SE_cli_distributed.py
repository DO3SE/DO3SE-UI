"""This cli entrypoint is for running distributed multiruns."""

import sys
import os
from multiprocessing import Process
from do3se.automate import run, main


def dummy_process(args):
    print('Dummy Process=====')
    print(args)


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) < 3:
        raise ValueError('Not enough arguments')

    print(args[-3:])
    options = args[:-3]
    print(options)
    input_dir, config_dir, output_dir = args[-3:]
    processes_running = []
    for config_file in os.listdir(config_dir):
        output_dir_full = output_dir + '/' + config_file.split('.')[0]
        config_loc = config_dir + '/' + config_file
        if not os.path.exists(output_dir_full):
            os.makedirs(output_dir_full)
        for input_file in os.listdir(input_dir):
            print(f"Running config: {config_file} on input: {input_file}")
            output_name = output_dir_full + '/' + input_file
            input_loc = input_dir + '/' + input_file
            args_in = options + \
                [f'--outfile={output_name}'] + [config_loc, input_loc]
            p = Process(target=main, args=(args_in, ))
            # p = Process(target=main, args=(config_file, input_file, ))
            p.start()
            processes_running.append(p)
