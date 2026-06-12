from sympy import *
from lib_display import *
# PRIMITIVE PROPIETIES
def unisymbols(ksym):   
    '''
    unisymbols() :  this function homegenize diferent variables whit 
                    the same symbolic name in omly one in all symbols expresion
    '''                         
    try:
        kres=parse_expr(str(ksym))
    except:
        kres=ksym
    return(kres)
def tree_apply(expr, func_to_apply, target_type='pow'):
    """
    Navegador universal. Aplica 'func_to_apply' a cada nodo 
    que coincida con 'target_type'.
    """
    expr = sympify(expr)
    
    # Si el nodo actual coincide con lo que buscamos (ej. es una potencia)
    if whotype(expr, target_type):
        return func_to_apply(expr)

    # Si no es el objetivo pero tiene hijos (Add, Mul, etc.), navegamos
    if expr.args:
        new_args = [tree_apply(a, func_to_apply, target_type) for a in expr.args]
        return expr.func(*new_args, evaluate=False)

    return expr
    
def float2int(expr):
    return intfloat2int(expr)
    
def intfloat2int(expr):
    """
    Convierte floats enteros:
        5.0 -> 5
        2.000 -> 2

    preservando EXACTAMENTE
    la estructura simbólica.
    """

    expr = sympify(expr)

    # =========================
    # 1) NÚMEROS
    # =========================
    if expr.is_Number:

        # Integer ya está bien
        if expr.is_Integer:
            return expr

        # Float
        if expr.is_Float:
            try:
                f = float(expr)

                if f.is_integer():
                    return Integer(int(f))

            except:
                pass

        return expr

    # =========================
    # 2) ÁTOMOS
    # =========================
    if expr.is_Atom:
        return expr

    # =========================
    # 3) RECURSIÓN GENERAL
    # =========================
    new_args = [intfloat2int(a) for a in expr.args]

    # reconstrucción SEGURA
    return expr.func(*new_args, evaluate=False)    
        
def Sadd(*args):
    # Sadd(1,3,5) return 1+3+5 not 9
    return Add(*args,evaluate=False)
 
sadd = Sadd
def Smul(*args):
    # Smul(2,2) return 2/2 not 1
    if len(args)==2:
        p1=args[0]
        p2=args[1]
        if denom(p1)!=1 or denom(p2)!=1:
            if numer(p1)==1 or numer(p2)==1:
                P1=numer(p1)*numer(p2)
                P2=denom(p1)*denom(p2)
                return cleanmul(Sdiv(P1,P2))
            else:
                return cleanmul(Mul(*args,evaluate=False))  
        else:
            return cleanmul(Mul(*args,evaluate=False))
    else:        
        return cleanmul(Mul(*args,evaluate=False) )
 
snul = Smul
def Sdiv(p1,p2):
    #  Sdiv(4,2) return 4/2 not 2
 
    if p1==0:
        return 0
    elif p2==1:
        return p1
    elif p1==1:
        return Sinverse(p2)
    else:
        sexpr='('+str(p1)+')/('+str(p2)+')'
        return cleanmul(parse_expr(sexpr,evaluate=False))

sdiv = Sdiv            

 
def Spow(a, b):
    if b==1:
        return a 
    elif b==-1:
        return cf(1,a)
    elif whotype(b,'integer') and b<0:
        return Pow(a, UnevaluatedExpr(b))

    else:    
        return Pow(a,b,evaluate=False)
spow=Spow

def Sroot(bb, *args):
    if len(args)==1 and args[0]==1:
        return bb
     
    if len(args)==0:
        ee=1
        rr=2
    elif len(args)==1:
        ee=1
        rr=args[0]
    else:
        ee=args[0]
        rr=args[1]
    if bb==0:
        return 0
    if ee==0:
        return  1
    if ee==1:
        if rr==1:
            return bb
        else:   
            return Pow(bb,cfrac(1,rr),evaluate=False)
    else:
        return Pow(Spow(bb,ee),cfrac(1,rr),evaluate=False)
sroot = Sroot 
        
def Sinverse(expr):
    """
    Retorna el inverso de n (1/n) sin evaluar.
    Sinverse(2) -> 1/2 (no 0.5)
    Sinverse(x/y) -> y/x
    """
    sexpr='1/('+str(expr)+')'
    kres=parse_expr(sexpr,evaluate=False)
    return kres.args[1]
    
Sinversa=Sinverse
Sinv=Sinverse

 

from sympy import *
from sympy import MatrixBase
from sympy.ntheory import isprime
from sympy.core.traversal import preorder_traversal


