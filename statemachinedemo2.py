import statemachine.contrib.diagram
from statemachine import StateMachine, State
from statemachine.contrib.diagram import DotGraphMachine


class AdrControl(StateMachine):
    unknown_state = State(initial=True)
    temp_control = State()
    ending_temp_control = State()
    ramp_up = State()
    soak = State()
    ramp_down = State()
    after_ramp_down_chill = State()
    open_loop = State()

    evaluate_unknown_state = unknown_state.to(open_loop) | unknown_state.to(temp_control)
    begin_adr_cycle = open_loop.to(ramp_up)
    abort_adr_cycle = ramp_up.to(ramp_down) | soak.to(ramp_down)
    complete_ramp_up = ramp_up.to(soak)
    complete_soak = soak.to(ramp_down)
    complete_ramp_down = ramp_down.to(after_ramp_down_chill)
    complete_after_ramp_down_chill = after_ramp_down_chill.to(open_loop)
    start_control = open_loop.to(temp_control)
    end_control = temp_control.to(ending_temp_control)
    control_done = ending_temp_control.to(open_loop)


sm = AdrControl()

graph = DotGraphMachine(sm)  # also accepts instances
graph().write_png("out.png")