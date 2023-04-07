import os

from PyTealCodeGenerator import parse_and_generate_code, get_schema_metrics
from macro.AlgoClientBuilder import AlgoClientBuilder

algo_client = AlgoClientBuilder("mnemonic", "address", "token")


if __name__ == '__main__':
    path_to_file = './test_cases/Counter.py'
    with open(path_to_file, 'r') as file:
        data = file.read()
    parse_and_generate_code(data)
    global_ints, global_bytes, local_ints, local_bytes = get_schema_metrics()

    # pep 8 generated files
    os.system("autopep8 ./generated_code/server_code.py --in-place")
    os.system("autopep8 ./generated_code/blockchain_code.py --in-place")

    algo_client.init_algo_client(local_ints, local_bytes, global_ints, global_bytes)
