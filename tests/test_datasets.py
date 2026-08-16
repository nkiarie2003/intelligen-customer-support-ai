from app.ai.datasets import map_cfpb_product


def test_cfpb_product_mapping():
    assert map_cfpb_product("Debt collection") == "debt_collection"
    assert map_cfpb_product("Mortgage") == "mortgage"
    assert map_cfpb_product("Credit card or prepaid card") == "credit_card"
    assert map_cfpb_product("Checking or savings account") == "bank_account"
    assert map_cfpb_product("Student loan") == "loan"
    assert map_cfpb_product("Money transfer, virtual currency, or money service") == "payments_transfers"
    assert map_cfpb_product("Credit reporting, credit repair services, or other personal consumer reports") == "credit_reporting"
