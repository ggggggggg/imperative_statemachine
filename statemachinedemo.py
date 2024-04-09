from collections import OrderedDict
import time
from dataclasses import dataclass, field

@dataclass
class Command:
    pass

@dataclass
class ChangeStateCommand(Command):
    next_state_name: str

@dataclass
class WorldCommand(Command):
    todo: str

@dataclass 
class CompleteCommand(Command):
    pass

@dataclass
class State:
    pass
@dataclass
class StateMachine(State):
    states: list[State]
    name: str
    current_state: State = field(init=False)
    name2state: OrderedDict[str, State] = field(init=False)
    def __post_init__(self):
        self.current_state = self.states[0]
        self.name2state = OrderedDict((state.name, state) for state in self.states)
        assert len(self.name2state) == len(self.states), "state names must be unique"

    def on_enter(self, world_view):
        pass

    def on_exit(self, world_view):
        pass

    def on_complete(self, world_view):
        print(f"StateMachine {self.name=} complete")

    def send(self, world_view):
        command = self.current_state.send(world_view)
        if isinstance(command, ChangeStateCommand):
            self.go_to_next_state_by_name(command.next_state_name, world_view)
            return None #consume the command, so return None
        elif isinstance(command, CompleteCommand):
            self.on_complete(world_view)
            return CompleteCommand()     
        return command
    
    def go_to_next_state_by_name(self, name, world_view):
        next_state = self.name2state[name]
        self.current_state.on_exit(world_view)
        next_state.on_enter(world_view)
        self.current_state = next_state

    def run_forever_with_world(self, world):
        world.on_enter()
        while True:
            try:
                world.update_world()
                world_view = world.read_only_view()
                command = self.send(world_view)
                if isinstance(command, WorldCommand):
                    world.do_command(command)
                elif isinstance(command, CompleteCommand):
                    self.on_complete(world_view)
                    world.on_exit()
                    return 
            except KeyboardInterrupt:
                world.on_exit()
                return

@dataclass
class DummyWorld():
    update_count: int = 0
    def on_enter(self):
        print("DummyWorld on_enter")

    def on_exit(self):
        print("DummyWorld on_exit")

    def update_world(self):
        self.update_count += 1
        if self.update_count % 10==0:
            print("""here we're updating the world! like polling instruments in an async way!
                  we update more often! I only print out sometimes!""")
        time.sleep(0.1)
        return self
    
    def read_only_view(self):
        return DummyWorldView() # but should be read only
    
    def do_command(self, command):
        print(f"do_command {command=}")

class DummyWorldView():
    pass



@dataclass
class DoNothingForereverState(State):
    name: str = "DoNothingForereverState"
    def on_enter(self, world_view):
        pass

    def on_exit(self, world_view):
        pass
    
    def send(self, world_view):
        pass



@dataclass
class CounterState(State):
    max_count: int
    name: str = "CounterState"
    next_state_name: str = "CounterState"
    times_entered: int = field(default=0, init=False)
    count: int = field(default=0, init=False)

    def on_enter(self, world_view):
        self.times_entered+=1
        self.count = 0

    def on_exit(self, world_view):
        pass
    
    def send(self, world_view):
        if self.count == self.max_count:
            if self.next_state_name == "Complete":
                return CompleteCommand()
            return ChangeStateCommand(self.next_state_name)
        elif self.count > self.max_count:
            raise Exception("invalid state")
        self.count += 1
        print(f"{self=}")



if __name__ == "__main__":
    states_for_sm1 = [
        CounterState(max_count=10, name="CounterState1", next_state_name="CounterState2"),
        CounterState(max_count=2, name="CounterState2", next_state_name="Complete") 
    ]
    world = DummyWorld()
    sm1 = StateMachine(states_for_sm1, name="sm1")
    states_for_sm2 = [
        CounterState(max_count=3, name="ABC", next_state_name="sm1"),
        sm1
    ]
    sm2 = StateMachine(states_for_sm2, name="sm2")
    sm2.run_forever_with_world(world)