# =========================================================
# ALIAS / SYNONYM DICTIONARY
# =========================================================
# =========================================================
# DICCIONARIO UNIFICADO GLOBAL (Fuera de la función)
# =========================================================
WHOTYPE_TAGS = {
    'string': ['string','str','text','texto'],
    'number': ['number', 'numero', 'num', 'constante', 'constant'],
    'nfraction':['nfraction','nfrac'],
    'add': ['add', 'addition', 'suma', 'plus', 'Add', 'Suma'],
    'mul': ['mul', 'multiplication', 'producto', 'Mul', 'Prod'],
    'div': ['div', 'Div', 'division', 'frac', 'fraction', 'cociente'],
    'integer': ['integer', 'int', 'entero'],
    'real': ['real', 'float', 'decimal', 'Real'],
    'negative': ['negative', 'neg', 'negativo'],
    'positive': ['positive', 'pos', 'positivo'],
    'symbols': ['symbols', 'symbol', 'sym', 'variable', 'var', 'Symbol'],
    'pow': ['pow', 'power', 'potencia', 'exponent'],
    'root': ['root', 'raiz', 'sqrt'],
    'pow2pow': ['pow2pow', 'tower', 'nested_pow'],
    'monomie': ['monomie', 'monomial', 'monomio', 'mono'],
    'polinomie': ['polinomie', 'polynomial', 'polinomio', 'poly'],
    'imaginary': ['imaginary', 'i', 'imaginario'],
    'complex': ['complex', 'complejo'],
    'matrix': ['matrix', 'matriz', 'mat'],
    'factor': ['factor', 'factored', 'producto_de_factores'],
    'cero': ['cero', 'zero', 'null', 'nada'],
    'identity': ['identity', 'identidad', 'disfraz'],
    'equation': ['equation', 'ecuacion', 'equal', 'eq'],
    'monster': ['monster', 'monstruo'],
    'cube': ['cube', 'Cube'],
    'square': ['square', 'Square'],
    'prime': ['prime', 'primo'],
    'odd': ['odd', 'impar'],
    'even': ['even', 'par'],
    'integral': ['integral', 'Integral'],
    'log': ['log', 'Log', 'Ln', 'ln'],
    'exp': ['exp', 'Exp'],
    'trigonometric': ['trigonometric', 'trig', 'trigfunc'], # <-- LIMPIO: Sin sin, cos, tan adentro
    'sin': ['sin', 'Sin'],
    'cos': ['cos', 'Cos'],
    'tan': ['tan', 'Tan'],
    'inversa': ['inversa', 'inverse', 'inv'],
    'minipow': ['minipow', 'simplepow', 'purepow', 'potencia_simple'],
    'minimul': ['minimul', 'simplemul'],
    'inversesum': ['inversesum','suminverse', 'inverseadd'],
    'inversemul': ['inversemul','mulinverse',  'inverseprod'],
    'inversepow': ['inversepow','powinverse'],
    'inverseroot': ['inverseroot','rootinverse']
}

def get_whotype_canonical(q):
    if q is None: return None
    for key, aliases in WHOTYPE_TAGS.items():
        if str(q).lower() in aliases: 
            return key
    return str(q).lower()


