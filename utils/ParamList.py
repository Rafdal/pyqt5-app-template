""" 
This module contains different data structures that can be used to set parameter Objects, configure tools or modules from the application.

The parameters that can be used are:
- TextParam:    Text parameter with a string
- NumParam:     Numerical parameter with (interval) and (step)
- ChoiceParam:  Choice parameter with a list of strings (choices)
- BoolParam:    Boolean parameter

The parameters should be grouped in a ParameterList object. 
Each one can be accessed and modified by its name key using the [] operator of the ParameterList object

The parameter list is used to automatically generate a GUI for the user to interact with the parameters.

Each parameter will be displayed as:
- NumParam      ->  NumberInput (Slider + TextInput)
- ChoiceParam   ->  DropDownMenu
- BoolParam     ->  SwitchButton
- TextParam     ->  TextInput

 """

import typing
# import sympy as sp
# import numpy as np

class ParameterBase():
    def __init__(self, name="parameter", text="", *args, **kwargs):
        self.internal_name = name
        self.text = text
        if "render" in kwargs:
            self.render = kwargs["render"]
        else:
            self.render = True

    @property
    def name(self):
        return self.internal_name

class ConstParam(ParameterBase):
    def __init__(self, name="const", value="CONST VAL", text="Constant", *args, **kwargs):
        super().__init__(name, text, *args, **kwargs)
        self.type = "const"
        self.value = value

    @property
    def data(self):
        return self.value
    
    @data.setter
    def data(self, value):
        self.value = value

class TextParam(ParameterBase):
    """ Text parameter with a string"""
    def __init__(self, name="txt", value="", text="text parameter", regex="^$|^[a-zA-Z0-9\\*\\+\\-\\^\\/\\(\\)\\s\\.]*", default=None, *args, **kwargs):
        super().__init__(name, text, *args, **kwargs)
        self.type = "text"
        self.regex = regex
        if default is not None:
            self.value = default
        else:
            self.value = value

    @property
    def data(self):
        return self.value

    @data.setter
    def data(self, value):
        self.value = value


class NumParam(ParameterBase):
    """ Numerical parameter with interval and step"""
    def __init__(self, name="x", interval=(0, 100), step=1, value=0, text="numerical parameter", default=None, *args, **kwargs):
        super().__init__(name, text, *args, **kwargs)
        self.type = "Number"
        self.interval = interval
        self.step = step
        self.sliderRelease = kwargs.get("sliderRelease", False)
        if default is not None:
            self.value = default
        else:
            self.value = value

    @property
    def data(self):
        return {"value": self.value, "interval": self.interval, "step": self.step, "sliderRelease": self.sliderRelease}
    
    @data.setter
    def data(self, data):
        if not isinstance(data, dict):
            raise ValueError("NumParam data must be a dict")

        if "value" in data:
            if not isinstance(data["value"], (int, float)):
                raise ValueError("NumParam value must be a number")
            self.value = data["value"]

        if "interval" in data:
            if not isinstance(data["interval"], (tuple, list)) or len(data["interval"]) != 2:
                raise ValueError("NumParam interval must be a tuple with two elements")
            if data["interval"][0] >= data["interval"][1]:
                raise ValueError("NumParam interval must have the first element smaller than the second")
            self.interval = data["interval"]

        if "step" in data:
            if not isinstance(data["step"], (int, float)):
                raise ValueError("NumParam step must be a number")
            self.step = data["step"]

        if "sliderRelease" in data:
            if not isinstance(data["sliderRelease"], bool):
                raise ValueError("NumParam sliderRelease must be a boolean")
            self.sliderRelease = data["sliderRelease"]
    

class ChoiceParam(ParameterBase):
    """ Choice parameter with a list of choices"""
    def __init__(self, name: str, options: typing.List[str] = ["None"], value="None", text="choice parameter", default=None, *args, **kwargs):
        super().__init__(name, text, *args, **kwargs)
        self.type = "Choice"
        self.options = options
        if default is not None:
            self.value = default
        else:
            self.value = value

    @property
    def data(self):
        return self.value
    @data.setter
    def data(self, data):
        if data not in self.options:
            raise ValueError(f"ChoiceParam value must be one of the options: {self.options}")
        self.value = data


class BoolParam(ParameterBase):
    """ Boolean parameter"""
    def __init__(self, name="z", value=False, text="boolean parameter", default=None, *args, **kwargs):
        super().__init__(name, text, *args, **kwargs)
        self.type = "Boolean"
        if default is not None:
            self.value = default
        else:
            self.value = value

    @property
    def data(self):
        return self.value
    
    @data.setter
    def data(self, value):
        if not isinstance(value, bool):
            raise ValueError("BoolParam value must be a boolean")
        self.value = value


