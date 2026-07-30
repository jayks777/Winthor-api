from db.models import Produtos, Categorias, Departamentos

def def_cat(session, codprod):
    result = (
        session.query(Categorias.DESCRICAO)
        .join(Produtos, Produtos.CODSEC == Categorias.CODSEC)
        .filter(Produtos.CODPROD == codprod)
        .scalar()
    )
    
    return result

def def_departamento(session, codprod):
    result = (
        session.query(Departamentos.DESCRICAO)
        .join(Produtos, Produtos.CODEPTO == Departamentos.CODEPTO)
        .filter(Produtos.CODPROD == codprod)
        .scalar()
    )
    
    return result