# =========================================================
# MAIN CLASSIFIER (whotype)
# =========================================================
def whotype(obj, query=None):
    # 1. Obtener el token canónico de manera segura inmediatamente
    q = get_whotype_canonical(query)
    
    # 2. 🛡️ EL ESCUDO SUPREMO CONTRA CADENAS DE TEXTO
    if isinstance(obj, str):
        if q == 'string': 
            return True
        if query is None:
            return 'str'
        return False

    # Si piden ayuda explícita
    if query in ['help', 'ayuda', '?', 'info']:
        print(whotype.__doc__)
        return

    # 3. Normalización inicial para SymPy
    try:
        obj = sympify(obj)
    except:
        pass

    if query is None:
        return type(obj).__name__

    has_is = lambda o, attr: hasattr(o, attr) and getattr(o, attr) is not None

    # =========================================================================
    # JERARQUÍA NIVEL 1: FILTROS ELEMENTALES Y MONSTRUOS
    # =========================================================================
    if q == 'cero': return obj == 0 or obj is S.Zero
    if q == 'equation': return isinstance(obj, Equality)
    if q == 'matrix': return isinstance(obj, (Matrix, MatrixBase))
    if q == 'monster':
        try: return len(list(preorder_traversal(obj))) > 20
        except: return False

    # =========================================================================
    # JERARQUÍA NIVEL 2: DOMINIOS NUMÉRICOS Y PROPIEDADES ARITMÉTICAS
    # =========================================================================
    props = {
        'integer': has_is(obj, 'is_integer') and obj.is_integer,
        'real': has_is(obj, 'is_real') and obj.is_real,
        'negative': has_is(obj, 'is_negative') and obj.is_negative,
        'positive': has_is(obj, 'is_positive') and obj.is_positive,
        'imaginary': has_is(obj, 'is_imaginary') and obj.is_imaginary,
        'complex': has_is(obj, 'is_complex') and obj.is_complex,
    }
    if q in props: return bool(props[q])
    
    if q == 'prime':
        try: return isprime(obj)
        except: return False
    if q == 'odd':
        try: return obj.is_integer and obj % 2 != 0
        except: return False
    if q == 'even':
        try: return obj.is_integer and obj % 2 == 0
        except: return False
    if q == 'number': return has_is(obj, 'is_number') and obj.is_number
    if q == 'symbols': return isinstance(obj, Symbol)

    # =========================================================================
    # JERARQUÍA NIVEL 3: DIVISIONES E INVERSAS ESPECIALIZADAS
    # =========================================================================
    if q == 'div': return denom(obj) != 1
    if q == 'inversa': return numer(obj) == 1 and denom(obj) != 1
    if q == 'nfraction' :
        if denom(obj)!=1 and istype(numer(obj),'number') and numer(obj)!=1 and numer(obj)!=-1:
            return True
        return False    
    # 1. Inversa de una Suma: 1 / (x + y)
    if q == 'inversesum':
        expr = factor(obj)
        return numer(expr) == 1 and isinstance(denom(expr), Add) and not isinstance(denom(obj),Pow)

    # 2. Inversa de un Producto: 1 / (x * y)
    if q == 'inversemul':
        expr = factor(obj)
        # Aseguramos que abajo sea Mul y que no sea una simple potencia (ej: x**2 no es mulinverse, es powinverse)
        return numer(expr) == 1 and isinstance(denom(expr), Mul) and not isinstance(denom(expr), Pow)

    # 3. Inversa de una Potencia: 1 / (x**n) o x**(-n)
    if q == 'inversepow':
        expr = factor(obj)
        # Caso A: Estructura fraccionaria con potencia abajo
        if numer(expr) == 1 and isinstance(denom(expr), Pow):
            return True
        # Caso B: Potencia directa con exponente negativo
         
        return False

    # 4. Inversa de una Raíz: 1 / sqrt(x)
    if q == 'inverseroot':
        expr = factor(obj)
        # Caso A: Fracción con potencia fraccionaria abajo (raíz)
        if numer(expr) == 1 and isinstance(denom(expr), Pow):
            base_inf = denom(expr)
            return hasattr(base_inf.exp, 'is_Rational') and base_inf.exp.is_Rational and abs(base_inf.exp) < 1
        # Caso B: Exponente directo negativo y fraccionario < 1
        if isinstance(expr, Pow):
            en = expr.exp
            return hasattr(en, 'is_Rational') and en.is_Rational and en < 0 and abs(en) < 1
        return False

    # =========================================================================
    # JERARQUÍA NIVEL 4: OPERACIONES COLECTIVAS (SUMAS Y PRODUCTOS)
    # =========================================================================
    if q == 'add': return isinstance(obj, Add)
    
    if q == 'mul':
        if denom(obj) != 1: return False
        return isinstance(obj, Mul)

    if q == 'factor':
        return isinstance(obj, Mul) and all(not isinstance(a, Add) for a in obj.args)

    if q == 'monomie':
        try:
            if not obj.is_polynomial(): return False
            P = Poly(expand(obj))
            return len(P.monoms()) == 1 and len(list(obj.free_symbols)) > 0
        except:
            return False

    if q == 'polinomie':
        if not obj.is_polynomial():
            return False
        
        # 2. Opcional: Si quieres que SOLO sean polinomios con variables
        # (Esto excluye al 1, 5, -10, etc.)
        if not obj.free_symbols:
            return False
            
        return True        

    # =========================================================================
    # JERARQUÍA NIVEL 5: POTENCIAS Y RAÍCES
    # =========================================================================
    if q == 'pow2pow':
        if denom(obj) != 1: return False
        return isinstance(obj, Pow) and isinstance(obj.base, Pow)

    if q == 'minipow':
        if denom(obj) != 1: return False
        if not isinstance(obj, Pow): return False
        try: return obj.base.is_Atom and obj.exp.is_Atom
        except: return False

    if q == 'pow':
        if denom(obj) != 1: return False
        if istype(obj,'root') : return False    
        return isinstance(obj, Pow)

    if q == 'square': return issquare(obj)
    if q == 'cube': return iscube(obj)
        
    if q == 'root':
        if denom(obj) != 1: return False
        return isinstance(obj, Pow) and has_is(obj.exp, 'is_Rational') and obj.exp.is_Rational and abs(obj.exp) < 1

    # =========================================================================
    # JERARQUÍA NIVEL 6: IDENTIDADES Y FUNCIONES TRASCENDENTALES
    # =========================================================================
    if q == 'identity':
        try: return not obj.is_number and simplify(obj).is_number
        except: return False

    if q == 'trigonometric': return obj.has(sin, cos, tan, cot, sec, csc)
    if q == 'integral': return isinstance(obj, Integral)
    
    if q == 'sin': return obj.has(sin)
    if q == 'cos': return obj.has(cos)
    if q == 'tan': return obj.has(tan)
    if q == 'log': return obj.has(log)
    if q == 'exp': return obj.has(exp)

    if q == 'minimul':
        if not isinstance(obj, Mul): return False
        return not any(isinstance(data, Pow) for data in obj.args)
        
    return False


# =========================================================
# INTERNAL UTILITIES
# =========================================================

def canonical_type(q):
    """
    Translate aliases/synonyms into canonical names.

    Examples
    --------
    canonical_type('symbol')
    -> 'symbols'

    canonical_type('sqrt')
    -> 'root'
    """

    q = str(q).lower()

    for key, aliases in TAGS.items():
        if q in aliases:
            return key

    return q


# =========================================================
# PRIMARY TYPE DETECTOR
# =========================================================

PRIMARY_MAP = {

    # Numbers
    'Integer': 'integer',
    'One': 'integer',
    'NegativeOne': 'integer',
    'Zero': 'integer',

    'Float': 'real',
    'Rational': 'real',

    # Algebra
    'Add': 'add',
    'Mul': 'mul',
    'Pow': 'pow',

    # Objects
    'Symbol': 'symbols',
    'Equality': 'equation',
    'Integral': 'integral',

    # Matrix
    'MutableDenseMatrix': 'matrix',
    'ImmutableDenseMatrix': 'matrix',

    # Functions
    'sin': 'sin',
    'cos': 'cos',
    'tan': 'tan',
    'log': 'log',
    'exp': 'exp',
}




def matchtypes(expr):
    """Genera la tupla ordenada de etiquetas que aplican al objeto."""
    categorias = [
        'string', 'cero', 'equation', 'matrix', 'monster',
        'integer', 'real', 'complex', 'imaginary', 'prime', 'even', 'odd',
        'number', 'symbols', 'positive', 'negative','nfraction',
        'div', 'inversa', 'add', 'mul', 'factor', 'monomie', 'polinomie','inversesum','inversemul','inversepow','inverseroot',
        'pow2pow', 'minipow', 'pow', 'square', 'cube', 'root',  # <-- ¡Tus dos joyas aquí adentro!
        'identity', 'trigonometric', 'log', 'exp', 'sin', 'cos', 'tan', 'integral', 'minimul'
    ]
    return tuple(cat for cat in categorias if whotype(expr, cat))


    