class ParameterList():
    """ List of parameters with unique names"""
    def __init__(self, paramList: typing.List[ParameterBase]):
        self.internal_parameter_list = {}
        
        if (not isinstance(paramList, list)) or not isinstance(paramList[0], ParameterBase):
            raise ValueError("ParameterList must be initialized with a list of ParameterBase derived objects")

        # look for repeated names
        names = [p.name for p in paramList]
        if len(names) != len(set(names)):
            raise ValueError("Repeated parameter names")
        
        for p in paramList:
            if not isinstance(p, ParameterBase):
                raise ValueError("All parameters must inherit ParameterBase")
            self.internal_parameter_list[p.name] = p

    def setData(self, key, value):
        if key not in self.internal_parameter_list:
            raise KeyError(f"Parameter {key} not found in the ParameterList")
        self.internal_parameter_list[key].data = value

    def toDict(self) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        return {name: {"type": param.type, "data": param.data} for name, param in self.internal_parameter_list.items()}

    def fromDict(self, data: typing.Dict[str, typing.Dict[str, typing.Any]]):
        for name, param_data in data.items():
            if name not in self.internal_parameter_list:
                raise KeyError(f"Parameter {name} not found in the ParameterList")
            param = self.internal_parameter_list[name]
            if param.type != param_data["type"]:
                raise ValueError(f"Parameter {name} type mismatch. Expected {param.type}, got {param_data['type']}")
            param.data = param_data["data"]


    def addParameter(self, param: ParameterBase):
        if not isinstance(param, ParameterBase):
            raise ValueError("Parameter must be of type ParameterBase")
        if param.name in self.internal_parameter_list:
            raise ValueError(f"Parameter {param.name} already exists")
        self.internal_parameter_list[param.name] = param


    def __len__(self):
        return len(self.internal_parameter_list)
    
    def keys(self):
        return self.internal_parameter_list.keys()
    
    def __iter__(self):
        params = self.internal_parameter_list.values()
        return iter(params)

    def __getitem__(self, key):
        if key not in self.internal_parameter_list:
            raise KeyError("Parameter not found")
        return self.internal_parameter_list[key].value
    
    def asInt(self, key):
        if key not in self.internal_parameter_list:
            raise KeyError("Parameter not found")
        return int(self.internal_parameter_list[key].value)
    
    def __setitem__(self, key, value):
        if key not in self.internal_parameter_list:
            raise KeyError(f"Parameter {key} not found")
        # if not isinstance(value, type(self.internal_parameter_list[key].v)):
        #     raise ValueError(f"Parameter {key} type mismatch. Expected {type(self.internal_parameter_list[key].step)}, got {type(value)}")
        self.internal_parameter_list[key].value = value



    # def getFunction(self, eq: str, var: str, const = {}):
    #     '''
    #     If a TextParam is a valid equation, this function returns a lambda function that can be used to evaluate the equation with a given variable, the exising parameters and constants.
    #     - eq: name of the TextParam that contains the equation
    #     - var: name of the variable to be used in the equation (is not needed to be present in the equation)
    #     - const: dictionary with constant values (optional)
    #     '''
    #     eqstr = self[eq]
    #     try:
    #         eq = sp.sympify(eqstr)
    #     except Exception as e:
    #         raise ValueError(f"Error parsing equation: {eqstr}")            
        
    #     if var in const.keys():
    #         raise ValueError(f"Variable {var} is also a constant")
    #     if var in self.keys():
    #         raise ValueError(f"Variable {var} is also a parameter")

    #     # Substitute constants and parameters
    #     for symbol in eq.free_symbols:
    #         if symbol.name in self.keys():
    #             eq = eq.subs(symbol, self[symbol.name])
    #         elif symbol.name in const.keys():
    #             eq = eq.subs(symbol, const[symbol.name])

    #     if len(eq.free_symbols) > 1:
    #         raise ValueError(f"Equation '{eqstr}' has more than one free symbols: {eq.free_symbols}")

    #     if len(eq.free_symbols) == 0:
    #         return lambda x: complex(eq.evalf())
        

    #     eq = eq.simplify()
    #     x = eq.free_symbols.pop()

    #     # Lambdify the equation
    #     func = sp.lambdify(x, eq, "numpy")
    #     return func