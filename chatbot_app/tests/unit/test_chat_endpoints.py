from unittest.mock import patch

from tests.factories.graph_state_factory import generate_graph_state


def test_chat_success(client):
    # Mock response from the graph_flow.invoke method
    mock_response = generate_graph_state()

    # Mock the invoke method in the graph_flow module
    with patch("main.graph_flow.invoke", return_value=mock_response):
        response = client.post("/chat", json={"question": "What is AI?"})
        assert response.status_code == 200
        assert response.json() == {"response": mock_response}
