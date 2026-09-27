import sympy as sp, math

class HybridSolverV4_3:
    def solve(self, text):
        if not text or '=' not in text:
            return {"status":"ERROR","solution":None}
        lines=[l.strip() for l in text.strip().split('\n') if '=' in l]
        eqs=[]; syms=set(); const_false=None
        for line in lines:
            clean=line.replace('²','**2').replace('^','**')
            lhs_s,rhs_s=clean.split('=',1)
            lhs=sp.sympify(lhs_s); rhs=sp.sympify(rhs_s)
            eq=sp.Eq(lhs,rhs)
            if len(eq.free_symbols)==0:
                if not bool(eq): const_false=eq
                continue
            eqs.append(eq); syms.update(eq.free_symbols)
        if const_false is not None:
            return {"status":"INCONSISTENT","solution":None}
        if not eqs:
            return {"status":"ERROR","solution":None}
        symbols=sorted(list(syms), key=lambda s: s.name)
        A,b=sp.linear_eq_to_matrix(eqs, symbols)
        m,n=A.shape; n_vars=len(symbols)
        rank_A=A.rank(); rank_aug=A.row_join(b).rank()
        if rank_A==rank_aug==n_vars:
            sol=A.LUsolve(b) if m==n_vars else A.QRsolve(b)
            return {"status":"UNIQUE","solution":dict(zip(symbols,sol))}
        elif rank_A==rank_aug < n_vars:
            sol_tuple=list(sp.linsolve(eqs,symbols))[0]
            return {"status":"INFINITE","solution":dict(zip(symbols,sol_tuple))}
        elif rank_A!=rank_aug:
            if m>n_vars:
                sol_ls=A.pinv()*b if rank_A<n_vars else A.QRsolve(b)
                return {"status":"LEAST_SQUARES","solution":dict(zip(symbols,sol_ls))}
            return {"status":"INCONSISTENT"}
