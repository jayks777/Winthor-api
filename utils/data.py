from db.models import Produtos, Categorias

def def_cat(session, codprod):
    result = (
        session.query(Categorias.DESCRICAO)
        .join(Produtos, Produtos.CODSEC == Categorias.CODSEC)
        .filter(Produtos.CODPROD == codprod)
        .scalar()
    )
    
    return result