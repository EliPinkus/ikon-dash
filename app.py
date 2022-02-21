import panel as pn
import datetime as dt
import param
import pandas as pd

class BaseClass(param.Parameterized):
    x                       = param.Parameter(default=3.14, doc="X position")
    y                       = param.Parameter(default="Not editable", constant=True)
    string_value            = param.String(default="str", doc="A string")
    num_int                 = param.Integer(50000, bounds=(-200, 100000))
    unbounded_int           = param.Integer(23)
    float_with_hard_bounds  = param.Number(8.2, bounds=(7.5, 10))
    float_with_soft_bounds  = param.Number(0.5, bounds=(0, None), softbounds=(0,2))
    unbounded_float         = param.Number(30.01, precedence=0)
    hidden_parameter        = param.Number(2.718, precedence=-1)
    integer_range           = param.Range(default=(3, 7), bounds=(0, 10))
    float_range             = param.Range(default=(0, 1.57), bounds=(0, 3.145))
    dictionary              = param.Dict(default={"a": 2, "b": 9})


class Example(BaseClass):
    """An example Parameterized class"""
    timestamps = []

    boolean                 = param.Boolean(True, doc="A sample Boolean parameter")
    color                   = param.Color(default='#FFFFFF')
    date                    = param.Date(dt.datetime(2017, 1, 1),
                                         bounds=(dt.datetime(2017, 1, 1), dt.datetime(2017, 2, 1)))
    dataframe               = param.DataFrame(pd._testing.makeDataFrame().iloc[:3])
    select_string           = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])
    select_fn               = param.ObjectSelector(default=list,objects=[list, set, dict])
    int_list                = param.ListSelector(default=[3, 5], objects=[1, 3, 5, 7, 9], precedence=0.5)
    single_file             = param.FileSelector(path='../../*/*.py*', precedence=0.5)
    multiple_files          = param.MultiFileSelector(path='../../*/*.py?', precedence=0.5)
    record_timestamp        = param.Action(lambda x: x.timestamps.append(dt.datetime.utcnow()), 
                                           doc="""Record timestamp.""", precedence=0.7)
    
pn.extension()

base = BaseClass()
a = pn.Row(Example.param, base.param)
a.show()