def iscube(expr):
    expr = factor(expr)

    if isinstance(expr, Pow):
        ee=getexpo(expr)
        if isinstance(ee , Mul):
            if denom(ee.args[0]/3)==1:
                return True

    # CASO 1: Potencia directa
    if isinstance(expr, Pow):

        expo = expand(expr.exp)

        coef, rest = expo.as_coeff_Mul()

        if coef.is_number and coef % 3 == 0:
            return True

    # CASO 2: Inversa con cubo abajo
    if numer(expr) == 1 and isinstance(denom(expr), Pow):

        expo = expand(denom(expr).exp)

        coef, rest = expo.as_coeff_Mul()

        if coef.is_number and coef % 3 == 0:
            return True

    return False 

def issquare(expr):

    expr = factor(expr)

    # CASO 1: Potencia directa
    if isinstance(expr, Pow):

        expo = expand(expr.exp)

        coef, rest = expo.as_coeff_Mul()

        if coef.is_number and coef % 2 == 0:
            return True

    # CASO 2: Inversa con cuadrado abajo
    if numer(expr) == 1 and isinstance(denom(expr), Pow):

        expo = expand(denom(expr).exp)

        coef, rest = expo.as_coeff_Mul()

        if coef.is_number and coef % 2 == 0:
            return True

    return False
# =========================================================
# SHORTCUTS
# =========================================================

getype = whotype
gettype = whotype


# =========================================================
# ALL TYPES MATCH
# =========================================================

def istype(expr, *args):

    """
    Return True if ALL requested types match.

    Examples
    --------
    istype(x**2,'pow','square')
    -> True
    """

    return all(
        whotype(expr, q)
        for q in args
    )


# =========================================================
# ANY TYPES MATCH
# =========================================================
def anytype(expr, *args):

    """
    Return True if ANY requested type matches.
    """

    return any(
        whotype(expr, q)
        for q in args
    )


# aliases
isanytype = anytype


# =========================================================
# NO TYPES MATCH
# =========================================================

def isnottype(expr,*args):

    """
    Return True if expression does NOT match
    any requested type.
    """

    return not anytype(expr,*args)


# aliases
notype   = isnottype
nottype  = isnottype
isnotype = isnottype
# =========================================================
# MATCH ALL DETECTED TYPES
# =========================================================


types = matchtypes

def isanytype(expr,*args):
    '''
    return true if any arguments in *args are inside matchtype(expr)
    '''
    done = False
    L=matchtypes(expr)
    for data in args:
        if data in L:
            done = True
    return done
    

def cfrac(*args):
    """
    Convierte a fracción simbólica o Rational exacto.
    Versión blindada para trabajar con Sdiv.
    """
    evaluate = True
    vec = []

    # 1. Filtro de evaluación (tu lógica original)
    for data in args:
        if str(data).lower() in ['noevaluate', 'noeval', 'false']:
            evaluate = False
        else:
            vec.append(data)

    n = len(vec)

    # 2. Caso de 1 argumento (ej. cfrac("x/2"))
    if n == 1:
        expr = vec[0]
        if isinstance(expr, str):
            # Usamos sympify para que entienda "x**2/y" sin romperse con split
            s_expr = sympify(expr)
            if not evaluate:
                # Extraemos numerador y denominador del sympify para pasarlo a Sdiv
                return Sdiv(numer(s_expr), denom(s_expr))
            return s_expr
        return sympify(expr)

    # 3. Caso de 2 argumentos (ej. cfrac(x, 2))
    elif n == 2:
        a, b = vec
        if not evaluate:
            # Aquí es donde ocurre la magia anti-sympy
            return Sdiv(a, b)
        
        # Si queremos evaluar, sympify se encarga de la división estándar
        return sympify(a) / sympify(b)
    
    else:
        raise ValueError("cfrac acepta 1 o 2 argumentos (más opcional 'noeval')")
cf = cfrac    
 
def getexpo2(expr):
    if isinstance(expr, Pow):
        base, exp = expr.args
        # Si la base es OTRA potencia, el exponente que buscas está adentro
        if isinstance(base, Pow):
            return getexpo2(base) 
        return exp
    return 1

def get_expo(expr):
    e1=getexpo2(expr)
    e2=getmexpo(expr)
    if e1==e2:
        return numer(e1)
    else:
        return e1
def getmexpo(expr):
    """Exponente total propagado a la base real."""

    if not isinstance(expr, Pow):
        return 1

    base, exp = expr.args
    return exp * getmexpo(base)

def get_base(expr):
    """Extrae la base real, ignorando raíces y exponentes."""
    if isinstance(expr, Pow):
        return get_base(expr.base)
    return expr
def getroot(expr):

    """Extrae el índice de raíz si existe."""

    if not isinstance(expr, Pow):
        return 1

    base, exp = expr.args

    try:
        return denom(exp)
    except:
        return 1 
