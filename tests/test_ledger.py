import pytest

from broker.ledger import _make_buy_receipt, _make_sell_receipt


@pytest.mark.unit
class TestBuyReceipt:
    def test_balanced(self) -> None:
        r = _make_buy_receipt(
            "AAPL", quantity=10.0, price=5.0, fee_rate=0.01, tax_rate=0.005
        )
        assert r.balanced()

    def test_gross(self) -> None:
        r = _make_buy_receipt(
            "AAPL", quantity=10.0, price=5.0, fee_rate=0.0, tax_rate=0.0
        )
        assert r.gross == 50.0

    def test_fees(self) -> None:
        r = _make_buy_receipt(
            "AAPL", quantity=10.0, price=5.0, fee_rate=0.02, tax_rate=0.0
        )
        assert abs(r.fees - 1.0) < 1e-9

    def test_taxes(self) -> None:
        r = _make_buy_receipt(
            "AAPL", quantity=10.0, price=5.0, fee_rate=0.0, tax_rate=0.005
        )
        assert abs(r.taxes - 0.25) < 1e-9

    def test_net_is_gross_plus_costs(self) -> None:
        r = _make_buy_receipt(
            "AAPL", quantity=10.0, price=5.0, fee_rate=0.02, tax_rate=0.005
        )
        assert abs(r.net - (r.gross + r.fees + r.taxes)) < 1e-9

    def test_action(self) -> None:
        r = _make_buy_receipt(
            "AAPL", quantity=1.0, price=1.0, fee_rate=0.0, tax_rate=0.0
        )
        assert r.action == "BUY"

    def test_symbol(self) -> None:
        r = _make_buy_receipt(
            "TSLA", quantity=1.0, price=1.0, fee_rate=0.0, tax_rate=0.0
        )
        assert r.symbol == "TSLA"

    def test_securities_account_named_correctly(self) -> None:
        r = _make_buy_receipt(
            "MSFT", quantity=1.0, price=1.0, fee_rate=0.0, tax_rate=0.0
        )
        accounts = [e.account for e in r.entries]
        assert "securities:MSFT" in accounts


@pytest.mark.unit
class TestSellReceipt:
    def test_balanced(self) -> None:
        r = _make_sell_receipt(
            "AAPL", quantity=10.0, price=6.0, fee_rate=0.01, tax_rate=0.0
        )
        assert r.balanced()

    def test_gross(self) -> None:
        r = _make_sell_receipt(
            "AAPL", quantity=10.0, price=6.0, fee_rate=0.0, tax_rate=0.0
        )
        assert r.gross == 60.0

    def test_net_is_gross_minus_costs(self) -> None:
        r = _make_sell_receipt(
            "AAPL", quantity=10.0, price=6.0, fee_rate=0.02, tax_rate=0.0
        )
        assert abs(r.net - (r.gross - r.fees - r.taxes)) < 1e-9

    def test_action(self) -> None:
        r = _make_sell_receipt(
            "AAPL", quantity=1.0, price=1.0, fee_rate=0.0, tax_rate=0.0
        )
        assert r.action == "SELL"

    def test_zero_fees_zero_taxes_net_equals_gross(self) -> None:
        r = _make_sell_receipt(
            "AAPL", quantity=5.0, price=10.0, fee_rate=0.0, tax_rate=0.0
        )
        assert abs(r.net - r.gross) < 1e-9


@pytest.mark.unit
class TestMockBrokerLedger:
    def test_buy_appends_receipt(self) -> None:
        from examples.brokers.mockbroker import MockBroker

        broker = MockBroker()
        broker.buy("AAPL", 50.0)
        assert len(broker.ledger) == 1
        assert broker.ledger[0].action == "BUY"

    def test_sell_appends_receipt(self) -> None:
        from examples.brokers.mockbroker import MockBroker

        broker = MockBroker()
        broker.buy("AAPL", 50.0)
        broker.sell("AAPL", 50.0)
        assert len(broker.ledger) == 2
        assert broker.ledger[1].action == "SELL"

    def test_receipts_are_balanced(self) -> None:
        from examples.brokers.mockbroker import MockBroker

        broker = MockBroker()
        broker.buy("AAPL", 50.0)
        broker.sell("AAPL", 50.0)
        assert all(r.balanced() for r in broker.ledger)
