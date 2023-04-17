# Algorand_MacroFramework

This Algorand MacroFramework is a Final Year Project for University of Malta. The implementation is far from perfect, but that was not
the goal of my studies. The main goal was to see if the appraoch is viable in any case.
I hope you will have enough patience to test out my project and provide me with some feedback using a google form with some questions, that takes around
10 minutes to complete. (For more detail see the Quiz section)

## Short Abstract Idea

This project aims to contribute to the existing research in macroprogramming of smart contract systems,
with a focus on developing a Python framework for decentralised application systems on the Algorand blockchain.
The proposed framework utilises a Python abstract syntax tree (AST) parser to generate both on-chain and off-chain
code for Algorand blockchain decentralised applications (dApp). The primary objective was to design and build a 
framework for the smart contract system's domain that provides a unified view of the entire system while significantly 
reducing the lines of code and minimising the time required for developing dApps.

The framework was carefully designed to abstract away low-level code and provide seamless communication between on-chain
and off-chain platforms. The goal was to enable developers to exploit Algorand's smart contract functionality while minimising
the time and effort required to develop dApps. The framework supports computing and storing data on both on-chain and off-chain
platforms through a macroprogramming tag-based approach and Python wrapper classes.

## Data and Computation separation tools

The idea behind this project is to use macroprogramming tag-based approach, to decide the locality of data and computation. 
This approach involved labeling code blocks and statements to guide the parser to deploy the particular code on the annotated
platform. As a result, three labels were established to represent each computation scenario:
(I) @XOnServer , (II) @XOnBlockchain and (III) @XAll. Logic can be computed either on-chain, off-chain, or on both platforms. 

As Python does not support annotations fro varialbes, the decision was made to employ a wrapper class, XWrapper,
to indicate the variable's association with the blockchain. The XWrapper class is able to store any given value
and customize its behaviour by selecting available enum classes. This approach allows the developers to determine whether
the variable should exist solely on the on-chain platform or allow the compiler decide on the data locality itself and whether 
it should be a global or a local variable within the smart contract.

Sample .py files can be found in the test_cases file. It includes a working "Hello" decentralised application (dApp),
a working "Counter" and "Casino" dApp and a "Stupid_Counter" dApp wich also compiles, with no actual use as just to show possible code writing.

## How to use the System

You should start by creating a .py file, in which you will write and annotate methods and classes. Whenever you are finished, go to main.py and 
enter the path of your original file into 'path_to_file' variable. Do not forget to customize AlgoClientBuilder with your own parameters.
When the compiltaion is complete, go to ./generated_code/blockchain_code.py, find at the bottom of the code another main programm and run it to compile
Teal approval and clear code, as well as ABI for the contract.

## Specifications and Limitations

There are some specifications that must be followed in order for the code to work properly.

### IMPORTANT

1. When tagging a method with @XAll or @XOnBlockchain and passing arguments to a method, it should be noted that you must specify the type
of the arguments as well, as Teal compiler is sensitive to this sort of things, so it will not be able to compile otherwise.

2. If there is need to use PyTeal packages like "Global" or "Txn", they should be called in the python code. as if they would return normal Python types.
This is crucial, as there is no support these packages yet.

3. For now, only Opt_in, Close_out and Custom Methods are customisable for the generated smart contract. In future, other Bare Call Apps will be
supported too.

4. There is no support for Box storage yet.

5. Match cases in python represent the Cond expression. 

6. Pass in Python is interpreted as Return(1) in PyTeal.

7. Python assert is interpreted as PyTeal's Assert(...) (Other Python functionality is converted to PyTeal as close as possible to make it self-explanatory)

8. No support for 'For' loops is available right now, it is advised to use While loops.

9. If you need to use alogrand API on server code. use only 'algod_client' naming for it. And if you need to call method from smart contract on server side,
use 'algo_client.call_app(...)'. algo_client itself dhould be imported from main.


# Bugs, Errors

As this program is written only by 1 developer, there are bound to be mistakes and bugs, which I am glad to hear about in the quiz below as well as your overall
experience using this framework.

# Quiz

It would mean a lot if you would take a quiz to give me feedback on my project. The quiz is fully anonymous, but the data collected will be used in my
FYP diploma to help me evaluate the proposed approach and system.

link: 