def sfactor(expr, kdiv, *args):
    # PRE-PROCESAMIENTO
    if 'factor' in args: expr = factor(expr)
    if 'expand' in args: expr = expand(expr)
    if 'simplify' in args: expr = simplify(expr)
    
    expr = sympify(expr)
    kdiv = sympify(kdiv)

    # 1. CASO SUMA (El corazón del algoritmo)
    if istype(expr, 'add'):
        con_kdiv = []
        sin_kdiv = []
        
        for term in expr.args:
            # PRUEBA QUIRÚRGICA: 
            # Intentamos extraer el factor usando la lógica interna de SymPy (extract_multiplicatively)
            # Esto solo devuelve algo si kdiv está contenido sin dejar denominadores nuevos.
            quo = term.extract_multiplicatively(kdiv)
            
            if quo is not None:
                con_kdiv.append(quo)
            else:
                sin_kdiv.append(term)
        
        if con_kdiv:
            # Solo factorizamos lo que realmente tenía el factor
            parte_factorizada = Smul(kdiv, Sadd(*con_kdiv))
            if sin_kdiv:
                return Sadd(parte_factorizada, *sin_kdiv)
            return parte_factorizada
        return expr

    # 2. CASO POTENCIA
    if istype(expr, 'pow'):
        bb = sfactor(getbase(expr), kdiv, *args)
        ee = getexpo(expr)
        return Spow(bb, ee)

    # 3. CASO DIVISIÓN
    if istype(expr, 'div'):
        return Sdiv(sfactor(numer(expr), kdiv, *args), 
                    sfactor(denom(expr), kdiv, *args))

    # 4. CASO MULTIPLICACIÓN
    if istype(expr, 'mul'):
        return Smul(*[sfactor(a, kdiv, *args) for a in expr.args])

    return expr
superfactor = sfactor

 
def pow2all(expr, mode='both'):
    expr = sympify(expr)
        
    if isanytype(expr, 'integer', 'symbols', 'minimul'):
        return expr
    
    if istype(expr, 'add'):
        return Sadd(*[pow2all(data, mode) for data in expr.args])

    if istype(expr, 'div'):
        return Sdiv(pow2all(numer(expr), mode), pow2all(denom(expr), mode))        
    
    if istype(expr, 'mul'):
        return Smul(*[pow2all(data, mode) for data in expr.args])

    if istype(expr, 'root'):
        return Sroot(pow2all(insideroot(expr), mode), getroot(expr))
    
    # --- Lógica Selectiva ---
    
    # Caso DivPow: (a/b)**n -> a**n / b**n
    if istype(expr, 'divpow') and mode in ['div', 'both']:
        bb, ee = getbase(expr), getexpo(expr)
        return Sdiv(pow2all(Spow(numer(bb), ee), mode), 
                    pow2all(Spow(denom(bb), ee), mode))

    # Caso MulPow: (a*b)**n -> a**n * b**n
    if istype(expr, 'mulpow') and mode in ['mul', 'both']:
        bb, ee = getbase(expr), getexpo(expr)
        return Smul(*[pow2all(Spow(f, ee), mode) for f in bb.args])

    return expr

    
# Solo expande potencias de divisiones
def powdiv2divpow(expr):
    return pow2all(expr, mode='div')

# Solo expande potencias de multiplicaciones
def powmul2mulpow(expr):
    return pow2all(expr, mode='mul')

expandpowdiv = powdiv2divpow
expandpowmul = powmul2mulpow


def rsimplify(expr):
    if getroot(expr)==getexpo(expr) and istype(expr,'root'):
        return getbase(expr)
    if isinstance(expr,Symbol):
        return expr
    elif whotype(expr,'number'):
        return expr
    if isinstance(expr,Add):
        return sum([rsimplify(data) for data in expr.args])
    elif whotype(expr,'div'):
        return rsimplify(numer(expr))/rsimplify(denom(expr))
    elif isinstance(expr,Mul):
        return prod([rsimplify(data) for data in expr.args])
        
    elif istype(expr, 'root'):
        content = insideroot(expr)
        rr = getroot(expr) # Índice de la raíz
        
        # --- Lógica de Extracción y Simplificación de Índice ---
        if istype(content, 'minipow'):
            bb_mini = getbase(content)
            ee_mini = getexpo(content)
            
            # 1. Simplificación de Índice (ej: root(x**2, 4) -> root(x, 2))
            # Buscamos el máximo común divisor entre el exponente y el índice
            comun = gcd(ee_mini, rr)
            if comun > 1:
                ee_mini = ee_mini // comun
                rr = rr // comun
            
            # 2. Lógica de Extracción (ee_out y ee_in) con los nuevos valores
            ee_out = ee_mini // rr
            ee_in  = ee_mini % rr
            
            base_clean = rsimplify(bb_mini)
            
            parte_fuera  = Spow(base_clean, ee_out)
            parte_dentro = Sroot(base_clean, ee_in, rr)
            
            # Ensamblaje Estético
            if ee_in == 0:
                return parte_fuera
            if ee_out == 0:
                return parte_dentro
            
            # Retorno ordenado: x*sqrt(x)
            return parse_expr(f"{parte_fuera}*{parte_dentro}", evaluate=False)
        
        # --- Lógica para Productos (Mul) ---
        elif istype(content, 'mul'):
            factores_raiz = [rsimplify(Sroot(arg, rr)) for arg in content.args]
            return rsimplify(Smul(*factores_raiz))
            
        return Sroot(rsimplify(content), rr)      
    return expr
    
def tree_walker(expr, logic_func):
    """Navegador universal de árboles SymPy blindado."""
    # LA CURA: Convertimos a SymPy inmediatamente para que tenga .args
    if not hasattr(expr, 'args'):
        expr = sympify(expr)
        
    # Si no tiene hijos (es un átomo como un Símbolo o Integer solo)
    if not expr.args:
        return logic_func(expr)

    # Procesamos los hijos primero
    new_args = [tree_walker(a, logic_func) for a in expr.args]

    # Reconstruimos la expresión
    return logic_func(expr.func(*new_args, evaluate=False))

