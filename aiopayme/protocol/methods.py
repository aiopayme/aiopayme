from aiopayme.types import (
    CreateTransactionCtx,
    PerformTransactionCtx,
    CancelTransactionCtx,
    CheckTransactionCtx,
    CheckPerformTransactionCtx,
    GetStatementCtx,
    SetFiscalDataCtx,
)

METHODS = {
    "CheckPerformTransaction": ("check_perform_transaction", CheckPerformTransactionCtx),
    "CreateTransaction":       ("create_transaction",        CreateTransactionCtx),
    "PerformTransaction":      ("perform_transaction",       PerformTransactionCtx),
    "CancelTransaction":       ("cancel_transaction",        CancelTransactionCtx),
    "CheckTransaction":        ("check_transaction",         CheckTransactionCtx),
    "GetStatement":            ("get_statement",             GetStatementCtx),
    "SetFiscalData":           ("set_fiscal_data",           SetFiscalDataCtx),
}