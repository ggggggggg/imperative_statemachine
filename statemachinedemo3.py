from collections import OrderedDict
import time
from dataclasses import dataclass, field
import types
import inspect
from imperative_statemachine import state
from typing import Callable, Union
import random

# how to compile function from text
# https://stackoverflow.com/questions/32429154/how-to-compile-a-function-at-run-time
# how to get function source
# https://stackoverflow.com/questions/427453/how-can-i-get-the-source-code-of-a-python-function


@state
def blah():
    print("blah")
    for i in range(10):
        if i%3 == 2:
            print("fizz")
    return foo

@state 
def fizz():
    for i in range(4):
        print("fizz")
        if random.randint(0,1) == 1:
            return blah
        return foo
    
@state
def foo():
    print("foo")
    if random.randint(0,1) == 1:
        return blah
    return

line_numbers, next_state = fizz.run_until_complete()

def run_state_then_next_and_so_on(state):
    while True:
        if state == None:
            return
        line_numbers, state = state.run_until_complete()

run_state_then_next_and_so_on(fizz)