def prime_logic(e):
    """Regla para números primos."""
    if isinstance(e, (int, Integer)) and e > 1:
        fac = factorint(e)
        return Mul(*[Pow(p, exp, evaluate=False) for p, exp in fac.items()], evaluate=False)
    return e



def super_logic(expr, kdiv):
    """
    Intenta dividir el término por kdiv. 
    Si la división es exacta (p2 == 1), devuelve el cociente para ser multiplicado luego.
    """
    # Intentamos la división
    kres = expr / kdiv
    p1, p2 = fraction(kres)
    
    if p2 == 1:
        # División exacta: devolvemos el cociente (p1) marcado para reconstrucción
        return ('match', p1)
    else:
        # No es divisible: se queda como está
        return ('no_match', expr)    

def joinbase(expr):
    """
    Recorre toda la expresión y agrupa potencias con la misma base.
    Ejemplo: x**2 * x**3 -> x**5
    """
    if istype(expr,'div') and istype(numer(expr),'pow') and istype(denom(expr),'pow'):
        if getbase(numer(expr))==getbase(denom(expr)):
            return Spow(getbase(numer(expr)),getexpo(numer(expr))-getexpo(denom(expr)))
             
    if not expr.args: return expr

    # Navegamos primero por los hijos
    new_args = [joinbase(a) for a in expr.args]
    
    # Si es una multiplicación, aplicamos powsimp forzado
    if isinstance(expr, Mul):
        # powsimp agrupa bases, combine='all' es para que no tenga piedad
        res = powsimp(Mul(*new_args, evaluate=False), combine='all', force=True)
        return res

    return expr.func(*new_args, evaluate=False)

def disjoinbase(expr,deep=False):
        
    if isanytype(expr, 'integer', 'symbols', 'minimul'):
        return expr
    
    if istype(expr, 'add'):
        return Sadd(*[disjoinbase(data, deep=deep) for data in expr.args])

    if istype(expr, 'div'):
        return Sdiv(disjoinbase(numer(expr),  deep=deep), disjoinbase(denom(expr), deep=deep))        
    
    if istype(expr, 'mul'):
        return Smul(*[disjoinbase(data, deep=deep) for data in expr.args])

    
    if istype(expr, 'root'):
        return Sroot(disjoinbase(insideroot(expr), deep=deep), getroot(expr))
    if istype(expr,'pow') and not istype(expr,'exposum'):
        bb,ee=getbase(expr),getexpo(expr)
        if deep:
            return Spow(disjoinbase(bb,deep=deep),disjoinbase(ee,deep=deep))
        else:
            return expr
            
    if istype(expr,'exposum'):
        bb,ee=getbase(expr),getexpo(expr)
        if deep:
            return Smul(*[Spow(bb,disjoinbase(data)) for data in ee.args])
        else:
            return Smul(*[Spow(bb,data) for data in ee.args])
            
    return expr      


def joinexpo(expr):
    """
    Une potencias con la misma base sumando sus exponentes.
    Ejemplo: x**a * x**b -> x**(a+b)
    """
    expr = sympify(expr)
    if not expr.args: return expr

    # 1. Navegamos por los hijos para que la limpieza sea profunda
    new_args = [joinexpo(a) for a in expr.args]
    
    # 2. Si es una multiplicación, aplicamos powsimp
    # Pero aquí el truco es 'combine=base' para que SOLO una exponentes
    if isinstance(expr, Mul):
        # combine='base' obliga a SymPy a buscar bases iguales y sumar exponentes
        res = powsimp(Mul(*new_args, evaluate=False), combine='base', force=True)
        return res

    return expr.func(*new_args, evaluate=False) 

def disjoinexpo(expr):
    """
    Rompe sumas en los exponentes: x**(a+b) -> x**a * x**b
    """
    expr = sympify(expr)
    if not expr.args: return expr

    # 1. Recursión para limpiar niveles internos
    new_args = [disjoinexpo(a) for a in expr.args]
    
    # 2. Aplicamos la expansión de potencias
    # mul=True le dice que rompa el exponente si es una suma
    res = expand_power_exp(expr.func(*new_args, evaluate=False))
    
    return res  

def expo2factorprime(obj):
    bb=obj.base
    ee=obj.exp
    ee=primefactor(ee)
    return  Spow(bb,ee)

expo2primefactor = expo2factorprime    
def signo(expr):
    if str(expr)[0]=='-':
        return -1
    elif expr==0:
        return 0
    else:
        return 1
        


def eqsimplify(p1, p2):
    # Guardamos el estado anterior para comparar
    p1_old, p2_old = None, None
    
    # El bucle se repite mientras haya cambios
    while (p1, p2) != (p1_old, p2_old):
        p1_old, p2_old = p1, p2
        p1, p2 = _reduscore(p1, p2)
    
    return p1, p2
