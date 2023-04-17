import os
import time
from PyTealCodeGenerator import parse_and_generate_code, get_schema_metrics
from macro.AlgoClientBuilder import AlgoClientBuilder


algo_client = AlgoClientBuilder("mnemonic",
                                "YYU5DABNUNDIVNFUQG2VHRJ6V3IAQK5FOSGUAO5IIEOERYGFQ3FDTVGM7E",
                                "http://localhost:4001",
                                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                                2
                                )

if __name__ == '__main__':
    start = time.time_ns()
    path_to_file = './test_cases/Casino.py'
    with open(path_to_file, 'r') as file:
        data = file.read()
    parse_and_generate_code(data)
    global_ints, global_bytes, local_ints, local_bytes = get_schema_metrics()

    # pep 8 generated files
    os.system("autopep8 ./generated_code/server_code.py --in-place")
    os.system("autopep8 ./generated_code/blockchain_code.py --in-place")

    print(time.time_ns() - start)

    from memory_profiler import memory_usage

    print(memory_usage())

    algo_client.init_algo_client()
