"""Portable atomic insert-if-absent for immutable content-addressed records."""


def once(session, model, values):
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert

    insert = sqlite_insert if session.bind.dialect.name == "sqlite" else pg_insert
    session.execute(insert(model).values(**values).on_conflict_do_nothing())


def many(session, model, rows, *, returning=None):
    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from sqlalchemy.dialects.sqlite import insert as sqlite_insert

    insert = sqlite_insert if session.bind.dialect.name == "sqlite" else pg_insert
    statement = insert(model.__table__).on_conflict_do_nothing()
    if returning is not None:
        statement = statement.returning(returning)
    inserted = []
    for offset in range(0, len(rows), 500):
        result = session.execute(statement, rows[offset : offset + 500])
        if returning is not None:
            inserted.extend(result.scalars())
    return inserted