def _reduscore(p1, p2):
    # Tipos de funciones que queremos "pelar" estructuralmente
    tiposf = (sin, cos, tan, log, exp, cot, sec)
    
    # Caso base: si son idénticos, la reducción es total
    if p1 == p2: 
        return 1, 1
    p1=dsimplify(p1)
    p2=dsimplify(p2)
    # 1. Pelar funciones iguales: f(A) = f(B) -> A, B
    if type(p1) == type(p2) and isinstance(p1, tiposf):
        return p1.args[0], p2.args[0]

    # 2. Pelar potencias: A**z = B**z o z**A = z**B
    if isinstance(p1, Pow) and isinstance(p2, Pow):
        if p1.exp == p2.exp: return p1.base, p2.base
        if p1.base == p2.base: return p1.exp, p2.exp

    # 3. Pelar fracciones: A/C = B/C o C/A = C/B
    num1, den1 = fraction(p1)
    num2, den2 = fraction(p2)
    if den1 == den2 and den1 != 1: return num1, num2
    if num1 == num2 and num1 != 1: return den1, den2

    # 4. Pelar sumas: (A + B + C) = (A + D) -> B + C, D
    if isinstance(p1, Add) and isinstance(p2, Add):
        common = set(p1.args) & set(p2.args)
        if common:
            res1 = [a for a in p1.args if a not in common]
            res2 = [a for a in p2.args if a not in common]
            # Seguro de identidad: si se vacía la suma, queda 0
            return Add(*(res1 if res1 else [0])), Add(*(res2 if res2 else [0]))

    # 5. Pelar multiplicaciones: (A * B * C) = (A * D) -> B * C, D
    if isinstance(p1, Mul) and isinstance(p2, Mul):
        common = set(p1.args) & set(p2.args)
        if common:
            res1 = [a for a in p1.args if a not in common]
            res2 = [a for a in p2.args if a not in common]
            # Seguro de identidad: si se vacía el producto, queda 1
            return Mul(*(res1 if res1 else [1])), Mul(*(res2 if res2 else [1]))
    
    # 6. El toque maestro: Cancelación de signos negativos
    # Usa tu función signo() recursiva para limpiar la ecuación
    if signo(p1) == -1 and signo(p2) == -1:
        return -1 * p1, -1 * p2

    # Si no entra en ninguna regla, devuelve lo que recibió para cerrar el bucle
    return p1, p2

def dsimplify(expr):
    from sympy import numer, denom, Mul, prod, gcd, Integer
    
    n = numer(expr)
    d = denom(expr)
    
    if d == 1:
        return n

    # 1. SEPARACIÓN: Aislamos la parte numérica de la simbólica
    # as_coeff_Mul() devuelve (coeficiente_numérico, resto_de_la_expresión)
    n_coeff, n_simb = n.as_coeff_Mul()
    d_coeff, d_simb = d.as_coeff_Mul()

    # 2. SIMPLIFICACIÓN NUMÉRICA: Usamos el Máximo Común Divisor (gcd)
    comun = gcd(n_coeff, d_coeff)
    new_n_coeff = cf(n_coeff , comun)
    new_d_coeff = cf(d_coeff , comun)

    # 3. SIMPLIFICACIÓN SIMBÓLICA (Tu lógica de listas mejorada)
    list_n = list(n_simb.args) if isinstance(n_simb, Mul) else ([n_simb] if n_simb != 1 else [])
    list_d = list(d_simb.args) if isinstance(d_simb, Mul) else ([d_simb] if d_simb != 1 else [])
    
    final_n = list_n[:]
    final_d = list_d[:]
    
    for factor in list_n:
        if factor in final_d:
            final_n.remove(factor)
            final_d.remove(factor)

    # 4. RECONSTRUCCIÓN FINAL
    # Combinamos el nuevo coeficiente con los símbolos restantes
    res_n = new_n_coeff * prod(final_n) if final_n else new_n_coeff
    res_d = new_d_coeff * prod(final_d) if final_d else new_d_coeff

    # Salida según tus funciones personalizadas
    if res_d == 1:
        return res_n
    if res_n == 1:
        return Sinv(res_d)
    
    return Sdiv(res_n, res_d)
    
def insideroot(expr):

    if istype(expr,'pow','root'):
    
        bb,rr2=expr.args
    
        return bb
    
    else:
    
        return expr 

def lexpand(expr):
    return expand_log(expr,force=True)

def lfactor(expr):
    return logcombine(expr)

def real_subs(expr, **kwargs):
    """
    QQ= symbols function
    ** kwargs c7=6,g4=z..etc..
    RETURN real substitucion when variable have underscore name like 'c_7' 'g_4'
    """
    if isnotype(expr,'number'):
        if len(kwargs) > 0:
            key, value = unpack(kwargs)
            kres = expr
            for i, j in zip(key, value):
                jj = j
                try:
                    jj = j.ksym
                except:
                    pass    
                kres = kres.subs(i, j)
                if len(i) > 1:
                    newi = i[0] + "_" + i[1::]
                    try:
                        kres = kres.subs(newi, j)
                    except:
                        pass

            return kres
        else:
            return expr
    else:
        return expr    

def unpack(mm):
    return kunpakDic(mm=mm)
    
def kunpakDic(mm):
     
    kkey=list(mm.keys())
    kvalu=list(mm.values())

    return( kkey,kvalu) 

def numerfunc(expr, func, *args, **kwargs):
    """
    Applies any function (SymPy native or custom) ONLY to the NUMERATOR 
    of a fractional expression, leaving the denominator untouched.
    """
    # Si es un objeto MyEq, extraemos su ksym interno
    is_custom_obj = hasattr(expr, 'ksym')
    pure_expr = expr.ksym if is_custom_obj else expr
    
    # fraction viene directo de sympy (que ya lo tienes importado arriba con *)
    n, d = fraction(pure_expr)
    
    # Aplicamos la función al numerador
    new_n = func(n, *args, **kwargs)
    
    # Reconstruimos usando tu Sdiv de lib_basicmath
    res = Sdiv(new_n, d)
    
    # Devolvemos el mismo tipo de objeto que entró
    return expr.__class__(res) if is_custom_obj else res


