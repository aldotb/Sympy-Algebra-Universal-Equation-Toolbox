
from IPython.display import Image, display,Math
from sympy import *
import numpy as np
import inspect
from functools import wraps 

from lib_Variables import *
from lib_Mathbasic import *
from lib_Mathematica import *
from lib_Algorith import *
from lib_Exponencial import *
 
  
from lib_MyEq import *
from lib_MyEqEq import *
from lib_MyFunctions import *
from math2latex import * 
  
 
import inspect
from functools import wraps
 
 

def _apply_symbolic_options(result, kwargs):
    try:
        if not isinstance(result, Basic):
            return result
        
        if kwargs.get("simplify"):
            result = simplify(result)
        if kwargs.get("factor"):
            result = factor(result)
        if kwargs.get("expand"):
            result = expand(result)
            
        return result
    except Exception:
        return result

def _to_latex(obj):
    try:
        if isinstance(obj, Basic):
            return latex(obj)
        if isinstance(obj, tuple):
            return r"\left(" + ",".join(_to_latex(x) for x in obj) + r"\right)"
        return latex(obj)
    except Exception:
        return str(obj)

def show_assignment(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # ⭐ aplicar opciones simbólicas
        result = _apply_symbolic_options(result, kwargs)
        
        try:
            frame = inspect.currentframe().f_back
            info = inspect.getframeinfo(frame)
            
            if info.code_context:
                line = info.code_context[0].strip()
                
                if "=" in line and not line.startswith(("return","if","while")):
                    varname = line.split("=")[0].strip()
                    display(Math(f"{varname} = {_to_latex(result)}"))
        except Exception:
            pass
        
        return result
    return wrapper
    
@show_assignment   
def formula(expr):
    return expr
@show_assignment   
def Fm(expr):
    return expr    