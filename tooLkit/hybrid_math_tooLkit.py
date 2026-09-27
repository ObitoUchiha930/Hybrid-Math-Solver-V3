"""
Hybrid Math Toolkit - Math Tool for AI Agents
V5.0 - MCP Compatible
"""
import sympy as sp, math, json

class HybridMathToolkit:
    def __init__(self):
        pass

    def parse(self, text):
        if not text or '=' not in text:
            return None, None, None, None, {"status":"ERROR","verified":False}
        lines=[l.strip() for l in text.strip().split('\n') if '=' in l]
        eqs=[]; syms=set(); const_false=None
        for line in lines:
            clean=line.replace('²','**2').replace('^','**')
            if '=' not in clean: continue
            lhs_s,rhs_s=clean.split('=',1)
            try:
                lhs=sp.sympify(lhs_s); rhs=sp.sympify(rhs_s)
            except Exception as e:
                return None,None,None,None,{"status":"ERROR","message":str(e),"verified":False}
            eq=sp.Eq(lhs,rhs)
            if len(eq.free_symbols)==0:
                if not bool(eq): const_false=eq
                continue
            eqs.append(eq); syms.update(eq.free_symbols)
        if const_false is not None:
            return None,None,None,None,{"status":"INCONSISTENT","verified":True,"message":f"مستحيل {const_false}"}
        if not eqs:
            return None,None,None,None,{"status":"ERROR","verified":False}
        symbols=sorted(list(syms), key=lambda s: s.name)
        try:
            A,b=sp.linear_eq_to_matrix(eqs, symbols)
        except Exception as e:
            return None,None,None,None,{"status":"NONLINEAR","verified":False}
        return A,b,symbols,eqs,None

    def verified_solve(self, problem: str, strict: bool = False):
        parsed = self.parse(problem)
        if parsed[-1] is not None:
            return parsed[-1]
        A,b,symbols,eqs,_ = parsed
        m,n = A.shape
        n_vars = len(symbols)
        rank_A = A.rank()
        rank_aug = A.row_join(b).rank()

        if rank_A == rank_aug == n_vars:
            sol = A.LUsolve(b) if m==n_vars else A.QRsolve(b)
            residual = A*sol - b
            is_verified = all(sp.simplify(v)==0 for v in residual)
            return {
                "status": "UNIQUE",
                "verified": is_verified,
                "solution": {str(k): str(v) for k,v in zip(symbols, sol)},
                "residual": str(residual.T),
                "method": "LUsolve"
            }
        elif rank_A == rank_aug < n_vars:
            sol_tuple = list(sp.linsolve(eqs,symbols))[0]
            return {
                "status": "INFINITE",
                "verified": True,
                "solution": {str(k): str(v) for k,v in zip(symbols, sol_tuple)}
            }
        elif rank_A!= rank_aug:
            rref,_ = A.row_join(b).rref()
            if m > n_vars:
                sol_ls = A.pinv()*b if rank_A < n_vars else A.QRsolve(b)
                residual = A*sol_ls - b
                return {
                    "status": "LEAST_SQUARES",
                    "verified": False,
                    "solution": {str(k): str(v) for k,v in zip(symbols, sol_ls)},
                    "residual": str(residual.T)
                }
            return {"status": "INCONSISTENT","verified": True,"solution": None}

toolkit = HybridMathToolkit()
def verified_solve(problem: str, strict: bool = False):
    return toolkit.verified_solve(problem, strict=strict)