def denomfunc(expr, func, *args, **kwargs):
    """
    Applies any function (SymPy native or custom) ONLY to the DENOMINATOR 
    of a fractional expression, leaving the numerator untouched.
    """
    is_custom_obj = hasattr(expr, 'ksym')
    pure_expr = expr.ksym if is_custom_obj else expr
    
    n, d = fraction(pure_expr)
    
    # Aplicamos la función al denominador
    new_d = func(d, *args, **kwargs)
    
    # Reconstruimos usando tu Sdiv de lib_basicmath
    res = Sdiv(n, new_d)
    
    return expr.__class__(res) if is_custom_obj else res
    
def streplace(expr,p1,p2):
    sexpr=str(expr)
    sp1=str(p1)
    sp2=str(p2)
    sexpr=sexpr.replace(sp1,'('+sp2+')')
    return parse_expr(sexpr)

def mulmixto(*args):
    p1=[numer(data) for data in args]
    p2=[denom(data) for data in args]
    P1=prod(p1)
    P2=prod(p2)
    if P2==1:
        return P1
    elif P1==1:
        return Sinversa(P2)
    else:    
        return dsimplify(Sdiv(P1,P2))

def tree_apply(expr, func_to_apply, target_type='pow'):
    """
    Navegador universal para tus librerías.
    """
    expr = sympify(expr)
    
    # --- BLOQUES DE ESTRUCTURA ESPECIAL ---
    
    if istype(expr, 'root') and target_type != 'root':
        bb = tree_apply(getbase(expr), func_to_apply, target_type)
        ee = tree_apply(getexpo(expr), func_to_apply, target_type)
        rr = tree_apply(getroot(expr), func_to_apply, target_type)
        return Sroot(Spow(bb, ee), rr)
 
    if istype(expr, 'div') and target_type != 'div':
        p1 = tree_apply(numer(expr), func_to_apply, target_type)
        p2 = tree_apply(denom(expr), func_to_apply, target_type)
        return Sdiv(p1, p2)
        
    if istype(expr, 'mul') and target_type != 'mul':
        args_procesados = [tree_apply(data, func_to_apply, target_type) for data in expr.args]
        # Limpieza inmediata de unos al reconstruir la multiplicación
        return Smul(*[a for a in args_procesados if a != 1])
    
    # --- APLICACIÓN DE REGLA ---
    if istype(expr, target_type):
        return func_to_apply(expr)

    # --- RECURSIÓN GENERAL ---
    if hasattr(expr, 'args') and expr.args:
        new_args = [tree_apply(a, func_to_apply, target_type) for a in expr.args]
        
        # Filtro de seguridad para operadores genéricos
        if istype(expr, 'mul'):
            new_args = [a for a in new_args if a != 1]
            if len(new_args) == 0: return S(1)
            if len(new_args) == 1: return new_args[0]
            
        return expr.func(*new_args, evaluate=False)

    return expr 

def cleanmul(expr):
    # Si la expresión es un producto (Mul)
    if isinstance(expr, Mul):
        # Filtramos todos los argumentos que no sean el número 1
        args_sin_uno = [arg for arg in expr.args if arg != 1]
        
        # Si después de quitar el 1 solo queda un elemento, lo devolvemos solo
        if len(args_sin_uno) == 1:
            return args_sin_uno[0]
        # Si queda más de uno, reconstruimos el producto
        return Mul(*args_sin_uno)
    if istype(expr,'pow'):
        return Spow(cleanmul(getbase(expr)),cleanmul(getexpo(expr)))    
    return expr        


def findall(expr, sub):
    # Convertimos la expresión a string para buscar en ella
    texto = str(expr)
    posiciones = []
    inicio = 0
    
    # Buscamos de forma recurrente
    while True:
        idx = texto.find(sub, inicio)
        if idx == -1:  # Si ya no hay más coincidencias
            break
        posiciones.append(idx)
        # Avanzamos la posición para seguir buscando el siguiente
        inicio = idx + 1
        
    return posiciones
def getbalance(expr):
    sexpr=str(expr) 
    B=0
    for data in sexpr:
        if data=='(':
            B+=1
        elif data==')':
            B+=-1
        else:
            pass
    return B 

def powsimetrico(expr):
    sexpr=str(expr)
    P=findall(expr,'**')
    for p1 in P:
        if getbalance(sexpr[0:p1])==0  and getbalance(sexpr[p1+2::])==0:
            bb,ee = parse_expr(sexpr[0:p1],evaluate=False) ,  killmulone(parse_expr(sexpr[p1+2::],evaluate=False) )
                         
            return bb,ee    
    return get_base(expr),get_expo(expr) 
    
def killpar(sexpr):
    sexpr=str(sexpr)
    if sexpr[0]=='(' and sexpr[-1]==')':
        return parse_expr(sexpr[1:-1],evaluate=False)
    else:
        return parse_expr(sexpr ,evaluate=False)

def getbase(expr):
    bb,ee=powsimetrico(expr)
    return bb
    
    
def getexpo(expr):
    bb,ee=powsimetrico(expr)
    if '**('+str(ee)+')' in str(expr):
       kres= cleanmul(ee)
    else:
        if istype(get_expo(expr),'root'):
           ee=simplify(ee)
        rr=getroot(expr)
        if denom(ee)==rr:
           kres= numer(ee)
        else:    
            kres=cleanmul(ee)
    if istype(kres,'decimal'):
        return nsimplify(kres)
    return kres        
     
def killmulone(expr):
    sexpr=str(expr)
    if istype(expr,'mul'):
        if sexpr[0:2]=='1*' :
            return parse_expr(sexpr[2::],evaluate=False)
        elif sexpr[0:3]=='-1*' :    
            return parse_expr('-'+sexpr[3::],evaluate=False)
        else:
            return expr
    return expr     