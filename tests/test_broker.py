import pytest

from examples.brokers.mockbroker import MockBroker


@pytest.mark.unit
class TestMockBroker:
    def test_initial_capital(self) -> None:
        assert MockBroker().capital() == 500.0

    def test_initial_position(self) -> None:
        assert MockBroker().position("AAPL") == 0.0

    def test_buy_returns_position(self) -> None:
        broker = MockBroker()
        result = broker.buy("AAPL", 100.0)
        assert result == 100.0

    def test_sell_returns_capital(self) -> None:
        broker = MockBroker()
        broker.buy("AAPL", 100.0)
        result = broker.sell("AAPL", 100.0)
        assert result == 100.0

    def test_buy_depletes_capital(self) -> None:
        broker = MockBroker()
        broker.buy("AAPL", 500.0)
        assert broker.current_capital == 0.0

    def test_sell_clears_position(self) -> None:
        broker = MockBroker()
        broker.buy("AAPL", 100.0)
        broker.sell("AAPL", 100.0)
        assert broker.current_position == 0.0
